from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class OsuAccount(ProviderAccount):
    def get_cover_url(self):
        return self.account.extra_data.get("cover_url")

    def get_avatar_url(self):
        return self.account.extra_data.get("avatar_url")

    def to_str(self):
        dflt = super(OsuAccount, self).to_str()
        return next(
            value
            for value in (
                self.account.extra_data.get("name", None),
                self.account.extra_data.get("login", None),
                dflt,
            )
            if value is not None
        )


class OsuProvider(OAuth2Provider):
    id = "osu"
    name = "osu!"
    account_class = OsuAccount

    def get_default_scope(self):
        scope = []
        if app_settings.QUERY_EMAIL:
            scope.append("user:email")
        return scope

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        return dict(
            username=data.get("username"),
            name=data.get("username"),
        )


provider_classes = [OsuProvider]
