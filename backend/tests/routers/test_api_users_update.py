"""
Tests for user profile update endpoint (PATCH /users/me)
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User
from app.core.security import hash_password
from app.utils.timezone import now_utc
from tests.factories.user import UserFactory


client = TestClient(app)


@pytest.fixture
def auth_user(db: Session) -> tuple[User, str]:
    """Create a test user and return (user, access_token)."""
    user = UserFactory.create(db)
    # Assume user is created confirmed and active
    user.is_confirmed = True
    user.is_active = True
    db.commit()
    db.refresh(user)
    
    # Generate JWT token (assuming auth endpoint exists)
    # For this test, we'll use the dependency injection mock
    from app.utils.jwt import create_access_token
    token = create_access_token(user.id)
    
    return user, token


def test_read_user_me_success(auth_user: tuple[User, str]):
    """Test GET /users/me returns current user profile."""
    user, token = auth_user
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user.id
    assert data["email"] == user.email
    assert data["username"] == user.username
    assert data["first_name"] == user.first_name
    assert data["last_name"] == user.last_name
    assert data["is_confirmed"] is True
    assert data["is_active"] is True


def test_read_user_me_unauthorized():
    """Test GET /users/me without token returns 401."""
    response = client.get("/api/users/me")
    assert response.status_code == 401


def test_update_user_me_first_name_only(auth_user: tuple[User, str], db: Session):
    """Test PATCH /users/me with first_name only updates only that field."""
    user, token = auth_user
    original_username = user.username
    
    response = client.patch(
        "/api/users/me",
        json={"first_name": "UpdatedFirstName"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "UpdatedFirstName"
    assert data["username"] == original_username  # Unchanged
    
    # Verify in DB
    db_user = db.query(User).filter(User.id == user.id).first()
    assert db_user.first_name == "UpdatedFirstName"
    assert db_user.username == original_username


def test_update_user_me_all_fields(auth_user: tuple[User, str], db: Session):
    """Test PATCH /users/me with all fields updates all of them."""
    user, token = auth_user
    
    response = client.patch(
        "/api/users/me",
        json={
            "first_name": "NewFirst",
            "last_name": "NewLast",
            "username": "newusername"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "NewFirst"
    assert data["last_name"] == "NewLast"
    assert data["username"] == "newusername"


def test_update_user_me_username_conflict(auth_user: tuple[User, str], db: Session):
    """Test PATCH /users/me with existing username returns 409."""
    user, token = auth_user
    
    # Create another user with a specific username
    other_user = UserFactory.create(db, username="existingusername")
    
    response = client.patch(
        "/api/users/me",
        json={"username": "existingusername"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_update_user_me_can_reuse_own_username(auth_user: tuple[User, str], db: Session):
    """Test PATCH /users/me allows user to reuse their own username."""
    user, token = auth_user
    own_username = user.username
    
    response = client.patch(
        "/api/users/me",
        json={"username": own_username},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == own_username


def test_update_user_me_invalid_first_name_too_short(auth_user: tuple[User, str]):
    """Test PATCH /users/me with empty first_name returns 422."""
    user, token = auth_user
    
    response = client.patch(
        "/api/users/me",
        json={"first_name": ""},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 422  # Validation error


def test_update_user_me_invalid_username_too_short(auth_user: tuple[User, str]):
    """Test PATCH /users/me with short username returns 422."""
    user, token = auth_user
    
    response = client.patch(
        "/api/users/me",
        json={"username": "short"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 422  # Validation error


def test_update_user_me_unauthorized():
    """Test PATCH /users/me without token returns 401."""
    response = client.patch(
        "/api/users/me",
        json={"first_name": "Test"}
    )
    assert response.status_code == 401


def test_update_user_me_partial_update_idempotent(auth_user: tuple[User, str], db: Session):
    """Test PATCH /users/me can be called multiple times without side effects."""
    user, token = auth_user
    
    # First update
    response1 = client.patch(
        "/api/users/me",
        json={"first_name": "FirstUpdate"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response1.status_code == 200
    
    # Second update with different field
    response2 = client.patch(
        "/api/users/me",
        json={"last_name": "SecondUpdate"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response2.status_code == 200
    data = response2.json()
    assert data["first_name"] == "FirstUpdate"  # Retained from first update
    assert data["last_name"] == "SecondUpdate"
