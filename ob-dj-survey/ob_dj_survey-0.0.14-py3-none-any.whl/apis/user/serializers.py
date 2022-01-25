import logging

from django.contrib.auth import get_user_model
from rest_framework import serializers

logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "first_name", "last_name", "email")
