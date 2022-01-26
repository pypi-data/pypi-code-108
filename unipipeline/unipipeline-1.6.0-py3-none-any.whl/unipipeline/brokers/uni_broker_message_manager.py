class UniBrokerMessageManager:
    def reject(self) -> None:
        raise NotImplementedError(f'method reject must be specified for class "{type(self).__name__}"')

    def ack(self) -> None:
        raise NotImplementedError(f'method acknowledge must be specified for class "{type(self).__name__}"')
