import aiofiles
from pathlib import Path
from typing import BinaryIO


class LocalStorage:
    def __init__(self, base_path: str = "./storage"):
        self.base_path = Path(base_path)
        # Create all required directories on initialization
        self.base_path.mkdir(exist_ok=True)
        (self.base_path / "uploads").mkdir(exist_ok=True)
        (self.base_path / "processed").mkdir(exist_ok=True)
        (self.base_path / "temp").mkdir(exist_ok=True)
    
    async def save_file(self, file_content: bytes, filename: str, subfolder: str = "uploads") -> str:
        """Save file to local storage and return the path"""
        folder = self.base_path / subfolder
        folder.mkdir(exist_ok=True)
        
        file_path = folder / filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        return str(file_path)
    
    async def delete_file(self, path: str) -> bool:
        """Delete a file from storage"""
        try:
            file_path = Path(path)
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def get_file_url(self, path: str) -> str:
        """Return the URL/path for file access"""
        return f"/storage/{Path(path).name}"


# Global storage instance
storage = LocalStorage()

