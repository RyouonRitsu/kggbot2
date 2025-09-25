import datetime

from pydantic import BaseModel


class User(BaseModel):
    id: str
    lucky_value: float = -1
    lucky_value_acquisition_date: datetime.date = datetime.date.min
    sexy_value: float = -1
    sexy_value_acquisition_date: datetime.date = datetime.date.min
    check_in_count: int = 0
    check_in_date: datetime.date = datetime.date.min
    energy_value: int = 0
    tag: str = ""
    offer: str = ""
    order: list[str] = []
    times: int = 0
    lock_time: int = 0


class UserDict(BaseModel):
    user_id_2_user: dict[str, User] = {}


user_dict: UserDict


def get_user(user_id: str) -> User:
    user_id_2_user = user_dict.user_id_2_user
    if user_id not in user_id_2_user:
        user_id_2_user[user_id] = User(id=user_id)

    return user_id_2_user[user_id]
