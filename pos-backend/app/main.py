from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.connection_monitor import connection_monitor
from app.core.sync_engine import sync_engine
from app.core.seed import seed_database
from app.core.database import engine, Base  # ← AJOUT
from app.routers import tenant, auth, product, sale, users, admin, customer
from app.models.customer import Customer
from app.models.sale import Sale
from sqlalchemy import inspect, text
from app.middleware.tenant import TenantMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'app"""
    print("🚀 Démarrage de l'application...")
    
    # 1. CRÉER LES TABLES D'ABORD
    print("📦 Création des tables...")
    Base.metadata.create_all(bind=engine)
    # Les instances déjà déployées reçoivent la nouvelle colonne sans migration manuelle.
    columns = {column["name"] for column in inspect(engine).get_columns("sales")}
    if "customer_id" not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE sales ADD COLUMN customer_id INTEGER"))
    print("✅ Tables créées")
    
    # 2. ENSUITE EXÉCUTER LE SEED
    seed_database()
    
    await connection_monitor.start()
    await sync_engine.start()
    print("✅ Application prête")
    
    yield
    
    print("🛑 Arrêt de l'application...")
    await sync_engine.stop()
    await connection_monitor.stop()


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Middleware Tenant
app.add_middleware(TenantMiddleware)

# Routers
app.include_router(tenant.router)
app.include_router(auth.router)
app.include_router(product.router)
app.include_router(customer.router)
app.include_router(sale.router)
app.include_router(users.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "status": "running",
        "connection": connection_monitor.status.value,
        "sync_queue": sync_engine.queue_size
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "connection": connection_monitor.status.value,
        "sync_queue": sync_engine.queue_size
    }
