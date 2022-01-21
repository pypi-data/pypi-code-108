import requests

from allauth.socialaccount.providers.osu.provider import OsuProvider
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class OsuOAuth2Adapter(OAuth2Adapter):
    provider_id = OsuProvider.id
    access_token_url = "https://osu.ppy.sh/oauth/token"
    authorize_url = "https://osu.ppy.sh/oauth/authorize"
    profile_url = "https://osu.ppy.sh/api/v2/me"

    def complete_login(self, request, app, token, **kwargs):
        headers = {
            "Authorization": "Bearer {0}".format(token.token),
            "Content-Type": "application/json",
        }
        extra_data = requests.get(self.profile_url, headers=headers)

        return self.get_provider().sociallogin_from_response(request, extra_data.json())


oauth2_login = OAuth2LoginView.adapter_view(OsuOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(OsuOAuth2Adapter)
