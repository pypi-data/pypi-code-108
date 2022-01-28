from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from six import text_type
from social_django.utils import load_strategy

from drf_auth_service.models import SSOUser
from drf_auth_service.settings import settings
from drf_auth_service.socials.helpers import get_user_data_from_provider
from drf_auth_service.socials.serializers import SocialSerializer, ReturnSocialSerializer

oauth_response = openapi.Response('Respond with jwt secret token if user exists', ReturnSocialSerializer)


@swagger_auto_schema(method='POST', request_body=SocialSerializer, responses={200: oauth_response})
@api_view(['POST'])
@permission_classes([settings.PERMISSIONS.SERVICE_TOKEN_PERMISSION])
def social_login(self, request):
    """Authenticate user through the provider(facebook/google/apple) and access_token"""

    user_exist = False
    serializer = self.serializer_class(data=request.data)
    serializer.is_valid(raise_exception=True)
    provider = serializer.data.get('provider', None)
    strategy = load_strategy(request)
    user_data = get_user_data_from_provider(strategy, provider, serializer.data.get('social_token'),
                                            serializer.data.get('device_type'))
    response_data = dict(exists=user_exist, data=user_data)

    if provider == settings.ENUMS.SOCIAL_TYPES.Facebook:
        response_data['data'].update(dict(picture=user_data['picture']['data'].get('url', None)))
        user_exist = SSOUser.objects.filter(user_social_identifier__identifier=user_data.get('id'))

    elif provider == settings.ENUMS.SOCIAL_TYPES.Google:
        user_exist = SSOUser.objects.filter(user_social_identifier__identifier=user_data.get('sub'))
        response_data['data'] = dict(id=user_data.get('sub'), first_name=user_data.get('given_name', None),
                                     last_name=user_data.get('family_name', None),
                                     picture=user_data.get('picture', None), email=user_data.get('email', None))

    elif provider == settings.ENUMS.SOCIAL_TYPES.Apple:
        raise NotImplementedError()

    if user_exist and user_exist.exists():
        refresh = TokenObtainPairSerializer.get_token(user_exist.first())
        response_data['exists'] = user_exist.exists()
        response_data['auth'] = dict(pwd_token=user_exist.first().pwd_token, access=text_type(refresh.access_token))

    return Response(response_data)
