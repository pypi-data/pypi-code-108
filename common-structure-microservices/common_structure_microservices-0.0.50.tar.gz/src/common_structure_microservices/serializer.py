import datetime
import uuid

from rest_framework import serializers


class AuditorySerializer(serializers.ModelSerializer):

    created_by = serializers.HiddenField(default=uuid.uuid4)
    created_date = serializers.HiddenField(default=datetime.datetime.now)
    updated_by = serializers.HiddenField(default=uuid.uuid4)
    updated_date = serializers.HiddenField(default=datetime.datetime.now)
