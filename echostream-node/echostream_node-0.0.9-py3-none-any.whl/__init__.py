from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from os import cpu_count, environ
from threading import get_ident
from time import time
from typing import TYPE_CHECKING, Any, Callable, Union
from uuid import uuid4

import awsserviceendpoints
import simplejson as json
from boto3.session import Session
from botocore.config import Config
from botocore.credentials import DeferredRefreshableCredentials
from botocore.session import Session as BotocoreSession
from gql import Client as GqlClient
from gql import gql
from pycognito import Cognito


def getLogger() -> logging.Logger:
    return logging.getLogger("echostream-node")


getLogger().addHandler(logging.NullHandler())

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table
    from mypy_boto3_sqs.client import SQSClient
    from mypy_boto3_sqs.type_defs import MessageAttributeValueTypeDef
else:
    MessageAttributeValueTypeDef = dict
    SQSClient = object
    Table = object

_CREATE_AUDIT_RECORDS = gql(
    """
    query getNode($name: String!, $tenant: String!, $messageType: String!, $auditRecords: [AuditRecord!]!) {
        GetNode(name: $name, tenant: $tenant) {
            ... on AppChangeReceiverNode {
                CreateAuditRecords(messageType: $messageType, auditRecords: $auditRecords) 
            }
            ... on ExternalNode {
                CreateAuditRecords(messageType: $messageType, auditRecords: $auditRecords) 
            }
            ... on ManagedNode {
                CreateAuditRecords(messageType: $messageType, auditRecords: $auditRecords)
            }
        }
    }
    """
)

_GET_APP_GQL = gql(
    """
    query getNode($name: String!, $tenant: String!) {
        GetNode(name: $name, tenant: $tenant) {
            __typename
            ... on AppChangeReceiverNode {
                app {
                    __typename
                    ... on CrossAccountApp {
                        name
                        tableAccess
                    }
                    ... on ExternalApp {
                        name
                        tableAccess
                    }
                    ... on ManagedApp {
                        name
                        tableAccess
                    }
                }
            }
            ... on ExternalNode {
                app {
                    __typename
                    ... on CrossAccountApp {
                        name
                        tableAccess
                    }
                    ... on ExternalApp {
                        name
                        tableAccess
                    }
                }
            }
            ... on ManagedNode {
                app {
                    __typename
                    name
                    tableAccess
                }
            }
            tenant {
                region
                table
            }
        }
    }
    """
)

_GET_AWS_CREDENTIALS_GQL = gql(
    """
    query getAppAwsCredentials($name: String!, $tenant: String!, $duration: Int!) {
        GetApp(name: $name, tenant: $tenant) {
            ... on ExternalApp {
                GetAwsCredentials(duration: $duration) {
                    accessKeyId
                    secretAccessKey
                    sessionToken
                    expiration
                }
            }
            ... on ManagedApp {
                GetAwsCredentials(duration: $duration) {
                    accessKeyId
                    secretAccessKey
                    sessionToken
                    expiration
                }
            }
        }
    }
    """
)

_GET_BULK_DATA_STORAGE_GQL = gql(
    """
    query getBulkDataStorage($tenant: String!) {
        GetBulkDataStorage(tenant: $tenant, contentEncoding: gzip, count: 20) {
            presignedGet
            presignedPost {
                expiration
                fields
                url
            }
        }
    }
    """
)

_GET_NODE_GQL = gql(
    """
    query getNode($name: String!, $tenant: String!) {
        GetNode(name: $name, tenant: $tenant) {
            ... on AppChangeReceiverNode {
                receiveEdge {
                    queue
                    source {
                        name
                    }
                }
                receiveMessageType {
                    auditor
                    name
                }
            }
            ... on ExternalNode {
                app {
                    ... on CrossAccountApp {
                        config
                    }
                    ... on ExternalApp {
                        config
                    }
                }
                config
                receiveEdges {
                    queue
                    source {
                        name
                    }
                }
                receiveMessageType {
                    auditor
                    name
                }
                sendEdges {
                    queue
                    target {
                        name
                    }
                }
                sendMessageType {
                    auditor
                    name
                }
            }
            ... on ManagedNode {
                app {
                    config
                }
                config
                receiveEdges {
                    queue
                    source {
                        name
                    }
                }
                receiveMessageType {
                    auditor
                    name
                }
                sendEdges {
                    queue
                    target {
                        name
                    }
                }
                sendMessageType {
                    auditor
                    name
                }
            }
            tenant {
                config
            }
        }
    }
    """
)


