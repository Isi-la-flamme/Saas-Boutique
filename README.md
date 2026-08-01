# Tenant Python - Démarrage local

Ce dépôt contient une application POS multi-tenant avec un backend Python et une interface frontend.

## Structure du projet

- `pos-backend/` : application backend Python
- `pos-frontend/` : application frontend JavaScript/React
- `start.sh` : script de démarrage macOS / Linux
- `start.ps1` : script de démarrage Windows PowerShell

## Commandes de démarrage

### macOS / Linux

```bash
chmod +x start.sh
./start.sh preflight
./start.sh backend
./start.sh frontend
./start.sh all
```

### Windows (PowerShell)

```powershell
.\start.ps1 -Action preflight
.\start.ps1 -Action backend
.\start.ps1 -Action frontend
.\start.ps1 -Action all
```

## Actions disponibles

- `preflight` : vérifie les dépendances et les fichiers requis, puis quitte
- `backend` : démarre le backend Python avec uvicorn
- `frontend` : démarre le frontend avec npm
- `all` : démarre backend et frontend ensemble
- `help` : affiche l’aide

## Vérifications effectuées par les scripts

Les scripts de lancement vérifient explicitement :

- la présence des dossiers `pos-backend/` et `pos-frontend/`
- la présence d’un environnement virtuel local (`venv`, `.venv`, `env`, `.env`, etc.) et son utilisation
- que Python est installé
- que `uvicorn` est disponible dans l’environnement Python
- que `npm` est disponible
- que `pos-frontend/package.json` existe

Si une étape critique échoue, le script s’arrête et affiche un message clair.

## Prérequis

- Python 3.11+ installé
- `uvicorn` installé dans l’environnement Python (`pip install -r pos-backend/requirements.txt` ou `pip install uvicorn`)
- Node.js et npm installés
- Dossier racine du dépôt
- Accès en lecture aux dossiers `pos-backend/` et `pos-frontend/`

## Exemple de lancement

```bash
./start.sh preflight
./start.sh backend
```

```powershell
.\start.ps1 -Action preflight
.\start.ps1 -Action backend
```
