# Akademia Formation IA — TP LLM, Ollama, n8n et RAG

## 1. Présentation du laboratoire

Ce projet est un laboratoire pédagogique consacré aux modèles de langage
(LLM), aux agents IA, à l'orchestration avec n8n et aux architectures RAG
(Retrieval-Augmented Generation).

L'objectif est de comprendre chaque composant, de l'installation à la
validation, en exécutant les commandes progressivement.

## 2. Architecture

Les services prévus dans Docker Compose sont :

- Ollama : exécution locale des modèles de langage.
- Qwen : modèle conversationnel utilisé pour les tests.
- nomic-embed-text : modèle d'embeddings pour la recherche documentaire.
- n8n : création et orchestration des workflows.
- PostgreSQL : base de données relationnelle.
- Qdrant : base de données vectorielle.
- MinIO : stockage des documents.
- FastAPI : API backend.
- React et Nginx : interface web.

## 3. Prérequis

Installer :

- Git
- Docker
- Docker Compose v2 (commande `docker compose`)
- Un terminal
- Un navigateur web

Vérifier les installations :

    git --version
    docker --version
    docker compose version

Sous Linux, vérifier également :

    docker info

Si Docker renvoie une erreur de permission, vérifier les droits de l'utilisateur
sur le socket Docker. Ne pas exécuter automatiquement tous les conteneurs en root.

## 4. Récupérer le projet

### Option A — Cloner le dépôt de référence

    git clone --branch dev https://gitlab.com/santoudllo/akademia-formation-ia.git
    cd akademia-formation-ia

### Option B — Forker le projet

1. Ouvrir https://gitlab.com/santoudllo/akademia-formation-ia
2. Cliquer sur Fork si l'option est disponible.
3. Cloner son propre fork en remplaçant IDENTIFIANT par son compte GitLab :

    git clone --branch dev https://gitlab.com/IDENTIFIANT/akademia-formation-ia.git
    cd akademia-formation-ia

Un dépôt privé nécessite les autorisations d'accès correspondantes.

## 5. Préparer la configuration

Créer un fichier de configuration local à partir du modèle :

    cp .env.example .env

Éditer ensuite `.env` et remplacer toutes les valeurs CHANGE_ME par des
valeurs locales adaptées.

Ne jamais publier `.env`, un jeton, un mot de passe ou une clé secrète.

Le fichier `.env.example` est un modèle : il ne contient pas les identifiants
du serveur de formation.

Vérifier la configuration Docker Compose :

    docker compose config --quiet

Si la commande affiche une erreur, corriger la configuration avant de continuer.

## 6. TP 1 — Démarrer Ollama

Démarrer uniquement le service Ollama :

    docker compose up -d ollama

Vérifier son état :

    docker compose ps ollama

Consulter les logs :

    docker compose logs --tail=50 ollama

Vérifier que l'API Ollama répond depuis le conteneur :

    docker compose exec ollama ollama list

Si le service est en cours de démarrage, attendre quelques secondes et réessayer.

## 7. TP 1.1 — Télécharger Qwen

Télécharger le modèle conversationnel :

    docker compose exec ollama ollama pull qwen2.5:3b

Vérifier qu'il est disponible :

    docker compose exec ollama ollama list

Le modèle `qwen2.5:3b` est un modèle de démonstration relativement compact.
Il nécessite tout de même de la mémoire vive et de l'espace disque.

## 8. TP 1.2 — Tester Qwen

Exécuter une première génération :

    docker compose exec ollama ollama run qwen2.5:3b

Dans le terminal interactif, saisir :

    Parle-moi de la France en cinq phrases.

Lire la réponse, puis quitter le mode interactif avec `/bye` si cette commande
est prise en charge par la version utilisée, ou fermer l'entrée interactive.

On peut aussi tester directement l'API Ollama :

    docker compose exec ollama ollama run qwen2.5:3b "Parle-moi de la France."

Résultat attendu : une réponse textuelle produite par le modèle.

## 9. TP 1.3 — Télécharger le modèle d'embeddings

Télécharger le modèle utilisé pour transformer les textes en vecteurs :

    docker compose exec ollama ollama pull nomic-embed-text

Vérifier la présence des deux modèles :

    docker compose exec ollama ollama list

Qwen sert à générer des réponses. `nomic-embed-text` sert à calculer des
embeddings pour la recherche sémantique. Ce sont deux usages différents.

## 10. TP 2 — Démarrer n8n

Démarrer n8n :

    docker compose up -d n8n

Vérifier l'état du conteneur :

    docker compose ps n8n

Examiner les logs :

    docker compose logs --tail=50 n8n

Tester la réponse HTTP depuis le serveur qui héberge Docker :

    curl -I http://127.0.0.1:5678/

Un code HTTP 200, 301, 302 ou parfois 401/403 peut indiquer que le service
répond. Interpréter le résultat avec les logs et la configuration d'authentification.

### Accéder à n8n sur une machine distante

Si Docker publie le port sur 127.0.0.1, il n'est pas directement accessible
depuis un autre ordinateur.

Depuis l'ordinateur de l'étudiant, ouvrir un tunnel SSH :

    ssh -N -L 5678:127.0.0.1:5678 UTILISATEUR@ADRESSE_DU_SERVEUR

