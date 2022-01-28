"""
API for using dbsamizdat as a library
"""

from argparse import Namespace as _Namespace
from typing import Iterable, Union

from .runner import cmd_refresh as _cmd_refresh, cmd_sync as _cmd_sync, cmd_nuke as _cmd_nuke, txstyle
from .samizdat import Samizdat

_CMD_ARG_DEFAULTS = dict(
    log_rather_than_print=True,
    in_django=False,
    verbosity=1,
)


def refresh(dburl: str, samizdatmodules: Iterable[str], transaction_style: txstyle = txstyle.JUMBO, belownodes: Iterable[Union[str, tuple, Samizdat]] = tuple()):
    """Refresh materialized views, in dependency order, optionally restricted to views depending directly or transitively on any of the DB objects specified in `belownodes`."""
    args = _Namespace(
        **_CMD_ARG_DEFAULTS,
        dburl=dburl,
        samizdatmodules=samizdatmodules,
        txdiscipline=transaction_style.value,
        belownodes=belownodes,
    )
    _cmd_refresh(args)


def sync(dburl: str, samizdatmodules: Iterable[str], transaction_style: txstyle = txstyle.JUMBO):
    """Sync dbsamizdat state to the DB."""
    args = _Namespace(
        **_CMD_ARG_DEFAULTS,
        dburl=dburl,
        samizdatmodules=samizdatmodules,
        txdiscipline=transaction_style.value,
    )
    _cmd_sync(args)


def nuke(dburl: str, transaction_style: txstyle = txstyle.JUMBO):
    """Remove any database object tagged as samizdat."""
    args = _Namespace(
        **_CMD_ARG_DEFAULTS,
        dburl=dburl,
        txdiscipline=transaction_style.value,
    )
    _cmd_nuke(args)
