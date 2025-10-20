import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models import User, Video, Vote
from app.utils.security import get_password_hash
from app.utils.jwt import create_access_token

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://anb_user:anb_pass@localhost:5432/anb_db_test"


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ⭐ NUEVO: Mock de Celery para tests
@pytest.fixture(autouse=True)
def mock_celery():
    """Mock Celery tasks para evitar conexión a RabbitMQ en tests"""
    with patch('app.tasks.video_tasks.process_video_task.delay') as mock_task:
        # Simular que la tarea se ejecuta exitosamente
        mock_result = MagicMock()
        mock_result.id = "test-task-id"
        mock_task.return_value = mock_result
        yield mock_task


@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator:
    """Create a test database for each test function"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
    )
    
    async with async_session() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def client(test_db) -> AsyncGenerator:
    """Create an HTTP client for testing"""
    from httpx import ASGITransport
    
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(test_db) -> User:
    """Create a test user"""
    from app.repositories.user_repository import user_repository
    
    user = await user_repository.create(
        db=test_db,
        first_name="Test",
        last_name="User",
        email="test@example.com",
        password_hash=get_password_hash("Test123456"),
        city="Bogotá",
        country="Colombia"
    )
    await test_db.commit()
    await test_db.refresh(user)
    
    return user


@pytest.fixture
async def test_user_token(test_user) -> str:
    """Create JWT token for test user"""
    token = create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email}
    )
    return token


@pytest.fixture
async def another_test_user(test_db) -> User:
    """Create another test user"""
    from app.repositories.user_repository import user_repository
    
    user = await user_repository.create(
        db=test_db,
        first_name="Another",
        last_name="User",
        email="another@example.com",
        password_hash=get_password_hash("Test123456"),
        city="Medellín",
        country="Colombia"
    )
    await test_db.commit()
    await test_db.refresh(user)
    
    return user


@pytest.fixture
async def another_test_user_token(another_test_user) -> str:
    """Create JWT token for another test user"""
    token = create_access_token(
        data={"sub": str(another_test_user.id), "email": another_test_user.email}
    )
    return token


@pytest.fixture
async def test_video(test_db, test_user) -> Video:
    """Create a test video"""
    from app.repositories.video_repository import video_repository
    
    video = await video_repository.create(
        db=test_db,
        user_id=test_user.id,
        title="Test Video",
        original_filename="test.mp4",
        file_path="storage/uploads/test.mp4",
        duration_seconds=30,
        file_size_bytes=1024000,
        status="processed"
    )
    await test_db.commit()
    await test_db.refresh(video)
    
    return video


@pytest.fixture
async def public_test_video(test_db, test_user) -> Video:
    """Create a public test video"""
    from app.repositories.video_repository import video_repository
    
    video = await video_repository.create(
        db=test_db,
        user_id=test_user.id,
        title="Public Test Video",
        original_filename="public_test.mp4",
        file_path="storage/uploads/public_test.mp4",
        duration_seconds=45,
        file_size_bytes=2048000,
        status="processed"
    )
    video.is_public = True
    await test_db.commit()
    await test_db.refresh(video)
    
    return video


@pytest.fixture
async def processing_video(test_db, test_user) -> Video:
    """Create a video in processing state"""
    from app.repositories.video_repository import video_repository
    
    video = await video_repository.create(
        db=test_db,
        user_id=test_user.id,
        title="Processing Video",
        original_filename="processing.mp4",
        file_path="storage/uploads/processing.mp4",
        duration_seconds=0,
        file_size_bytes=1024000,
        status="processing"
    )
    await test_db.commit()
    await test_db.refresh(video)
    
    return video