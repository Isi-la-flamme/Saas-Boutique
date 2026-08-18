from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.connection_monitor import connection_monitor
from app.core.sync_engine import sync_engine
from app.core.seed import seed_database
from app.core.database import Base
from app.core.database_router import db_router
from app.routers import tenant, auth, product, sale, users, admin, customer
from app.models.customer import Customer
from app.models.sale import Sale
from sqlalchemy import inspect, text
from app.core.connection_monitor import ConnectionStatus
from app.middleware.tenant import TenantMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'app"""
    print("🚀 Démarrage de l'application...")
    
    # SQLite est toujours initialisée en premier : elle est la source locale
    # persistante, y compris quand PostgreSQL est disponible au démarrage.
    engine = db_router.get_local_engine()
    
    # 1. CRÉER LES TABLES D'ABORD
    print("📦 Création des tables...")
    Base.metadata.create_all(bind=engine)
    
    # Les instances déjà déployées reçoivent la nouvelle colonne sans migration manuelle.
    try:
        columns = {column["name"] for column in inspect(engine).get_columns("sales")}
        if "customer_id" not in columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE sales ADD COLUMN customer_id INTEGER"))
    except Exception as e:
        print(f"⚠️ Note sur la colonne customer_id (peut-être déjà présente ou gérée par Postgres): {e}")
        
    print("✅ Tables créées")
    
    # 2. ENSUITE EXÉCUTER LE SEED
    seed_database(engine=engine)
    
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


@app.get("/connection-status")
async def get_connection_status():
    # Force un test instantané dès que le frontend le demande
    current_status = await connection_monitor.check()
    
    return {
        "is_online": current_status == ConnectionStatus.ONLINE,
        "status": current_status.value,
        "sync_queue": sync_engine.queue_size
    }
