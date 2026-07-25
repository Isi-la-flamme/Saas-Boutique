from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from app.core.dependencies import get_tenant_id
from app.schemas.customer import CustomerCreate, CustomerListResponse, CustomerResponse, CustomerUpdate
from app.services.customer import customer_service

router = APIRouter(prefix="/customers", tags=["customers"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(data: CustomerCreate, tenant_id: str = Depends(get_tenant_id), token: str = Depends(oauth2_scheme)):
    return customer_service.create(tenant_id, data)


@router.get("/", response_model=CustomerListResponse)
async def list_customers(tenant_id: str = Depends(get_tenant_id), skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), token: str = Depends(oauth2_scheme)):
    return customer_service.list(tenant_id, skip, limit)


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int, tenant_id: str = Depends(get_tenant_id), token: str = Depends(oauth2_scheme)):
    customer = customer_service.get(customer_id, tenant_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(customer_id: int, data: CustomerUpdate, tenant_id: str = Depends(get_tenant_id), token: str = Depends(oauth2_scheme)):
    customer = customer_service.update(customer_id, tenant_id, data)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(customer_id: int, tenant_id: str = Depends(get_tenant_id), token: str = Depends(oauth2_scheme)):
    if not customer_service.delete(customer_id, tenant_id):
        raise HTTPException(status_code=404, detail="Customer not found")
