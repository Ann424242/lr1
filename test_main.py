from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200

def test_get_users():
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "username" in data[0]

def test_create_user():
    test_user = {
        "username": "testuser_ermolina",
        "email": "testuser_ermolina@example.com",
        "full_name": "Test User Ermolina",
        "password": "password123"
    }
    
    # Test successful registration
    response = client.post("/register/", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    
    # Test duplicate registration
    response = client.post("/register/", json=test_user)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_auth():
    # First create a test user
    test_user = {
        "username": "authuser_ermolina",
        "email": "authuser_ermolina@example.com",
        "full_name": "Auth User Ermolina",
        "password": "authpass123"
    }
    client.post("/register/", json=test_user)
    
    # Test successful authentication
    auth_data = {
        "username": "authuser_ermolina",
        "password": "authpass123",
        "grant_type": "password"
    }
    response = client.post("/token", data=auth_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    
    # Test failed authentication
    bad_auth_data = {
        "username": "authuser_ermolina",
        "password": "wrongpassword",
        "grant_type": "password"
    }
    response = client.post("/token", data=bad_auth_data)
    assert response.status_code == 400

def test_protected_routes():
    # Create test user and get token
    test_user = {
        "username": "protecteduser_ermolina",
        "email": "protecteduser_ermolina@example.com",
        "full_name": "Protected User Ermolina",
        "password": "protected123"
    }
    client.post("/register/", json=test_user)
    
    auth_data = {
        "username": "protecteduser_ermolina",
        "password": "protected123",
        "grant_type": "password"
    }
    token_response = client.post("/token", data=auth_data)
    token = token_response.json()["access_token"]
    
    # Test access to protected route with valid token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "protecteduser_ermolina"
    
    # Test access with invalid token
    bad_headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get("/users/me", headers=bad_headers)
    assert response.status_code == 401

def test_update_user():
    # Create test user and get token
    test_user = {
        "username": "updateuser_ermolina",
        "email": "updateuser_ermolina@example.com",
        "full_name": "Update User Ermolina",
        "password": "update123"
    }
    client.post("/register/", json=test_user)
    
    auth_data = {
        "username": "updateuser_ermolina",
        "password": "update123",
        "grant_type": "password"
    }
    token_response = client.post("/token", data=auth_data)
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get user ID
    users_response = client.get("/users/")
    user_id = next(u["id"] for u in users_response.json() if u["username"] == "updateuser_ermolina")
    
    # Test successful update
    update_data = {"full_name": "Updated Name Ermolina"}
    response = client.put(f"/users/{user_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name Ermolina"
    
    # Test update without token
    response = client.put(f"/users/{user_id}", json=update_data)
    assert response.status_code == 401

def test_delete_user():
    # Create test user and get token
    test_user = {
        "username": "deleteuser_ermolina",
        "email": "deleteuser_ermolina@example.com",
        "full_name": "Delete User Ermolina",
        "password": "delete123"
    }
    client.post("/register/", json=test_user)
    
    auth_data = {
        "username": "deleteuser_ermolina",
        "password": "delete123",
        "grant_type": "password"
    }
    token_response = client.post("/token", data=auth_data)
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get user ID
    users_response = client.get("/users/")
    user_id = next(u["id"] for u in users_response.json() if u["username"] == "deleteuser_ermolina")
    
    # Test successful delete
    response = client.delete(f"/users/{user_id}", headers=headers)
    assert response.status_code == 200
    
    # Test delete non-existent user
    response = client.delete(f"/users/{user_id}", headers=headers)
    assert response.status_code == 404

def test_cors_headers():
    # Test CORS headers
    response = client.options("/users/", headers={
        "Origin": "http://localhost:8080",
        "Access-Control-Request-Method": "GET"
    })
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers