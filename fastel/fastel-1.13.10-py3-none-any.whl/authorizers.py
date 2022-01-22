import json
from typing import Any, Optional, TypeVar, Union

import boto3
from botocore.exceptions import ClientError
from mongoengine import DoesNotExist
from mongoengine.document import BaseDocument  # ignore: type
from pydantic import BaseModel, ValidationError

from fastel import jwt

from . import exceptions


class ClientConfig(BaseModel):
    client_id: str
    client_secret: str


AuthType = TypeVar("AuthType", bound="BaseAuth")
ClientType = TypeVar("ClientType", bound="ClientConfig")


class Credential:
    def __init__(
        self,
        client: Union[ClientType, BaseDocument, None],
        user: Any = None,
        server_call: bool = False,
    ) -> None:
        self.client = client
        self.user = user
        self.server_call = server_call


class BaseAuth:
    client_model_class: BaseDocument = None
    error_status_code: int = 410

    def __init__(self, force: bool = False):
        self.force = force

    def __or__(self, other: AuthType) -> "BaseAuth":
        return OR(self, other)

    def __call__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Optional[Credential]:
        return self.verify(
            client_id=client_id, token=token, client_secret=client_secret
        )

    def verify(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Optional[Credential]:
        raise NotImplementedError("verify() should be implemented")  # pragma: no cover


class ClientIdAuth(BaseAuth):
    def __init__(self, force: bool = False):
        super().__init__(force)
        if self.client_model_class is None:
            raise ValueError(
                "client_model_class should not be None"
            )  # pragma: no cover

    def verify(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Optional[Credential]:
        if not client_id and self.force:
            raise exceptions.APIException(
                status_code=self.error_status_code,
                error="access_denied",
                detail="client_id is required",
            )
        if not client_id:
            return None
        try:
            client = self.client_model_class.objects.get(client_id=client_id)
        except self.client_model_class.DoesNotExist as exc:
            raise exceptions.APIException(
                status_code=self.error_status_code,
                error="access_denied",
                detail=f"{client_id} not found",
            ) from exc
        return Credential(client=client)


class JWBaseAuth(BaseAuth):
    expected_aud: Optional[str] = None

    def verify(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Optional[Credential]:
        if not token and self.force:
            raise exceptions.APIException(
                status_code=self.error_status_code,
                error="permission_denied",
                detail="token is required",
            )
        if not token:
            return None

        try:
            decoded = jwt.decode_static(token)
        except Exception as exc:
            raise exceptions.APIException(
                status_code=self.error_status_code,
                error="permission_denied",
                detail=str(exc),
            )

        if self.expected_aud and decoded["aud"] != self.expected_aud:
            raise exceptions.APIException(
                status_code=self.error_status_code,
                error="aud_denied",
                detail=f"required aud: {self.expected_aud}",
            )

        if self.client_model_class:
            try:
                client = self.client_model_class.objects.get(client_id=decoded["aud"])
            except self.client_model_class.DoesNotExist as exc:
                raise exceptions.APIException(
                    status_code=self.error_status_code,
                    error="permission_denied",
                    detail=f"{client_id} not found",
                ) from exc
        else:
            client = None
        return Credential(client=client, user=decoded)


class ClientSecretAuth(BaseAuth):
    root_client_class: BaseDocument

    def __init__(self, force: bool = False):
        super().__init__(force)
        if self.client_model_class is None:
            raise ValueError(
                "client_model_class should not be None"
            )  # pragma: no cover

    def verify(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Optional[Credential]:

        if self.force and (client_secret is None or client_id is None):
            raise exceptions.APIException(
                status_code=self.error_status_code,
                error="permission_denied",
                detail="client_secret is required",
            )

        if client_secret is None or client_id is None:
            return None

        try:
            client = self.client_model_class.objects.get(client_id=client_id)
            root = self.root_client_class.objects.get(client_id=client_id)
        except DoesNotExist as exc:
            raise exceptions.APIException(
                status_code=self.error_status_code,
                error="permission_denied",
                detail=f"{client_id} not found",
            ) from exc

        if root.client_secret != client_secret:
            raise exceptions.APIException(
                status_code=self.error_status_code,
                error="permission_denied",
                detail="client_sercet not match",
            )

        return Credential(client=client, server_call=True)


class OR(BaseAuth):
    def __init__(self, left: BaseAuth, right: BaseAuth):
        super().__init__()
        self.left = left
        self.right = right

    def verify(self, *args: Any, **kwargs: Any) -> Optional[Credential]:
        result = self.left(*args, **kwargs)
        if not result:
            result = self.right(*args, **kwargs)
        return result


class StaticClientAuth(BaseAuth):
    s3_client = boto3.client("s3", "ap-northeast-1")
    client_bucket: str
    prefix_key: str = ""
    client_model = ClientConfig

    def verify(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Optional[Credential]:
        if not client_id and self.force:
            raise exceptions.APIException(
                status_code=self.error_status_code,
                error="access_denied",
                detail="client_id is required",
            )
        if not client_id:
            return None
        try:
            obj = self.s3_client.get_object(
                Bucket=self.client_bucket, Key=f"{self.prefix_key}/{client_id}.json"
            )
            client_dict = json.load(obj["Body"])
            root = self.client_model.validate(client_dict)
        except ClientError:
            raise exceptions.APIException(
                status_code=self.error_status_code,
                error="access_denied",
                detail=f"{client_id} not found",
            )
        except ValidationError as exc:
            raise exceptions.APIException(
                status_code=411,
                error="config_error",
                detail=exc.errors(),
            )

        return Credential(client=root)


class StaticSecretAuth(BaseAuth):
    s3_client = boto3.client("s3", "ap-northeast-1")
    client_bucket: str
    prefix_key: str = ""
    client_model = ClientConfig

    def verify(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Optional[Credential]:

        if self.force and (client_secret is None or client_id is None):
            raise exceptions.APIException(
                status_code=self.error_status_code,
                error="permission_denied",
                detail="client_secret is required",
            )

        if client_secret is None or client_id is None:
            return None
        try:
            obj = self.s3_client.get_object(
                Bucket=self.client_bucket, Key=f"{self.prefix_key}/{client_id}.json"
            )
            client_dict = json.load(obj["Body"])
            root = self.client_model.validate(client_dict)
        except ClientError:
            raise exceptions.APIException(
                status_code=self.error_status_code,
                error="access_denied",
                detail=f"{client_id} not found",
            )
        except ValidationError as exc:
            raise exceptions.APIException(
                status_code=411,
                error="config_error",
                detail=exc.errors(),
            )

        if root.client_secret != client_secret:
            raise exceptions.APIException(
                status_code=self.error_status_code,
                error="permission_denied",
                detail="client_sercet not match",
            )

        return Credential(client=root, server_call=True)


class StaticJWTAuth(BaseAuth):
    s3_client = boto3.client("s3", "ap-northeast-1")
    client_bucket: str
    prefix_key: str = ""
    client_model: Optional[ClientConfig] = None
    expected_aud: Optional[str] = None

    def __init__(self, force: bool = False) -> None:
        self.force = force

    def verify(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Optional[Credential]:
        if not token and self.force:
            raise exceptions.APIException(
                status_code=self.error_status_code,
                error="permission_denied",
                detail="token is required",
            )
        if not token:
            return None

        try:
            decoded = jwt.decode_static(token)
        except Exception as exc:
            raise exceptions.APIException(
                status_code=self.error_status_code,
                error="permission_denied",
                detail=str(exc),
            )

        if self.expected_aud and decoded["aud"] != self.expected_aud:
            raise exceptions.APIException(
                status_code=self.error_status_code,
                error="aud_denied",
                detail=f"required aud: {self.expected_aud}",
            )

        if not self.client_model:
            return Credential(client=None, user=decoded, server_call=False)

        client_id = decoded["aud"]
        try:
            obj = self.s3_client.get_object(
                Bucket=self.client_bucket, Key=f"{self.prefix_key}/{client_id}.json"
            )
            client_dict = json.load(obj["Body"])
            root = self.client_model.validate(client_dict)
        except ClientError:
            raise exceptions.APIException(
                status_code=self.error_status_code,
                error="access_denied",
                detail=f"{client_id} not found",
            )
        except ValidationError as exc:
            raise exceptions.APIException(
                status_code=411,
                error="config_error",
                detail=exc.errors(),
            )

        return Credential(client=root, server_call=True, user=decoded)
