from rest_framework import serializers

from aparnik.api.serializers import ModelSerializer
from aparnik.utils.utils import convert_iran_phone_number_to_world_number

from ..models import ContactUs


class ContactUsListSerializer(ModelSerializer):
    url = serializers.SerializerMethodField()
    resourcetype = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(ContactUsListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = ContactUs
        fields = [
            'id',
            'url',
            'first_name',
            'last_name',
            'title',
            'is_active',
            'update_at',
            'resourcetype',
        ]

        read_only_fields = [
            'id',
            'url',
            'is_active',
            'update_at',
            'resourcetype',
        ]

    def get_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_uri())

    def get_resourcetype(self, obj):
        return 'ContactUs'


class ContactUsDestailSerializer(ContactUsListSerializer):
    phone = serializers.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(ContactUsDestailSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = ContactUs
        fields = ContactUsListSerializer.Meta.fields + [
            'website',
            'address',
            'phone',
            'email',
            'content',
        ]

        read_only_fields = ContactUsListSerializer.Meta.read_only_fields + [
        ]

    def validate_phone(self, value):
        return convert_iran_phone_number_to_world_number(value)
