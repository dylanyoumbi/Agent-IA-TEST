import hashlib
import os
import uuid
from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import Annotated

import jwt
import requests
from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from minio import Minio
from pydantic import BaseModel, Field
from pwdlib import PasswordHash
from pypdf import PdfReader
from psycopg.rows import dict_row
import psycopg
from qdrant_client import QdrantClient, models

APP_NAME = os.getenv("APP_NAME", "Akademia Formation")
DATABASE_URL = (f"host=postgres dbname={os.environ['POSTGRES_DB']} "
                f"user={os.environ['POSTGRES_USER']} password={os.environ['POSTGRES_PASSWORD']}")
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
JWT_ALGORITHM = "HS256"
CHAT_MODEL = os.getenv("CHAT_MODEL", "qwen2.5:3b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434").rstrip("/")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_USER = os.environ["MINIO_ROOT_USER"]
MINIO_PASSWORD = os.environ["MINIO_ROOT_PASSWORD"]
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "documents")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "documents")
MAX_PDF_BYTES = 30 * 1024 * 1024
password_hasher = PasswordHash.recommended()
bearer = OAuth2PasswordBearer(tokenUrl="/auth/login")
app = FastAPI(title=f"{APP_NAME} — API du laboratoire IA", description="API d'authentification, de gestion des espaces documentaires et de RAG privé. Tous les endpoints protégés nécessitent un jeton Bearer.", version="2.0.0", docs_url="/docs", redoc_url="/redoc", openapi_url="/openapi.json")


def db_conn():
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        yield conn


def minio_client():
    client = Minio(MINIO_ENDPOINT, access_key=MINIO_USER, secret_key=MINIO_PASSWORD, secure=False)
    if not client.bucket_exists(MINIO_BUCKET):
        client.make_bucket(MINIO_BUCKET)
    return client


def qdrant_client():
    return QdrantClient(url=QDRANT_URL, timeout=30)


def make_token(user):
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": str(user["id"]), "iat": now, "exp": now + timedelta(hours=8)}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def get_current_user(token: Annotated[str, Depends(bearer)], conn=Depends(db_conn)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = uuid.UUID(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Jeton invalide ou expiré", headers={"WWW-Authenticate": "Bearer"})
    user = conn.execute("SELECT id, username, role, is_active FROM users WHERE id=%s", (user_id,)).fetchone()
    if not user or not user["is_active"]:
        raise HTTPException(status_code=401, detail="Compte inactif ou introuvable")
    return user


def admin_only(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé à l'administrateur")
    return user


def authorized_directory(conn, user, directory_id, permission="can_read"):
    d = conn.execute("""SELECT d.*, u.username AS owner_username FROM directories d JOIN users u ON u.id=d.owner_id WHERE d.id=%s""", (directory_id,)).fetchone()
    if not d:
        raise HTTPException(status_code=404, detail="Répertoire introuvable")
    if user["role"] == "admin" or d["owner_id"] == user["id"]:
        return d
    p = conn.execute(f"SELECT {permission} AS allowed FROM directory_permissions WHERE directory_id=%s AND user_id=%s", (directory_id, user["id"])).fetchone()
    if not p or not p["allowed"]:
        raise HTTPException(status_code=403, detail="Vous n'avez pas accès à ce répertoire")
    return d


def chunks(text, size=900, overlap=150):
    text = " ".join(text.split())
    result, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        result.append(text[start:end])
        if end == len(text): break
        start = end - overlap
    return result


def embed(texts):
    vectors = []
    for text in texts:
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": text},
            timeout=300,
        )
        response.raise_for_status()
        vectors.append(response.json()["embedding"])
    return vectors


def ensure_collection(size):
    client = qdrant_client()
    if QDRANT_COLLECTION not in [x.name for x in client.get_collections().collections]:
        client.create_collection(collection_name=QDRANT_COLLECTION, vectors_config=models.VectorParams(size=size, distance=models.Distance.COSINE))


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")
    password: str = Field(min_length=12, max_length=128)
    role: str = Field(default="user", pattern="^(admin|user)$")


class DirectoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class PermissionUpdate(BaseModel):
    can_read: bool = True
    can_write: bool = False
    can_delete: bool = False


class ChatQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=8000)


@app.get("/health", tags=["Système"])
def health():
    return {"status": "ok", "app": APP_NAME, "model": CHAT_MODEL, "embedding_model": EMBED_MODEL}


