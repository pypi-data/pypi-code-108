from typing import Any, Optional

import django.apps
from django.apps import apps
from django.conf import settings
from django.http import HttpRequest
from django.utils.module_loading import autodiscover_modules
from django.utils.translation import gettext as _

from dynamic_preferences.registries import preference_models
from health_check.plugins import plugin_dir
from oauthlib.common import Request as OauthlibRequest

from .registries import (
    group_preferences_registry,
    person_preferences_registry,
    site_preferences_registry,
)
from .util.apps import AppConfig
from .util.core_helpers import (
    create_default_celery_schedule,
    get_or_create_favicon,
    get_site_preferences,
    has_person,
)
from .util.sass_helpers import clean_scss


class CoreConfig(AppConfig):
    name = "aleksis.core"
    verbose_name = "AlekSIS — The Free School Information System"
    dist_name = "AlekSIS-Core"

    urls = {
        "Repository": "https://edugit.org/AlekSIS/official/AlekSIS/",
    }
    licence = "EUPL-1.2+"
    copyright_info = (
        ([2017, 2018, 2019, 2020, 2021, 2022], "Jonathan Weth", "wethjo@katharineum.de"),
        ([2017, 2018, 2019, 2020], "Frank Poetzsch-Heffter", "p-h@katharineum.de"),
        ([2018, 2019, 2020, 2021, 2022], "Hangzhi Yu", "yuha@katharineum.de"),
        ([2018, 2019, 2020, 2021], "Julian Leucker", "leuckeju@katharineum.de"),
        ([2019, 2020, 2021, 2022], "Dominik George", "dominik.george@teckids.org"),
        ([2019, 2020, 2021, 2022], "Tom Teichler", "tom.teichler@teckids.org"),
        ([2019], "mirabilos", "thorsten.glaser@teckids.org"),
        ([2021], "Lloyd Meins", "meinsll@katharineum.de"),
        ([2021], "magicfelix", "felix@felix-zauberer.de"),
        ([2022], "Benedict Suska", "benedict.suska@teckids.org"),
    )

    def ready(self):
        super().ready()

        from django.conf import settings  # noqa

        # Autodiscover various modules defined by AlekSIS
        autodiscover_modules("model_extensions", "form_extensions", "checks")

        sitepreferencemodel = self.get_model("SitePreferenceModel")
        personpreferencemodel = self.get_model("PersonPreferenceModel")
        grouppreferencemodel = self.get_model("GroupPreferenceModel")

        preference_models.register(sitepreferencemodel, site_preferences_registry)
        preference_models.register(personpreferencemodel, person_preferences_registry)
        preference_models.register(grouppreferencemodel, group_preferences_registry)

        self._load_data_checks()

        from .health_checks import (
            BackupJobHealthCheck,
            DataChecksHealthCheckBackend,
            DbBackupAgeHealthCheck,
            MediaBackupAgeHealthCheck,
        )

        plugin_dir.register(DataChecksHealthCheckBackend)
        plugin_dir.register(DbBackupAgeHealthCheck)
        plugin_dir.register(MediaBackupAgeHealthCheck)
        plugin_dir.register(BackupJobHealthCheck)

    @classmethod
    def _load_data_checks(cls):
        """Get all data checks from all loaded models."""
        from aleksis.core.data_checks import DataCheckRegistry

        data_checks = set()
        for model in apps.get_models():
            data_checks.update(getattr(model, "data_checks", []))
        DataCheckRegistry.data_checks = data_checks

    def preference_updated(
        self,
        sender: Any,
        section: Optional[str] = None,
        name: Optional[str] = None,
        old_value: Optional[Any] = None,
        new_value: Optional[Any] = None,
        **kwargs,
    ) -> None:
        from django.conf import settings  # noqa

        if section == "theme":
            if name in ("primary", "secondary"):
                clean_scss()
            elif name in ("favicon", "pwa_icon"):
                from favicon.models import Favicon, FaviconImg  # noqa

                is_favicon = name == "favicon"

                if new_value:
                    # Get file object from preferences instead of using new_value
                    # to prevent problems with special file storages
                    file_obj = get_site_preferences()[f"{section}__{name}"]

                    favicon = Favicon.on_site.update_or_create(
                        title=name,
                        defaults={"isFavicon": is_favicon, "faviconImage": file_obj},
                    )[0]
                    FaviconImg.objects.filter(faviconFK=favicon).delete()
                else:
                    Favicon.on_site.filter(title=name, isFavicon=is_favicon).delete()
                    if name in settings.DEFAULT_FAVICON_PATHS:
                        get_or_create_favicon(
                            name, settings.DEFAULT_FAVICON_PATHS[name], is_favicon=is_favicon
                        )

    def post_migrate(
        self,
        app_config: django.apps.AppConfig,
        verbosity: int,
        interactive: bool,
        using: str,
        **kwargs,
    ) -> None:
        from django.conf import settings  # noqa

        super().post_migrate(app_config, verbosity, interactive, using, **kwargs)

        # Ensure presence of an OTP YubiKey default config
        apps.get_model("otp_yubikey", "ValidationService").objects.using(using).update_or_create(
            name="default", defaults={"use_ssl": True, "param_sl": "", "param_timeout": ""}
        )

        # Ensure that default Favicon object exists
        for name, default in settings.DEFAULT_FAVICON_PATHS.items():
            get_or_create_favicon(name, default, is_favicon=name == "favicon")

        # Create default periodic tasks
        create_default_celery_schedule()

    def user_logged_in(
        self, sender: type, request: Optional[HttpRequest], user: "User", **kwargs
    ) -> None:
        if has_person(user):
            # Save the associated person to pick up defaults
            user.person.save()

    @classmethod
    def get_all_scopes(cls) -> dict[str, str]:
        scopes = {
            "read": "Read anything the resource owner can read",
            "write": "Write anything the resource owner can write",
        }
        if settings.OAUTH2_PROVIDER.get("OIDC_ENABLED", False):
            scopes |= {
                "openid": _("OpenID Connect scope"),
                "profile": _("Given name, family name, link to profile and picture if existing."),
                "address": _("Full home postal address"),
                "email": _("Email address"),
                "phone": _("Home and mobile phone"),
                "groups": _("Groups"),
            }
        return scopes

    @classmethod
    def get_additional_claims(cls, scopes: list[str], request: OauthlibRequest) -> dict[str, Any]:
        django_request = HttpRequest()
        django_request.META = request.headers

        claims = {
            "preferred_username": request.user.username,
        }

        if "profile" in scopes:
            if has_person(request.user):
                claims["given_name"] = request.user.person.first_name
                claims["family_name"] = request.user.person.last_name
                claims["profile"] = django_request.build_absolute_uri(
                    request.user.person.get_absolute_url()
                )
                if request.user.person.photo:
                    claims["picture"] = django_request.build_absolute_uri(
                        request.user.person.photo.url
                    )
            else:
                claims["given_name"] = request.user.first_name
                claims["family_name"] = request.user.last_name

        if "email" in scopes:
            if has_person(request.user):
                claims["email"] = request.user.person.email
            else:
                claims["email"] = request.user.email

        if "address" in scopes and has_person(request.user):
            claims["address"] = {
                "street_address": request.user.person.street
                + " "
                + request.user.person.housenumber,
                "locality": request.user.person.place,
                "postal_code": request.user.person.postal_code,
            }

        if "groups" in scopes and has_person(request.user):
            claims["groups"] = list(
                request.user.person.member_of.values_list("name", flat=True).all()
            )

        return claims
