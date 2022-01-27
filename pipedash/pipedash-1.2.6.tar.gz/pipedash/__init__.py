import logging

from typing import Type

from pipedash.DrawableComponent import TDrawableComponent
from pipedash.PipedashWorker import PipedashWorker
from pipedash.helper import set_loglevel
from pipedash.helper import pip_install_or_ignore
from pipedash.helper import log, debug

from pipedash import DrawableComponent
from pipedash.Registrar import Registrar

registrar = Registrar()

pip_install_or_ignore = pip_install_or_ignore
set_loglevel = set_loglevel
debug = debug

registrar.worker = PipedashWorker()


def connect(api_key="", secret_key=""):
    log.info("Welcome to pipedash. We are connceting...")
    return registrar.worker.connect(api_key, secret_key)


def registerDrawable(component: Type[TDrawableComponent], name: str, description: str, imageUrl: str,
                     identifier: str = None):
    return registrar.worker.registerDrawable(component, name, description, identifier, imageUrl)