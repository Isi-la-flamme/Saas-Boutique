from fastapi import Request, HTTPException, status, Header, Depends
from fastapi.security import OAuth2PasswordBearer
from app.services.tenant import tenant_service
from app.services.user import user_service
from app.core.security import decode_token
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_tenant(request: Request):
    tenant = getattr(request.state, "tenant", None)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No tenant found in request"
        )
    return tenant


async def get_tenant_id(
    x_tenant_id: str = Header(..., alias="X-Tenant-ID")
) -> str:
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-Tenant-ID header"
        )
    return x_tenant_id


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = user_service.get_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User is inactive")
    
    return user


async def get_current_superuser(current_user = Depends(get_current_user)):
    """Vérifie que l'utilisateur est le super admin"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin privileges required"
        )
    return current_user