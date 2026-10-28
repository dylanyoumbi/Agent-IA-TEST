# Akademia Formation IA — Guide des participants

Bienvenue dans le laboratoire pédagogique Akademia Formation IA.

Ce laboratoire permet de découvrir les modèles de langage (LLM), les agents IA, l'orchestration de workflows avec n8n et les architectures RAG (Retrieval-Augmented Generation).

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

Vous n'avez pas besoin d'installer Docker, Ollama, n8n ou Qdrant sur votre ordinateur pour suivre le parcours participant.

Les services sont préparés et démarrés par le formateur.

## 3. Connexion au serveur

Chaque participant utilise exclusivement le compte SSH qui lui a été attribué par le formateur.

Exemple de connexion SSH classique :

```bash
ssh participant1@81.17.98.238
```

Les comptes sont individuels. Ne partagez jamais vos identifiants.

### Accéder à votre espace n8n

Pour accéder à votre espace n8n depuis Windows, ouvrez PowerShell et exécutez uniquement la commande correspondant à votre binôme.

**Binôme 1**

```powershell
ssh -N -L 15679:127.0.0.1:5679 participant1@81.17.98.238
```

Interface : http://localhost:15679

**Binôme 2**

```powershell
ssh -N -L 15680:127.0.0.1:5680 participant2@81.17.98.238
```

Interface : http://localhost:15680

**Binôme 3**

```powershell
ssh -N -L 15681:127.0.0.1:5681 participant3@81.17.98.238
```

Interface : http://localhost:15681

**Binôme 4**

```powershell
ssh -N -L 15682:127.0.0.1:5682 participant4@81.17.98.238
```

Interface : http://localhost:15682

**Binôme 5**

```powershell
ssh -N -L 15683:127.0.0.1:5683 participant5@81.17.98.238
```

Interface : http://localhost:15683

Gardez la fenêtre PowerShell ouverte pendant toute la session. Pour fermer le tunnel à la fin du TP, utilisez `Ctrl+C`.

Ne lancez pas la commande d'un autre binôme et n'utilisez pas le compte `root`.

### Créer votre compte n8n

Lors de la première ouverture de votre espace n8n, le formulaire de création du compte propriétaire apparaît.

Chaque binôme doit renseigner :
- une adresse e-mail ;
- son prénom ;
- son nom ;
- un mot de passe robuste, comportant au moins 8 caractères, un chiffre et une majuscule.

Conservez vos identifiants en lieu sûr. Ne partagez pas votre compte avec les autres binômes.

Chaque espace possède son propre stockage et ses propres workflows n8n.

**Important :** les commandes individuelles doivent être accompagnées de restrictions SSH configurées par l'administrateur afin que chaque compte ne puisse transférer que le port qui lui est attribué.

## 4. Explorer la documentation et les fichiers

Si votre compte est autorisé à accéder au répertoire du projet, vous pouvez consulter les fichiers en lecture seule.

Afficher le guide :

```bash
cat README.md
```

Consulter le fichier Docker Compose si les permissions vous y autorisent :

```bash
cat docker-compose.yml
```

Lire le guide plus facilement :

```bash
less README.md
```

Dans `less`, appuyez sur `q` pour quitter.

Explorer les répertoires autorisés :

```bash
ls -l
ls -l data
```

Certains fichiers ou répertoires peuvent être volontairement inaccessibles. Ne tentez pas de contourner les permissions.

## 5. Découvrir les composants

### Ollama et le modèle de langage

Ollama exécute les modèles de langage utilisés par le laboratoire. Le modèle conversationnel préparé pour les exercices est Qwen 2.5 3B (`qwen2.5:3b`).

### n8n

n8n permet de construire visuellement des workflows et des agents IA en reliant des nœuds, sans avoir à développer toute l'application.

### MinIO

MinIO fournit un stockage objet pour les fichiers et les documents.

### Qdrant

Qdrant est une base de données vectorielle utilisée notamment pour la recherche sémantique et les architectures RAG.

### PostgreSQL

PostgreSQL assure le stockage de données relationnelles du projet.

### API et interface web

L'API permet aux composants applicatifs de communiquer. L'interface web fournit un point d'entrée pour utiliser l'application.

## 6. Activités proposées

### Activité 1 — Lire l'architecture

1. Lire la section architecture de ce guide.
2. Examiner `docker-compose.yml` si l'accès est autorisé.
3. Identifier les services, leurs images, leurs ports et leurs volumes.
4. Expliquer le rôle de chaque service.

### Activité 2 — Observer le laboratoire

1. Ouvrir l'interface n8n attribuée à votre binôme.
2. Identifier les services accessibles.
3. Observer les interfaces et relever les informations importantes.
4. Signaler tout service inaccessible au formateur.

### Activité 3 — Construire un agent IA avec n8n

1. Ouvrir votre interface n8n.
2. Créer un workflow de test selon les consignes du formateur.
3. Ajouter le déclencheur de conversation.
4. Ajouter un nœud AI Agent.
5. Connecter le modèle Ollama préparé pour le TP.
6. Tester l'agent avec une question simple.
7. Observer la réponse et le déroulement du workflow.

### Activité 4 — Comprendre le stockage et le RAG

1. Découvrir l'interface MinIO si elle vous est accessible.
2. Identifier le rôle des documents dans le laboratoire.
3. Découvrir Qdrant selon les consignes du formateur.
4. Expliquer pourquoi une application RAG utilise des embeddings et une base de données vectorielle.

## 7. Règles d'utilisation du serveur partagé

- Ne modifiez pas les fichiers du projet.
- Ne supprimez pas de conteneurs, de volumes ou de données.
- Ne lancez pas de commandes Docker qui modifient l'environnement.
- Ne consultez, ne copiez et ne partagez aucun fichier contenant des secrets.
- N'essayez pas d'accéder aux comptes ou aux espaces des autres participants.
- Ne partagez pas les clés de chiffrement des instances.
- Signalez les erreurs au formateur.

Les comptes participants sont prévus pour les activités pédagogiques. Les opérations d'administration sont réservées au formateur.

## 8. Accès aux interfaces web et dépannage

Les adresses des espaces n8n sont indiquées à la section 3.

Si votre interface ne répond pas :

1. Vérifiez que la fenêtre PowerShell est toujours ouverte.
2. Vérifiez que vous utilisez l'adresse attribuée à votre binôme.
3. Notez le message affiché et transmettez-le au formateur.
4. Ne modifiez pas la configuration réseau et ne tentez pas d'accéder aux ports des autres binômes.

Ne supposez pas qu'un service est accessible publiquement simplement parce qu'il fonctionne sur le serveur.

## 9. Reproduire le laboratoire sur sa propre machine

Si vous disposez de votre propre serveur ou machine et souhaitez installer et reproduire l'ensemble du laboratoire, consultez le guide séparé :

`README_REPRODUCTION.md`

Ce second guide décrit le parcours d'installation et de configuration autonome. Il est distinct du présent guide participant.

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
