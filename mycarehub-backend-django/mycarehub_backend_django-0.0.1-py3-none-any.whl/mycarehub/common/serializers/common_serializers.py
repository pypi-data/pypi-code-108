"""Common serializers."""
import logging

from rest_framework import serializers

from mycarehub.users.api.serializers import SimpleUserSerializer

from ..models import Facility, UserFacilityAllotment
from .base_serializers import BaseSerializer

LOGGER = logging.getLogger(__name__)


class FacilitySerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = Facility
        fields = "__all__"


class UserFacilityAllotmentSerializer(BaseSerializer):

    user_data = SimpleUserSerializer(source="user", read_only=True)
    user_name = serializers.ReadOnlyField(source="user.__str__")
    allotment_type_name = serializers.ReadOnlyField(source="get_allotment_type_display")

    class Meta(BaseSerializer.Meta):
        model = UserFacilityAllotment
        fields = "__all__"
