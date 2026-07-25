import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
import uuid

# Base de données de test SQLite en mémoire
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    """Crée les tables avant chaque test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Client de test FastAPI"""
    return TestClient(app)


@pytest.fixture
def test_tenant(client):
    """Crée un tenant de test avec un ID unique"""
    unique_id = uuid.uuid4().hex[:8]
    response = client.post(
        "/tenants/",
        json={
            "name": f"Test Tenant {unique_id}",
            "description": "Tenant pour les tests"
        }
    )
    return response.json()


@pytest.fixture
def test_user(client, test_tenant):
    """Crée un utilisateur de test avec des données uniques"""
    unique_id = uuid.uuid4().hex[:8]
    tenant_id = test_tenant["tenant_id"]
    headers = {"X-Tenant-ID": tenant_id}
    
    response = client.post(
        "/auth/register",
        json={
            "email": f"test_{unique_id}@test.com",
            "username": f"testuser_{unique_id}",
            "password": "password123",
            "full_name": "Test User"
        },
        headers=headers
    )
    
    # Si erreur, on affiche le détail
    if response.status_code != 201:
        print(f"Erreur création user: {response.json()}")
    
    return response.json()


@pytest.fixture
def test_token(client, test_user):
    """Récupère un token JWT de test"""
    email = test_user.get("email")
    if not email:
        pytest.fail("test_user n'a pas d'email")
    
    response = client.post(
        "/auth/login",
        json={"email": email, "password": "password123"}
    )
    
    if response.status_code != 200:
        pytest.fail(f"Login échoué: {response.json()}")
    
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(test_tenant):
    """Headers d'authentification avec tenant"""
    return {"X-Tenant-ID": test_tenant["tenant_id"]}


@pytest.fixture
def full_auth_headers(test_token, test_tenant):
    """Headers complets avec token et tenant"""
    return {
        "Authorization": f"Bearer {test_token}",
        "X-Tenant-ID": test_tenant["tenant_id"]
    }