from src.application.exceptions import UserNotFoundError
from src.application.ports.uow import UnitOfWork
from src.application.ports.usecases import DeleteUserPort


class DeleteUser(DeleteUserPort):
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, user_id: int) -> None:
        async with self._uow:
            delete_user = await self._uow.users.delete(user_id)

            if not delete_user:
                raise UserNotFoundError

            await self._uow.commit()
