"""
Script de seed pour initialiser les données de base.
Exécuté au premier démarrage uniquement.
"""

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.tenant import Tenant
from app.services.tenant import tenant_service
from app.schemas.tenant import TenantCreate


SUPERUSER_EMAIL = "admin@saas.com"
SUPERUSER_USERNAME = "superadmin"
SUPERUSER_PASSWORD = "SuperAdmin123!"
SUPERUSER_FULL_NAME = "Super Admin"
SUPERUSER_TENANT_NAME = "SaaS Platform"


def seed_database():
    """
    Initialise les données de base de l'application.
    - Tenant par défaut
    - Super Admin
    - Comptes de démo (optionnel)
    """
    db = SessionLocal()
    try:
        # 1. Vérifier si le super admin existe déjà
        existing = db.query(User).filter(User.email == SUPERUSER_EMAIL).first()
        if existing:
            print(f"✅ Super admin déjà existant: {SUPERUSER_EMAIL}")
            return
        
        # 2. Créer le tenant
        print("📦 Création du tenant SaaS Platform...")
        tenant_data = TenantCreate(
            name=SUPERUSER_TENANT_NAME,
            description="Plateforme SaaS - Administration"
        )
        tenant = tenant_service.create(tenant_data)
        print(f"✅ Tenant créé: {tenant.tenant_id}")
        
        # 3. Créer le super admin
        print("👤 Création du super admin...")
        superuser = User(
            tenant_id=tenant.tenant_id,
            email=SUPERUSER_EMAIL,
            username=SUPERUSER_USERNAME,
            full_name=SUPERUSER_FULL_NAME,
            hashed_password=get_password_hash(SUPERUSER_PASSWORD),
            is_active=True,
            is_superuser=True
        )
        db.add(superuser)
        db.commit()
        db.refresh(superuser)
        
        print(f"✅ Super admin créé avec succès !")
        print(f"   📧 Email: {SUPERUSER_EMAIL}")
        print(f"   🔑 Mot de passe: {SUPERUSER_PASSWORD}")
        print(f"   🏢 Tenant: {SUPERUSER_TENANT_NAME}")
        
        # 4. Optionnel : Créer des données de démo
        # seed_demo_data(db, tenant.tenant_id)
        
    except Exception as e:
        print(f"❌ Erreur lors du seed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def seed_demo_data(db: Session, tenant_id: str):
    """Ajoute des données de démo pour le tenant (optionnel)"""
    from app.models.product import Product
    
    demo_products = [
        {"name": "Café", "price": 2.50, "stock": 100},
        {"name": "Croissant", "price": 1.50, "stock": 50},
        {"name": "Jus d'orange", "price": 3.00, "stock": 30},
    ]
    
    for p in demo_products:
        product = Product(
            tenant_id=tenant_id,
            name=p["name"],
            price=p["price"],
            stock=p["stock"],
            sync_source="local"
        )
        db.add(product)
    
    db.commit()
    print(f"✅ {len(demo_products)} produits de démo créés")