class _NodeSession(BotocoreSession):
    def __init__(self, node: Node, duration: int = 3600) -> None:
        super().__init__()

        def refresher():
            credentials = node._get_aws_credentials(duration)
            return dict(
                access_key=credentials["accessKeyId"],
                expiry_time=credentials["expiration"],
                secret_key=credentials["secretAccessKey"],
                token=credentials["sessionToken"],
            )

        setattr(
            self,
            "_credentials",
            DeferredRefreshableCredentials(
                method="GetApp.GetAwsCredentials", refresh_using=refresher
            ),
        )


Auditor = Callable[..., dict[str, Any]]


@dataclass(frozen=True, init=False)
class BulkDataStorage:
    presigned_get: str
    presigned_post: PresignedPost

    def __init__(self, bulk_data_storage: dict[str, Union[str, PresignedPost]]) -> None:
        super().__init__()
        super().__setattr__("presigned_get", bulk_data_storage["presignedGet"])
        super().__setattr__(
            "presigned_post",
            PresignedPost(
                expiration=bulk_data_storage["presignedPost"]["expiration"],
                fields=json.loads(bulk_data_storage["presignedPost"]["fields"]),
                url=bulk_data_storage["presignedPost"]["url"],
            ),
        )

    @property
    def expired(self) -> bool:
        return self.presigned_post.expiration < time()


@dataclass(frozen=True)
class Edge:
    name: str
    queue: str


LambdaEvent = Union[bool, dict, float, int, list, str, tuple, None]


@dataclass(frozen=True, init=False)
class Message:
    body: str
    group_id: str
    length: int
    message_attributes: dict[str, MessageAttributeValueTypeDef]
    message_type: MessageType
    tracking_id: str
    previous_tracking_ids: list[str]

    def __init__(
        self,
        body: str,
        message_type: MessageType,
        group_id: str = None,
        previous_tracking_ids: Union[list[str], str] = None,
        tracking_id: str = None,
    ) -> None:
        super().__init__()
        super().__setattr__("body", body)
        super().__setattr__("group_id", group_id)
        super().__setattr__("message_type", message_type)
        super().__setattr__("tracking_id", tracking_id or uuid4().hex)
        if isinstance(previous_tracking_ids, str):
            previous_tracking_ids = json.loads(previous_tracking_ids)
        super().__setattr__(
            "previous_tracking_ids",
            previous_tracking_ids if previous_tracking_ids else None,
        )
        message_attributes = dict(
            trackingId=MessageAttributeValueTypeDef(
                DataType="String", StringValue=self.tracking_id
            )
        )
        if self.previous_tracking_ids:
            message_attributes["prevTrackingIds"] = MessageAttributeValueTypeDef(
                DataType="String",
                StringValue=json.dumps(
                    self.previous_tracking_ids, separators=(",", ":")
                ),
            )
        super().__setattr__("message_attributes", message_attributes)
        length = len(self.body)
        for name, attribute in self.message_attributes.items():
            value = attribute[
                "StringValue"
                if (data_type := attribute["DataType"]) in ("String", "Number")
                else "BinaryValue"
            ]
            length += len(name) + len(data_type) + len(value)
        if length > 262144:
            raise ValueError(f"Message is > 262,144 in size")
        super().__setattr__("length", length)

    def __len__(self) -> int:
        return self.length

    def _sqs_message(self, node: Node) -> dict:
        return dict(
            MessageAttributes=self.message_attributes,
            MessageBody=self.body,
            MessageGroupId=self.group_id or node.name.replace(" ", "_"),
        )


@dataclass(frozen=True)
class MessageType:
    auditor: Auditor
    name: str


