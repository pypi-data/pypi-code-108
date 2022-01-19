from django.db import models
from psu_base.classes.Log import Log

log = Log()


class Xss(models.Model):
    """Potential XSS attempts"""

    # Fields
    app_code = models.CharField(
        max_length=15,
        verbose_name="Application Code",
        help_text="Application that this attempt was made in.",
        blank=False,
        null=False,
    )
    path = models.CharField(
        max_length=200, help_text="Request path", blank=False, null=False
    )
    username = models.CharField(
        max_length=30,
        help_text="Authenticated username",
        default=None,
        blank=True,
        null=True,
    )
    parameter_name = models.CharField(
        max_length=80, help_text="Parameter name", default=None, blank=True, null=True
    )
    parameter_value = models.CharField(
        max_length=500,
        help_text="Parameter content",
        default=None,
        blank=True,
        null=True,
    )
    review_username = models.CharField(
        max_length=30, help_text="Reviewed by", default=None, blank=True, null=True
    )
    date_created = models.DateTimeField(auto_now_add=True)
