# Tenant-python

Ce dépôt contient une application POS multi-tenant avec un backend Python et une interface frontend.

## Structure du projet

- `docker-compose.yml` : configuration Docker Compose pour `backend`, `frontend`, et `db`
- `pos-backend/` : application backend Python
- `pos-frontend/` : application frontend JavaScript/React

## Démarrage multiplateforme

### Windows

Ouvrez PowerShell dans le dossier racine et exécutez :

```powershell
.
start.ps1 -Action preflight
.
start.ps1 -Action up -Detach
```

### macOS / Linux

Ouvrez un terminal dans le dossier racine puis exécutez :

```bash
chmod +x start.sh
./start.sh preflight
./start.sh up --detach
```

## Commandes disponibles

- `preflight` : vérifie les fichiers requis et l’accès à Docker
- `up` : démarre le projet via Docker Compose
- `down` : arrête et supprime les conteneurs
- `ps` : affiche l’état des services
- `help` : affiche l’aide

## Prérequis

- Docker Engine installé et lancé
- Docker Compose disponible (`docker compose` ou `docker-compose`)
- Les dossiers `pos-backend` et `pos-frontend` présents
- Le fichier `docker-compose.yml` présent à la racine

## Vérification manuelle

Le script vérifie automatiquement :

- la présence de `docker-compose.yml`
- la présence des dossiers `pos-backend/` et `pos-frontend/`
- que Docker est installé et que le démon Docker fonctionne
- l’existence éventuelle d’un fichier `.env` racine

Si une vérification échoue, le script arrête l’exécution et affiche un message explicite.

## Exemple de lancement

```bash
./start.sh preflight
./start.sh up --detach
```

ou sur Windows :

```powershell
.
start.ps1 -Action preflight
.
start.ps1 -Action up -Detach
```
