import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestVotes:
    
    async def test_vote_success(self, client: AsyncClient, test_user, another_test_user, public_test_video):
        """Test voting for a public video"""
        response = await client.post(
            f"/api/public/videos/{public_test_video.id}/vote",
            json={"user_id": str(another_test_user.id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "vote registered successfully" in data["message"].lower()
    
    async def test_vote_duplicate(self, client: AsyncClient, another_test_user, public_test_video):
        """Test duplicate vote (should fail)"""
        # First vote
        await client.post(
            f"/api/public/videos/{public_test_video.id}/vote",
            json={"user_id": str(another_test_user.id)}
        )
        
        # Second vote (duplicate)
        response = await client.post(
            f"/api/public/videos/{public_test_video.id}/vote",
            json={"user_id": str(another_test_user.id)}
        )
        
        assert response.status_code == 400
        assert "already voted" in response.json()["detail"].lower()
    
    async def test_vote_non_public_video(self, client: AsyncClient, another_test_user, test_video):
        """Test voting for non-public video (should fail)"""
        response = await client.post(
            f"/api/public/videos/{test_video.id}/vote",
            json={"user_id": str(another_test_user.id)}
        )
        
        assert response.status_code == 404
        assert "not found or not public" in response.json()["detail"].lower()
    
    async def test_vote_non_existent_video(self, client: AsyncClient, test_user):
        """Test voting for non-existent video"""
        import uuid
        fake_id = str(uuid.uuid4())
        
        response = await client.post(
            f"/api/public/videos/{fake_id}/vote",
            json={"user_id": str(test_user.id)}
        )
        
        assert response.status_code == 404
    
    async def test_vote_invalid_user_id(self, client: AsyncClient, public_test_video):
        """Test voting with invalid user_id"""
        response = await client.post(
            f"/api/public/videos/{public_test_video.id}/vote",
            json={"user_id": "invalid-uuid"}
        )
        
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()

