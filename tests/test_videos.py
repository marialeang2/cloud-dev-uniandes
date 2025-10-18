import pytest
from httpx import AsyncClient
from io import BytesIO
from pathlib import Path


@pytest.mark.asyncio
class TestVideos:
    
    async def test_upload_video_success(self, client: AsyncClient, test_user, test_user_token):
        """Test uploading a valid video file with JWT"""
        video_path = Path("tests/test_data/flex_mini.mp4")
        
        if not video_path.exists():
            pytest.skip("Test video file not found")
        
        with open(video_path, "rb") as f:
            video_content = f.read()
        
        files = {
            "video_file": ("flex_mini_mini.mp4", video_content, "video/mp4")
        }
        data = {
            "title": "My Flex Video"
        }
        
        response = await client.post(
            "/api/videos/upload",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 201
        response_data = response.json()
        assert "task_id" in response_data
        assert "message" in response_data
        assert "successfully" in response_data["message"].lower()
    
    async def test_upload_video_without_auth(self, client: AsyncClient, test_user):
        """Test uploading without authentication"""
        video_path = Path("tests/test_data/flex_mini.mp4")
        
        if not video_path.exists():
            pytest.skip("Test video file not found")
        
        with open(video_path, "rb") as f:
            video_content = f.read()
        
        files = {
            "video_file": ("flex_mini.mp4", video_content, "video/mp4")
        }
        data = {
            "title": "My flex_mini Video"
        }
        
        response = await client.post(
            "/api/videos/upload",
            files=files,
            data=data
        )
        
        assert response.status_code == 401
        # Cambiar la validación para aceptar cualquier mensaje de auth missing
        detail = response.json()["detail"].lower()
        assert "authorization" in detail or "unauthorized" in detail
    
    async def test_upload_video_invalid_token(self, client: AsyncClient):
        """Test uploading with invalid token"""
        video_path = Path("tests/test_data/flex_mini.mp4")
        
        if not video_path.exists():
            pytest.skip("Test video file not found")
        
        with open(video_path, "rb") as f:
            video_content = f.read()
        
        files = {
            "video_file": ("flex_mini.mp4", video_content, "video/mp4")
        }
        data = {
            "title": "My flex_mini Video"
        }
        
        response = await client.post(
            "/api/videos/upload",
            files=files,
            data=data,
            headers={"Authorization": "Bearer invalid-token-12345"}
        )
        
        assert response.status_code == 401
    
    async def test_upload_video_missing_file(self, client: AsyncClient, test_user_token):
        """Test uploading without a file"""
        data = {
            "title": "No File Video"
        }
        
        response = await client.post(
            "/api/videos/upload",
            data=data,
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 422
    
    async def test_upload_video_wrong_format(self, client: AsyncClient, test_user_token):
        """Test uploading non-video file"""
        fake_video = b"This is not a video file"
        
        files = {
            "video_file": ("fake.txt", fake_video, "text/plain")
        }
        data = {
            "title": "Fake Video"
        }
        
        response = await client.post(
            "/api/videos/upload",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 400
    
    async def test_list_videos_success(self, client: AsyncClient, test_user, test_user_token, test_video):
        """Test listing user's videos with JWT"""
        response = await client.get(
            "/api/videos",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["title"] == "Test Video"
    
    async def test_list_videos_without_auth(self, client: AsyncClient):
        """Test listing videos without authentication"""
        response = await client.get("/api/videos")
        
        assert response.status_code == 401
    
    async def test_list_videos_empty(self, client: AsyncClient, another_test_user_token):
        """Test listing videos for user with no videos"""
        response = await client.get(
            "/api/videos",
            headers={"Authorization": f"Bearer {another_test_user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    async def test_get_video_success(self, client: AsyncClient, test_user_token, test_video):
        """Test getting video details with JWT"""
        response = await client.get(
            f"/api/videos/{test_video.id}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["video_id"] == str(test_video.id)
        assert data["title"] == "Test Video"
        assert "votes" in data
        assert "duration_seconds" in data
    
    async def test_get_video_without_auth(self, client: AsyncClient, test_video):
        """Test getting video without authentication"""
        response = await client.get(f"/api/videos/{test_video.id}")
        
        assert response.status_code == 401
    
    async def test_get_video_not_found(self, client: AsyncClient, test_user_token):
        """Test getting non-existent video"""
        import uuid
        fake_id = str(uuid.uuid4())
        
        response = await client.get(
            f"/api/videos/{fake_id}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 404
    
    async def test_get_video_not_owner(self, client: AsyncClient, another_test_user_token, test_video):
        """Test getting video by non-owner"""
        response = await client.get(
            f"/api/videos/{test_video.id}",
            headers={"Authorization": f"Bearer {another_test_user_token}"}
        )
        
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    async def test_publish_video_success(self, client: AsyncClient, test_user_token, test_video):
        """Test publishing a video"""
        response = await client.put(
            f"/api/videos/{test_video.id}/publish",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "published successfully" in data["message"].lower()
    
    async def test_publish_video_without_auth(self, client: AsyncClient, test_video):
        """Test publishing without authentication"""
        response = await client.put(f"/api/videos/{test_video.id}/publish")
        
        assert response.status_code == 401
    
    async def test_publish_video_not_owner(self, client: AsyncClient, another_test_user_token, test_video):
        """Test publishing video by non-owner"""
        response = await client.put(
            f"/api/videos/{test_video.id}/publish",
            headers={"Authorization": f"Bearer {another_test_user_token}"}
        )
        
        assert response.status_code == 403
    
    async def test_delete_video_success(self, client: AsyncClient, test_user_token, test_video):
        """Test deleting a video with JWT"""
        response = await client.delete(
            f"/api/videos/{test_video.id}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "deleted successfully" in data["message"].lower()
        assert data["video_id"] == str(test_video.id)
    
    async def test_delete_video_without_auth(self, client: AsyncClient, test_video):
        """Test deleting without authentication"""
        response = await client.delete(f"/api/videos/{test_video.id}")
        
        assert response.status_code == 401
    
    async def test_delete_video_not_owner(self, client: AsyncClient, another_test_user_token, test_video):
        """Test deleting video by non-owner"""
        response = await client.delete(
            f"/api/videos/{test_video.id}",
            headers={"Authorization": f"Bearer {another_test_user_token}"}
        )
        
        assert response.status_code == 403
    
    async def test_delete_public_video(self, client: AsyncClient, test_user_token, public_test_video):
        """Test deleting a public video (should fail)"""
        response = await client.delete(
            f"/api/videos/{public_test_video.id}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 400
        assert "public" in response.json()["detail"].lower()
    
    async def test_delete_video_not_found(self, client: AsyncClient, test_user_token):
        """Test deleting non-existent video"""
        import uuid
        fake_id = str(uuid.uuid4())
        
        response = await client.delete(
            f"/api/videos/{fake_id}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 404