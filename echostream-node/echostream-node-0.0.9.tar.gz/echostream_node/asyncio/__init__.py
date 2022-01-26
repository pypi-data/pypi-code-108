from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from functools import partial
from gzip import GzipFile
from io import BytesIO
from typing import TYPE_CHECKING, Any, AsyncGenerator, BinaryIO, Union

import dynamic_function_loader
import simplejson as json
from aiohttp import ClientSession, FormData
from aws_error_utils import catch_aws_error
from gql.transport.aiohttp import AIOHTTPTransport
from pycognito import Cognito

from .. import (
    _CREATE_AUDIT_RECORDS,
    _GET_AWS_CREDENTIALS_GQL,
    _GET_BULK_DATA_STORAGE_GQL,
    _GET_NODE_GQL,
)
from .. import BulkDataStorage as BaseBulkDataStorage
from .. import Edge, Message, MessageType
from .. import Node as BaseNode
from .. import PresignedPost, getLogger

if TYPE_CHECKING:
    from mypy_boto3_sqs.type_defs import (
        DeleteMessageBatchRequestEntryTypeDef,
        SendMessageBatchRequestEntryTypeDef,
    )
else:
    DeleteMessageBatchRequestEntryTypeDef = dict
    SendMessageBatchRequestEntryTypeDef = dict


class _AuditRecordQueue(asyncio.Queue):
    def __init__(self, message_type: MessageType, node: Node) -> None:
        super().__init__()

        async def sender() -> None:
            cancelled = asyncio.Event()

            async def batcher() -> AsyncGenerator[
                list[dict],
                None,
            ]:
                batch: list[dict] = list()
                while not (cancelled.is_set() and self.empty()):
                    try:
                        try:
                            batch.append(
                                await asyncio.wait_for(self.get(), timeout=node.timeout)
                            )
                        except asyncio.TimeoutError:
                            if batch:
                                yield batch
                                batch = list()
                        else:
                            if len(batch) == 500:
                                yield batch
                                batch = list()
                    except asyncio.CancelledError:
                        cancelled.set()
                        if batch:
                            yield batch
                            batch = list()

            async for batch in batcher():
                try:
                    async with node._gql_client_lock:
                        async with node._gql_client as session:
                            await session.execute(
                                _CREATE_AUDIT_RECORDS,
                                variable_values=dict(
                                    name=node.name,
                                    tenant=node.tenant,
                                    messageType=message_type.name,
                                    auditRecords=batch,
                                ),
                            )
                except asyncio.CancelledError:
                    cancelled.set()
                except Exception:
                    getLogger().exception("Error creating audit records")
                finally:
                    for _ in range(len(batch)):
                        self.task_done()

        self.__task = asyncio.create_task(sender(), name=f"AuditRecordsSender")

    async def get(self) -> dict:
        return await super().get()


class _BulkDataStorageQueue(asyncio.Queue):
    def __init__(self, node: Node) -> None:
        super().__init__()
        self.__fill = asyncio.Event()

        async def filler() -> None:
            async with ClientSession() as client_session:
                while True:
                    await self.__fill.wait()
                    try:
                        async with node._gql_client_lock:
                            async with node._gql_client as session:
                                bulk_data_storages: list[dict] = (
                                    await session.execute(
                                        _GET_BULK_DATA_STORAGE_GQL,
                                        variable_values={"tenant": node.tenant},
                                    )
                                )["GetBulkDataStorage"]
                    except Exception:
                        getLogger().exception("Error getting bulk data storage")
                    else:
                        for bulk_data_storage in bulk_data_storages:
                            self.put_nowait(
                                BulkDataStorage(bulk_data_storage, client_session)
                            )
                    self.__fill.clear()

        self.__task = asyncio.create_task(filler(), name="BulkDataStorageQueueFiller")

    async def get(self) -> BulkDataStorage:
        if self.qsize() < 20:
            self.__fill.set()
        bulk_data_storage: BulkDataStorage = await super().get()
        return bulk_data_storage if not bulk_data_storage.expired else await self.get()


class BulkDataStorage(BaseBulkDataStorage):
    def __init__(
        self,
        bulk_data_storage: dict[str, Union[str, PresignedPost]],
        session: ClientSession,
    ) -> None:
        super().__init__(bulk_data_storage)
        self.__client_session = session

    async def handle_bulk_data(self, data: Union[bytearray, bytes, BinaryIO]) -> str:
        if isinstance(data, BinaryIO):
            data = data.read()
        with BytesIO() as buffer:
            with GzipFile(mode="wb", fileobj=buffer) as gzf:
                gzf.write(data)
            buffer.seek(0)
            form_data = FormData(self.presigned_post.fields)
            form_data.add_field("file", buffer, filename="bulk_data")
            async with self.__client_session.post(
                self.presigned_post.url, data=form_data
            ) as response:
                response.raise_for_status()
        return self.presigned_get


