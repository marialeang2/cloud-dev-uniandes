import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuth:
    
    async def test_signup_success(self, client: AsyncClient):
        """Test successful user registration"""
        response = await client.post("/api/auth/signup", json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "password1": "SecurePass123",
            "password2": "SecurePass123",
            "city": "Bogotá",
            "country": "Colombia"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert "user_id" in data
        assert "message" in data
        assert data["message"] == "User created successfully"
    
    async def test_signup_duplicate_email(self, client: AsyncClient, test_user):
        """Test signup with duplicate email"""
        response = await client.post("/api/auth/signup", json={
            "first_name": "Another",
            "last_name": "User",
            "email": "test@example.com",  # Email already exists
            "password1": "SecurePass123",
            "password2": "SecurePass123",
            "city": "Medellín",
            "country": "Colombia"
        })
        
        assert response.status_code == 400
        assert "email already registered" in response.json()["detail"].lower()
    
    async def test_signup_password_mismatch(self, client: AsyncClient):
        """Test signup with mismatched passwords"""
        response = await client.post("/api/auth/signup", json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john2@example.com",
            "password1": "SecurePass123",
            "password2": "DifferentPass123",
            "city": "Bogotá",
            "country": "Colombia"
        })
        
        assert response.status_code == 400  # Changed from 422 to 400 (contract requirement)
    
    async def test_signup_invalid_email(self, client: AsyncClient):
        """Test signup with invalid email"""
        response = await client.post("/api/auth/signup", json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "not-an-email",
            "password1": "SecurePass123",
            "password2": "SecurePass123",
            "city": "Bogotá",
            "country": "Colombia"
        })
        
        assert response.status_code == 400  # Changed from 422 to 400 (contract requirement)
    
    async def test_login_success(self, client: AsyncClient, test_user):
        """Test successful login"""
        response = await client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "Test123456"
        })
        
        assert response.status_code == 200
        data = response.json()
        # Updated to match TokenResponse contract
        assert "access_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 3600
    
    async def test_login_invalid_email(self, client: AsyncClient):
        """Test login with non-existent email"""
        response = await client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "WrongPassword"
        })
        
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()
    
    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """Test login with wrong password"""
        response = await client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "WrongPassword123"
        })
        
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()

