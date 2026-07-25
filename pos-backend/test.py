from app.core.database import engine
from app.core.database import Base
from app.models.tenant import Tenant
from app.models.user import User

print("📦 Création des tables SQLite...")
Base.metadata.create_all(bind=engine)
print("✅ Tables créées")

from sqlalchemy import inspect
inspector = inspect(engine)
print("📋 Tables:", inspector.get_table_names())
exit()