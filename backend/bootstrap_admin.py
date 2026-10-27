import os
import getpass
import psycopg
from pwdlib import PasswordHash

url = (f"host=postgres dbname={os.environ['POSTGRES_DB']} user={os.environ['POSTGRES_USER']} password={os.environ['POSTGRES_PASSWORD']}")
username = input("Nom du compte administrateur [admin]: ").strip() or "admin"
password = getpass.getpass("Mot de passe admin (12 caractères minimum) : ")
confirm = getpass.getpass("Confirmer le mot de passe : ")
if password != confirm or len(password) < 12:
    raise SystemExit("Erreur : les mots de passe doivent correspondre et compter au moins 12 caractères.")
with psycopg.connect(url) as conn:
    existing = conn.execute("SELECT id FROM users WHERE username=%s", (username,)).fetchone()
    if existing:
        raise SystemExit("Ce compte existe déjà ; aucune modification effectuée.")
    conn.execute("INSERT INTO users(username,password_hash,role) VALUES (%s,%s,'admin')", (username, PasswordHash.recommended().hash(password)))
print(f"Compte administrateur {username!r} créé.")
