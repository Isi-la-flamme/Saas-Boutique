from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.services.user import user_service
from app.core.dependencies import get_tenant_id
from fastapi.security import OAuth2PasswordBearer
from app.schemas.user import UserCreate, UserResponse
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.get("/", response_model=dict)
async def list_users(
    tenant_id: str = Depends(get_tenant_id),
    current_user = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    """Liste les utilisateurs du tenant"""
    if current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant access denied")
    users = user_service.list_by_tenant(tenant_id)
    return {"items": users, "total": len(users)}


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    """Crée un utilisateur dans la boutique de l'utilisateur connecté."""
    if current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant access denied")
    try:
        return user_service.create(tenant_id, user_data)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.patch("/{user_id}/status", response_model=UserResponse)
async def toggle_user_status(
    user_id: int,
    tenant_id: str = Depends(get_tenant_id),
    current_user = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    """Suspend ou réactive un utilisateur de la même boutique."""
    if current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant access denied")
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="You cannot suspend your own account")
    user = user_service.toggle_status(user_id, tenant_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    tenant_id: str = Depends(get_tenant_id),
    current_user = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    """Supprime un utilisateur de la même boutique."""
    if current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant access denied")
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")
    if not user_service.delete(user_id, tenant_id):
        raise HTTPException(status_code=404, detail="User not found")
