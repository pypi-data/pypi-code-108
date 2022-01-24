import logging
import asyncio

from .loop import ChihuoLoop
from .signal_handlers import set_signal_handlers

logger = logging.getLogger(__name__)


def run(*classes_or_instances):
    if not classes_or_instances:
        logger.error("No provide factory class or instance")

    assert classes_or_instances, "No provide factory class or instance"

    factories = []
    for obj in classes_or_instances:
        if isinstance(obj, ChihuoLoop):
            if obj.NAME is None:
                raise TypeError("factory.NAME must be given")
            factories.append(obj)
        else:
            if type(obj) is not type:
                raise TypeError("factory must be a class or instance of ChihuoLoop")
            if not issubclass(obj, ChihuoLoop):
                raise TypeError(
                    "factory must be a subclass of ChihuoLoop or instance of ChihuoLoop"
                )
            if obj.NAME is None:
                raise TypeError("factory.NAME must be given")

            factories.append(obj())

    logger.info("Find factories: %s", [factory.NAME for factory in factories])

    loop = asyncio.get_event_loop()
    set_signal_handlers(factories, loop)

    for factory in factories:
        factory._run_()

    loop.run_forever()
