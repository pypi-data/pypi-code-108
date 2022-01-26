# -*- coding: utf-8 -*-
from pip_services3_commons.refer import Descriptor

from pip_services3_aws.services.CommandableLambdaService import CommandableLambdaService


class DummyCommandableLambdaService(CommandableLambdaService):
    def __init__(self):
        super().__init__('dummies')
        self._dependency_resolver.put('controller',
                                      Descriptor('pip-services-dummies', 'controller', 'default', '*', '*'))
