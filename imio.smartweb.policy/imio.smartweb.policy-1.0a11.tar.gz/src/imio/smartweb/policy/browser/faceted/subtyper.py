from eea.facetednavigation.subtypes.interfaces import IFacetedSubtyper
from eea.facetednavigation.subtypes.subtyper import FacetedPublicSubtyper
from zope.interface import implementer


@implementer(IFacetedSubtyper)
class FolderFacetedPublicSubtyper(FacetedPublicSubtyper):
    """Deactivate faceted navigation on imio.smartweb.Folder content type."""

    @property
    def can_enable(self):
        """See IFacetedSubtyper"""
        return False

    @property
    def can_disable(self):
        """See IFacetedSubtyper"""
        return False

    def enable(self):
        """See IFacetedSubtyper"""
        return False

    def disable(self):
        """See IFacetedSubtyper"""
        return False
