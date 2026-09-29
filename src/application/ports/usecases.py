from abc import ABC, abstractmethod

from src.domain.entities import TokenPair, User


class RegisterUserPort(ABC):
    @abstractmethod
    async def execute(self, name: str, email: str, password: str) -> int: ...


class LoginUserPort(ABC):
    @abstractmethod
    async def execute(self, email: str, password: str) -> TokenPair: ...


class RefreshTokenPort(ABC):
    @abstractmethod
    async def execute(self, refresh_token: str) -> TokenPair: ...


class GetUserPort(ABC):
    @abstractmethod
    async def execute(self, user_id: int) -> User: ...


class DeleteUserPort(ABC):
    @abstractmethod
    async def execute(self, user_id: int) -> None: ...
