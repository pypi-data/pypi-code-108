from typing import Type

from smsit import Gateway, Message


class GatewayManager:
    _config = dict()
    _gateways = dict()

    def register(self, alias, gateway: Type[Gateway]):
        self._gateways[alias] = gateway
        return self

    def configure(self, config):
        for alias, config in config.items():
            if alias in self._gateways:
                self._gateways[alias] = self._gateways[alias](config=config)
            else:
                raise ValueError("Gateway %s not registered." % alias)
        return self

    def get_gateway(self, alias) -> Gateway:
        return self._gateways[alias]

    def send(self, alias: str, message: Message) -> bool:
        return self.get_gateway(alias).send(message)
