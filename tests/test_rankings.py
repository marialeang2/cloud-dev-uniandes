import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRankings:
    
    async def test_list_public_videos(self, client: AsyncClient, public_test_video):
        """Test listing public videos"""
        response = await client.get("/api/public/videos")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        # Updated to match PublicVideoItem contract
        assert data[0]["title"] == "Public Test Video"
        assert "processed_url" in data[0]
        assert "username" in data[0]
        assert "city" in data[0]
        assert "votes" in data[0]
    
    async def test_list_public_videos_pagination(self, client: AsyncClient, public_test_video):
        """Test pagination for public videos"""
        response = await client.get("/api/public/videos?limit=5&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
    
    async def test_list_public_videos_empty(self, client: AsyncClient, test_video):
        """Test listing public videos when only private videos exist"""
        response = await client.get("/api/public/videos")
        
        assert response.status_code == 200
        data = response.json()
        # Should not include private videos
        assert all(v["title"] != "Test Video" for v in data)
    
    async def test_get_rankings(self, client: AsyncClient, public_test_video):
        """Test getting rankings"""
        response = await client.get("/api/public/rankings")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_get_rankings_with_votes(
        self, 
        client: AsyncClient, 
        test_user,
        another_test_user,
        public_test_video
    ):
        """Test rankings with votes"""
        # Add a vote
        await client.post(
            f"/api/public/videos/{public_test_video.id}/vote",
            json={"user_id": str(another_test_user.id)}
        )
        
        response = await client.get("/api/public/rankings")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            assert "position" in data[0]
            assert "username" in data[0]
            assert "city" in data[0]
            assert "votes" in data[0]
            # Check if votes count is correct
            assert data[0]["votes"] >= 1
    
    async def test_get_rankings_filter_by_city(
        self,
        client: AsyncClient,
        public_test_video
    ):
        """Test filtering rankings by city"""
        response = await client.get("/api/public/rankings?city=Bogotá")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All results should be from Bogotá
        assert all(item["city"] == "Bogotá" for item in data)
    
    async def test_get_rankings_pagination(self, client: AsyncClient):
        """Test pagination for rankings"""
        response = await client.get("/api/public/rankings?limit=10&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
    
    async def test_get_rankings_empty(self, client: AsyncClient):
        """Test rankings when no public videos exist"""
        response = await client.get("/api/public/rankings")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