Garder le terminal ouvert, puis visiter :

    http://127.0.0.1:5678

Remplacer UTILISATEUR et ADRESSE_DU_SERVEUR par les informations du serveur
autorisé. Ne jamais publier les identifiants SSH dans le dépôt.

## 11. TP 2.1 — Créer un agent IA dans n8n

Créer un workflow comprenant :

1. When chat message received
2. AI Agent
3. Ollama Chat Model
4. Send a message, si l'on choisit le mode de réponse utilisant les nœuds de réponse

Relier la sortie du déclencheur à l'entrée principale de l'AI Agent.

Relier le port Ollama Chat Model au port Chat Model de l'AI Agent.

Configurer le modèle Ollama avec l'adresse interne :

    http://ollama:11434

Sélectionner le modèle :

    qwen2.5:3b

Cette adresse suppose que n8n et Ollama sont sur le même réseau Docker Compose.

Dans le déclencheur Chat, sélectionner le mode de réponse approprié.
Si l'on utilise un nœud Send a message, sélectionner le mode
Using Response Nodes.

Dans Send a message, utiliser l'expression de sortie de l'AI Agent :

    {{ $json.output }}

Tester le workflow avec :

    Parle-moi de la France et présente trois lieux touristiques célèbres.

Résultat attendu : une réponse générée par Qwen et affichée dans le chat.

Selon la version de n8n, vérifier les noms des champs et les options disponibles.
Si le workflow ne répond pas, consulter l'historique d'exécution et les logs.

## 12. TP 3 — Démarrer l'application Akademia

Après les tests Ollama et n8n, démarrer les services applicatifs :

    docker compose up -d --build

Vérifier l'état des services :

    docker compose ps

Consulter les logs d'un service :

    docker compose logs --tail=50 api
    docker compose logs --tail=50 frontend
    docker compose logs --tail=50 postgres
    docker compose logs --tail=50 qdrant
    docker compose logs --tail=50 minio

Vérifier l'API locale depuis la machine qui héberge Docker :

    curl -I http://127.0.0.1:8000/

L'API peut répondre avec un code différent de 200 sur la racine si aucune
route n'y est définie. Consulter la documentation Swagger lorsque disponible.

## 13. Accès local aux interfaces

Les ports peuvent être liés à 127.0.0.1 afin de limiter l'exposition réseau.
Sur une installation locale, utiliser les adresses et ports définis dans
docker-compose.yml.

Pour une installation distante, préférer un tunnel SSH ou un reverse proxy
sécurisé avec HTTPS et authentification. Ne pas exposer directement les
interfaces d'administration ou les bases de données à Internet.

## 14. Dépannage

### Le service ne démarre pas

    docker compose ps
    docker compose logs --tail=100 NOM_DU_SERVICE

### Le modèle Qwen est absent

    docker compose exec ollama ollama list
    docker compose exec ollama ollama pull qwen2.5:3b

### n8n ne répond pas

    docker compose ps n8n
    docker compose logs --tail=50 n8n
    curl -I http://127.0.0.1:5678/

### L'application manque de mémoire

- Arrêter les services non nécessaires au TP.
- Ne pas démarrer simultanément tous les composants si la machine est limitée.
- Utiliser une VM distante autorisée avec suffisamment de RAM et de disque.
- Éviter de télécharger plusieurs grands modèles inutilement.

### Tout arrêter

    docker compose down

Cette commande arrête et supprime les conteneurs du projet, mais conserve
normalement les volumes nommés.

Ne pas utiliser `docker compose down -v` sans comprendre que cette option
supprime les volumes du projet et peut entraîner la perte de données.

## 15. Machines peu puissantes et environnements cloud

Parcours local :
- Installer Docker Desktop sous Windows ou macOS, ou Docker Engine sous Linux.
- Utiliser les modèles compacts du TP.
- Démarrer uniquement les services nécessaires à l'exercice.

Parcours distant :
- Utiliser une VM Linux ou un environnement cloud autorisant Docker Compose.
- Vérifier la RAM, le stockage, les limites CPU et les règles réseau.
- Protéger les interfaces avec un tunnel SSH ou HTTPS.

Un IDE web ne garantit pas la disponibilité d'un démon Docker, du réseau requis
ou des ressources nécessaires au modèle. Vérifier les capacités de l'environnement
avant de lancer les services.

## 16. Travail à rendre

Chaque étudiant doit fournir :

1. La sortie de `docker compose ps ollama`.
2. La liste des modèles obtenue avec `ollama list`.
3. Une capture de la réponse de Qwen.
4. Une capture du workflow n8n fonctionnel.
5. Les éventuelles erreurs rencontrées et leur résolution.
6. Une courte explication de la différence entre LLM, embeddings, agent IA et RAG.

## 17. Sécurité

- Ne jamais versionner `.env`.
- Ne jamais publier de tokens ou mots de passe.
- Ne pas partager les identifiants n8n du formateur.
- Utiliser des identifiants propres à chaque étudiant.
- Ne pas exposer publiquement les ports d'administration sans protection.
- Exporter les workflows n8n et vérifier qu'ils ne contiennent aucun secret
  avant de les publier dans le dépôt.
