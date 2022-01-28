"""
API for using dbsamizdat as a library in Django
"""

from argparse import Namespace as _Namespace
from typing import Iterable, Union

from .runner import cmd_refresh as _cmd_refresh, cmd_sync as _cmd_sync, cmd_nuke as _cmd_nuke, txstyle
from .samizdat import Samizdat

_CMD_ARG_DEFAULTS = dict(
    in_django=True,
    verbosity=1,
    log_rather_than_print=True,
    samizdatmodules=tuple(),
)


def refresh(dbconn: str = 'default', transaction_style: txstyle = txstyle.JUMBO, belownodes: Iterable[Union[str, tuple, Samizdat]] = tuple()):
    """Refresh materialized views, in dependency order, optionally restricted to views depending directly or transitively on any of the DB objects specified in `belownodes`."""
    args = _Namespace(
        **_CMD_ARG_DEFAULTS,
        dbconn=dbconn,
        txdiscipline=transaction_style.value,
        belownodes=belownodes,
    )
    _cmd_refresh(args)


def sync(dbconn: str = 'default', transaction_style: txstyle = txstyle.JUMBO):
    """Sync dbsamizdat state to the DB."""
    args = _Namespace(
        **_CMD_ARG_DEFAULTS,
        dbconn=dbconn,
        txdiscipline=transaction_style.value,
    )
    _cmd_sync(args)


def nuke(dbconn: str = 'default', transaction_style: txstyle = txstyle.JUMBO):
    """Remove any database object tagged as samizdat."""
    args = _Namespace(
        **_CMD_ARG_DEFAULTS,
        dbconn=dbconn,
        txdiscipline=transaction_style.value,
    )
    _cmd_nuke(args)
