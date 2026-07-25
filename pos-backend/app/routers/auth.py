from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta
from jose import JWTError
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.user import user_service
from app.core.security import create_access_token, verify_password, decode_token
from app.core.dependencies import get_tenant_id
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    tenant_id: str = Depends(get_tenant_id)
):
    """Inscription d'un nouvel utilisateur"""
    try:
        return user_service.create(tenant_id, user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """Connexion - retourne un token JWT"""
    user = user_service.get_by_email(user_data.email)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User is inactive")
    
    # Créer le token
    access_token = create_access_token(
        data={"sub": user.email, "tenant_id": user.tenant_id, "user_id": user.id}
    )
    
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Récupère l'utilisateur courant"""
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = user_service.get_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return UserResponse.model_validate(user)