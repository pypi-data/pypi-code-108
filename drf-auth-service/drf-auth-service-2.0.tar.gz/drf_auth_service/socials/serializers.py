from rest_framework import serializers

from drf_auth_service.models import Social
from drf_auth_service.settings import settings
from drf_auth_service.socials.constants import DeviceTypes


class ReturnUserSocialDataSerializer(serializers.Serializer): # noqa
    id = serializers.IntegerField(label='Social Id', required=False)
    first_name = serializers.CharField(label='Social first name', required=False)
    last_name = serializers.CharField(label='Social last name', required=False)
    picture = serializers.ImageField(label='Social image', required=False)
    email = serializers.ImageField(label='Social email', required=False)


class ReturnSocialSerializer(serializers.Serializer): # noqa
    data = ReturnUserSocialDataSerializer()
    exists = serializers.BooleanField(label='True if user with this email or social'
                                            ' identifier already exists in our database')


class SocialSerializer(serializers.Serializer): # noqa
    """
    Serializer which accepts an OAuth2 access token and provider.
    """

    social_token = serializers.CharField(required=True, allow_blank=False, trim_whitespace=True)
    provider = serializers.ChoiceField(required=True, allow_blank=False, allow_null=False,
                                       choices=settings.ENUMS.SOCIAL_TYPES)
    device_type = serializers.ChoiceField(choices=DeviceTypes.choices, default=DeviceTypes.ANDROID)


class SocialModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Social
        fields = ('label', 'identifier', 'social_type')
