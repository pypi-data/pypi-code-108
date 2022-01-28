import base64
import logging
import os
from base64 import b64decode
from datetime import timedelta
from hashlib import sha256
from pathlib import Path
from typing import Set
from uuid import UUID

from fastapi import HTTPException
import fastapi.security
from starlette.requests import Request

from ..server.security import SimpleAuthorization
from ..http_protocol import AuthenticationFailedException


logger = logging.getLogger(__name__)


class BasicAuthDb:
    _REFRESH_INTERVAL = timedelta(seconds=10)

    def __init__(self, auth_file: Path):
        self._auth_file = auth_file

    def authenticate(self, username: str, password: str):
        try:
            with self._auth_file.open('r') as file:
                for line in file:
                    name, salt, stored_pw_hash = line.split(":", 2)
                    if name == username:
                        break
                else:
                    raise AuthenticationFailedException(f'Could not authenticate user {username}')
        except OSError as ex:
            raise AuthenticationFailedException(f'Could not authenticate user {username}') from ex
        self._check_hash(username, password, salt, stored_pw_hash)

    def register_user(self, username: str, password: str):
        def _write(file, *_):
            file.write(f"{username}:{salt}:{password_hash}\n")

        logger.debug(f"Creating user {username}")
        salt, password_hash = self._hash_new_password(password)
        self.modify_db_record(username=username, on_found=_write, on_not_found=_write)
        logger.info(f"User {username} created")

    def unregister_user(self, username: str):
        def _raise(*_):
            raise RuntimeError("Not found")

        def _write(*_):
            pass

        logger.debug(f"Deleting user {username}")
        self.modify_db_record(username=username, on_found=_write, on_not_found=_raise)
        logger.info(f"User {username} deleted")

    def list_users(self) -> Set[str]:
        all_users = set()
        try:
            with self._auth_file.open('r') as file:
                for line in file:
                    username, _ = line.split(':', 1)
                    all_users.add(username)
            return all_users
        except OSError:
            logger.warning(f"Listing users, but {self._auth_file} is empty")
            return all_users

    def modify_db_record(self, username: str, on_found, on_not_found):
        new_file_path = self._auth_file.parent / (self._auth_file.name + '.new')
        new_file_path.touch(mode=0o600, exist_ok=False)
        found = False
        try:
            with new_file_path.open('w') as new_file:
                try:
                    with self._auth_file.open('r') as old_file:
                        for line in old_file:
                            line_user, line_salt, line_hash_pw = line.split(":", 3)
                            if line_user == username:
                                found = True
                                on_found(new_file, line_salt, line_hash_pw)
                            else:
                                new_file.write(line)
                    if not found:
                        on_not_found(new_file)
                except FileNotFoundError:
                    on_not_found(new_file)
            new_file_path.rename(self._auth_file)
        except:
            new_file_path.unlink()
            raise

    @classmethod
    def _hash_new_password(cls, password: str):
        salt = os.urandom(16)
        return base64.b64encode(salt).decode(), base64.b64encode(cls._generate_hash(salt, password)).decode()

    @staticmethod
    def _generate_hash(salt: bytes, password: str) -> bytes:
        hasher = sha256()
        hasher.update(salt)
        hasher.update(password.encode())
        return hasher.digest()

    @classmethod
    def _check_hash(cls, username: str, password: str, salt: str, stored_pw_hash: str):
        salt = b64decode(salt)
        stored_pw_hash = b64decode(stored_pw_hash)
        if stored_pw_hash != cls._generate_hash(salt, password):
            raise AuthenticationFailedException(f'Could not authenticate user {username}')


class BasicAuthenticatorAuthorizer:

    def __init__(self, auth_db: BasicAuthDb):
        self._auth_db = auth_db
        self._request_parser = fastapi.security.HTTPBasic()

    async def __call__(self, request: Request):
        try:
            credentials: fastapi.security.HTTPBasicCredentials = await self._request_parser(request)
        except HTTPException as ex:
            if ex.status_code == 401:
                raise AuthenticationFailedException(f"Could not authenticate user (unknown)") from ex
            raise
        self._auth_db.authenticate(credentials.username, credentials.password)
        # TODO map usernames onto client_id and remove the requirement to have username==client_id
        return SimpleAuthorization(UUID(credentials.username),
                                   self_permissions=set(),
                                   global_permissions=set())