from .drf_common_views import FacilityViewSet, UserFacilityViewSet
from .vanilla_common_views import (
    AboutView,
    FacilityCreateView,
    FacilityDeleteView,
    FacilityUpdateView,
    FacilityView,
    HomeView,
    UserFacilityAllotmentCreateView,
    UserFacilityAllotmentDeleteView,
    UserFacilityAllotmentUpdateView,
    UserFacilityAllotmentView,
)

__all__ = [
    "AboutView",
    "FacilityCreateView",
    "FacilityDeleteView",
    "FacilityUpdateView",
    "FacilityView",
    "FacilityViewSet",
    "HomeView",
    "UserFacilityAllotmentCreateView",
    "UserFacilityAllotmentDeleteView",
    "UserFacilityAllotmentUpdateView",
    "UserFacilityAllotmentView",
    "UserFacilityViewSet",
]
