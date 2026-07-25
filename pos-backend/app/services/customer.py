from typing import Optional
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.core import db_router, sync_engine


class CustomerService:
    @staticmethod
    def _get_db():
        return db_router.get_session()

    @staticmethod
    def create(tenant_id: str, data: CustomerCreate) -> CustomerResponse:
        db = CustomerService._get_db()
        try:
            customer = Customer(tenant_id=tenant_id, **data.model_dump(), sync_source="local")
            db.add(customer)
            db.commit()
            db.refresh(customer)
            sync_engine.add_operation("customers", "create", {"id": customer.id, "tenant_id": tenant_id, "name": customer.name, "sync_version": customer.sync_version}, tenant_id)
            return CustomerResponse.model_validate(customer)
        finally:
            db.close()

    @staticmethod
    def list(tenant_id: str, skip: int = 0, limit: int = 100) -> dict:
        db = CustomerService._get_db()
        try:
            query = db.query(Customer).filter(Customer.tenant_id == tenant_id)
            return {"items": [CustomerResponse.model_validate(customer) for customer in query.order_by(Customer.name).offset(skip).limit(limit).all()], "total": query.count()}
        finally:
            db.close()

    @staticmethod
    def get(customer_id: int, tenant_id: str) -> Optional[CustomerResponse]:
        db = CustomerService._get_db()
        try:
            customer = db.query(Customer).filter(Customer.id == customer_id, Customer.tenant_id == tenant_id).first()
            return CustomerResponse.model_validate(customer) if customer else None
        finally:
            db.close()

    @staticmethod
    def update(customer_id: int, tenant_id: str, data: CustomerUpdate) -> Optional[CustomerResponse]:
        db = CustomerService._get_db()
        try:
            customer = db.query(Customer).filter(Customer.id == customer_id, Customer.tenant_id == tenant_id).first()
            if not customer:
                return None
            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(customer, field, value)
            customer.sync_version += 1
            db.commit()
            db.refresh(customer)
            return CustomerResponse.model_validate(customer)
        finally:
            db.close()

    @staticmethod
    def delete(customer_id: int, tenant_id: str) -> bool:
        db = CustomerService._get_db()
        try:
            customer = db.query(Customer).filter(Customer.id == customer_id, Customer.tenant_id == tenant_id).first()
            if not customer:
                return False
            db.delete(customer)
            db.commit()
            return True
        finally:
            db.close()


customer_service = CustomerService()
