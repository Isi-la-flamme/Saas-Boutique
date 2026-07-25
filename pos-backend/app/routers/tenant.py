from fastapi import APIRouter, HTTPException, status, Query
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse, TenantListResponse
from app.services.tenant import tenant_service

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(tenant_data: TenantCreate):
    """Crée un nouveau tenant"""
    return tenant_service.create(tenant_data)


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(tenant_id: str):
    """Récupère un tenant par son tenant_id"""
    tenant = tenant_service.get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.get("/", response_model=TenantListResponse)
async def list_tenants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Liste tous les tenants"""
    return tenant_service.list(skip, limit)


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(tenant_id: str, tenant_data: TenantUpdate):
    """Met à jour un tenant"""
    tenant = tenant_service.update(tenant_id, tenant_data)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(tenant_id: str):
    """Supprime un tenant"""
    deleted = tenant_service.delete(tenant_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Tenant not found")