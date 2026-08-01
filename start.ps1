param(
  [Parameter(Position=0)]
  [ValidateSet('preflight','backend','frontend','all','help')]
  [string]$Action = 'help',

  [switch]$Detach
)

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $Root 'pos-backend'
$FrontendDir = Join-Path $Root 'pos-frontend'

function Fail($Message) {
  Write-Error "ERROR: $Message"
  exit 1
}

function Info($Message) {
  Write-Host "INFO: $Message"
}

function Usage() {
  Write-Host "Usage: .\start.ps1 [-Action <preflight|backend|frontend|all|help>]"
  Write-Host "Commands:"
  Write-Host "  preflight   Verify prerequisites and required files, then exit."
  Write-Host "  backend     Start the Python backend with uvicorn."
  Write-Host "  frontend    Start the frontend with npm."
  Write-Host "  all         Start backend and frontend together."
  Write-Host "  help        Show this help text."
  exit 0
}

function ValidateDir($path) {
  if (-Not (Test-Path $path -PathType Container)) {
    Fail "Required directory not found: $path"
  }
}

function Find-VirtualEnvPython() {
  if ($env:VIRTUAL_ENV) {
    $virtualPath = $env:VIRTUAL_ENV
    $pythonExe = Join-Path $virtualPath 'Scripts\python.exe'
    if (Test-Path $pythonExe -PathType Leaf) {
      return $pythonExe
    }
    $pythonBin = Join-Path $virtualPath 'bin/python'
    if (Test-Path $pythonBin -PathType Leaf) {
      return $pythonBin
    }
  }

  $searchPaths = @($Root, $BackendDir)
  $patterns = @('venv*','env*','.venv*','.env*','virtualenv','pyenv','python-env')
  foreach ($base in $searchPaths) {
    foreach ($pattern in $patterns) {
      Get-ChildItem -Path $base -Directory -Filter $pattern -ErrorAction SilentlyContinue | ForEach-Object {
        $candidate = $_.FullName
        $pythonExe = Join-Path $candidate 'Scripts\python.exe'
        if (Test-Path $pythonExe -PathType Leaf) { return $pythonExe }
        $pythonBin = Join-Path $candidate 'bin/python'
        if (Test-Path $pythonBin -PathType Leaf) { return $pythonBin }
      }
    }
  }
  return $null
}

function Find-Python() {
  $venvPython = Find-VirtualEnvPython
  if ($venvPython) {
    Info "Utilisation du Python du virtualenv : $venvPython"
    return $venvPython
  }
  if (Get-Command python -ErrorAction SilentlyContinue) {
    return 'python'
  }
  if (Get-Command python3 -ErrorAction SilentlyContinue) {
    return 'python3'
  }
  Fail "Python n'est pas disponible. Installez Python 3.11+ et relancez le script."
}

function Normalize-PythonPath($python) {
  if ($python -is [System.Array]) {
    return $python[0]
  }
  return $python
}

function Preflight() {
  Info "Vérification des dossiers du projet..."
  ValidateDir $BackendDir
  ValidateDir $FrontendDir

  $python = Find-Python
  try {
    & $python -m uvicorn --help > $null 2>&1
  } catch {
    Fail "uvicorn n'est pas installé dans l'environnement Python. Installez les dépendances du backend."
  }

  if (-Not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Fail "npm n'est pas disponible. Installez Node.js et npm."
  }

  if (-Not (Test-Path (Join-Path $FrontendDir 'package.json') -PathType Leaf)) {
    Fail "Fichier package.json introuvable dans pos-frontend."
  }

  Info "Préflight terminé. Tous les prérequis clés sont présents."
}

function Start-Backend() {
  $python = Find-Python
  Info "Démarrage du backend Python avec uvicorn..."
  Set-Location $BackendDir
  & $python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

function Start-Frontend() {
  Info "Démarrage du frontend avec npm..."
  Set-Location $FrontendDir
  if (-Not (Test-Path 'node_modules' -PathType Container)) {
    Info "Installation des dépendances frontend..."
    npm install
  }
  & npm run dev -- --host 0.0.0.0 --port 5173
}

function Start-All() {
  $python = Normalize-PythonPath (Find-Python)
  Info "Démarrage du backend en arrière-plan..."
  Set-Location $BackendDir
  Start-Process -NoNewWindow -FilePath $python -ArgumentList '-m','uvicorn','app.main:app','--reload','--host','0.0.0.0','--port','8000'

  Set-Location $FrontendDir
  if (-Not (Test-Path 'node_modules' -PathType Container)) {
    Info "Installation des dépendances frontend..."
    npm install
  }
  Info "Démarrage du frontend..."
  & npm run dev -- --host 0.0.0.0 --port 5173
}

if ($PSBoundParameters.ContainsKey('Action')) {
  $Action = $Action
} else {
  $Action = 'help'
}

switch ($Action) {
  'help' { Usage }
  'preflight' { Preflight }
  'backend' { Preflight; Start-Backend }
  'frontend' { Preflight; Start-Frontend }
  'all' { Preflight; Start-All }
  default { Fail "Commande inconnue: $Action" }
}
