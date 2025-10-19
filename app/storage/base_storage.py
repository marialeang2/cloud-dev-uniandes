from abc import ABC, abstractmethod
from typing import BinaryIO

class BaseStorage(ABC):
    @abstractmethod
    async def save_file(self, file_content: bytes, filename: str, subfolder: str = "uploads") -> str:
        pass

    @abstractmethod
    async def delete_file(self, path: str) -> bool:
        pass

    @abstractmethod
    def get_file_url(self, path: str) -> str:
        pass
