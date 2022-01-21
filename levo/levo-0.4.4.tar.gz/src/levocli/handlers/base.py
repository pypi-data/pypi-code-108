class EventHandler:
    def get_name(self) -> str:
        return self.__class__.__name__

    def handle_event(self, context, event) -> None:
        raise NotImplementedError

    def shutdown(self) -> None:
        # Do nothing by default
        pass