class _DeleteMessageQueue(asyncio.Queue):
    def __init__(self, edge: Edge, node: Node) -> None:
        super().__init__()

        async def deleter() -> None:
            cancelled = asyncio.Event()

            async def batcher() -> AsyncGenerator[
                list[str],
                None,
            ]:
                batch: list[str] = list()
                while not (cancelled.is_set() and self.empty()):
                    try:
                        try:
                            batch.append(
                                await asyncio.wait_for(self.get(), timeout=node.timeout)
                            )
                        except asyncio.TimeoutError:
                            if batch:
                                yield batch
                                batch = list()
                        else:
                            if len(batch) == 10:
                                yield batch
                                batch = list()
                    except asyncio.CancelledError:
                        cancelled.set()
                        if batch:
                            yield batch
                            batch = list()

            async for receipt_handles in batcher():
                try:
                    response = await asyncio.get_running_loop().run_in_executor(
                        None,
                        partial(
                            node._sqs_client.delete_message_batch,
                            Entries=[
                                DeleteMessageBatchRequestEntryTypeDef(
                                    Id=str(id), ReceiptHandle=receipt_handle
                                )
                                for id, receipt_handle in enumerate(receipt_handles)
                            ],
                            QueueUrl=edge.queue,
                        ),
                    )
                except asyncio.CancelledError:
                    cancelled.set()
                except Exception:
                    getLogger().exception(f"Error deleting messages from {edge.name}")
                finally:
                    for failed in response.get("Failed", list()):
                        id = failed.pop("Id")
                        getLogger().error(
                            f"Unable to delete message {receipt_handles[id]} from {edge.name}, reason {failed}"
                        )
                    for _ in range(len(receipt_handles)):
                        self.task_done()

        self.__task = asyncio.create_task(
            deleter(), name=f"SourceMessageDeleter({edge.name})"
        )

    def cancel(self) -> bool:
        return self.__task.cancel()

    async def get(self) -> str:
        return await super().get()


class _SourceMessageReceiver:
    def __init__(self, edge: Edge, node: Node) -> None:
        self.__delete_message_queue = _DeleteMessageQueue(edge, node)

        async def receive() -> None:
            getLogger().info(f"Receiving messages from {edge.name}")
            error_count = 0
            while True:
                try:
                    response = await asyncio.get_running_loop().run_in_executor(
                        None,
                        partial(
                            node._sqs_client.receive_message,
                            AttributeNames=["All"],
                            MaxNumberOfMessages=10,
                            MessageAttributeNames=["All"],
                            QueueUrl=edge.queue,
                            WaitTimeSeconds=20,
                        ),
                    )
                    error_count = 0
                except asyncio.CancelledError:
                    raise
                except catch_aws_error("AWS.SimpleQueueService.NonExistentQueue"):
                    getLogger().warning(f"Queue {edge.queue} does not exist, exiting")
                    break
                except Exception:
                    error_count += 1
                    if error_count == 10:
                        getLogger().critical(
                            f"Recevied 10 errors in a row trying to receive from {edge.queue}, exiting"
                        )
                        raise
                    else:
                        getLogger().exception(
                            f"Error receiving messages from {edge.name}, retrying"
                        )
                        await asyncio.sleep(10)
                else:
                    if not (sqs_messages := response.get("Messages")):
                        continue
                    getLogger().info(f"Received {len(sqs_messages)} from {edge.name}")
                    for sqs_message in sqs_messages:
                        message = Message(
                            body=sqs_message["Body"],
                            group_id=sqs_message["Attributes"]["MessageGroupId"],
                            message_type=node.receive_message_type,
                            tracking_id=sqs_message["MessageAttributes"]
                            .get("trackingId", {})
                            .get("StringValue"),
                            previous_tracking_ids=sqs_message["MessageAttributes"]
                            .get("prevTrackingIds", {})
                            .get("StringValue"),
                        )
                        receipt_handle = sqs_message["ReceiptHandle"]
                        try:
                            await node.handle_received_message(
                                message=message, source=edge.name
                            )
                        except asyncio.CancelledError:
                            raise
                        except Exception:
                            getLogger().exception(
                                f"Error handling recevied message for {edge.name}"
                            )
                        else:
                            self.__delete_message_queue.put_nowait(receipt_handle)
            getLogger().info(f"Stopping receiving messages from {edge.name}")

        self.__task = asyncio.create_task(
            receive(), name=f"SourceMessageReceiver({edge.name})"
        )

    async def join(self) -> None:
        done, pending = await asyncio.wait([self.__task])
        await self.__delete_message_queue.join()


