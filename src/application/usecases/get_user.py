from src.application.ports.uow import UnitOfWork
from src.application.ports.usecases import GetUserPort
from src.domain.entities import User


class GetUser(GetUserPort):
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, user_id: int) -> User:
        raise NotImplementedError
