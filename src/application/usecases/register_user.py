import bcrypt

from src.application.exceptions import EmailAlreadyTakenError
from src.application.ports.uow import UnitOfWork
from src.application.ports.usecases import RegisterUserPort


class RegisterUser(RegisterUserPort):
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, name: str, email: str, password: str) -> int:
        async with self._uow:
            existing = await self._uow.users.get_by_email(email)
            if existing is not None:
                raise EmailAlreadyTakenError

            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            user = await self._uow.users.create(name=name, email=email, password=hashed)
            await self._uow.commit()
            return user.id
