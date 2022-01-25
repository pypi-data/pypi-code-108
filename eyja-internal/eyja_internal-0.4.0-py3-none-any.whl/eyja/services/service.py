import asyncio
import uvloop
import importlib

class Service:
    @classmethod
    def run(cls, module_name: str):
        module = importlib.import_module(module_name)
        service_name = getattr(module, 'SERVICE_NAME', 'common')
        logger = getattr(module, 'logger', None)
        run_app = getattr(module, 'run_app', None)

        uvloop.install()

        loop = asyncio.get_event_loop()

        if logger:
            logger.info(f'Service [{service_name}] has been launched')
        if run_app:
            loop.run_until_complete(run_app())

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            if logger:
                logger.info(f'Service [{service_name}] has been stopped')
            loop.stop()

        loop.close()
