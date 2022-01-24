# -*- coding: utf-8 -*-
"""Init and utils."""

from zope.i18nmessageid import MessageFactory

import logging


ActionsPanelMessageFactory = MessageFactory('imio.actionspanel')
logger = logging.getLogger("imio.actionspanel")


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
