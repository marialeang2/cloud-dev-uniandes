import pytest
from httpx import AsyncClient
from io import BytesIO


@pytest.mark.asyncio
class TestVideos:
    
    async def test_list_videos_success(self, client: AsyncClient, test_user, test_video):
        """Test listing user's videos"""
        response = await client.get(
            f"/api/videos?user_id={test_user.id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["title"] == "Test Video"
    
    async def test_list_videos_empty(self, client: AsyncClient, another_test_user):
        """Test listing videos for user with no videos"""
        response = await client.get(
            f"/api/videos?user_id={another_test_user.id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    async def test_list_videos_invalid_user_id(self, client: AsyncClient):
        """Test listing videos with invalid user_id"""
        response = await client.get(
            "/api/videos?user_id=invalid-uuid"
        )
        
        assert response.status_code == 400
    
    async def test_get_video_success(self, client: AsyncClient, test_user, test_video):
        """Test getting video details"""
        response = await client.get(
            f"/api/videos/{test_video.id}?user_id={test_user.id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["video_id"] == str(test_video.id)
        assert data["title"] == "Test Video"
        assert "votes" in data
        assert "duration_seconds" in data
    
    async def test_get_video_not_found(self, client: AsyncClient, test_user):
        """Test getting non-existent video"""
        import uuid
        fake_id = str(uuid.uuid4())
        
        response = await client.get(
            f"/api/videos/{fake_id}?user_id={test_user.id}"
        )
        
        assert response.status_code == 404
    
    async def test_get_video_not_owner(self, client: AsyncClient, another_test_user, test_video):
        """Test getting video by non-owner"""
        response = await client.get(
            f"/api/videos/{test_video.id}?user_id={another_test_user.id}"
        )
        
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    async def test_delete_video_success(self, client: AsyncClient, test_user, test_video):
        """Test deleting a video"""
        response = await client.delete(
            f"/api/videos/{test_video.id}?user_id={test_user.id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "deleted successfully" in data["message"].lower()
        assert data["video_id"] == str(test_video.id)
    
    async def test_delete_video_not_owner(self, client: AsyncClient, another_test_user, test_video):
        """Test deleting video by non-owner"""
        response = await client.delete(
            f"/api/videos/{test_video.id}?user_id={another_test_user.id}"
        )
        
        assert response.status_code == 403
    
    async def test_delete_public_video(self, client: AsyncClient, test_user, public_test_video):
        """Test deleting a public video (should fail)"""
        response = await client.delete(
            f"/api/videos/{public_test_video.id}?user_id={test_user.id}"
        )
        
        assert response.status_code == 400
        assert "public" in response.json()["detail"].lower()
    
    async def test_delete_video_not_found(self, client: AsyncClient, test_user):
        """Test deleting non-existent video"""
        import uuid
        fake_id = str(uuid.uuid4())
        
        response = await client.delete(
            f"/api/videos/{fake_id}?user_id={test_user.id}"
        )
        
        assert response.status_code == 404

