from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.schemas.sale import SaleCreate, SaleUpdate, SaleResponse, SaleListResponse
from app.services.sale import sale_service
from app.core.dependencies import get_tenant_id
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/sales", tags=["sales"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
async def create_sale(
    sale_data: SaleCreate,
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme)
):
    """Crée une nouvelle vente (POS)"""
    try:
        return sale_service.create(tenant_id, sale_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=SaleListResponse)
async def list_sales(
    tenant_id: str = Depends(get_tenant_id),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    token: str = Depends(oauth2_scheme)
):
    """Liste les ventes du tenant"""
    return sale_service.list(tenant_id, skip, limit)


@router.get("/{sale_id}", response_model=SaleResponse)
async def get_sale(
    sale_id: int,
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme)
):
    """Récupère une vente par son ID"""
    sale = sale_service.get(sale_id, tenant_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale


@router.put("/{sale_id}", response_model=SaleResponse)
async def update_sale(
    sale_id: int,
    sale_data: SaleUpdate,
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme)
):
    """Met à jour une vente (status)"""
    sale = sale_service.update(sale_id, tenant_id, sale_data)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale


@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sale(
    sale_id: int,
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme)
):
    """Supprime une vente"""
    deleted = sale_service.delete(sale_id, tenant_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sale not found")