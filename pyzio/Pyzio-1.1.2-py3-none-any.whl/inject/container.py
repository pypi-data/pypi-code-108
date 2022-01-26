from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer

from ..config.brainer_config import BrainerConfig
from ..config.mqtt_topics_config import MQTTTopicsConfig
from ..port.adapter.brainer_client import BrainerClient
from ..port.adapter.mqtt.message_factory import MessageFactory
from ..port.adapter.mqtt.message_handler_factory import MessageHandlerFactory
from ..port.adapter.mqtt.mqtt_operation_cache import OperationQueue
from ..port.adapter.mqtt.phasio_mqtt_client import PhasioMQTTClient
from ..port.adapter.phasio_mqtt_adapter import PhasioMQTTAdapter
from ..pyzio_logger import PyzioLogger
from ..pyzio_printer import PyzioPrinter
from ..pyzio_settings import PyzioSettings
from ..repository.local_job_repository import LocalJobRepository
from ..repository.printer_state_repository import PrinterStateRepository
from ..resource.platform_emitter import PlatformEmitter
from ..service.job_service import JobService
from ..service.printer_service import PrinterService
from ..service.update_service import UpdateService


class PyzioContainer(DeclarativeContainer):
    logger = providers.Dependency()
    printer = providers.Dependency()
    settings = providers.Dependency()
    mqtt_config = providers.ThreadSafeSingleton(
        MQTTTopicsConfig,
        settings=settings
    )
    brainer_config = providers.ThreadSafeSingleton(
        BrainerConfig,
        settings=settings)
    brainer_client = providers.ThreadSafeSingleton(
        BrainerClient,
        brainer_config=brainer_config)
    operation_queue = providers.ThreadSafeSingleton(
        OperationQueue
    )
    client = providers.ThreadSafeSingleton(
        PhasioMQTTClient,
        logger=logger, mqtt_config=mqtt_config, operation_queue=operation_queue)

    local_job_repo = providers.ThreadSafeSingleton(
        LocalJobRepository,
        logger=logger)
    printer_state_repo = providers.ThreadSafeSingleton(
        PrinterStateRepository,
        settings=settings)

    printer_service = providers.ThreadSafeSingleton(
        PrinterService,
        printer_state_repo=printer_state_repo, brainer_client=brainer_client)
    job_service = providers.ThreadSafeSingleton(
        JobService,
        printer=printer, brainer_client=brainer_client,
        local_job_repo=local_job_repo, printer_state_repo=printer_state_repo,
        logger=logger, settings=settings)

    update_service = providers.ThreadSafeSingleton(UpdateService)
    message_factory = providers.ThreadSafeSingleton(MessageFactory)
    message_handler_factory = providers.ThreadSafeSingleton(
        MessageHandlerFactory,
        logger=logger, job_service=job_service, update_service=update_service,
        printer_service=printer_service)
    phasio_port = providers.ThreadSafeSingleton(
        PhasioMQTTAdapter,
        logger=logger, message_handler_factory=message_handler_factory,
        client=client, message_factory=message_factory,
        mqtt_config=mqtt_config, printer_service=printer_service)

    emitter = providers.ThreadSafeSingleton(
        PlatformEmitter,
        logger=logger, printer=printer, settings=settings,
        phasio_port=phasio_port, printer_service=printer_service, job_service=job_service)
