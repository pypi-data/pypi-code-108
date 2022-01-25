from __future__ import annotations
import typing as T
import time
import os
import random

from pydantic import BaseModel, Field
import httpx
import jwt

from dgraph_orm.execute import finish, ThrottleException, IOTimeoutException
from dgraph_orm import GQLException

ExceptionType = T.TypeVar("ExceptionType", bound=Exception)

TIMEOUT = float(os.getenv("DGRAPH_CLIENT_TIMEOUT", "25"))


def retry(
    times: int = 1,
    delay: float = 0.25,
    exceptions_to_stop: T.List[T.Type[ExceptionType]] = None,
):
    """delay is in seconds to delay between retries"""
    exceptions_to_stop = exceptions_to_stop or []

    def decorator(function):
        async def wrapper(*args, **kwargs):
            count = 0
            last_e = None
            while count < times:
                try:
                    result = await function(*args, **kwargs)
                    return result
                except Exception as e:
                    last_e = e
                    if type(e) in exceptions_to_stop:
                        raise e
                print(f"{count=}")
                count += 1
                time.sleep(delay)
            raise last_e

        return wrapper

    return decorator


class LoginResponse(BaseModel):
    access_jwt: str = Field(..., alias="accessJWT")
    refresh_jwt: str = Field(..., alias="refreshJWT")


class DecodedAccessToken(BaseModel):
    exp: int
    groups: T.List[str]
    namespace: int
    userid: str


class InvalidCredsException(Exception):
    pass


class DgraphClient:
    def __init__(
        self,
        client_url: str,
        api_key: str = None,
        timeout: float = None,
        admin_url: str = None,
        user_id: str = None,
        password: str = None,
        namespace: int = None,
    ):
        self.api_key = api_key
        self.admin_url = admin_url
        self.timeout = timeout or TIMEOUT
        self.client_url = client_url
        self.user_id = user_id
        self.password = password
        self.namespace = namespace

        self._access_jwt: T.Optional[str] = None
        self._refresh_jwt: T.Optional[str] = None

        self._httpx_client = httpx.AsyncClient(
            timeout=self.timeout, headers=self.headers
        )
        self._httpx_admin_client = httpx.AsyncClient(
            timeout=self.timeout, headers=self.headers
        )

    @property
    def headers(self) -> dict:
        headers = {}
        if self.api_key:
            headers["Authorization"] = self.api_key
        if self._access_jwt:
            headers["X-Dgraph-AccessToken"] = self._access_jwt
        return headers

    @classmethod
    def from_cloud(
        cls, client_url: str, api_key: str = None, timeout: float = None
    ) -> DgraphClient:
        return cls(client_url=client_url, api_key=api_key, timeout=timeout)

    async def login_into_namespace(
        self, user_id: str, password: str, namespace: int, admin_url: str = None
    ):
        self.user_id = user_id
        self.password = password
        self.namespace = namespace
        self.admin_url = admin_url or self.client_url.replace("/graphql", "/admin")
        await self.generate_tokens()

    def update_tokens(self, jwts: LoginResponse, /) -> None:
        self._access_jwt = jwts.access_jwt
        self._refresh_jwt = jwts.refresh_jwt
        self._httpx_client.headers = self.headers
        self._httpx_admin_client.headers = self.headers

    @retry(times=3, exceptions_to_stop=[InvalidCredsException])
    async def generate_tokens(self) -> None:
        jwts = await self._generate_tokens()
        self.update_tokens(jwts)

    @retry(times=3, exceptions_to_stop=[InvalidCredsException])
    async def refresh_tokens(self) -> None:
        jwts = await self._refresh_tokens()
        self.update_tokens(jwts)

    async def _generate_tokens(self) -> LoginResponse:
        query = """mutation Login($namespace: Int, $password: String, $userId: String) {
          login(userId: $userId, namespace: $namespace, password: $password) {
            response {
              accessJWT
              refreshJWT
            }
          }
        }
        """
        variables = {
            "userId": self.user_id,
            "password": self.password,
            "namespace": self.namespace,
        }
        try:
            j = await self.execute(
                query_str=query, variables=variables, use_admin=True, use_one_time=True
            )
        except GQLException as e:
            if "invalid username or password" in str(e):
                raise InvalidCredsException(str(e))
            raise e
        return LoginResponse.parse_obj(j["data"]["login"]["response"])

    async def _refresh_tokens(self) -> LoginResponse:
        query = """mutation Login($refreshToken: String) {
              login(refreshToken: $refreshToken) {
                response {
                  accessJWT
                  refreshJWT
                }
              }
            }
            """
        variables = {"refreshToken": self._refresh_jwt}
        try:
            j = await self.execute(
                query_str=query, variables=variables, use_admin=True, use_one_time=True
            )
        except GQLException as e:
            if "invalid username or password" in str(e):
                raise InvalidCredsException(
                    str(e) + "--which means refresh token is invalid"
                )
            # just try to totally restart everything
            return await self.generate_tokens()
        return LoginResponse.parse_obj(j["data"]["login"]["response"])

    def access_token_expired(self) -> bool:
        if self._access_jwt:
            try:
                decoded = DecodedAccessToken.parse_obj(
                    jwt.decode(self._access_jwt, options={"verify_signature": False})
                )
            except jwt.ExpiredSignature:
                print("Invalid Token, will refresh")
                return True
            if decoded.exp < time.time() - 120:
                print(f"token is about to expire at {decoded.exp=}")
                return True
        return False

    async def refresh_token_if_expired(self) -> None:
        if self.access_token_expired():
            await self.refresh_tokens()

    async def execute(
        self,
        query_str: str,
        variables: dict = None,
        use_admin: bool = False,
        should_print: bool = False,
        use_one_time: bool = False,
        times: int = 0,
    ) -> dict:
        if not use_admin:
            await self.refresh_token_if_expired()

        start = time.time()
        client = self._httpx_client if not use_admin else self._httpx_admin_client
        url = self.client_url if not use_admin else self.admin_url
        json = {"query": query_str, "variables": variables or {}}
        if use_one_time:
            async with httpx.AsyncClient(timeout=TIMEOUT) as onetime_client:
                response = await onetime_client.post(
                    url=url, json=json, headers=client.headers
                )
        else:
            response = await self._httpx_client.post(url=url, json=json)
        try:
            return finish(
                response=response,
                query_str=query_str,
                should_print=should_print,
                start_time=start,
            )
        except (
            ThrottleException,
            IOTimeoutException,
        ) as e:
            time.sleep(random.randint(50, 250) / 1000)
            if times > 10:
                print(f"{times=}")
                raise e
            return await self.execute(
                query_str=query_str,
                variables=variables,
                use_admin=use_admin,
                should_print=should_print,
                use_one_time=use_one_time,
                times=times + 1,
            )
