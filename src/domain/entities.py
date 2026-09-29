from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: int
    name: str
    email: str
    password: str
    created_at: datetime


@dataclass
class TokenPair:
    access_token: str
    refresh_token: str
