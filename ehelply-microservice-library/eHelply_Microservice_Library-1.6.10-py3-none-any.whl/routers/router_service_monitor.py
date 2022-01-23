from fastapi import APIRouter
from ehelply_bootstrapper.utils.state import State
from ehelply_bootstrapper.utils.service import ServiceMeta, ServiceStatus, KPI

from pydantic import BaseModel

from fastapi.encoders import jsonable_encoder

from ehelply_batcher.abstract_batching_service import AbstractBatchingService
from ehelply_batcher.abstract_timer_service import AbstractTimerService

import time
import json
import platform
import threading
import datetime
import asyncio
import requests
from typing import List
from ehelply_logger.Logger import Logger

router = APIRouter()


@router.get(
    '/heartbeat',
    tags=["heartbeat"],
)
async def heartbeat():
    return {"message": "Heartbeat"}


@router.get(
    '/kpi',
    tags=["kpi"],
)
async def kpis():
    return KPIFetcher.kpi_holder


class ServicePython(BaseModel):
    version: str
    implementation: str


class ServicePlatform(BaseModel):
    system: str
    node: str
    release: str
    version: str
    machine: str
    processor: str
    python: ServicePython


class Heartbeat(BaseModel):
    service: ServiceMeta
    platform: ServicePlatform
    status: ServiceStatus
    process: str
    stage: str


class KPIHolder(BaseModel):
    kpis: List[KPI] = []
    fetched_at: datetime.datetime


class KPIMQ(BaseModel):
    kpi_holder: KPIHolder
    service: ServiceMeta


class KPIFetcher(AbstractTimerService):
    kpi_holder: KPIHolder = None

    """
    Periodically checks for KPIs and stores them for later use
    """

    def __init__(self, logger: Logger, queue_url: str, service_meta: ServiceMeta):
        super().__init__(
            name="KPIFetcher",
            delay_seconds=1 * 60 * 60,
            logger=logger,
        )

        self.service_meta: ServiceMeta = service_meta
        self.sqs = State.aws.make_client("sqs")
        self.queue_url: str = queue_url

    def is_time_between(self, begin_time: datetime.time, end_time: datetime.time, check_time=None) -> bool:
        # If check time is not given, default to current UTC time
        check_time = check_time or datetime.datetime.utcnow().time()
        if begin_time < end_time:
            return check_time >= begin_time and check_time <= end_time
        else:  # crosses midnight
            return check_time >= begin_time or check_time <= end_time

    def fetch_kpis(self) -> List[KPI]:
        return State.bootstrapper.get_kpi()

    async def proc(self):
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=6)

        time_0200am = datetime.time(2, 0)
        time_0400am = datetime.time(4, 0)

        if KPIFetcher.kpi_holder is None or (
                KPIFetcher.kpi_holder.fetched_at <= cutoff and self.is_time_between(time_0200am, time_0400am)):
            self.logger.info("Fetched a new set of KPIs")
            KPIFetcher.kpi_holder = KPIHolder(kpis=self.fetch_kpis(), fetched_at=datetime.datetime.utcnow())

            kpi_mq: KPIMQ = KPIMQ(
                kpi_holder=KPIFetcher.kpi_holder,
                service=self.service_meta
            )

            self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(jsonable_encoder(kpi_mq.dict()))
            )


class KPIFetcherThread(threading.Thread):
    def __init__(self, logger: Logger, queue_url: str, service_meta: ServiceMeta):
        super().__init__()
        self.timer: KPIFetcher = None
        self.logger = logger
        self.daemon = True
        self.queue_url: str = queue_url
        self.service_meta: ServiceMeta = service_meta

    def run(self) -> None:
        self.timer = KPIFetcher(
            logger=self.logger,
            queue_url=self.queue_url,
            service_meta=self.service_meta
        )
        asyncio.run(self.timer.run())


