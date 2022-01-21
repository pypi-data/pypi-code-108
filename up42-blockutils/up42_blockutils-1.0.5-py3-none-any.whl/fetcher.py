"""
Important:
    DEPRECATED in favour of `blockutils.blocks.DataBlock`.
    See documentation [here](blocks.md#blockutils.blocks.DataBlock).

Abstract classes for data blocks.
"""
from .stac import STACQuery


class AbstractFetcher:
    """
    Base abstract fetcher.
    """

    def fetch(self, query: STACQuery, dry_run: bool = False):
        raise NotImplementedError


class AbstractAOIClippedFetcher(AbstractFetcher):
    """
    AOIClipped abstract fetcher.
    """

    def fetch(self, query: STACQuery, dry_run: bool = False):
        raise NotImplementedError


class AbstractFullSceneFetcher(AbstractFetcher):
    """
    FullScene abstract fetcher.
    """

    def fetch(self, query: STACQuery, dry_run: bool = False):
        raise NotImplementedError
