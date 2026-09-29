from abc import ABC, abstractmethod

from src.domain.entities import User


class UserRepository(ABC):
    @abstractmethod
    async def create(self, name: str, email: str, password: str) -> User: ...

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def delete(self, user_id: int) -> bool: ...
