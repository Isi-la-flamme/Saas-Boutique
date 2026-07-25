from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from app.services.product import product_service
from app.core.dependencies import get_tenant_id
from app.core.security import decode_token
from fastapi.security import OAuth2PasswordBearer
from app.services.user import user_service

router = APIRouter(prefix="/products", tags=["products"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme)
):
    """Crée un nouveau produit"""
    return product_service.create(tenant_id, product_data)


@router.get("/", response_model=ProductListResponse)
async def list_products(
    tenant_id: str = Depends(get_tenant_id),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    token: str = Depends(oauth2_scheme)
):
    """Liste les produits du tenant"""
    return product_service.list(tenant_id, skip, limit)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme)
):
    """Récupère un produit par son ID"""
    product = product_service.get(product_id, tenant_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme)
):
    """Met à jour un produit"""
    product = product_service.update(product_id, tenant_id, product_data)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme)
):
    """Supprime un produit"""
    deleted = product_service.delete(product_id, tenant_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")