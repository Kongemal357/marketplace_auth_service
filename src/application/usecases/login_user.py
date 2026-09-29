from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from src.application.exceptions import InvalidCredentialsError
from src.application.ports.uow import UnitOfWork
from src.application.ports.usecases import LoginUserPort
from src.domain.entities import TokenPair
from src.domain.jwt import AccessTokenPayload, RefreshTokenPayload


class LoginUser(LoginUserPort):
    def __init__(
        self,
        uow: UnitOfWork,
        jwt_secret: str,
        jwt_algorithm: str,
        jwt_expire_hours: int,
        jwt_refresh_expire_days: int,
    ) -> None:
        self._uow = uow
        self._jwt_secret = jwt_secret
        self._jwt_algorithm = jwt_algorithm
        self._jwt_expire_hours = jwt_expire_hours
        self._jwt_refresh_expire_days = jwt_refresh_expire_days

    async def execute(self, email: str, password: str) -> TokenPair:
        async with self._uow:
            user = await self._uow.users.get_by_email(email)
            if user is None:
                raise InvalidCredentialsError

            if not bcrypt.checkpw(password.encode(), user.password.encode()):
                raise InvalidCredentialsError

        now = datetime.now(UTC)

        access_payload: AccessTokenPayload = {
            "user_id": user.id,
            "email": user.email,
            "type": "access",
            "exp": now + timedelta(hours=self._jwt_expire_hours),
        }
        refresh_payload: RefreshTokenPayload = {
            "user_id": user.id,
            "type": "refresh",
            "exp": now + timedelta(days=self._jwt_refresh_expire_days),
        }

        return TokenPair(
            access_token=jwt.encode(
                access_payload,
                self._jwt_secret,
                algorithm=self._jwt_algorithm,
            ),
            refresh_token=jwt.encode(
                refresh_payload,
                self._jwt_secret,
                algorithm=self._jwt_algorithm,
            ),
        )
