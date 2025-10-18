from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "anb_video_tasks",
    broker="pyamqp://guest:guest@localhost//",
    backend="rpc://",
    include=["app.tasks.video_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)