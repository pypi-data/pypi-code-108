from rest_framework import serializers

from .models import SAMLConfiguration


class SAMLConfigurationSerializer(serializers.ModelSerializer):
    """Serializes the SAMLConfiguration Model"""

    class Meta:
        model = SAMLConfiguration

        fields = ['name', 'endpoint']
