from multiprocessing import Process
from time import sleep
from typing import List, Optional
from rich.console import Console

from pyfactcast.client import sync as FS

from fact_lake.config import get_configuration, get_factcast_configuration, get_logger
from fact_lake.projectors import project_namespace


app_config = get_configuration()  # TODO make configurable
fs_config = get_factcast_configuration(app_config)


fact_store = FS.FactStore(
    FS.get_synchronous_grpc_client(get_factcast_configuration(app_config))
)


class Server:
    def __init__(self, console: Optional[Console] = None) -> None:
        self.processes: List[Process] = []
        self.log = get_logger(self.__class__.__name__)
        if not console:
            self.console = Console()
        else:
            self.console = console

    def run(self) -> None:
        with fact_store as fs:
            namespaces = set(fs.enumerate_namespaces())

            if app_config.whitelist:
                namespaces_to_work_on = namespaces.intersection(app_config.whitelist)
            elif app_config.blacklist:
                namespaces_to_work_on = namespaces - set(app_config.blacklist)
            else:
                namespaces_to_work_on = namespaces

            self.processes = [
                Process(target=project_namespace, args=(namespace,), name=namespace)
                for namespace in namespaces_to_work_on
            ]

            for process in self.processes:
                process.start()

            self._restart_dead_namespaces()

    def _restart_dead_namespaces(self) -> None:
        while True:
            sleep(60)
            self.log.info("Checking processes for liveness.")
            for process in self.processes:
                namespace = process.name

                if not process.is_alive():
                    self.log.debug(
                        f"Found dead process for namespace {namespace}. Restarting..."
                    )
                    self.processes.remove(process)
                    replacement = Process(
                        target=project_namespace, args=(namespace,), name=namespace
                    )
                    self.processes.append(replacement)
                    replacement.start()
                    self.log.debug("Restarted.")
                else:
                    self.log.debug(f"Process for namespace {namespace} is alive.")

    def print_process_status(self) -> None:
        for process in self.processes:
            self.console.print(
                f"Process for namespace {process.name} is alive: {process.is_alive()}"
            )

    def join(self) -> None:
        for process in self.processes:
            process.join()
