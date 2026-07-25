import pytest
from app.services.tenant import tenant_service
from app.schemas.tenant import TenantCreate


def test_create_tenant():
    """Test création d'un tenant"""
    data = TenantCreate(name="Unit Test Tenant", description="Test description")
    tenant = tenant_service.create(data)
    
    assert tenant.id is not None
    assert tenant.name == "Unit Test Tenant"
    assert tenant.tenant_id.startswith("tenant_")
    assert tenant.is_active is True


def test_get_tenant(test_tenant):
    """Test récupération d'un tenant"""
    tenant = tenant_service.get(test_tenant["tenant_id"])
    assert tenant is not None
    assert tenant.id == test_tenant["id"]
    assert tenant.name == test_tenant["name"]


def test_list_tenants(test_tenant):
    """Test liste des tenants"""
    result = tenant_service.list()
    assert result["total"] >= 1
    assert len(result["items"]) >= 1


def test_update_tenant(test_tenant):
    """Test mise à jour d'un tenant"""
    from app.schemas.tenant import TenantUpdate
    update_data = TenantUpdate(name="Updated Name")
    
    tenant = tenant_service.update(test_tenant["tenant_id"], update_data)
    assert tenant is not None
    assert tenant.name == "Updated Name"


def test_delete_tenant(test_tenant):
    """Test suppression d'un tenant"""
    result = tenant_service.delete(test_tenant["tenant_id"])
    assert result is True
    
    # Vérifier que le tenant n'existe plus
    tenant = tenant_service.get(test_tenant["tenant_id"])
    assert tenant is None