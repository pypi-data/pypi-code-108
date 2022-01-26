from __future__ import annotations

import asyncio
import functools
from base64 import b64decode
from datetime import datetime
from logging import INFO, WARNING, Formatter, getLogger
from logging.handlers import WatchedFileHandler
from os import environ, system
from time import gmtime
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Literal, TypedDict
from uuid import uuid4

import aiorun
import boto3
import simplejson as json
from docker.client import DockerClient
from docker.models.containers import Container, ContainerCollection
from docker.models.networks import Network
from docker.types.containers import LogConfig
from docker.types.services import Mount
from echostream_node import Message
from echostream_node.asyncio import CognitoAIOHTTPTransport, Node
from gql.client import Client as GqlClient
from gql.gql import gql
from pycognito import Cognito
from sdnotify import SystemdNotifier

if TYPE_CHECKING:
    from mypy_boto3_ecr.client import ECRClient
    from mypy_boto3_ecr_public.client import ECRPublicClient
else:
    ECRClient = object
    ECRPublicClient = object

getLogger().setLevel(environ.get("LOGGING_LEVEL") or INFO)
watched_file_handler = WatchedFileHandler(
    filename="/var/log/echostream/echostream-managed-app.log"
)
formatter = Formatter(
    fmt="[%(levelname)s] %(asctime)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%SZ"
)
formatter.converter = gmtime
watched_file_handler.setFormatter(formatter)
getLogger().addHandler(watched_file_handler)
getLogger("gql.transport.aiohttp").setLevel(environ.get("LOGGING_LEVEL") or WARNING)
getLogger("gql.transport.awsappsyncwebsockets").setLevel(
    environ.get("LOGGING_LEVEL") or WARNING
)


async def _run_in_executor(func: Callable, *args, **kwargs) -> Any:
    return await asyncio.get_running_loop().run_in_executor(
        None,
        functools.partial(func, *args, **kwargs),
    )


class AtBy(TypedDict):
    at: datetime
    by: str


class Change(TypedDict, total=False):
    datetime: str
    lastModified: AtBy
    new: dict[str, Any]
    old: dict[str, Any]
    system: bool
    tenant: str


class ManagedNode(TypedDict, total=False):
    managedNodeType: ManagedNodeType
    mounts: list[Mount]
    name: str
    ports: list[Port]
    receiveMessageType: MessageType
    sendMessageType: MessageType


class ManagedNodeType(TypedDict, total=False):
    imageUri: str
    name: str


class MessageType(TypedDict):
    name: str


class Mount(TypedDict, total=False):
    description: str
    source: str
    target: str


class Port(TypedDict):
    containerPort: int
    description: str
    hostAddress: str
    hostPort: int
    protocol: Literal["sctp", "tcp", "udp"]


class ManagedNodeContainer(Container):
    @property
    def managed_node_type(self) -> str:
        return self.labels.get("managed_node_type")

    @property
    def receive_message_type(self) -> str:
        return self.labels.get("receive_message_type")

    async def remove_async(self) -> None:
        await _run_in_executor(self.remove, force=True, v=True)

    async def restart_async(self) -> None:
        await _run_in_executor(self.restart, timeout=30)

    @property
    def send_message_type(self) -> str:
        return self.labels.get("send_message_type")

    async def start_async(self) -> None:
        await _run_in_executor(self.start)

    async def stop_async(self) -> None:
        await _run_in_executor(self.stop, timeout=30)


class ManagedAppContainerCollection(ContainerCollection):
    model = ManagedNodeContainer

    async def create_async(
        self,
        image: str,
        managed_app: ManagedApp,
        managed_node: ManagedNode,
        command=None,
        **kwargs,
    ) -> ManagedNodeContainer:
        utc_now = datetime.utcnow()
        kwargs |= dict(
            detach=True,
            environment=dict(
                managed_app.environment,
                NODE=managed_node["name"],
            ),
            hostname=managed_node["name"],
            labels=dict(
                managed_node_type=managed_node["managedNodeType"]["name"],
                receiveMessageType=(managed_node.get("receiveMessageType") or {}).get(
                    "name"
                ),
                send_message_type=(managed_node.get("send_message_type") or {}).get(
                    "name"
                ),
            ),
            log_config=LogConfig(
                type="awslogs",
                config={
                    "awslogs-group": f'{managed_app.log_group_name}/node/{managed_node["name"]}',
                    "awslogs-multiline-pattern": "^\[(CRITICAL|DEBUG|ERROR|INFO|WARNING)\]",
                    "awslogs-stream": f"{utc_now.year}/{utc_now.month:02}/{utc_now.day:02}/{uuid4().hex}",
                },
            ),
            mounts=[
                Mount(
                    source=mount.get("source", ""),
                    target=mount["target"],
                )
                for mount in managed_node.get("mounts") or []
            ],
            name=managed_node["name"],
            network=managed_app.docker_network.name,
            ports={
                f'{port["containerPort"]}/{port["protocol"]}': (
                    port.get("hostAddress", "0.0.0.0"),
                    port["hostPort"],
                )
                for port in managed_node.get("ports", [])
            },
            restart_policy=dict(Name="unless-stopped"),
        )
        return await _run_in_executor(self.create, image, command=command, **kwargs)

    async def list_async(
        self,
        all=False,
        before=None,
        filters=None,
        limit=-1,
        since=None,
        sparse=False,
        ignore_removed=False,
    ) -> list[ManagedNodeContainer]:
        return await _run_in_executor(
            self.list,
            all=all,
            before=before,
            filters=filters,
            limit=limit,
            since=since,
            sparse=sparse,
            ignore_removed=ignore_removed,
        )

    async def prune_async(self):
        return await _run_in_executor(self.prune)


