import shutil
from pathlib import Path
from time import sleep
from uuid import UUID
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from moviepy import ImageClip, VideoFileClip, CompositeVideoClip, vfx

from app.core.celery_app import celery_app
from app.core.config import settings
from app.utils.video_validator_sync import validate_video_sync
from app.models.video import Video

# Create synchronous database session for Celery worker
SYNC_DATABASE_URL = settings.DATABASE_URL.replace("+asyncpg", "")
sync_engine = create_engine(SYNC_DATABASE_URL)
SyncSessionLocal = sessionmaker(bind=sync_engine)


@celery_app.task(name="process_video")
def process_video_task(video_id: str, temp_file_path: str):
    """
    Process uploaded video asynchronously.
    
    Steps:
    1. Update status to 'processing'
    2. Validate video with FFprobe
    3. Process video (cutting, resizing, adding banner)
    4. Move to processed folder
    5. Update status to 'processed' or 'failed'
    """
    db = SyncSessionLocal()
    
    try:
        # Get video record
        video = db.query(Video).filter(Video.id == UUID(video_id)).first()
        
        if not video:
            raise Exception(f"Video {video_id} not found in database")
        
        # Update status to processing
        video.status = "processing"
        db.commit()
        
        # Validate video with FFprobe
        metadata = validate_video_sync(temp_file_path)
        
        # Update duration
        video.duration_seconds = int(metadata['duration'])
        db.commit()
        
        # Process video (cutting, adding banner, watermark and resizing.)
        videoclip = VideoFileClip("../../" + video.file_path)

        if video.duration_seconds > 30:
            videoclip = videoclip.with_end(30)
            watermark = ImageClip("../res/ANBLogo-1920x1080.png").set_start(2.5).set_duration(30).set_pos(("center","center")).with_position(("center", 0.25), relative=True)
            outro = ImageClip("../res/ANBLogo-1920x1080.png").set_start(32.5).set_duration(3.5).set_pos(("center","center")).with_position(("center", 0.25), relative=True)
        else:
            watermark = ImageClip("../res/ANBLogo-1920x1080.png").set_start(2.5).set_duration(video.duration_seconds).set_pos(("center","center")).with_position(("center", 0.25), relative=True)
            outro = ImageClip("../res/ANBLogo-1920x1080.png").set_start(video.duration_seconds + 3.5).set_duration(3.5).set_pos(("center","center"))

        intro = ImageClip("../res/ANBLogo-1920x1080.png").set_start(0).set_duration(3.5).set_pos(("center","center"))

        videoclip_with_intro = CompositeVideoClip([intro, videoclip.with_effects([vfx.CrossFadeIn(1)]), watermark.with_effects(vfx.CrossFadeIn(1)), outro.with_effects(vfx.CrossFadeIn(1))])

        videoclip_with_intro = videoclip_with_intro.without_audio().with_effects([vfx.resize(height=1080)])

        videoclip_with_intro.write_videofile("../../storage/processed/" + str(video.id))
        
        # Move file from uploads to processed folder
        temp_path = Path(temp_file_path)
        processed_folder = Path(settings.STORAGE_PATH) / "processed"
        processed_folder.mkdir(parents=True, exist_ok=True)
        
        processed_file_path = processed_folder / temp_path.name
        shutil.copy2(temp_path, processed_file_path)
        
        # Update database record
        video.file_path = str(processed_file_path)
        video.status = "processed"
        db.commit()
        
        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()
        
        return {
            "status": "success",
            "video_id": video_id,
            "message": "Video processed successfully"
        }
        
    except Exception as e:
        # Update status to failed
        if video:
            video.status = "failed"
            db.commit()
        
        return {
            "status": "failed",
            "video_id": video_id,
            "error": str(e)
        }
        
    finally:
        db.close()