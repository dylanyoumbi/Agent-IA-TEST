# Akademia Formation IA — Guide des participants

Bienvenue dans le laboratoire pédagogique Akademia Formation IA.

Ce laboratoire permet de découvrir les modèles de langage (LLM), les
agents IA, l'orchestration de workflows avec n8n et les architectures
RAG (Retrieval-Augmented Generation).

## 1. Objectifs du TP

À la fin des activités, vous devez être capables de :

- Identifier les composants d'une architecture IA.
- Comprendre le rôle d'Ollama et d'un modèle de langage.
- Découvrir la création visuelle d'un agent IA avec n8n.
- Comprendre les rôles de MinIO et de Qdrant.
- Explorer les fichiers de configuration du projet.
- Observer le fonctionnement des services du laboratoire.

## 2. Environnement de travail

Le laboratoire est hébergé sur un serveur partagé administré par le formateur.

Vous n'avez pas besoin d'installer Docker, Ollama, n8n ou Qdrant sur votre
ordinateur pour suivre le parcours participant.

Les services sont préparés et démarrés par le formateur.

## 3. Connexion au serveur

Depuis un terminal compatible SSH, connectez-vous avec les identifiants
communiqués individuellement par le formateur.

Exemple :

    ssh participant1@81.17.98.238

Chaque participant doit utiliser son propre compte.

Une fois connecté, accédez au répertoire du projet :

    cd /opt/ia-lab

Vérifiez le répertoire courant :

    pwd

## 4. Explorer la documentation et les fichiers

Afficher ce guide :

    cat README.md

Consulter le fichier de configuration Docker Compose :

    cat docker-compose.yml

Pour lire le fichier plus facilement :

    less README.md

Dans less, appuyez sur q pour quitter.

Vous pouvez également explorer les répertoires auxquels votre compte
est autorisé à accéder :

    ls -l
    ls -l data

Certains fichiers ou répertoires peuvent être volontairement inaccessibles.
Ne tentez pas de contourner les permissions.

## 5. Découvrir les composants

### Ollama et le modèle de langage

Ollama exécute les modèles de langage utilisés par le laboratoire.
Le modèle conversationnel préparé pour les exercices est Qwen 2.5 3B.

### n8n

n8n permet de construire visuellement des workflows et des agents IA
en reliant des nœuds, sans avoir à développer toute l'application.

### MinIO

MinIO fournit un stockage objet pour les fichiers et les documents.

### Qdrant

Qdrant est une base de données vectorielle utilisée notamment pour
la recherche sémantique et les architectures RAG.

### PostgreSQL

PostgreSQL assure le stockage de données relationnelles du projet.

### API et interface web

L'API permet aux composants applicatifs de communiquer.
L'interface web fournit un point d'entrée pour utiliser l'application.

## 6. Activités proposées

### Activité 1 — Lire l'architecture

1. Lire la section architecture de ce guide.
2. Examiner docker-compose.yml.
3. Identifier les services, leurs images, leurs ports et leurs volumes.
4. Expliquer le rôle de chaque service.

### Activité 2 — Observer le laboratoire

1. Ouvrir les interfaces web communiquées par le formateur.
2. Identifier les services accessibles.
3. Observer les interfaces et relever les informations importantes.
4. Signaler tout service inaccessible au formateur.

### Activité 3 — Construire un agent IA avec n8n

1. Ouvrir l'interface n8n.
2. Créer un workflow de test selon les consignes du formateur.
3. Ajouter le déclencheur de conversation.
4. Ajouter un nœud AI Agent.
5. Connecter le modèle Ollama préparé pour le TP.
6. Tester l'agent avec une question simple.
7. Observer la réponse et le déroulement du workflow.

### Activité 4 — Comprendre le stockage et le RAG

1. Découvrir l'interface MinIO.
2. Identifier le rôle des documents dans le laboratoire.
3. Découvrir l'interface Qdrant.
4. Expliquer pourquoi une application RAG utilise des embeddings
   et une base de données vectorielle.

## 7. Règles d'utilisation du serveur partagé

- Ne modifiez pas les fichiers du projet.
- Ne supprimez pas de conteneurs, de volumes ou de données.
- Ne lancez pas de commandes Docker qui modifient l'environnement.
- Ne consultez, ne copiez et ne partagez aucun fichier contenant des secrets.
- N'essayez pas d'accéder aux comptes des autres participants.
- Signalez les erreurs au formateur.

Les comptes participants sont prévus pour la consultation et les activités
pédagogiques. Les opérations d'administration sont réservées au formateur.

## 8. Accès aux interfaces web

Les adresses et identifiants des interfaces sont communiqués par le formateur.

Ne supposez pas qu'un service est accessible publiquement simplement parce
qu'il fonctionne sur le serveur.

Si une interface ne répond pas, notez le message affiché et transmettez-le
au formateur. Ne modifiez pas la configuration réseau.

## 9. Reproduire le laboratoire sur sa propre machine

Si vous disposez de votre propre serveur ou machine et souhaitez installer
et reproduire l'ensemble du laboratoire, consultez le guide séparé :

    README_REPRODUCTION.md

Ce second guide décrit le parcours d'installation et de configuration autonome.

## 10. Questions de synthèse

À la fin du TP, vous devez pouvoir expliquer :

1. Quelle est la différence entre un LLM et un agent IA ?
2. Quel est le rôle d'Ollama ?
3. À quoi sert n8n ?
4. Pourquoi utiliser MinIO pour stocker des documents ?
5. Quel est le rôle de Qdrant dans une architecture RAG ?
6. Pourquoi séparer l'API, l'interface web et les bases de données ?
7. Pourquoi faut-il protéger les fichiers de configuration contenant des secrets ?

Bon TP !
