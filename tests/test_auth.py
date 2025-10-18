import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuth:
    
    async def test_signup_success(self, client: AsyncClient):
        """Test successful user registration"""
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password1": "SecurePass123",
            "password2": "SecurePass123",
            "city": "Bogotá",
            "country": "Colombia"
        }
        
        response = await client.post("/api/auth/signup", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "user_id" in data
        assert "message" in data
        assert "successfully" in data["message"].lower()
    
    async def test_signup_duplicate_email(self, client: AsyncClient, test_user):
        """Test signup with existing email"""
        user_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": test_user.email,
            "password1": "SecurePass123",
            "password2": "SecurePass123",
            "city": "Medellín",
            "country": "Colombia"
        }
        
        response = await client.post("/api/auth/signup", json=user_data)
        
        assert response.status_code == 409
        assert "already" in response.json()["detail"].lower()
    
    async def test_signup_password_mismatch(self, client: AsyncClient):
        """Test signup with mismatched passwords"""
        user_data = {
            "first_name": "Bob",
            "last_name": "Smith",
            "email": "bob@example.com",
            "password1": "SecurePass123",
            "password2": "DifferentPass456",
            "city": "Cali",
            "country": "Colombia"
        }
        
        response = await client.post("/api/auth/signup", json=user_data)
        
        assert response.status_code == 422
    
    async def test_signup_invalid_email(self, client: AsyncClient):
        """Test signup with invalid email format"""
        user_data = {
            "first_name": "Alice",
            "last_name": "Johnson",
            "email": "not-an-email",
            "password1": "SecurePass123",
            "password2": "SecurePass123",
            "city": "Cartagena",
            "country": "Colombia"
        }
        
        response = await client.post("/api/auth/signup", json=user_data)
        
        assert response.status_code == 422
    
    async def test_signup_short_password(self, client: AsyncClient):
        """Test signup with password too short"""
        user_data = {
            "first_name": "Charlie",
            "last_name": "Brown",
            "email": "charlie@example.com",
            "password1": "Short1",
            "password2": "Short1",
            "city": "Barranquilla",
            "country": "Colombia"
        }
        
        response = await client.post("/api/auth/signup", json=user_data)
        
        assert response.status_code == 422
    
    async def test_login_success(self, client: AsyncClient, test_user):
        """Test successful login"""
        credentials = {
            "email": "test@example.com",
            "password": "Test123456"
        }
        
        response = await client.post("/api/auth/login", json=credentials)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "user_id" in data
        assert "email" in data
        assert data["email"] == test_user.email
    
    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """Test login with incorrect password"""
        credentials = {
            "email": test_user.email,
            "password": "WrongPassword123"
        }
        
        response = await client.post("/api/auth/login", json=credentials)
        
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()
    
    async def test_login_non_existent_user(self, client: AsyncClient):
        """Test login with non-existent email"""
        credentials = {
            "email": "nonexistent@example.com",
            "password": "AnyPassword123"
        }
        
        response = await client.post("/api/auth/login", json=credentials)
        
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()
    
    async def test_login_invalid_email_format(self, client: AsyncClient):
        """Test login with invalid email format"""
        credentials = {
            "email": "not-an-email",
            "password": "Password123"
        }
        
        response = await client.post("/api/auth/login", json=credentials)
        
        assert response.status_code == 422
    
    async def test_token_usage(self, client: AsyncClient, test_user, test_user_token):
        """Test using JWT token to access protected endpoint"""
        response = await client.get(
            "/api/videos",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 200
    
    async def test_invalid_token(self, client: AsyncClient):
        """Test using invalid JWT token"""
        response = await client.get(
            "/api/videos",
            headers={"Authorization": "Bearer invalid-token-xyz"}
        )
        
        assert response.status_code == 401
    
    async def test_missing_bearer_prefix(self, client: AsyncClient, test_user_token):
        """Test JWT without Bearer prefix"""
        response = await client.get(
            "/api/videos",
            headers={"Authorization": test_user_token}
        )
        
        assert response.status_code == 401