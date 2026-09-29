import pytest

from src.application.exceptions import UserNotFoundError
from src.application.usecases.delete_user import DeleteUser
from tests.conftest import FakeUnitOfWork


@pytest.mark.asyncio
async def test_delete_user_removes_user(fake_uow: FakeUnitOfWork) -> None:
    await fake_uow.users.create(name="Alice", email="alice@test.com", password="hash")
    usecase = DeleteUser(fake_uow)

    await usecase.execute(1)

    assert await fake_uow.users.get_by_id(1) is None
    assert fake_uow.committed


@pytest.mark.asyncio
async def test_delete_user_not_found_raises(fake_uow: FakeUnitOfWork) -> None:
    usecase = DeleteUser(fake_uow)

    with pytest.raises(UserNotFoundError):
        await usecase.execute(999)
