from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import get_active_engine
from app.core.security import get_password_hash
from app.models.tenant import Tenant
from app.models.user import User


def seed_database(engine=None):
    """Initialise une base précise avec le même tenant système et le même admin.

    Le seed ne passe volontairement pas par les services : ceux-ci choisissent
    une base selon l'état réseau, ce qui pouvait répartir le tenant et son
    utilisateur entre SQLite et PostgreSQL au démarrage.
    """
    target_engine = engine or get_active_engine()
    db = sessionmaker(autocommit=False, autoflush=False, bind=target_engine)()
    try:
        existing_user = db.query(User).filter(User.email == settings.SUPERUSER_EMAIL).first()
        if not existing_user:
            # Une base existante peut avoir été initialisée avec un ancien
            # e-mail de configuration. Son super-admin reste l'unique seed.
            existing_user = db.query(User).filter(User.is_superuser.is_(True)).first()

        # Préserve l'identifiant des anciens seeds : un utilisateur déjà créé
        # doit toujours retrouver son tenant après la mise à jour.
        tenant_id = existing_user.tenant_id if existing_user else settings.SUPERUSER_TENANT_ID
        tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
        if not tenant:
            tenant = Tenant(
                tenant_id=tenant_id,
                name=settings.SUPERUSER_TENANT_NAME,
                description="Plateforme SaaS - Administration",
                is_active=True,
                sync_source="seed",
            )
            db.add(tenant)
            db.flush()

        if existing_user:
            db.commit()
            print(f"Super admin déjà présent: {settings.SUPERUSER_EMAIL}")
            return

        superuser = User(
            tenant_id=tenant.tenant_id,
            email=settings.SUPERUSER_EMAIL,
            username=settings.SUPERUSER_USERNAME,
            full_name=settings.SUPERUSER_FULL_NAME,
            hashed_password=get_password_hash(settings.SUPERUSER_PASSWORD),
            is_active=True,
            is_superuser=True,
        )
        db.add(superuser)
        db.commit()
        print(f"Super admin créé: {settings.SUPERUSER_EMAIL}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
