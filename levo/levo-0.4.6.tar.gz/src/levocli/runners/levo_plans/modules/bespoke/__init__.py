from levo_commons.providers import Provider


class BespokeProvider(Provider):
    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def is_running(self) -> bool:
        return True
