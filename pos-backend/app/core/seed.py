from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.user import User
from app.schemas.tenant import TenantCreate
from app.services.tenant import TenantService
from app.core.security import get_password_hash


from app.core.database import get_active_engine # <-- Importez l'engine dynamique

def seed_database():
    """
    Initialise les données de base de l'application sur le moteur actif (PostgreSQL ou SQLite).
    """
    # Création dynamique de la session basée sur l'engine réellement actif
    active_engine = get_active_engine()
    DynamicSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=active_engine)
    
    db = DynamicSessionLocal()
    try:

        SUPERUSER_EMAIL = settings.SUPERUSER_EMAIL
        # 1. Vérifier si le super admin existe déjà
        existing = db.query(User).filter(User.email == SUPERUSER_EMAIL).first()
        if existing:
            print(f"✅ Super admin déjà existant: {SUPERUSER_EMAIL}")
            return
        
        # 2. Créer le tenant
        print("📦 Création du tenant SaaS Platform...")
        tenant_data = TenantCreate(
            name=settings.SUPERUSER_TENANT_NAME,
            description="Plateforme SaaS - Administration"
        )

        tenant = TenantService.create(tenant_data)
        print(f"✅ Tenant créé: {tenant.tenant_id}")
        
        # 3. Créer le super admin
        print("👤 Création du super admin...")
        superuser = User(
            tenant_id=tenant.tenant_id,
            email=settings.SUPERUSER_EMAIL,
            username=settings.SUPERUSER_USERNAME,
            full_name=settings.SUPERUSER_FULL_NAME,
            hashed_password=get_password_hash(settings.SUPERUSER_PASSWORD),
            is_active=True,
            is_superuser=True
        )
        db.add(superuser)
        db.commit()
        db.refresh(superuser)
        
        print(f"✅ Super admin créé avec succès !")
        print(f"   📧 Email: {settings.SUPERUSER_EMAIL}")
        print(f"   🔑 Mot de passe: {settings.SUPERUSER_PASSWORD}")
        print(f"   🏢 Tenant: {settings.SUPERUSER_TENANT_NAME}")
        
    except Exception as e:
        print(f"❌ Erreur lors du seed: {e}")
        db.rollback()
        raise
    finally:
        db.close()