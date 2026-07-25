from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.tenant import tenant_service
from app.core.config import settings


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware qui extrait le tenant_id du header X-Tenant-ID.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Routes qui n'ont pas besoin de tenant
        excluded_paths = [
            "/", 
            "/health", 
            "/tenants/",
            "/auth/register",
            "/auth/login",
            "/auth/me",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
        
        # Exclure aussi les méthodes OPTIONS (CORS)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Vérifier si la route est exclue
        if request.url.path in excluded_paths:
            return await call_next(request)
        
        # Extraire le tenant_id du header
        tenant_id = request.headers.get("X-Tenant-ID")
        
        # En développement, on peut utiliser un tenant par défaut
        if not tenant_id and settings.ENVIRONMENT == "development":
            # Chercher un tenant existant
            result = tenant_service.list(limit=1)
            if result["total"] > 0:
                tenant = result["items"][0]
                tenant_id = tenant.tenant_id
                request.state.tenant = tenant
                request.state.tenant_id = tenant_id
                return await call_next(request)
        
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing X-Tenant-ID header"
            )
        
        # Vérifier que le tenant existe
        tenant = tenant_service.get(tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tenant {tenant_id} not found"
            )
        
        # Stocker le tenant dans request.state
        request.state.tenant = tenant
        request.state.tenant_id = tenant_id
        
        response = await call_next(request)
        return response