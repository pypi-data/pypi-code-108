from rest_framework import serializers

from .models import StoredCredential


class StoredCredentialSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        extra_kwargs = {
            'url': {
                'lookup_url_kwarg': 'credential_id',
                'view_name': 'rest_api:credential-detail'
            },
        }
        fields = (
            'label', 'backend_path', 'backend_data', 'id', 'url'
        )
        model = StoredCredential