@app.post("/auth/login", tags=["Authentification"])
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], conn=Depends(db_conn)):
    user = conn.execute("SELECT id, username, password_hash, role, is_active FROM users WHERE username=%s", (form.username,)).fetchone()
    if not user or not user["is_active"] or not password_hasher.verify(form.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Identifiant ou mot de passe incorrect")
    return {"access_token": make_token(user), "token_type": "bearer", "username": user["username"], "role": user["role"]}


@app.get("/auth/me", tags=["Authentification"])
def me(user=Depends(get_current_user)):
    return {"id": str(user["id"]), "username": user["username"], "role": user["role"]}


@app.get("/admin/users", tags=["Administration"])
def list_users(_admin=Depends(admin_only), conn=Depends(db_conn)):
    return [{"id": str(x["id"]), "username": x["username"], "role": x["role"], "is_active": x["is_active"], "created_at": x["created_at"].isoformat()} for x in conn.execute("SELECT id, username, role, is_active, created_at FROM users ORDER BY created_at").fetchall()]


@app.post("/admin/users", status_code=201, tags=["Administration"])
def create_user(body: UserCreate, _admin=Depends(admin_only), conn=Depends(db_conn)):
    try:
        row = conn.execute("INSERT INTO users(username,password_hash,role) VALUES (%s,%s,%s) RETURNING id,username,role,is_active", (body.username, password_hasher.hash(body.password), body.role)).fetchone()
        conn.commit()
    except psycopg.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=409, detail="Ce nom d'utilisateur existe déjà")
    return {"id": str(row["id"]), "username": row["username"], "role": row["role"], "is_active": row["is_active"]}


@app.get("/directories", tags=["Répertoires"])
def list_directories(user=Depends(get_current_user), conn=Depends(db_conn)):
    if user["role"] == "admin":
        rows = conn.execute("SELECT d.id,d.name,d.owner_id,u.username owner_username,d.created_at FROM directories d JOIN users u ON u.id=d.owner_id ORDER BY d.created_at DESC").fetchall()
    else:
        rows = conn.execute("""SELECT DISTINCT d.id,d.name,d.owner_id,u.username owner_username,d.created_at FROM directories d JOIN users u ON u.id=d.owner_id LEFT JOIN directory_permissions p ON p.directory_id=d.id AND p.user_id=%s WHERE d.owner_id=%s OR p.can_read=TRUE ORDER BY d.created_at DESC""", (user["id"], user["id"])).fetchall()
    return [{"id": str(r["id"]), "name": r["name"], "owner_id": str(r["owner_id"]), "owner": r["owner_username"], "created_at": r["created_at"].isoformat()} for r in rows]


@app.post("/directories", status_code=201, tags=["Répertoires"])
def create_directory(body: DirectoryCreate, user=Depends(get_current_user), conn=Depends(db_conn)):
    directory_id = uuid.uuid4()
    # Storage keys use opaque UUIDs, never a user-provided filesystem path.
    row = conn.execute("INSERT INTO directories(id,name,owner_id,storage_key) VALUES (%s,%s,%s,%s) RETURNING id,name,owner_id", (directory_id, body.name.strip(), user["id"], str(directory_id))).fetchone()
    conn.execute("INSERT INTO directory_permissions(directory_id,user_id,can_read,can_write,can_delete) VALUES (%s,%s,TRUE,TRUE,TRUE) ON CONFLICT DO NOTHING", (directory_id, user["id"]))
    conn.commit()
    return {"id": str(row["id"]), "name": row["name"], "owner": user["username"]}


@app.put("/admin/directories/{directory_id}/permissions/{username}", tags=["Administration"])
def set_permission(directory_id: uuid.UUID, username: str, body: PermissionUpdate, _admin=Depends(admin_only), conn=Depends(db_conn)):
    directory = conn.execute("SELECT id FROM directories WHERE id=%s", (directory_id,)).fetchone()
    target = conn.execute("SELECT id FROM users WHERE username=%s", (username,)).fetchone()
    if not directory or not target:
        raise HTTPException(status_code=404, detail="Répertoire ou utilisateur introuvable")
    conn.execute("""INSERT INTO directory_permissions(directory_id,user_id,can_read,can_write,can_delete) VALUES (%s,%s,%s,%s,%s) ON CONFLICT(directory_id,user_id) DO UPDATE SET can_read=EXCLUDED.can_read,can_write=EXCLUDED.can_write,can_delete=EXCLUDED.can_delete""", (directory_id, target["id"], body.can_read, body.can_write, body.can_delete))
    conn.commit()
    return {"ok": True, "directory_id": str(directory_id), "username": username, **body.model_dump()}


