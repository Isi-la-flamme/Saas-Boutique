from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.core.database import Base # Votre base declarative_base locale

class SyncOutboxModel(Base):
    __tablename__ = "sync_outbox"

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    data = Column(Text, nullable=False) # Stocké en JSON string
    tenant_id = Column(String, nullable=False)
    sync_version = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)