class _TargetMessageQueue(asyncio.Queue):
    def __init__(self, node: Node, edge: Edge) -> None:
        super().__init__()

        async def sender() -> None:
            cancelled = asyncio.Event()

            async def batcher() -> AsyncGenerator[
                list[SendMessageBatchRequestEntryTypeDef], None
            ]:
                batch: list[SendMessageBatchRequestEntryTypeDef] = list()
                batch_length = 0
                id = 0
                while not (cancelled.is_set() and self.empty()):
                    try:
                        try:
                            message = await asyncio.wait_for(
                                self.get(), timeout=node.timeout
                            )
                        except asyncio.TimeoutError:
                            if batch:
                                yield batch
                            batch = list()
                            batch_length = 0
                            id = 0
                        else:
                            if batch_length + len(message) > 262144:
                                yield batch
                                batch = list()
                                batch_length = 0
                                id = 0
                            batch.append(
                                SendMessageBatchRequestEntryTypeDef(
                                    Id=str(id), **message._sqs_message(node)
                                )
                            )
                            if len(batch) == 10:
                                yield batch
                                batch = list()
                                batch_length = 0
                                id = 0
                            id += 1
                            batch_length += len(message)
                    except asyncio.CancelledError:
                        cancelled.set()
                        if batch:
                            yield batch
                        batch = list()
                        batch_length = 0
                        id = 0

            async for entries in batcher():
                try:
                    response = await asyncio.get_running_loop().run_in_executor(
                        None,
                        partial(
                            node._sqs_client.send_message_batch,
                            Entries=entries,
                            QueueUrl=edge.queue,
                        ),
                    )
                except asyncio.CancelledError:
                    cancelled.set()
                except Exception:
                    getLogger().exception(f"Error sending messages to {edge.name}")
                finally:
                    for failed in response.get("Failed", list()):
                        id = failed.pop("Id")
                        getLogger().error(
                            f"Unable to send message {entries[id]} to {edge.name}, reason {failed}"
                        )
                    for _ in range(len(entries)):
                        self.task_done()

        asyncio.create_task(sender(), name=f"TargetMessageSender({edge.name})")

    async def get(self) -> Message:
        return await super().get()


class CognitoAIOHTTPTransport(AIOHTTPTransport):
    def __init__(self, cognito: Cognito, url: str, **kwargs: Any) -> None:
        self._cognito = cognito
        super().__init__(url, **kwargs)

    def __getattribute__(self, name: str) -> Any:
        if name == "headers":
            self._cognito.check_token()
            return dict(Authorization=self._cognito.access_token)
        return super().__getattribute__(name)