class MonitorHeartbeat(AbstractBatchingService):
    def __init__(self, logger: Logger, queue_url: str, service_meta: ServiceMeta, service_status: ServiceStatus,
                 environment: str, batch_size: int = 1,
                 max_message_delay: float = 20,
                 sleep_interval: float = 20 * 60, debug=False):
        self.sqs = State.aws.make_client("sqs")
        self.queue_url: str = queue_url
        self.logger: Logger = logger

        self.environment = environment

        self.service_meta: ServiceMeta = service_meta
        self.service_status: ServiceStatus = service_status

        self.service_platform: ServicePlatform = ServicePlatform(
            system=platform.system(),
            node=platform.node(),
            release=platform.release(),
            version=platform.version(),
            machine=platform.machine(),
            processor=platform.processor(),
            python=ServicePython(
                version=platform.python_version(),
                implementation=platform.python_implementation()
            )
        )

        try:
            uptime_heartbeat_url: str = State.config.better_uptime.heartbeat.url
            if len(uptime_heartbeat_url) > 0:
                self.uptime_heartbeat_url = uptime_heartbeat_url
            else:
                State.logger.warning(message="Better Uptime Heartbeat URL is not set in config.")
                self.uptime_heartbeat_url = None
        except:
            self.uptime_heartbeat_url = None
            State.logger.warning(message="Invalid Better Uptime config.")
            State.logger.warning(message="Create a Better Uptime config in config/<env>/service/better_uptime.yaml.")
            State.logger.warning(message="""Load the config with the following yaml:
        better_uptime:
          heartbeat:
            url: <better_uptime_heartbeat_url>""")

        super().__init__(
            name="Monitor",
            batch_size=batch_size,
            max_message_delay_minutes=max_message_delay,
            sleep_interval_seconds=sleep_interval,
            mandatory_delay_seconds=sleep_interval,
            logger=logger,
        )

    # name: str = "",
    # batch_size: int = 16,
    # max_message_delay_minutes: float = 2,
    # sleep_interval_seconds: float = 20,
    # mandatory_delay_seconds: float = 0,
    # logger: Logger = None

    def release_batch(self) -> bool:
        for message in self.get():
            self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(jsonable_encoder(message))
            )

        if self.uptime_heartbeat_url:
            requests.post(self.uptime_heartbeat_url)

#         try:
#             uptime_heartbeat_url: str = State.config.better_uptime.heartbeat.url
#             if len(uptime_heartbeat_url) > 0:
#                 requests.post(self.uptime_heartbeat_url)
#         except:
#             State.logger.warning(message="Invalid Better Uptime config.")
#             State.logger.warning(message="Create a Better Uptime config in config/<env>/service/better_uptime.yaml.")
#             State.logger.warning(message="""Load the config with the following yaml:
# better_uptime:
#   heartbeat:
#     url: <better_uptime_heartbeat_url>""")

        return True

    def receive(self, limit: int) -> list:
        service_status_copy: ServiceStatus = ServiceStatus(**self.service_status.dict())
        self.service_status.health = None
        self.service_status.vitals = None
        self.service_status.stats = None

        heartbeat: Heartbeat = Heartbeat(
            service=self.service_meta,
            platform=self.service_platform,
            status=service_status_copy,
            process=self.logger.prefix,
            stage=self.environment,
        )

        time.sleep(self.sleep_interval)

        return [heartbeat]

    def is_message_valid(self, message) -> bool:
        return True

    def receipt_message(self, message) -> bool:
        return True

    def form_message(self, message):
        return message.dict()


class MonitorHeartbeatThread(threading.Thread):
    def __init__(self, logger: Logger, heartbeat_interval_minutes: int, queue_url: str, environment: str,
                 service_meta: ServiceMeta, service_status: ServiceStatus):
        super().__init__()
        self.batcher: MonitorHeartbeat = None
        self.logger = logger
        self.heartbeat_interval_minutes: int = heartbeat_interval_minutes
        self.queue_url: str = queue_url
        self.service_meta: ServiceMeta = service_meta
        self.service_status: ServiceStatus = service_status
        self.environment: str = environment
        self.daemon = True

    def run(self) -> None:
        self.batcher = MonitorHeartbeat(
            logger=self.logger, debug=True, queue_url=self.queue_url,
            environment=self.environment,
            service_meta=self.service_meta,
            service_status=self.service_status,
            sleep_interval=self.heartbeat_interval_minutes * 60,
            max_message_delay=self.heartbeat_interval_minutes
        )
        asyncio.run(self.batcher.run())
