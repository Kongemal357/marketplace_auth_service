import pytest

from src.application.exceptions import UserNotFoundError
from src.application.usecases.get_user import GetUser
from tests.conftest import FakeUnitOfWork


@pytest.mark.asyncio
async def test_get_user_returns_user(fake_uow: FakeUnitOfWork) -> None:
    await fake_uow.users.create(name="Alice", email="alice@test.com", password="hash")
    usecase = GetUser(fake_uow)

    user = await usecase.execute(1)

    assert user.id == 1
    assert user.name == "Alice"
    assert user.email == "alice@test.com"


@pytest.mark.asyncio
async def test_get_user_not_found_raises(fake_uow: FakeUnitOfWork) -> None:
    usecase = GetUser(fake_uow)

    with pytest.raises(UserNotFoundError):
        await usecase.execute(999)