class Node(BaseNode):
    def __init__(
        self,
        *,
        appsync_endpoint: str = None,
        client_id: str = None,
        name: str = None,
        password: str = None,
        tenant: str = None,
        timeout: float = None,
        user_pool_id: str = None,
        username: str = None,
    ) -> None:
        super().__init__(
            gql_transport_cls=CognitoAIOHTTPTransport,
            appsync_endpoint=appsync_endpoint,
            client_id=client_id,
            name=name,
            password=password,
            tenant=tenant,
            timeout=timeout,
            user_pool_id=user_pool_id,
            username=username,
        )
        self._gql_client_lock: asyncio.Lock = None
        self.__audit_records_queues: dict[str, _AuditRecordQueue] = dict()
        self.__bulk_data_storage_queue: _BulkDataStorageQueue = None
        self.__loop: asyncio.events.AbstractEventLoop = None
        self.__source_message_receivers: list[_SourceMessageReceiver] = list()
        self.__target_message_queues: dict[str, _TargetMessageQueue] = dict()

    def _get_aws_credentials(self, duration: int = 3600) -> dict[str, str]:
        async def get_aws_credentials() -> dict[str, str]:
            async with self._gql_client_lock:
                async with self._gql_client as session:
                    return (
                        await session.execute(
                            _GET_AWS_CREDENTIALS_GQL,
                            variable_values=dict(
                                name=self.app, tenant=self.tenant, duration=duration
                            ),
                        )
                    )["GetApp"]["GetAwsCredentials"]

        return asyncio.run_coroutine_threadsafe(
            get_aws_credentials(), self.__loop
        ).result()

    def audit_message(
        self,
        /,
        message: Message,
        *,
        extra_attributes: dict[str, Any] = None,
        source: str = None,
    ) -> None:
        extra_attributes = extra_attributes or dict()
        message_type = message.message_type
        record = dict(
            datetime=datetime.now(timezone.utc).isoformat(),
            previousTrackingIds=message.previous_tracking_ids,
            sourceNode=source,
            trackingId=message.tracking_id,
        )
        if attributes := (
            message_type.auditor(message=message.body) | extra_attributes
        ):
            record["attributes"] = json.dumps(attributes, separators=(",", ":"))
        try:
            self.__audit_records_queues[message_type.name].put_nowait(record)
        except KeyError:
            raise ValueError(f"Unrecognized message type {message_type.name}")

    async def handle_bulk_data(self, data: Union[bytearray, bytes]) -> str:
        return await (await self.__bulk_data_storage_queue.get()).handle_bulk_data(data)

    async def handle_received_message(self, *, message: Message, source: str) -> None:
        pass

    async def join(self) -> None:
        await asyncio.gather(
            *[
                source_message_receiver.join()
                for source_message_receiver in self.__source_message_receivers
            ]
        )
        await asyncio.gather(
            *[
                target_message_queue.join()
                for target_message_queue in self.__target_message_queues.values()
            ]
        )
        for audit_records_queue in self.__audit_records_queues.values():
            await audit_records_queue.join()

    def send_message(self, /, message: Message, *, targets: set[Edge] = None) -> None:
        self.send_messages([message], targets=targets)

    def send_messages(
        self, /, messages: list[Message], *, targets: set[Edge] = None
    ) -> None:
        if messages:
            for target in targets or self.targets:
                if target_message_queue := self.__target_message_queues.get(
                    target.name
                ):
                    for message in messages:
                        target_message_queue.put_nowait(message)
                else:
                    getLogger().warning(f"Target {target.name} does not exist")

    async def start(self) -> None:
        getLogger().info(f"Starting Node {self.name}")
        self._gql_client_lock = asyncio.Lock()
        self.__loop = asyncio.get_running_loop()
        self.__bulk_data_storage_queue = _BulkDataStorageQueue(self)
        async with self._gql_client_lock:
            async with self._gql_client as session:
                data: dict[str, Union[str, dict]] = (
                    await session.execute(
                        _GET_NODE_GQL,
                        variable_values=dict(name=self.name, tenant=self.tenant),
                    )
                )["GetNode"]
        self.config = (
            json.loads(data["tenant"].get("config") or "{}")
            | json.loads((data.get("app") or dict()).get("config") or "{}")
            | json.loads(data.get("config") or "{}")
        )
        if receive_message_type := data.get("receiveMessageType"):
            self._receive_message_type = MessageType(
                auditor=dynamic_function_loader.load(receive_message_type["auditor"]),
                name=receive_message_type["name"],
            )
            self.__audit_records_queues[
                receive_message_type["name"]
            ] = _AuditRecordQueue(self.receive_message_type, self)
        if send_message_type := data.get("sendMessageType"):
            self._send_message_type = MessageType(
                auditor=dynamic_function_loader.load(send_message_type["auditor"]),
                name=send_message_type["name"],
            )
            self.__audit_records_queues[send_message_type["name"]] = _AuditRecordQueue(
                self.send_message_type, self
            )
        if self.node_type == "AppChangeReceiverNode":
            if edge := data.get("receiveEdge"):
                self._sources = {Edge(name=edge["source"]["name"], queue=edge["queue"])}
            else:
                self._sources = set()
        else:
            self._sources = {
                Edge(name=edge["source"]["name"], queue=edge["queue"])
                for edge in (data.get("receiveEdges") or list())
            }
        self._targets = {
            Edge(name=edge["target"]["name"], queue=edge["queue"])
            for edge in (data.get("sendEdges") or list())
        }
        self.__target_message_queues = {
            edge.name: _TargetMessageQueue(self, edge) for edge in self._targets
        }
        self.__source_message_receivers = [
            _SourceMessageReceiver(edge, self) for edge in self._sources
        ]

    async def start_and_run_forever(self) -> None:
        await self.start()
        await self.join()
