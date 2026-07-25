import pytest


def test_create_product(client, full_auth_headers):
    """Test création d'un produit via API"""
    response = client.post(
        "/products/",
        json={
            "name": "API Product",
            "description": "Product from API",
            "price": 29.99,
            "stock": 20
        },
        headers=full_auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "API Product"
    assert data["price"] == 29.99
    assert data["stock"] == 20
    assert data["tenant_id"] == full_auth_headers["X-Tenant-ID"]


def test_list_products(client, full_auth_headers):
    """Test liste des produits via API"""
    # Créer un produit d'abord
    client.post(
        "/products/",
        json={"name": "List Test", "price": 10.00, "stock": 5},
        headers=full_auth_headers
    )
    
    response = client.get("/products/", headers=full_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


def test_get_product(client, full_auth_headers):
    """Test récupération d'un produit via API"""
    # Créer
    create_response = client.post(
        "/products/",
        json={"name": "Get API Test", "price": 15.00, "stock": 3},
        headers=full_auth_headers
    )
    product_id = create_response.json()["id"]
    
    # Récupérer
    response = client.get(f"/products/{product_id}", headers=full_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Get API Test"


def test_update_product(client, full_auth_headers):
    """Test mise à jour d'un produit via API"""
    # Créer
    create_response = client.post(
        "/products/",
        json={"name": "Update Test", "price": 20.00, "stock": 10},
        headers=full_auth_headers
    )
    product_id = create_response.json()["id"]
    
    # Mettre à jour
    response = client.put(
        f"/products/{product_id}",
        json={"name": "Updated Name", "price": 25.00},
        headers=full_auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["price"] == 25.00


def test_delete_product(client, full_auth_headers):
    """Test suppression d'un produit via API"""
    # Créer
    create_response = client.post(
        "/products/",
        json={"name": "Delete Test", "price": 5.00, "stock": 1},
        headers=full_auth_headers
    )
    product_id = create_response.json()["id"]
    
    # Supprimer
    response = client.delete(f"/products/{product_id}", headers=full_auth_headers)
    assert response.status_code == 204
    
    # Vérifier qu'il n'existe plus
    get_response = client.get(f"/products/{product_id}", headers=full_auth_headers)
    assert get_response.status_code == 404