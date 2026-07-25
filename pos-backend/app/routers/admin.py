from fastapi import APIRouter, HTTPException, status, Depends
from app.services.tenant import tenant_service
from app.services.user import user_service
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse
from app.schemas.user import UserCreate, UserResponse
from app.core.dependencies import get_current_superuser, get_tenant_id
from typing import List

router = APIRouter(prefix="/admin", tags=["admin"])


# ===== TENANTS =====
@router.get("/tenants", response_model=dict)
async def admin_list_tenants(
    skip: int = 0,
    limit: int = 100,
    superuser=Depends(get_current_superuser)
):
    """Liste tous les tenants (Super Admin)"""
    return tenant_service.list(skip, limit)


@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
async def admin_get_tenant(
    tenant_id: str,
    superuser=Depends(get_current_superuser)
):
    tenant = tenant_service.get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.post("/tenants", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_tenant(
    tenant_data: TenantCreate,
    superuser=Depends(get_current_superuser)
):
    return tenant_service.create(tenant_data)


@router.put("/tenants/{tenant_id}", response_model=TenantResponse)
async def admin_update_tenant(
    tenant_id: str,
    tenant_data: TenantUpdate,
    superuser=Depends(get_current_superuser)
):
    tenant = tenant_service.update(tenant_id, tenant_data)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.delete("/tenants/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_tenant(
    tenant_id: str,
    superuser=Depends(get_current_superuser)
):
    deleted = tenant_service.delete(tenant_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Tenant not found")


# ===== USERS =====
@router.post("/users/{tenant_id}", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_user(
    tenant_id: str,
    user_data: UserCreate,
    superuser=Depends(get_current_superuser)
):
    """Crée un utilisateur dans la société demandée (Super Admin)."""
    if not tenant_service.get(tenant_id):
        raise HTTPException(status_code=404, detail="Tenant not found")
    try:
        return user_service.create(tenant_id, user_data)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get("/users", response_model=dict)
async def admin_list_users(
    skip: int = 0,
    limit: int = 100,
    superuser=Depends(get_current_superuser)
):
    users = user_service.list_all(skip, limit)
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def admin_get_user(
    user_id: int,
    superuser=Depends(get_current_superuser)
):
    user = user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}/toggle-status", response_model=UserResponse)
async def admin_toggle_user_status(
    user_id: int,
    superuser=Depends(get_current_superuser)
):
    user = user_service.toggle_status(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_user(
    user_id: int,
    superuser=Depends(get_current_superuser)
):
    deleted = user_service.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
