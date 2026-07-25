import pytest
from app.services.product import product_service
from app.schemas.product import ProductCreate


def test_create_product(test_tenant):
    """Test création d'un produit"""
    tenant_id = test_tenant["tenant_id"]
    data = ProductCreate(
        name="Test Product",
        description="Test description",
        price=19.99,
        stock=10
    )
    product = product_service.create(tenant_id, data)
    
    assert product.id is not None
    assert product.name == "Test Product"
    assert product.price == 19.99
    assert product.stock == 10


def test_get_product(test_tenant):
    """Test récupération d'un produit"""
    tenant_id = test_tenant["tenant_id"]
    
    # Créer un produit
    data = ProductCreate(name="Get Test", price=9.99, stock=5)
    created = product_service.create(tenant_id, data)
    
    # Récupérer
    product = product_service.get(created.id, tenant_id)
    assert product is not None
    assert product.name == "Get Test"


def test_list_products(test_tenant):
    """Test liste des produits"""
    tenant_id = test_tenant["tenant_id"]
    
    # Créer plusieurs produits
    for i in range(3):
        data = ProductCreate(name=f"Product {i}", price=10.00, stock=10)
        product_service.create(tenant_id, data)
    
    result = product_service.list(tenant_id)
    assert result["total"] >= 3


def test_update_product(test_tenant):
    """Test mise à jour d'un produit"""
    tenant_id = test_tenant["tenant_id"]
    
    # Créer un produit
    data = ProductCreate(name="Original", price=10.00, stock=5)
    created = product_service.create(tenant_id, data)
    
    # Mettre à jour
    from app.schemas.product import ProductUpdate
    update_data = ProductUpdate(name="Updated", price=15.00)
    product = product_service.update(created.id, tenant_id, update_data)
    
    assert product is not None
    assert product.name == "Updated"
    assert product.price == 15.00


def test_delete_product(test_tenant):
    """Test suppression d'un produit"""
    tenant_id = test_tenant["tenant_id"]
    
    # Créer un produit
    data = ProductCreate(name="To Delete", price=5.00, stock=1)
    created = product_service.create(tenant_id, data)
    
    # Supprimer
    result = product_service.delete(created.id, tenant_id)
    assert result is True
    
    # Vérifier
    product = product_service.get(created.id, tenant_id)
    assert product is None