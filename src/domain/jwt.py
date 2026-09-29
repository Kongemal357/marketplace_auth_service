from datetime import datetime
from typing import Literal, TypedDict


class AccessTokenPayload(TypedDict):
    user_id: int
    email: str
    type: Literal["access"]
    exp: datetime


class RefreshTokenPayload(TypedDict):
    user_id: int
    type: Literal["refresh"]
    exp: datetime
