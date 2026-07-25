import pytest


def test_create_sale(client, full_auth_headers):
    """Test création d'une vente via API"""
    # Créer un produit d'abord
    product_response = client.post(
        "/products/",
        json={"name": "Sale Product", "price": 10.00, "stock": 50},
        headers=full_auth_headers
    )
    product_id = product_response.json()["id"]
    
    # Créer la vente
    response = client.post(
        "/sales/",
        json={
            "status": "completed",
            "items": [
                {"product_id": product_id, "quantity": 2, "unit_price": 10.00}
            ]
        },
        headers=full_auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["total"] == 20.00
    assert data["status"] == "completed"
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 2


def test_create_sale_updates_stock(client, full_auth_headers):
    """Test que le stock est mis à jour après une vente"""
    # Créer un produit avec stock
    product_response = client.post(
        "/products/",
        json={"name": "Stock Product", "price": 5.00, "stock": 10},
        headers=full_auth_headers
    )
    product_id = product_response.json()["id"]
    initial_stock = product_response.json()["stock"]
    
    # Vendre 3 unités
    response = client.post(
        "/sales/",
        json={
            "status": "completed",
            "items": [
                {"product_id": product_id, "quantity": 3, "unit_price": 5.00}
            ]
        },
        headers=full_auth_headers
    )
    assert response.status_code == 201
    
    # Vérifier le stock
    product_response = client.get(f"/products/{product_id}", headers=full_auth_headers)
    assert product_response.json()["stock"] == initial_stock - 3


def test_create_sale_insufficient_stock(client, full_auth_headers):
    """Test erreur quand stock insuffisant"""
    # Créer un produit avec stock limité
    product_response = client.post(
        "/products/",
        json={"name": "Limited Stock", "price": 5.00, "stock": 2},
        headers=full_auth_headers
    )
    product_id = product_response.json()["id"]
    
    # Essayer de vendre plus que le stock
    response = client.post(
        "/sales/",
        json={
            "status": "completed",
            "items": [
                {"product_id": product_id, "quantity": 5, "unit_price": 5.00}
            ]
        },
        headers=full_auth_headers
    )
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]


def test_list_sales(client, full_auth_headers):
    """Test liste des ventes"""
    # Créer un produit
    product_response = client.post(
        "/products/",
        json={"name": "List Sale Product", "price": 10.00, "stock": 50},
        headers=full_auth_headers
    )
    product_id = product_response.json()["id"]
    
    # Créer une vente
    client.post(
        "/sales/",
        json={
            "status": "completed",
            "items": [
                {"product_id": product_id, "quantity": 1, "unit_price": 10.00}
            ]
        },
        headers=full_auth_headers
    )
    
    # Lister
    response = client.get("/sales/", headers=full_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


def test_get_sale(client, full_auth_headers):
    """Test récupération d'une vente"""
    # Créer un produit
    product_response = client.post(
        "/products/",
        json={"name": "Get Sale Product", "price": 10.00, "stock": 50},
        headers=full_auth_headers
    )
    product_id = product_response.json()["id"]
    
    # Créer une vente
    sale_response = client.post(
        "/sales/",
        json={
            "status": "completed",
            "items": [
                {"product_id": product_id, "quantity": 1, "unit_price": 10.00}
            ]
        },
        headers=full_auth_headers
    )
    sale_id = sale_response.json()["id"]
    
    # Récupérer
    response = client.get(f"/sales/{sale_id}", headers=full_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sale_id
    assert len(data["items"]) == 1


def test_update_sale_status(client, full_auth_headers):
    """Test mise à jour du statut d'une vente"""
    # Créer un produit
    product_response = client.post(
        "/products/",
        json={"name": "Update Sale Product", "price": 10.00, "stock": 50},
        headers=full_auth_headers
    )
    product_id = product_response.json()["id"]
    
    # Créer une vente
    sale_response = client.post(
        "/sales/",
        json={
            "status": "pending",
            "items": [
                {"product_id": product_id, "quantity": 1, "unit_price": 10.00}
            ]
        },
        headers=full_auth_headers
    )
    sale_id = sale_response.json()["id"]
    
    # Mettre à jour le statut
    response = client.put(
        f"/sales/{sale_id}",
        json={"status": "completed"},
        headers=full_auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"


def test_delete_sale(client, full_auth_headers):
    """Test suppression d'une vente"""
    # Créer un produit
    product_response = client.post(
        "/products/",
        json={"name": "Delete Sale Product", "price": 10.00, "stock": 50},
        headers=full_auth_headers
    )
    product_id = product_response.json()["id"]
    
    # Créer une vente
    sale_response = client.post(
        "/sales/",
        json={
            "status": "completed",
            "items": [
                {"product_id": product_id, "quantity": 1, "unit_price": 10.00}
            ]
        },
        headers=full_auth_headers
    )
    sale_id = sale_response.json()["id"]
    
    # Supprimer
    response = client.delete(f"/sales/{sale_id}", headers=full_auth_headers)
    assert response.status_code == 204