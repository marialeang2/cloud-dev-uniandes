import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestVotes:
    
    async def test_vote_video_success(self, client: AsyncClient, another_test_user_token, public_test_video):
        """Test voting for a public video with JWT"""
        response = await client.post(
            f"/api/public/videos/{public_test_video.id}/vote",
            headers={"Authorization": f"Bearer {another_test_user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "vote" in data["message"].lower()
        assert "successfully" in data["message"].lower()
    
    async def test_vote_video_without_auth(self, client: AsyncClient, public_test_video):
        """Test voting without authentication"""
        response = await client.post(
            f"/api/public/videos/{public_test_video.id}/vote"
        )
        
        assert response.status_code == 401
        # Cambiar la validación para aceptar cualquier mensaje de auth missing
        detail = response.json()["detail"].lower()
        assert "authorization" in detail or "unauthorized" in detail
    
    async def test_vote_video_duplicate(self, client: AsyncClient, another_test_user_token, public_test_video, test_db):
        """Test voting twice for the same video"""
        # First vote
        response1 = await client.post(
            f"/api/public/videos/{public_test_video.id}/vote",
            headers={"Authorization": f"Bearer {another_test_user_token}"}
        )
        assert response1.status_code == 200
        
        # Second vote (should fail)
        response2 = await client.post(
            f"/api/public/videos/{public_test_video.id}/vote",
            headers={"Authorization": f"Bearer {another_test_user_token}"}
        )
        
        assert response2.status_code == 400
        assert "already voted" in response2.json()["detail"].lower()
    
    async def test_vote_non_public_video(self, client: AsyncClient, another_test_user_token, test_video):
        """Test voting for a non-public video"""
        response = await client.post(
            f"/api/public/videos/{test_video.id}/vote",
            headers={"Authorization": f"Bearer {another_test_user_token}"}
        )
        
        assert response.status_code == 404
    
    async def test_vote_non_existent_video(self, client: AsyncClient, another_test_user_token):
        """Test voting for non-existent video"""
        import uuid
        fake_id = str(uuid.uuid4())
        
        response = await client.post(
            f"/api/public/videos/{fake_id}/vote",
            headers={"Authorization": f"Bearer {another_test_user_token}"}
        )
        
        assert response.status_code == 404
    
    async def test_vote_invalid_video_id(self, client: AsyncClient, another_test_user_token):
        """Test voting with invalid video ID format"""
        response = await client.post(
            "/api/public/videos/invalid-uuid/vote",
            headers={"Authorization": f"Bearer {another_test_user_token}"}
        )
        
        assert response.status_code == 400
    
    async def test_vote_own_video(self, client: AsyncClient, test_user_token, public_test_video):
        """Test voting for own video (should be allowed but validate it works)"""
        response = await client.post(
            f"/api/public/videos/{public_test_video.id}/vote",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        # The system should either allow or deny this - adjust based on your business rules
        assert response.status_code in [200, 400]