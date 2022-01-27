# import uuid

# from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _
from django.utils.text import slugify

# from django.urls import reverse
from django.contrib.sites.models import Site


class SiteConfigModel(models.Model):
    key = models.CharField(_("Key"), max_length=120, blank=False) # Path to module
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="settings",
    )  # This uses a callable so it will not trigger a migration with the projects it's included in
    deleted = models.BooleanField(
        _("Deleted"), default=False, help_text=_("Soft Delete the Setting value")
    )
    value = models.JSONField(_("Value"), default=dict)

    # TODO: Create manager to get record by key slug
    #       ideally it would look something like Site.config.get("some-key")
    #       it should return a value or None, no matter wether or not the key is set for that site

    class Meta:
        verbose_name = _("Site Setting")
        verbose_name_plural = _("Site Settings")
        constraints = [
            models.UniqueConstraint(fields=["key", "site"], name="unique key per site")
        ]

    def __str__(self):
        return "{key} ({site}): {value}".format(
            key=self.key, site=self.site.name, value=str(self.value)
        )
