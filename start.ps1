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
  Write-Host "Usage: .\start.ps1 [-Action <preflight|backend|frontend|all|help>] [-Detach]"
  Write-Host "Commands:"
  Write-Host "  preflight   Verify prerequisites, setup venv if missing, then exit."
  Write-Host "  backend     Start the Python backend with uvicorn."
  Write-Host "  frontend    Start the frontend with npm."
  Write-Host "  all         Start backend and frontend together."
  Write-Host "  help        Show this help text."
  Write-Host "Options:"
  Write-Host "  -Detach     Run the service(s) in background / separate processes."
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
    if (Test-Path $pythonExe -PathType Leaf) { return $pythonExe }
    $pythonBin = Join-Path $virtualPath 'bin/python'
    if (Test-Path $pythonBin -PathType Leaf) { return $pythonBin }
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

function Get-BasePython() {
  if (Get-Command python -ErrorAction SilentlyContinue) {
    return 'python'
  }
  if (Get-Command python3 -ErrorAction SilentlyContinue) {
    return 'python3'
  }
  Fail "Python n'est pas disponible. Installez Python 3.11+ et relancez le script."
}

function Find-Python() {
  $venvPython = Find-VirtualEnvPython
  if ($venvPython) {
    return $venvPython
  }
  
  Info "Aucun environnement virtuel trouvé. Création d'un venv dans pos-backend..."
  $basePython = Get-BasePython
  $targetVenv = Join-Path $BackendDir '.venv'
  
  Set-Location $BackendDir
  & $basePython -m venv .venv
  
  $pythonExe = Join-Path $targetVenv 'Scripts\python.exe'
  if (-Not (Test-Path $pythonExe)) {
    $pythonExe = Join-Path $targetVenv 'bin/python'
  }

  if (Test-Path $pythonExe) {
    Info "Environnement virtuel créé avec succès. Installation des dépendances..."
    & $pythonExe -m pip install --upgrade pip
    if (Test-Path (Join-Path $BackendDir 'requirements.txt')) {
      & $pythonExe -m pip install -r requirements.txt
    }
    & $pythonExe -m pip install uvicorn fastapi
    return $pythonExe
  } else {
    Fail "Échec de la création de l'environnement virtuel."
  }
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

  # Un seul fichier de configuration est utilisé à la racine du projet.
  $EnvFile = Join-Path $Root '.env'
  if (-Not (Test-Path $EnvFile)) {
    $FoundExample = $null
    foreach ($name in @('.env.exemple', '.env.example')) {
      $candidateRoot = Join-Path $Root $name
      if (Test-Path $candidateRoot) {
        $FoundExample = $candidateRoot
        break
      }
    }

    if ($FoundExample) {
      Info "Copie de $(Split-Path $FoundExample -Leaf) vers .env..."
      Copy-Item $FoundExample $EnvFile
    } else {
      Info "Attention : Aucun fichier .env.exemple ou .env.example n'a été trouvé."
    }
  }

  $python = Normalize-PythonPath (Find-Python)
  try {
    & $python -m uvicorn --help > $null 2>&1
  } catch {
    Fail "uvicorn n'est pas installé dans l'environnement Python."
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
  $python = Normalize-PythonPath (Find-Python)
  Set-Location $BackendDir

  if ($Detach) {
    Info "Démarrage du backend Python en arrière-plan (détaché)..."
    Start-Process -FilePath $python -ArgumentList '-m','uvicorn','app.main:app','--reload','--host','0.0.0.0','--port','8000'
  } else {
    Info "Démarrage du backend Python avec uvicorn..."
    & $python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  }
}

function Start-Frontend() {
  Set-Location $FrontendDir
  if (-Not (Test-Path 'node_modules' -PathType Container)) {
    Info "Installation des dépendances frontend (npm install)..."
    npm install
  }

  if ($Detach) {
    Info "Démarrage du frontend en arrière-plan (détaché)..."
    Start-Process -FilePath "npm" -ArgumentList 'run','dev','--','--host','0.0.0.0','--port','5173'
  } else {
    Info "Démarrage du frontend avec npm..."
    & npm run dev -- --host 0.0.0.0 --port 5173
  }
}

function Start-All() {
  $python = Normalize-PythonPath (Find-Python)
  
  Info "Démarrage du backend en arrière-plan..."
  Set-Location $BackendDir
  Start-Process -FilePath $python -ArgumentList '-m','uvicorn','app.main:app','--reload','--host','0.0.0.0','--port','8000'

  Set-Location $FrontendDir
  if (-Not (Test-Path 'node_modules' -PathType Container)) {
    Info "Installation des dépendances frontend (npm install)..."
    npm install
  }

  if ($Detach) {
    Info "Démarrage du frontend en arrière-plan..."
    Start-Process -FilePath "npm" -ArgumentList 'run','dev','--','--host','0.0.0.0','--port','5173'
  } else {
    Info "Démarrage du frontend..."
    & npm run dev -- --host 0.0.0.0 --port 5173
  }
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
