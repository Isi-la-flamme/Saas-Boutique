from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional, List, Dict, Any
from app.models.sale import Sale, SaleItem, SaleStatus, PaymentStatus, PaymentMethod
from app.models.product import Product
from app.models.customer import Customer
from app.schemas.sale import SaleCreate, SaleUpdate, SaleResponse
from app.core import db_router, sync_engine


class SaleService:
    """Service Sale"""
    
    @staticmethod
    def _get_db():
        return db_router.get_session()
    
    @staticmethod
    def create(tenant_id: str, sale_data: SaleCreate) -> SaleResponse:
        db = SaleService._get_db()
        try:
            payment_status = sale_data.payment_status
            payment_method = sale_data.payment_method
            amount_paid = sale_data.amount_paid
            
            if sale_data.payment_method == PaymentMethod.DEFERRED:
                payment_status = PaymentStatus.UNPAID
                amount_paid = 0.0
            
            if sale_data.payment_method == PaymentMethod.CASH or sale_data.payment_method == PaymentMethod.CARD:
                payment_status = PaymentStatus.PAID
            
            if sale_data.customer_id is not None:
                customer = db.query(Customer).filter(Customer.id == sale_data.customer_id, Customer.tenant_id == tenant_id).first()
                if not customer:
                    raise ValueError("Customer not found for this tenant")

            sale = Sale(
                tenant_id=tenant_id,
                customer_id=sale_data.customer_id,
                status=sale_data.status,
                payment_status=payment_status,
                payment_method=payment_method,
                amount_paid=amount_paid,
                sync_source="local"
            )
            
            db.add(sale)
            db.flush()
            
            total = 0.0
            
            for item_data in sale_data.items:
                product = db.query(Product).filter(
                    Product.id == item_data.product_id,
                    Product.tenant_id == tenant_id
                ).first()
                
                if not product:
                    raise ValueError(f"Product {item_data.product_id} not found")
                
                if product.stock < item_data.quantity:
                    raise ValueError(f"Insufficient stock for product {product.name}")
                
                total_price = item_data.unit_price * item_data.quantity
                item = SaleItem(
                    sale_id=sale.id,
                    product_id=item_data.product_id,
                    quantity=item_data.quantity,
                    unit_price=item_data.unit_price,
                    total_price=total_price
                )
                db.add(item)
                total += total_price
                
                product.stock -= item_data.quantity
            
            sale.total = total
            sale.remaining_amount = total - sale.amount_paid
            
            if sale.remaining_amount <= 0:
                sale.payment_status = PaymentStatus.PAID
            elif sale.amount_paid > 0:
                sale.payment_status = PaymentStatus.PARTIAL
            
            db.commit()
            db.refresh(sale)
            if sale.customer:
                sale.customer_name = sale.customer.name
            
            # Ajouter à la queue de sync
            sync_engine.add_operation(
                table="sales",
                action="create",
                data={
                    "id": sale.id,
                    "tenant_id": sale.tenant_id,
                    "customer_id": sale.customer_id,
                    "total": sale.total,
                    "status": sale.status.value,
                    "payment_status": sale.payment_status.value,
                    "payment_method": sale.payment_method.value,
                    "amount_paid": sale.amount_paid,
                    "remaining_amount": sale.remaining_amount,
                    "sync_version": sale.sync_version
                },
                tenant_id=tenant_id
            )
            
            return SaleResponse.model_validate(sale)
        finally:
            db.close()
    
    @staticmethod
    def get(sale_id: int, tenant_id: str) -> Optional[SaleResponse]:
        """Récupère une vente par son ID avec les noms des produits"""
        db = SaleService._get_db()
        try:
            sale = db.query(Sale).filter(
                Sale.id == sale_id,
                Sale.tenant_id == tenant_id
            ).first()
            
            if sale:
                if sale.customer:
                    sale.customer_name = sale.customer.name
                # Récupérer les noms des produits pour chaque item
                for item in sale.items:
                    product = db.query(Product).filter(Product.id == item.product_id).first()
                    if product:
                        item.product_name = product.name
                return SaleResponse.model_validate(sale)
            return None
        finally:
            db.close()
    
    @staticmethod
    def list(tenant_id: str, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """Liste les ventes d'un tenant avec les noms des produits"""
        db = SaleService._get_db()
        try:
            query = db.query(Sale).filter(Sale.tenant_id == tenant_id)
            total = query.count()
            sales = query.order_by(Sale.created_at.desc()).offset(skip).limit(limit).all()
            
            # Récupérer les noms des produits pour chaque item de chaque vente
            for sale in sales:
                if sale.customer:
                    sale.customer_name = sale.customer.name
                for item in sale.items:
                    product = db.query(Product).filter(Product.id == item.product_id).first()
                    if product:
                        item.product_name = product.name
            
            return {
                "items": [SaleResponse.model_validate(s) for s in sales],
                "total": total
            }
        finally:
            db.close()
    
    @staticmethod
    def update(sale_id: int, tenant_id: str, sale_data: SaleUpdate) -> Optional[SaleResponse]:
        db = SaleService._get_db()
        try:
            sale = db.query(Sale).filter(
                Sale.id == sale_id,
                Sale.tenant_id == tenant_id
            ).first()
            if not sale:
                return None
            
            if sale_data.status is not None:
                sale.status = sale_data.status
            
            if sale_data.payment_status is not None:
                sale.payment_status = sale_data.payment_status
            
            if sale_data.payment_method is not None:
                sale.payment_method = sale_data.payment_method
            
            if sale_data.amount_paid is not None:
                sale.amount_paid = sale_data.amount_paid
                sale.remaining_amount = sale.total - sale.amount_paid
                
                if sale.remaining_amount <= 0:
                    sale.payment_status = PaymentStatus.PAID
                elif sale.amount_paid > 0:
                    sale.payment_status = PaymentStatus.PARTIAL
            
            sale.sync_version += 1
            sale.sync_source = "local"
            
            db.commit()
            db.refresh(sale)
            
            # Récupérer les noms des produits pour les items
            for item in sale.items:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                if product:
                    item.product_name = product.name
            
            return SaleResponse.model_validate(sale)
        finally:
            db.close()
    
    @staticmethod
    def delete(sale_id: int, tenant_id: str) -> bool:
        db = SaleService._get_db()
        try:
            sale = db.query(Sale).filter(
                Sale.id == sale_id,
                Sale.tenant_id == tenant_id
            ).first()
            if not sale:
                return False
            
            db.delete(sale)
            db.commit()
            
            return True
        finally:
            db.close()


sale_service = SaleService()
