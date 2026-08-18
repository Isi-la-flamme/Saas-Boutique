from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import get_password_hash
from app.core import db_router, sync_engine


class UserService:
    """Service User"""
    
    @staticmethod
    def _get_db():
        return db_router.get_session()
    
    @staticmethod
    def create(tenant_id: str, user_data: UserCreate) -> UserResponse:
        db = UserService._get_db()
        try:
            existing = db.query(User).filter(User.email == user_data.email).first()
            if existing:
                raise ValueError("Email already registered")
            
            existing = db.query(User).filter(User.username == user_data.username).first()
            if existing:
                raise ValueError("Username already taken")
            
            user = User(
                tenant_id=tenant_id,
                email=user_data.email,
                username=user_data.username,
                full_name=user_data.full_name,
                hashed_password=get_password_hash(user_data.password),
                is_active=True
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)

            sync_engine.add_operation(
                table="users",
                action="create",
                data={
                    "tenant_id": user.tenant_id,
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "hashed_password": user.hashed_password,
                    "is_active": user.is_active,
                    "is_superuser": user.is_superuser,
                },
                tenant_id=tenant_id,
            )
            
            return UserResponse.model_validate(user)
        finally:
            db.close()
    
    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        db = UserService._get_db()
        try:
            return db.query(User).filter(User.email == email).first()
        finally:
            db.close()
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional[UserResponse]:
        db = UserService._get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                return UserResponse.model_validate(user)
            return None
        finally:
            db.close()
    
    @staticmethod
    def list_by_tenant(tenant_id: str) -> List[UserResponse]:
        db = UserService._get_db()
        try:
            users = db.query(User).filter(User.tenant_id == tenant_id).all()
            return [UserResponse.model_validate(u) for u in users]
        finally:
            db.close()
    
    # ===== ADMIN METHODS =====
    @staticmethod
    def list_all(skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        db = UserService._get_db()
        try:
            query = db.query(User)
            total = query.count()
            users = query.offset(skip).limit(limit).all()
            return {
                "items": [UserResponse.model_validate(u) for u in users],
                "total": total
            }
        finally:
            db.close()
    
    @staticmethod
    def toggle_status(user_id: int, tenant_id: Optional[str] = None) -> Optional[UserResponse]:
        db = UserService._get_db()
        try:
            query = db.query(User).filter(User.id == user_id)
            if tenant_id is not None:
                query = query.filter(User.tenant_id == tenant_id)
            user = query.first()
            if not user:
                return None
            
            user.is_active = not user.is_active
            db.commit()
            db.refresh(user)
            sync_engine.add_operation(
                table="users",
                action="update",
                data={
                    "tenant_id": user.tenant_id,
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "hashed_password": user.hashed_password,
                    "is_active": user.is_active,
                    "is_superuser": user.is_superuser,
                },
                tenant_id=user.tenant_id,
            )
            return UserResponse.model_validate(user)
        finally:
            db.close()
    
    @staticmethod
    def delete(user_id: int, tenant_id: Optional[str] = None) -> bool:
        db = UserService._get_db()
        try:
            query = db.query(User).filter(User.id == user_id)
            if tenant_id is not None:
                query = query.filter(User.tenant_id == tenant_id)
            user = query.first()
            if not user:
                return False
            payload = {"email": user.email, "tenant_id": user.tenant_id}
            db.delete(user)
            db.commit()
            sync_engine.add_operation(
                table="users", action="delete", data=payload, tenant_id=user.tenant_id
            )
            return True
        finally:
            db.close()

    @staticmethod
    async def replay_sync(tenant_id: str, action: str, data: dict):
        """Rejoue un utilisateur sur PostgreSQL via son e-mail (clé stable)."""
        db = db_router.get_online_session()
        try:
            existing = db.query(User).filter(User.email == data.get("email")).first()
            if action == "delete":
                if existing:
                    db.delete(existing)
                    db.commit()
                return True

            if existing:
                for key, value in data.items():
                    setattr(existing, key, value)
            else:
                db.add(User(**data))
            db.commit()
            return existing
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()


user_service = UserService()
