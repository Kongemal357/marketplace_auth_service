from datetime import UTC, datetime
from types import TracebackType

import pytest

from src.application.ports.repositories import UserRepository
from src.application.ports.uow import UnitOfWork
from src.domain.entities import User


class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users: dict[int, User] = {}
        self._next_id = 1

    async def create(self, name: str, email: str, password: str) -> User:
        user = User(
            id=self._next_id,
            name=name,
            email=email,
            password=password,
            created_at=datetime.now(UTC),
        )
        self._users[user.id] = user
        self._next_id += 1
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        return self._users.get(user_id)

    async def get_by_email(self, email: str) -> User | None:
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    async def delete(self, user_id: int) -> bool:
        return self._users.pop(user_id, None) is not None


class FakeUnitOfWork(UnitOfWork):
    def __init__(self, user_repo: FakeUserRepository | None = None) -> None:
        self.users = user_repo or FakeUserRepository()
        self.committed = False
        self.rolled_back = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True

    async def __aenter__(self) -> "FakeUnitOfWork":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()


@pytest.fixture
def fake_user_repo() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def fake_uow(fake_user_repo: FakeUserRepository) -> FakeUnitOfWork:
    return FakeUnitOfWork(fake_user_repo)