@app.post("/directories/{directory_id}/documents", status_code=201, tags=["Documents & RAG"])
async def upload_pdf(directory_id: uuid.UUID, file: UploadFile = File(...), user=Depends(get_current_user), conn=Depends(db_conn)):
    directory = authorized_directory(conn, user, directory_id, "can_write")
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés")
    data = await file.read(MAX_PDF_BYTES + 1)
    if len(data) > MAX_PDF_BYTES:
        raise HTTPException(status_code=413, detail="PDF limité à 30 Mo")
    digest = hashlib.sha256(data).hexdigest()[:20]
    safe_name = os.path.basename(file.filename).replace("/", "_").replace("\\", "_")
    object_name = f"{directory['storage_key']}/{digest}_{safe_name}"
    try:
        minio_client().put_object(MINIO_BUCKET, object_name, BytesIO(data), len(data), content_type="application/pdf")
        reader = PdfReader(BytesIO(data))
        texts, payloads = [], []
        for page_no, page in enumerate(reader.pages, start=1):
            for index, chunk in enumerate(chunks(page.extract_text() or "")):
                texts.append(chunk)
                payloads.append({"directory_id": str(directory_id), "owner_id": str(directory["owner_id"]), "uploaded_by": str(user["id"]), "filename": safe_name, "object_name": object_name, "page": page_no, "chunk_index": index, "text": chunk})
        if not texts:
            raise HTTPException(status_code=422, detail="Aucun texte extractible : un PDF scanné nécessite un OCR")
        vectors = embed(texts)
        ensure_collection(len(vectors[0]))
        points = [models.PointStruct(id=str(uuid.uuid4()), vector=v, payload=p) for v, p in zip(vectors, payloads)]
        qdrant_client().upsert(collection_name=QDRANT_COLLECTION, points=points, wait=True)
        return {"ok": True, "filename": safe_name, "pages": len(reader.pages), "chunks": len(texts), "directory_id": str(directory_id)}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Indexation impossible : {type(exc).__name__}: {exc}")


@app.get("/directories/{directory_id}/documents", tags=["Documents & RAG"])
def list_documents(directory_id: uuid.UUID, user=Depends(get_current_user), conn=Depends(db_conn)):
    authorized_directory(conn, user, directory_id, "can_read")
    client = qdrant_client()
    if QDRANT_COLLECTION not in [x.name for x in client.get_collections().collections]: return []
    points, _ = client.scroll(collection_name=QDRANT_COLLECTION, scroll_filter=models.Filter(must=[models.FieldCondition(key="directory_id", match=models.MatchValue(value=str(directory_id)))]), limit=1000, with_payload=True, with_vectors=False)
    grouped = {}
    for point in points:
        payload = point.payload or {}
        key = payload.get("object_name")
        item = grouped.setdefault(key, {"filename": payload.get("filename", "document.pdf"), "pages": set(), "chunks": 0})
        item["pages"].add(payload.get("page")); item["chunks"] += 1
    return [{"filename": x["filename"], "pages": len(x["pages"]), "chunks": x["chunks"]} for x in grouped.values()]


@app.post("/directories/{directory_id}/chat", tags=["Documents & RAG"])
def chat(directory_id: uuid.UUID, body: ChatQuestion, user=Depends(get_current_user), conn=Depends(db_conn)):
    authorized_directory(conn, user, directory_id, "can_read")
    client = qdrant_client()
    if QDRANT_COLLECTION not in [x.name for x in client.get_collections().collections]: return {"answer": "Aucun document indexé dans ce répertoire.", "sources": []}
    try:
        vector = embed([body.question])[0]
        hits = client.query_points(collection_name=QDRANT_COLLECTION, query=vector, query_filter=models.Filter(must=[models.FieldCondition(key="directory_id", match=models.MatchValue(value=str(directory_id)))]), limit=5, with_payload=True).points
        if not hits: return {"answer": "Aucun passage pertinent. Ajoutez un PDF puis réessayez.", "sources": []}
        context, sources = [], []
        for hit in hits:
            p = hit.payload or {}
            context.append(f"[Document : {p.get('filename')}, page {p.get('page')}]\n{p.get('text','')}")
            sources.append({"filename": p.get("filename"), "page": p.get("page"), "score": round(float(hit.score or 0), 3)})
        prompt = "Réponds en français uniquement à partir du contexte. Si la réponse manque, dis-le. Cite les documents et pages.\n\nCONTEXTE:\n" + "\n\n".join(context) + "\n\nQUESTION:\n" + body.question
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": CHAT_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "options": {
                    "num_predict": 150,
                },
            },
            timeout=300,
        )
        response.raise_for_status()
        return {"answer": response.json()["message"]["content"], "sources": sources}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Erreur RAG : {type(exc).__name__}: {exc}")
