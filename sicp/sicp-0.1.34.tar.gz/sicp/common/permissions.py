from os import getenv

from common.rpc.auth import can_user_rpc
from common.course_config import get_course
from common.oauth_client import get_user, is_staff


def can_user(action: str):
    if getenv("ENV") != "prod":
        return True

    if get_course() == "cs61a":
        return can_user_rpc(
            course=get_course(),
            email=get_user()["email"],
            action=action,
        )
    else:
        return is_staff(get_course())
