import jwt
from datetime import datetime, timedelta, timezone
from threedi_api_client.auth import is_token_usable, REFRESH_TIME_DELTA


SECRET_KEY = "abcd1234"


def get_token_with_expiry(delta_time: timedelta) -> int:
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    exp = (utc_now + delta_time).replace(tzinfo=timezone.utc).timestamp()

    return jwt.encode({"user": "harry", "exp": exp}, SECRET_KEY, algorithm="HS256")


def test_not_expired_token():
    dt = timedelta(seconds=(REFRESH_TIME_DELTA + 10))
    assert is_token_usable(get_token_with_expiry(dt))


def test_expired_token():
    dt = timedelta(seconds=(REFRESH_TIME_DELTA - 10))
    assert not is_token_usable(get_token_with_expiry(dt))
