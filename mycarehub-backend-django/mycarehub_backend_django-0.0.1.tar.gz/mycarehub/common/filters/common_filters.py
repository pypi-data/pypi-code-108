from rest_framework import filters

from ..models import Facility, UserFacilityAllotment
from .base_filters import CommonFieldsFilterset


class FacilityFilter(CommonFieldsFilterset):
    """Filter facilities."""

    search = filters.SearchFilter()

    class Meta:
        """Set up filter options."""

        model = Facility
        fields = "__all__"


class UserFacilityAllotmentFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:
        model = UserFacilityAllotment
        fields = ("user",)