class ManagedAppChangeReceiver(Node):
    def __init__(self, *, managed_app: ManagedApp) -> None:
        super().__init__(name=f"{managed_app.name}:Change Receiver")
        self.__managed_app = managed_app

    async def handle_received_message(self, *, message: Message, source: str) -> None:
        self.audit_message(
            message, extra_attributes=dict(app=self.__managed_app.name), source=source
        )
        await self.__managed_app._handle_change(json.loads(message.body))


class ManagedAppDockerClient(DockerClient):
    @property
    def containers(self):
        return ManagedAppContainerCollection(client=self)

    async def login_async(self, *args, **kwargs) -> Any:
        return await _run_in_executor(self.login, *args, **kwargs)


class ManagedApp:
    __GET_APP_GQL = gql(
        """
        query getManagedApp($name: String!, $tenant: String!) {
            GetApp(name: $name, tenant: $tenant) {
                ... on ManagedApp {
                    nodes {
                        ... on ManagedNode {
                            managedNodeType {
                                imageUri
                                name
                            }
                            mounts {
                                description
                                source
                                target
                            }
                            name
                            ports {
                                containerPort
                                hostAddress
                                hostPort
                                protocol
                            }
                            receiveMessageType {
                                name
                            }
                            sendMessageType {
                                name
                            }
                        }
                    }
                }
            }
        }
        """
    )

    __GET_NODE_GQL = gql(
        """
        query getManagedNode($name: String!, $tenant: String!) {
            GetNode(name: $name, tenant: $tenant) {
                __typename
                ... on ManagedNode {
                    managedNodeType {
                        imageUri
                        name
                    }
                    mounts {
                        description
                        source
                        target
                    }
                    name
                    ports {
                        containerPort
                        hostAddress
                        hostPort
                        protocol
                    }
                    receiveMessageType {
                        name
                    }
                    sendMessageType {
                        name
                    }
                }
            }
        }
        """
    )

    def __init__(
        self,
    ) -> None:
        super().__init__()
        self.__docker_client = ManagedAppDockerClient.from_env()
        self.__cognito = Cognito(
            client_id=environ["CLIENT_ID"],
            user_pool_id=environ["USER_POOL_ID"],
            username=environ["USER_NAME"],
        )
        self.__cognito.authenticate(password=environ["PASSWORD"])
        self.__gql_client = GqlClient(
            fetch_schema_from_transport=True,
            transport=CognitoAIOHTTPTransport(
                self.__cognito,
                environ["APPSYNC_ENDPOINT"],
            ),
        )
        self.__name: str = environ["APP"]
        self.__tenant: str = environ["TENANT"]
        self.__ecr_client: ECRClient = boto3.client("ecr")
        self.__ecr_public_client: ECRPublicClient = boto3.client("ecr-public")
        self.__nodes: dict[str, ManagedNodeContainer] = dict()
        self.__sdnotify = SystemdNotifier()

    async def __login(self, image_uris: list[str]) -> None:
        registries = set()
        for image_uri in image_uris:
            registry = image_uri.split("/")[0]
            if registry != "public.ecr.aws":
                registries.add(registry)
        registries = list(registries)
        public_auth_token = (
            await _run_in_executor(self.ecr_public_client.get_authorization_token)
        )["authorizationData"]["authorizationToken"]
        private_auth_tokens = (
            [
                auth_data["authorizationToken"]
                for auth_data in (
                    await _run_in_executor(
                        self.ecr_client.get_authorization_token,
                        registryIds=[registry.split(".")[0] for registry in registries],
                    )
                )["authorizationData"]
            ]
            if registries
            else []
        )
        auth_tokens: list[str] = [public_auth_token, *private_auth_tokens]
        registries.insert(0, "public.ecr.aws")
        logins: list[Coroutine] = list()
        for index, auth_token in enumerate(auth_tokens):
            username, password = b64decode(auth_token).decode().split(":")
            logins.append(
                self.docker_client.login_async(
                    username=username,
                    password=password,
                    registry=registries[index],
                )
            )
        await asyncio.gather(*logins)

    def __validate_node(
        self, node: ManagedNodeContainer, managed_node: ManagedNode
    ) -> bool:
        if managed_node["managedNodeType"]["imageUri"] not in node.image.tags:
            return False
        container_ports: dict[str, list[dict[str, str]]] = node.attrs["HostConfig"].get(
            "PortBindings", {}
        )
        node_ports: list[Port] = managed_node.get("ports", [])
        if len(container_ports) != len(node_ports):
            return False
        for node_port in node_ports:
            if not (
                container_port := container_ports.get(
                    f'{node_port["containerPort"]}/{node_port["protocol"]}[0]'
                )
            ):
                return False
            if not (
                node_port.get("hostAddress", "") == container_port["HostIp"]
                and node_port["hostPort"] == container_port["HostPort"]
            ):
                return False
        container_mounts = node.attrs["HostConfig"].get("Mounts", [])
        node_mounts = managed_node.get("mounts", [])
        if len(container_mounts) != len(node_mounts):
            return False
        for node_mount in node_mounts:
            for container_mount in container_mounts:
                if (
                    node_mount.get("source", "") == container_mount.get("Source", "")
                    and node_mount["target"] == container_mount["Target"]
                ):
                    return True
        return False

    async def __get_managed_node(self, name: str) -> ManagedNode:
        async with self.gql_client as session:
            return (
                await session.execute(
                    self.__GET_NODE_GQL,
                    variable_values=dict(name=name, tenant=self.tenant),
                )
            )["GetNode"]

    async def __run_node(
        self, managed_node: ManagedNode, node: ManagedNodeContainer = None
    ) -> ManagedNodeContainer:
        if node:
            await node.stop_async()
            await node.remove_async()
        node: ManagedNodeContainer = await self.docker_client.containers.create_async(
            managed_node["managedNodeType"]["imageUri"],
            managed_app=self,
            managed_node=managed_node,
        )
        await node.start_async()
        return node

    async def _handle_change(self, change: Change) -> None:
        new = change.get("new")
        old = change.get("old")
        if new and old and new["type"] == "Tenant":
            # The tenant has changed, restart all nodes
            await asyncio.gather(
                *[node.restart_async() for node in self.__nodes.values()]
            )
        elif (new or old)["type"] == "ManagedApp" and (new or old)["name"] == self.name:
            if new and not old:
                # Got the creation, nothing to do
                return
            if new and new.get("removed"):
                # Our app has been removed, shutdown the host VM
                system("shutdown now")
            if new and old:
                # the app has changed, restart all nodes
                await asyncio.gather(
                    *[node.restart_async() for node in self.__nodes.values()]
                )
        elif (new or old)["type"] == "ManagedNode" and (new or old)["app"] == self.name:
            if new and not old:
                # We have a new node to start
                managed_node: ManagedNode = await self.__get_managed_node(new["name"])
                self.__nodes[new["name"]] = await self.__run_node(managed_node)
            elif (new and new.get("removed")) or (old and not new):
                # Node was removed, stop it
                if node := self.__nodes.pop((new or old)["name"], None):
                    await node.stop_async()
                    await node.remove_async()
            else:
                managed_node: ManagedNode = await self.__get_managed_node(new["name"])
                # The node changed, restart it
                if (node := self.__nodes.get(new["name"])) and not self.__validate_node(
                    node, managed_node
                ):
                    self.__nodes[new["name"]] = await self.__run_node(
                        managed_node, node
                    )
                else:
                    getLogger().critical(
                        f'No node named {new["name"]} found, cannot restart'
                    )
        elif (
            (new or old)["type"] == "ManagedNodeType"
            and (new and old)
            and new["imageUri"] != old["imageUri"]
        ):
            for node in list(self.__nodes.values()):
                if node.managed_node_type == new["name"]:
                    managed_node: ManagedNode = await self.__get_managed_node(node.name)
                    await self.__login([managed_node["managedNodeType"]["imageUri"]])
                    await _run_in_executor(
                        self.docker_client.images.pull,
                        managed_node["managedNodeType"]["imageUri"],
                    )
                    self.__nodes[new["name"]] = await self.__run_node(
                        managed_node, node
                    )
        elif (
            (new or old)["type"] == "MessageType"
            and (new and old)
            and new["auditor"] != old["auditor"]
        ):
            nodes: list[ManagedNodeContainer] = list()
            for node in self.__nodes.values():
                if (
                    node.receive_message_type == new["name"]
                    or node.send_message_type == new["name"]
                ):
                    nodes.append(node)
            if nodes:
                await asyncio.gather(*[node.restart_async() for node in nodes])
        elif (new or old)["type"] == "Edge" and (new is not None) ^ (old is not None):
            # find nodes that use edge and restart them
            edge = new or old
            nodes: list[ManagedNodeContainer] = list()
            for node in self.__nodes.values():
                if edge["source"] == node.name or edge["target"] == node.name:
                    nodes.append(node)
            if nodes:
                await asyncio.gather(*[node.restart_async() for node in nodes])
        else:
            getLogger().warning(
                f"Unknown Change received\n {json.dumps(change, indent=4)}"
            )

    @property
    def docker_client(self) -> ManagedAppDockerClient:
        return self.__docker_client

    @property
    def docker_network(self) -> Network:
        return self.__docker_network

    @property
    def ecr_client(self) -> ECRClient:
        return self.__ecr_client

    @property
    def ecr_public_client(self) -> ECRPublicClient:
        return self.__ecr_public_client

    @property
    def environment(self) -> dict[str, str]:
        return dict(
            APPSYNC_ENDPOINT=environ["APPSYNC_ENDPOINT"],
            CLIENT_ID=environ["CLIENT_ID"],
            PASSWORD=environ["PASSWORD"],
            TENANT=self.tenant,
            USER_POOL_ID=environ["USER_POOL_ID"],
            USER_NAME=environ["USER_NAME"],
        )

    @property
    def gql_client(self) -> GqlClient:
        return self.__gql_client

    @property
    def log_group_name(self) -> str:
        return environ["LOG_GROUP_NAME"]

    @property
    def name(self) -> str:
        return self.__name

    async def start(self) -> None:
        try:
            # Get/create the network
            network: list[Network] = await _run_in_executor(
                self.docker_client.networks.list, names=[self.name]
            )
            if not network:
                self.__docker_network: Network = await _run_in_executor(
                    self.docker_client.networks.create, name=self.name, driver="bridge"
                )
            else:
                self.__docker_network = network[0]
            # Get the managed app from Echo
            async with self.gql_client as session:
                managed_node_list: list[ManagedNode] = (
                    await session.execute(
                        self.__GET_APP_GQL,
                        variable_values=dict(name=self.name, tenant=self.tenant),
                    )
                )["GetApp"]["nodes"]
            managed_nodes: dict[str, ManagedNode] = {
                managed_node.get("name"): managed_node
                for managed_node in managed_node_list
                if managed_node
            }
            # Let's pull all images
            image_uris = [
                managed_nodes[node]["managedNodeType"]["imageUri"]
                for node in managed_nodes
            ]
            await self.__login(image_uris)
            await asyncio.gather(
                *[
                    _run_in_executor(self.docker_client.images.pull, image_uri)
                    for image_uri in image_uris
                ]
            )
            # Now list all existing containers, validate and prune
            nodes_list: list[
                ManagedNodeContainer
            ] = await self.docker_client.containers.list_async(all=True)
            self.__nodes: dict[str, ManagedNodeContainer] = dict()
            for node in nodes_list:
                await node.stop_async()
                if node.name not in managed_nodes or not self.__validate_node(
                    node, managed_nodes[node.name]
                ):
                    # Container either is no longer needed or has an old image
                    await node.remove_async()
                else:
                    self.__nodes[node.name] = node
            for managed_node in [
                managed_node
                for managed_node in managed_nodes.values()
                if managed_node["name"] not in self.__nodes
            ]:
                self.__nodes[
                    managed_node["name"]
                ] = await self.docker_client.containers.create_async(
                    managed_node["managedNodeType"]["imageUri"],
                    managed_app=self,
                    managed_node=managed_node,
                )
            # now start all of our nodes
            await asyncio.gather(
                *[node.start_async() for node in self.__nodes.values()]
            )

            # cleanup old images, volumes and containers
            await self.docker_client.containers.prune_async()
            await asyncio.gather(
                _run_in_executor(self.docker_client.images.prune),
                _run_in_executor(self.docker_client.volumes.prune),
            )
            # Notify systemd that we're going...
            self.__sdnotify.notify("READY=1")
            # Start up our change receiver
            self.__managed_app_change_receiver_node = await _run_in_executor(
                ManagedAppChangeReceiver, managed_app=self
            )
            await self.__managed_app_change_receiver_node.start()
            await self.__managed_app_change_receiver_node.join()
        finally:
            await asyncio.gather(*[node.stop_async() for node in self.__nodes.values()])

    @property
    def tenant(self) -> str:
        return self.__tenant


async def main_async() -> None:
    try:
        app = ManagedApp()
        await app.start()
    except asyncio.CancelledError:
        pass
    except Exception:
        getLogger().exception("Error running app")


def main() -> None:
    aiorun.run(main_async(), stop_on_unhandled_errors=True, use_uvloop=True)