class Node(ABC):
    def __init__(
        self,
        *,
        gql_transport_cls: type,
        appsync_endpoint: str = None,
        client_id: str = None,
        name: str = None,
        password: str = None,
        tenant: str = None,
        timeout: float = None,
        user_pool_id: str = None,
        username: str = None,
    ) -> None:
        super().__init__()
        cognito = Cognito(
            client_id=client_id or environ["CLIENT_ID"],
            user_pool_id=user_pool_id or environ["USER_POOL_ID"],
            username=username or environ["USER_NAME"],
        )
        cognito.authenticate(password=password or environ["PASSWORD"])
        self.__gql_client = GqlClient(
            fetch_schema_from_transport=True,
            transport=gql_transport_cls(
                cognito,
                appsync_endpoint or environ["APPSYNC_ENDPOINT"],
            ),
        )
        self.__name = name or environ["NODE"]
        self.__tenant = tenant or environ["TENANT"]
        data: dict[str, Union[str, dict]] = self.__gql_client.execute(
            _GET_APP_GQL,
            variable_values=dict(name=self.__name, tenant=self.__tenant),
        )["GetNode"]
        self.__app = data["app"]["name"]
        self.__node_type = data["__typename"]
        self.__app_type = data["app"]["__typename"]
        self.__session = Session(botocore_session=_NodeSession(self))
        self.__sqs_client: SQSClient = (
            Session() if self.__app_type == "CrossAccountApp" else self.__session
        ).client(
            "sqs",
            config=Config(
                max_pool_connections=min(20, ((cpu_count() or 1) + 4) * 2),
                retries={"mode": "standard"},
            ),
            region_name=data["tenant"]["region"],
        )
        self.__config: dict[str, Any] = None
        self.__sources: frozenset[Edge] = None
        self.__table: str = None
        if data["app"].get("tableAccess"):
            self.__table: str = data["tenant"]["table"]
        self.__tables: dict[int, Table] = dict()
        self.__targets: frozenset[Edge] = None
        self.__timeout = timeout or 0.1
        self._receive_message_type: MessageType = None
        self._send_message_type: MessageType = None

    @abstractmethod
    def _get_aws_credentials(self, duration: int = 900) -> dict[str, str]:
        pass

    @property
    def _gql_client(self) -> GqlClient:
        return self.__gql_client

    @property
    def _sources(self) -> frozenset[Edge]:
        return self.__sources

    @_sources.setter
    def _sources(self, sources: set[Edge]) -> None:
        self.__sources = frozenset(sources)

    @property
    def _sqs_client(self) -> SQSClient:
        return self.__sqs_client

    @property
    def _targets(self) -> frozenset[Edge]:
        return self.__targets

    @_targets.setter
    def _targets(self, targets: set[Edge]) -> None:
        self.__targets = frozenset(targets)

    @property
    def app(self) -> str:
        return self.__app

    @property
    def app_type(self) -> str:
        return self.__app_type

    @property
    def config(self) -> dict[str, Any]:
        return self.__config

    @config.setter
    def config(self, config: dict[str, Any]) -> None:
        self.__config = config

    def create_message(
        self,
        /,
        body: str,
        *,
        group_id: str = None,
        previous_tracking_ids: Union[list[str], str] = None,
    ) -> Message:
        return Message(
            body=body,
            group_id=group_id,
            message_type=self.send_message_type,
            previous_tracking_ids=previous_tracking_ids,
        )

    @property
    def name(self) -> str:
        return self.__name

    @property
    def node_type(self) -> str:
        return self.__node_type

    @property
    def receive_message_type(self) -> MessageType:
        return self._receive_message_type

    @property
    def send_message_type(self) -> MessageType:
        return self._send_message_type

    @property
    def sources(self) -> frozenset[Edge]:
        return self._sources

    @property
    def table(self) -> Table:
        table: Table = None
        if self.__table:
            thread_ident = get_ident()
            if not (table := self.__tables.get(thread_ident)):
                self.__tables[thread_ident] = table = self.__session.resource(
                    "dynamodb"
                ).Table(self.__table)
        return table

    @property
    def targets(self) -> frozenset[Edge]:
        return self._targets

    @property
    def tenant(self) -> str:
        return self.__tenant

    @property
    def timeout(self) -> float:
        return self.__timeout

    @timeout.setter
    def timeout(self, timeout: float) -> None:
        self.__timeout = timeout or 0.1


@dataclass(frozen=True)
class PresignedPost:
    expiration: int
    fields: dict[str, str]
    url: str
