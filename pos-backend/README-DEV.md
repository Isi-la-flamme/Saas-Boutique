# 🏪 Tenant SaaS - Multi-tenant Platform with POS

Une plateforme SaaS multi-tenant complète avec gestion de produits, crédits clients, factures, portefeuille et point de vente (POS).

## 📋 Table des matières

- [Architecture](#-architecture)
- [Technologies](#-technologies)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Démarrage](#-démarrage)
- [Base de données](#-base-de-données)
- [API Endpoints](#-api-endpoints)
- [Structure du projet](#-structure-du-projet)
- [Commandes utiles](#-commandes-utiles)
- [Dépannage](#-dépannage)
- [Contribution](#-contribution)
- [Licence](#-licence)

---

## 🏗 Architecture

┌─────────────────────────────────────────────────────────────┐
│ NGINX (Port 80) │
│ Reverse Proxy │
└─────────────────────────────────────────────────────────────┘
│
┌───────────────────┼───────────────────┐
│ │ │
┌───────▼───────┐ ┌───────▼───────┐ ┌───────▼───────┐
│ Frontend │ │ Backend │ │ PostgreSQL │
│ Next.js │──▶│ Node.js │──▶│ Database │
│ Port 3001 │ │ Port 3000 │ │ Port 5432 │
└───────────────┘ └───────────────┘ └───────────────┘
│
┌───────▼───────┐
│ Redis │
│ Cache │
│ Port 6379 │
└───────────────┘
text


---

## 🛠 Technologies

### Frontend
- **Next.js 16** - Framework React avec App Router
- **TypeScript** - Typage statique
- **Tailwind CSS** - Styling
- **Shadcn/ui** - Composants UI
- **NextAuth.js** - Authentification
- **TanStack React-Query** - Data fetching & caching
- **Zustand** - State management
- **React Hook Form** - Formulaires
- **Zod** - Validation
- **Recharts** - Graphiques

### Backend
- **Node.js 20** - Runtime
- **Express** - Framework API
- **PostgreSQL 16** - Base de données
- **Redis 7** - Cache & sessions
- **JWT** - Authentification
- **Multer** - Upload de fichiers
- **Winston** - Logging
- **Joi** - Validation

### Infrastructure
- **Docker** - Conteneurisation
- **Docker Compose** - Orchestration
- **Nginx** - Reverse proxy

---

## 📋 Prérequis

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac) ou Docker + Docker Compose (Linux)
- [Node.js 20+](https://nodejs.org/) (pour développement local)
- [Git](https://git-scm.com/)
- 4GB RAM minimum (8GB recommandé)
- 5GB d'espace disque

---

## 🚀 Installation

### 1. Cloner le projet

```bash
git clone https://github.com/votre-compte/tenant-saas.git
cd tenant-saas

2. Structure des fichiers
text

tenant-saas/
├── backend/
│   ├── src/
│   │   ├── config/          # Configuration (DB, Redis, JWT)
│   │   ├── database/        # Migrations & Pool Manager
│   │   ├── middleware/      # Auth, Tenant-resolver, RBAC
│   │   ├── routes/          # API Routes
│   │   ├── services/        # Business Logic
│   │   ├── utils/           # Helpers, Logger, Errors
│   │   └── validators/      # Validation schemas
│   ├── Dockerfile
│   └── package.json
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router
│   │   ├── components/      # Composants React
│   │   ├── lib/             # Utilitaires, Services API
│   │   └── types/           # TypeScript types
│   ├── Dockerfile
│   └── package.json
├── database/
│   └── init.sql             # Scripts d'initialisation
├── nginx/
│   └── default.conf         # Configuration Nginx
├── docker-compose.yml
└── README.md

3. Configuration des variables d'environnement
Backend - backend/.env
env

NODE_ENV=development
PORT=3000

# Base de données
DB_HOST=postgres
DB_PORT=5432
DB_USER=admin
DB_PASSWORD=secret
DB_NAME=multitenant_db

# Redis
REDIS_URL=redis://redis:6379

# JWT
JWT_SECRET=dev-secret-key-change-in-production
JWT_REFRESH_SECRET=dev-refresh-key-change-in-production
JWT_EXPIRATION=15m
JWT_REFRESH_EXPIRATION=30d

# Uploads
UPLOADS_PATH=/app/uploads
MAX_FILE_SIZE=5242880

Frontend - frontend/.env.local
env

# API Backend (Docker)
NEXT_PUBLIC_API_URL=http://backend:3000/api

# NextAuth
NEXTAUTH_URL=http://localhost:3001
NEXTAUTH_SECRET=super_secret_nextauth_key_change_me

# Environnement
NODE_ENV=development

🐳 Base de données
Création des bases de données

Le projet utilise PostgreSQL avec une approche multi-tenant. Les migrations sont automatiques.
1. Démarrer PostgreSQL
bash

docker-compose up -d postgres

2. Exécuter les migrations
bash

# Dans le conteneur
docker exec -it node-api node src/database/migrate-all-tenants.js

# Ou en local (si Node.js installé)
cd backend
node src/database/migrate-all-tenants.js

3. Structure des tables
sql

-- Table des tenants (multi-tenant)
tenants:
  - id (UUID)
  - name (VARCHAR)
  - subdomain (VARCHAR) UNIQUE
  - is_active (BOOLEAN)
  - created_at, updated_at

-- Table des utilisateurs
users:
  - id (UUID)
  - tenant_id (UUID) REFERENCES tenants
  - email (VARCHAR) UNIQUE
  - password (VARCHAR)
  - name (VARCHAR)
  - role (VARCHAR) ['admin', 'manager', 'user']
  - is_active (BOOLEAN)

-- Table des produits
products:
  - id (UUID)
  - tenant_id (UUID) REFERENCES tenants
  - name (VARCHAR)
  - description (TEXT)
  - price (DECIMAL)
  - category (VARCHAR)
  - stock (INTEGER)
  - barcode (VARCHAR)
  - image (VARCHAR)

-- Table des crédits clients
credit_clients:
  - id (UUID)
  - tenant_id (UUID) REFERENCES tenants
  - client_id (VARCHAR) UNIQUE
  - client_name (VARCHAR)
  - total_credit (DECIMAL)
  - used_credit (DECIMAL)
  - status (VARCHAR)

-- Table des transactions de crédit
credit_transactions:
  - id (UUID)
  - client_id (UUID) REFERENCES credit_clients
  - type (VARCHAR) ['debit', 'credit', 'payment']
  - amount (DECIMAL)
  - description (TEXT)
  - reference (VARCHAR)

-- Table des factures
invoices:
  - id (UUID)
  - tenant_id (UUID) REFERENCES tenants
  - invoice_number (VARCHAR) UNIQUE
  - client_id (VARCHAR)
  - client_name (VARCHAR)
  - items (JSONB)
  - subtotal (DECIMAL)
  - tax (DECIMAL)
  - total (DECIMAL)
  - status (VARCHAR) ['draft', 'pending', 'paid', 'overdue', 'cancelled']
  - due_date (DATE)
  - issued_date (DATE)
  - paid_date (DATE)
  - notes (TEXT)

-- Table des portefeuilles
wallets:
  - id (UUID)
  - user_id (UUID) REFERENCES users
  - balance (DECIMAL)
  - frozen_balance (DECIMAL)
  - currency (VARCHAR)

-- Table des transactions de portefeuille
wallet_transactions:
  - id (UUID)
  - wallet_id (UUID) REFERENCES wallets
  - type (VARCHAR) ['deposit', 'withdrawal', 'payment', 'refund', 'fee']
  - amount (DECIMAL)
  - balance_before (DECIMAL)
  - balance_after (DECIMAL)
  - description (TEXT)
  - reference (VARCHAR)
  - status (VARCHAR) ['pending', 'completed', 'failed', 'cancelled']

-- Table des ventes POS
pos_sales:
  - id (UUID)
  - tenant_id (UUID) REFERENCES tenants
  - invoice_number (VARCHAR) UNIQUE
  - cart (JSONB)
  - payment (JSONB)
  - status (VARCHAR) ['completed', 'pending', 'cancelled', 'refunded']
  - cashier_id (UUID)
  - cashier_name (VARCHAR)
  - customer_id (VARCHAR)
  - customer_name (VARCHAR)
  - refund_reason (TEXT)
  - created_at, updated_at

Suppression des bases de données
🔴 Suppression complète (ATTENTION: Perte de données)
bash

# 1. Arrêter tous les services
docker-compose down

# 2. Supprimer les volumes (données PostgreSQL et Redis)
docker-compose down -v

# 3. Supprimer le volume spécifique
docker volume rm tenant_postgres_data
docker volume rm tenant_redis_data

# 4. Supprimer les conteneurs
docker rm -f node-api next-app postgres-db redis-cache nginx-proxy

🟡 Suppression douce (Réinitialisation des données)
bash

# 1. Réinitialiser PostgreSQL
docker exec -it postgres-db psql -U admin -d multitenant_db -c "
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO admin;
"

# 2. Recréer les tables (migrations)
docker exec -it node-api node src/database/migrate-all-tenants.js

# 3. Créer un tenant par défaut
docker exec -it postgres-db psql -U admin -d multitenant_db -c "
INSERT INTO tenants (id, name, subdomain, is_active)
VALUES (gen_random_uuid(), 'Demo Tenant', 'demo', true);
"

🟢 Suppression d'un tenant spécifique
bash

# 1. Voir les tenants
docker exec -it postgres-db psql -U admin -d multitenant_db -c "SELECT * FROM tenants;"

# 2. Supprimer un tenant (et toutes ses données)
docker exec -it postgres-db psql -U admin -d multitenant_db -c "
DELETE FROM tenants WHERE subdomain = 'nom_tenant';
"

🚀 Démarrage
Avec Docker (Recommandé)
bash

# 1. Démarrer tous les services
docker-compose up -d

# 2. Attendre que tous les services soient prêts (10-15 secondes)
# 3. Exécuter les migrations
docker exec -it node-api node src/database/migrate-all-tenants.js

# 4. Voir les logs
docker-compose logs -f

Services disponibles
Service	Port	URL
Nginx	80	http://localhost
Backend API	3000	http://localhost:3000
Frontend	3001	http://localhost:3001
PostgreSQL	5432	localhost:5432
Redis	6379	localhost:6379
🔧 Commandes utiles
Docker
bash

# Démarrer tous les services
docker-compose up -d

# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v

# Voir les logs
docker-compose logs -f

# Voir les logs d'un service spécifique
docker-compose logs -f frontend
docker-compose logs -f backend

# Rebuild et démarrer
docker-compose up -d --build

# Redémarrer un service
docker-compose restart frontend

# Exécuter une commande dans un conteneur
docker exec -it node-api sh
docker exec -it next-app sh
docker exec -it postgres-db psql -U admin -d multitenant_db

Backend
bash

# Développement
npm run dev

# Production
npm start

# Migrations
node src/database/migrate-all-tenants.js

# Tests
npm test

Frontend
bash

# Développement
npm run dev

# Build
npm run build

# Production
npm start

# Lint
npm run lint

📡 API Endpoints
Authentification
Méthode	Endpoint	Description
POST	/api/auth/register	Inscription
POST	/api/auth/login	Connexion
POST	/api/auth/refresh	Rafraîchir le token
POST	/api/auth/logout	Déconnexion
GET	/api/auth/me	Profil utilisateur
Produits
Méthode	Endpoint	Description
GET	/api/products	Liste des produits
GET	/api/products/:id	Détail d'un produit
POST /api/products	Créer un produit
PUT	/api/products/:id	Modifier un produit
DELETE	/api/products/:id	Supprimer un produit
PATCH	/api/products/:id/stock	Mettre à jour le stock
Crédits Clients
Méthode	Endpoint	Description
GET	/api/credit	Liste des crédits
GET	/api/credit/:id	Détail d'un crédit
POST	/api/credit	Créer un crédit
PUT	/api/credit/:id	Modifier un crédit
DELETE	/api/credit/:id	Supprimer un crédit
GET	/api/credit/summary	Résumé des crédits
GET	/api/credit/:id/transactions	Historique des transactions
POST	/api/credit/:id/transactions	Ajouter une transaction
Factures
Méthode	Endpoint	Description
GET	/api/invoices	Liste des factures
GET	/api/invoices/:id	Détail d'une facture
POST	/api/invoices	Créer une facture
PUT	/api/invoices/:id	Modifier une facture
DELETE	/api/invoices/:id	Supprimer une facture
PATCH	/api/invoices/:id/paid	Marquer comme payée
PATCH	/api/invoices/:id/cancel	Annuler une facture
GET	/api/invoices/:id/pdf	Générer le PDF
Wallet
Méthode	Endpoint	Description
GET	/api/wallet/balance	Solde du portefeuille
GET	/api/wallet/transactions	Historique des transactions
POST	/api/wallet/deposit	Effectuer un dépôt
POST	/api/wallet/withdraw	Effectuer un retrait
POS
Méthode	Endpoint	Description
GET	/api/pos/products	Liste des produits POS
GET	/api/pos/products/barcode/:barcode	Produit par code-barres
POST	/api/pos/cart	Créer un panier
GET	/api/pos/cart/:cartId	Récupérer un panier
POST	/api/pos/cart/:cartId/items	Ajouter au panier
PUT	/api/pos/cart/:cartId/items/:itemId	Modifier quantité
DELETE	/api/pos/cart/:cartId/items/:itemId	Supprimer du panier
DELETE	/api/pos/cart/:cartId	Vider le panier
POST	/api/pos/checkout	Finaliser la vente
GET	/api/pos/sales	Historique des ventes
GET	/api/pos/sales/:id	Détail d'une vente
POST	/api/pos/sales/:id/refund	Rembourser une vente
GET	/api/pos/stats	Statistiques POS
🔍 Dépannage
Erreur: ECONNREFUSED - Le backend ne répond pas
bash

# Vérifier que le backend tourne
docker ps | grep node-api

# Voir les logs
docker-compose logs backend --tail 50

# Redémarrer
docker-compose restart backend

Erreur: Role "postgres" does not exist
bash

# Réinitialiser PostgreSQL
docker-compose down -v
docker-compose up -d postgres
docker exec -it postgres-db psql -U postgres -c "CREATE USER admin WITH SUPERUSER LOGIN PASSWORD 'secret';"
docker exec -it postgres-db psql -U postgres -c "CREATE DATABASE multitenant_db OWNER admin;"

Erreur CORS

Vérifier que les headers sont corrects :
bash

# Tester CORS
curl -X OPTIONS http://localhost:3000/api/products \
  -H "Origin: http://localhost:3001" \
  -H "Access-Control-Request-Method: GET" \
  -v

Erreur 401 - Token expiré
bash

# Se reconnecter
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'

Erreur 404 - Route non trouvée

Vérifier que toutes les routes sont bien enregistrées dans index.js :
bash

docker exec -it node-api cat /app/src/index.js | grep "app.use"

👥 Contribution

    Forker le projet

    Créer une branche pour votre fonctionnalité (git checkout -b feature/amazing-feature)

    Committer vos changements (git commit -m 'Add some amazing feature')

    Pusher (git push origin feature/amazing-feature)

    Ouvrir une Pull Request

Standards de code

    Backend: ESLint + Prettier

    Frontend: ESLint + Prettier + TypeScript

    Commits: Conventional Commits

📄 Licence

Ce projet est sous licence MIT.
🙏 Remerciements

    Next.js

    Tailwind CSS

    Shadcn/ui

    Docker

    PostgreSQL

    Redis

📞 Support

Pour toute question ou problème, ouvrez une issue sur le dépôt GitHub.