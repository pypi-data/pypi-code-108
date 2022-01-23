"""
3rd Party Libraries
Not much interesting here. We have some default imports for FastAPI endpoints and common SQL Alchemy use cases
"""
from fastapi import APIRouter, Body

"""
eHelply Bootstrapper
Now we are getting interesting.
- State provides you with access to the app state
- get_db is used with Dependency injection to obtain a fresh DB connection session
    `db: Session = Depends(get_db)`
- Responses imports a bunch of default HTTP responses that eHelply has standardized on. Use these where possible as your
    return from each endpoint
"""
from ehelply_bootstrapper.utils.state import State

from ehelply_bootstrapper.drivers.fast_api_utils.responses import *

from ehelply_batcher.abstract_timer_service import AbstractTimerService
from ehelply_logger.Logger import Logger
import threading
import asyncio

"""
Router
This is a self-contained router instance. By itself it does nothing, but by attaching endpoints to it using decorator
  notation, you can make an epic router!
"""
router = APIRouter()


@router.post(
    '/keys/categories/{category_name}',
    tags=["keys"],
)
async def add_key(category_name: str, data: dict = Body({})):
    """
    Add a new key
    :return:
    """
    State.secrets.add(data['key'], category=category_name)

    return http_200_ok({"message": "Added key"})


@router.delete(
    '/keys/categories/{category_name}',
    tags=["keys"],
)
async def remove_key(category_name: str, data: dict = Body({})):
    """
    Add a new key
    :return:
    """
    State.secrets.remove(data['key'], category=category_name)

    return http_200_ok({"message": "Removed key"})


async def refresh_encryption_keys(category: str):
    from ehelply_bootstrapper.utils.db_encryption import DBEncryption
    from ehelply_microservice_library.integrations.security import Security
    from ehelply_microservice_library.utils.secret_names import secret_name_security_vault

    security_integration: Security = State.integrations.get('security')

    secret_key: str = State.secrets.get(secret_name_security_vault())[0].secret_key

    keys: list = await security_integration.get_encryption_keys(category=category, secret_key=secret_key)

    if not keys:
        await security_integration.create_encryption_key(category=category, secret_key=secret_key)
        keys = await security_integration.get_encryption_keys(category=category, secret_key=secret_key)

    for key in keys:
        if not State.secrets.exists(secret=key['key'], category='database'):
            State.secrets.add(key['key'], category='database', prepend=True)
            DBEncryption.update_keys()


class SecurityKeys(AbstractTimerService):
    """
    Periodically checks for new or removed keys
    """

    def __init__(self, logger: Logger, delay_seconds: int, category: str):
        self.category: str = category

        super().__init__(
            name="SecurityKeys",
            delay_seconds=delay_seconds,
            logger=logger,
        )

    async def proc(self):
        await refresh_encryption_keys(category=self.category)


class SecurityKeysThread(threading.Thread):
    def __init__(self, logger: Logger, delay: int, category: str):
        super().__init__()
        self.timer: SecurityKeys = None
        self.logger = logger
        self.delay: int = delay
        self.category: str = category
        self.daemon = True

    def run(self) -> None:
        self.timer = SecurityKeys(
            logger=self.logger,
            delay_seconds=self.delay,
            category=self.category
        )
        asyncio.run(self.timer.run())
