#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/pos-backend"
FRONTEND_DIR="$SCRIPT_DIR/pos-frontend"

fail() {
  echo "ERROR: $1" >&2
  exit 1
}

info() {
  echo "INFO: $1"
}

usage() {
  cat <<EOF
Usage: $0 [preflight|backend|frontend|all|help]

Commands:
  preflight   Verify prerequisites and required files, then exit.
  backend     Start the Python backend with uvicorn.
  frontend    Start the frontend with npm.
  all         Start backend and frontend together.
  help        Show this help text.

Examples:
  $0 preflight
  $0 backend
  $0 frontend
  $0 all
EOF
  exit 0
}

validate_dir() {
  [[ -d "$1" ]] || fail "Required directory not found: $1"
}

check_command() {
  if command -v "$1" >/dev/null 2>&1; then
    info "Found $1"
    return 0
  fi
  return 1
}

find_virtualenv_python() {
  if [[ -n "${VIRTUAL_ENV:-}" ]]; then
    if [[ -x "$VIRTUAL_ENV/bin/python" ]]; then
      echo "$VIRTUAL_ENV/bin/python"
      return 0
    fi
    if [[ -x "$VIRTUAL_ENV/Scripts/python.exe" ]]; then
      echo "$VIRTUAL_ENV/Scripts/python.exe"
      return 0
    fi
  fi

  local bases=("$SCRIPT_DIR" "$BACKEND_DIR")
  local candidates=()
  for base in "${bases[@]}"; do
    candidates+=("$base/.venv" "$base/venv" "$base/env" "$base/.env" "$base/virtualenv" "$base/pyenv" "$base/python-env")
    shopt -s nullglob
    for dir in "$base"/{venv*,env*,.venv*,.env*}; do
      candidates+=("$dir")
    done
    shopt -u nullglob
  done

  for dir in "${candidates[@]}"; do
    if [[ -d "$dir" ]]; then
      if [[ -x "$dir/bin/python" ]]; then
        echo "$dir/bin/python"
        return 0
      fi
      if [[ -x "$dir/Scripts/python.exe" ]]; then
        echo "$dir/Scripts/python.exe"
        return 0
      fi
    fi
  done

  return 1
}

find_python() {
  local venv_python
  if venv_python="$(find_virtualenv_python)" && [[ -n "$venv_python" ]]; then
    info "Utilisation du Python du virtualenv : $venv_python"
    echo "$venv_python"
    return 0
  fi

  if check_command python; then
    echo "python"
    return 0
  fi
  if check_command python3; then
    echo "python3"
    return 0
  fi
  fail "Python n'est pas disponible. Installez Python 3.11+ et relancez le script."
}

preflight() {
  info "Vérification des dossiers du projet..."
  validate_dir "$BACKEND_DIR"
  validate_dir "$FRONTEND_DIR"

  info "Vérification des dépendances..."
  PYTHON_CMD="$(find_python)"
  if ! "$PYTHON_CMD" -m uvicorn --help >/dev/null 2>&1; then
    fail "uvicorn n'est pas installé dans l'environnement Python. Installez les dépendances du backend."
  fi
  if ! check_command npm; then
    fail "npm n'est pas disponible. Installez Node.js et npm."
  fi

  if [[ ! -f "$FRONTEND_DIR/package.json" ]]; then
    fail "Fichier package.json introuvable dans pos-frontend."
  fi

  info "Préflight terminé. Tous les prérequis clés sont présents."
}

backend() {
  PYTHON_CMD="$(find_python)"
  info "Démarrage du backend Python avec uvicorn..."
  cd "$BACKEND_DIR"
  exec "$PYTHON_CMD" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

frontend() {
  info "Démarrage du frontend avec npm..."
  cd "$FRONTEND_DIR"
  if [[ ! -d "node_modules" ]]; then
    info "Installation des dépendances frontend..."
    npm install
  fi
  exec npm run dev -- --host 0.0.0.0 --port 5173
}

all() {
  PYTHON_CMD="$(find_python)"
  info "Démarrage du backend en arrière-plan..."
  cd "$BACKEND_DIR"
  "$PYTHON_CMD" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
  BACKEND_PID=$!

  trap 'echo "Stopping backend..."; kill "$BACKEND_PID" 2>/dev/null || true; exit 0' INT TERM EXIT

  cd "$FRONTEND_DIR"
  if [[ ! -d "node_modules" ]]; then
    info "Installation des dépendances frontend..."
    npm install
  fi
  info "Démarrage du frontend..."
  npm run dev -- --host 0.0.0.0 --port 5173
}

if [[ $# -eq 0 ]]; then
  usage
fi

ACTION="$1"
shift

case "$ACTION" in
  help)
    usage
    ;;
  preflight)
    preflight
    ;;
  backend)
    preflight
    backend
    ;;
  frontend)
    preflight
    frontend
    ;;
  all)
    preflight
    all
    ;;
  *)
    fail "Commande inconnue: $ACTION"
    ;;
esac
