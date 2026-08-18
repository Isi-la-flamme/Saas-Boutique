from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.core import db_router, sync_engine


class ProductService:
    """Service Product"""
    
    @staticmethod
    def _get_db():
        return db_router.get_session()
    
    @staticmethod
    def create(tenant_id: str, product_data: ProductCreate) -> ProductResponse:
        """Crée un nouveau produit"""
        db = ProductService._get_db()
        try:
            product = Product(
                tenant_id=tenant_id,
                name=product_data.name,
                description=product_data.description,
                price=product_data.price,
                stock=product_data.stock,
                is_active=product_data.is_active,
                sync_source="local"
            )
            
            db.add(product)
            db.commit()
            db.refresh(product)
            
            # Ajouter à la queue de sync
            sync_engine.add_operation(
                table="products",
                action="create",
                data={
                    "id": product.id,
                    "tenant_id": product.tenant_id,
                    "name": product.name,
                    "description": product.description,
                    "price": product.price,
                    "stock": product.stock,
                    "is_active": product.is_active,
                    "sync_version": product.sync_version
                },
                tenant_id=tenant_id
            )
            
            return ProductResponse.model_validate(product)
        finally:
            db.close()
    
    @staticmethod
    def get(product_id: int, tenant_id: str) -> Optional[ProductResponse]:
        """Récupère un produit par son ID"""
        db = ProductService._get_db()
        try:
            product = db.query(Product).filter(
                Product.id == product_id,
                Product.tenant_id == tenant_id
            ).first()
            if product:
                return ProductResponse.model_validate(product)
            return None
        finally:
            db.close()
    
    @staticmethod
    def list(tenant_id: str, skip: int = 0, limit: int = 100) -> dict:
        """Liste les produits d'un tenant"""
        db = ProductService._get_db()
        try:
            query = db.query(Product).filter(Product.tenant_id == tenant_id)
            total = query.count()
            products = query.offset(skip).limit(limit).all()
            
            return {
                "items": [ProductResponse.model_validate(p) for p in products],
                "total": total
            }
        finally:
            db.close()
    
    @staticmethod
    def update(product_id: int, tenant_id: str, product_data: ProductUpdate) -> Optional[ProductResponse]:
        """Met à jour un produit"""
        db = ProductService._get_db()
        try:
            product = db.query(Product).filter(
                Product.id == product_id,
                Product.tenant_id == tenant_id
            ).first()
            if not product:
                return None
            
            if product_data.name is not None:
                product.name = product_data.name
            if product_data.description is not None:
                product.description = product_data.description
            if product_data.price is not None:
                product.price = product_data.price
            if product_data.stock is not None:
                product.stock = product_data.stock
            if product_data.is_active is not None:
                product.is_active = product_data.is_active
            
            product.sync_version += 1
            product.sync_source = "local"
            
            db.commit()
            db.refresh(product)
            
            # Ajouter à la queue de sync
            sync_engine.add_operation(
                table="products",
                action="update",
                data={
                    "id": product.id,
                    "tenant_id": product.tenant_id,
                    "name": product.name,
                    "description": product.description,
                    "price": product.price,
                    "stock": product.stock,
                    "is_active": product.is_active,
                    "sync_version": product.sync_version
                },
                tenant_id=tenant_id
            )
            
            return ProductResponse.model_validate(product)
        finally:
            db.close()
    
    @staticmethod
    def delete(product_id: int, tenant_id: str) -> bool:
        """Supprime un produit"""
        db = ProductService._get_db()
        try:
            product = db.query(Product).filter(
                Product.id == product_id,
                Product.tenant_id == tenant_id
            ).first()
            if not product:
                return False
            
            db.delete(product)
            db.commit()
            
            # Ajouter à la queue de sync
            sync_engine.add_operation(
                table="products",
                action="delete",
                data={"id": product_id, "tenant_id": tenant_id},
                tenant_id=tenant_id
            )
            
            return True
        finally:
            db.close()

    @staticmethod
    async def replay_sync(tenant_id: str, action: str, data: dict):
        # Le replay doit toujours écrire sur PostgreSQL, y compris quand les
        # requêtes utilisateur restent volontairement en mode offline.
        db = db_router.get_online_session()
        try:
            record_id = data.get("id")
            existing = db.query(Product).filter(Product.id == record_id, Product.tenant_id == tenant_id).first()

            if action == "create":
                if existing:
                    return existing
                new_record = Product(**data)
                db.add(new_record)
                db.commit()
                db.refresh(new_record)
                return new_record

            elif action == "update":
                if not existing:
                    new_record = Product(**data)
                    db.add(new_record)
                    db.commit()
                    db.refresh(new_record)
                    return new_record
                else:
                    incoming_version = data.get("sync_version", 0)
                    if existing.sync_version > incoming_version:
                        return existing
                    
                    for key, value in data.items():
                        setattr(existing, key, value)
                    
                    existing.sync_version = max(incoming_version, existing.sync_version + 1)
                    
                    db.commit()
                    db.refresh(existing)
                    return existing

            elif action == "delete":
                if existing:
                    db.delete(existing)
                    db.commit()
                return True
        finally:
            db.close()

product_service = ProductService()
