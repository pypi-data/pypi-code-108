from rest_framework import serializers

from drf_auth_service.models import Service


class ServiceSerializer(serializers.ModelSerializer):
    public_token = serializers.CharField(read_only=True)
    secret_token = serializers.CharField(read_only=True)

    class Meta:
        model = Service
        fields = '__all__'
