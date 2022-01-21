# -*- coding: utf-8 -*-
# Copyright 2021 - 2021, Sean Mooney and the arbiterd contributors
# SPDX-License-Identifier: Apache-2.0
import dataclasses
import logging
import typing as ty
from dataclasses import dataclass

from arbiterd import arbiters


@dataclass(init=False)
class Dispatcher:
    """Dispatcher and Manager of arbiters"""

    arbiters: ty.Dict = dataclasses.field(default_factory=dict)

    def __init__(self) -> None:
        logging.debug('initalising dispatcher')
        self.arbiters = {
            a_type: cls()
            for a_type, cls in arbiters.get_all_arbiters().items()}
        logging.debug(f'with self.arbiters={self.arbiters}')

    def arbitrate(self, a_type, context) -> str:
        return self.arbiters[a_type].arbitrate(context)

    def revoke(self, a_type, context) -> str:
        return self.arbiters[a_type].revoke(context)
