from mycarehub.common.dashboard import get_mycarehub_facilities_queryset
from mycarehub.common.filters import FacilityFilter, UserFacilityAllotmentFilter
from mycarehub.common.models import UserFacilityAllotment
from mycarehub.common.serializers import FacilitySerializer, UserFacilityAllotmentSerializer

from ..base_views import BaseView


class FacilityViewSet(BaseView):
    queryset = get_mycarehub_facilities_queryset()
    serializer_class = FacilitySerializer
    filterset_class = FacilityFilter
    ordering_fields = ("name", "mfl_code", "county", "phone", "sub_county", "ward")
    search_fields = (
        "name",
        "mfl_code",
        "registration_number",
    )
    facility_field_lookup = "pk"


class UserFacilityViewSet(BaseView):
    queryset = UserFacilityAllotment.objects.active().order_by(
        "user__name", "user__username", "-updated", "-created"
    )
    serializer_class = UserFacilityAllotmentSerializer
    filterset_class = UserFacilityAllotmentFilter
    ordering_fields = ("user__name", "user__username", "allotment_type")
    search_fields = ("allotment_type", "user__name", "user__username")
