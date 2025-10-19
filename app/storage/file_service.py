from app.storage.base_storage import BaseStorage
from app.storage.local_storage import LocalStorage 

class FileService:
    def __init__(self, storage: BaseStorage):
        self.storage = storage

    async def save_file(self, file_content: bytes, filename: str, subfolder: str = "uploads"):
        path = await self.storage.save_file(file_content, filename, subfolder)
        return str(path)

    async def delete_file(self, path: str):
        await self.storage.delete_file(path)
    
    def get_file_url(self, path:str):
        return self.storage.get_file_url(path)


storage = LocalStorage()
fileservice = FileService(storage)