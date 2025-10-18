import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRankings:
    
    async def test_get_rankings_success(self, client: AsyncClient, public_test_video):
        """Test getting rankings (no auth required)"""
        response = await client.get("/api/public/rankings")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_get_rankings_with_city_filter(self, client: AsyncClient, public_test_video):
        """Test getting rankings filtered by city"""
        response = await client.get("/api/public/rankings?city=Bogotá")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All results should be from Bogotá
        for item in data:
            assert item["city"] == "Bogotá"
    
    async def test_get_rankings_with_pagination(self, client: AsyncClient, public_test_video):
        """Test rankings pagination"""
        response = await client.get("/api/public/rankings?limit=5&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
    
    async def test_get_rankings_empty_city(self, client: AsyncClient):
        """Test rankings for city with no videos"""
        response = await client.get("/api/public/rankings?city=NonExistentCity")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    async def test_list_public_videos(self, client: AsyncClient, public_test_video):
        """Test listing public videos (no auth required)"""
        response = await client.get("/api/public/videos")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Verify structure
        if len(data) > 0:
            video = data[0]
            assert "video_id" in video
            assert "title" in video
            assert "username" in video
            assert "city" in video
            assert "votes" in video
    
    async def test_list_public_videos_pagination(self, client: AsyncClient, public_test_video):
        """Test public videos pagination"""
        response = await client.get("/api/public/videos?limit=10&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
    
    async def test_list_public_videos_only_public(self, client: AsyncClient, test_video, public_test_video):
        """Test that only public videos are listed"""
        response = await client.get("/api/public/videos")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify private video is not in the list
        video_ids = [v["video_id"] for v in data]
        assert str(test_video.id) not in video_ids
        assert str(public_test_video.id) in video_ids