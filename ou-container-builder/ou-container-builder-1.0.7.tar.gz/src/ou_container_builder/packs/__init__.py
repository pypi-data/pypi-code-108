"""Packs group together related settings and configuration files.

Packs are split into two group. The core packs :mod:`~ou_container_content.packs.services` and
:mod:`~ou_container_content.packs.content`, which are automatically included and the optional
packs :mod:`~ou_container_content.packs.tutorial_server` and :mod:`~ou_container_content.packs.mariadb`,
which must be explicitly included in the ``ContainerConfig.yaml``.
"""
from .tutorial_server import apply_pack as tutorial_server  # noqa
from .mariadb import apply_pack as mariadb  # noqa
from .services import apply_pack as services  # noqa
from .content import apply_pack as content  # noqa
from .scripts import apply_pack as scripts  # noqa
