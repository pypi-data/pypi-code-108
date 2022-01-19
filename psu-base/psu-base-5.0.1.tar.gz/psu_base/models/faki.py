from django.db import models
from psu_base.classes.Log import Log
import datetime

log = Log()


class FakiResponse(models.Model):
    """
    Faki - Fake Finti
      Store a Finti endpoint's URL (not including the host), and the response that it would generate.
    """

    path = models.CharField(
        max_length=500,
        verbose_name="Finti Endpoint URL",
        help_text="Do not include the host portion of the URL",
    )

    method = models.CharField(
        max_length=10,
        verbose_name="Request Method",
        help_text="GET, POST, PUT, PATCH, DELETE, etc",
        default="GET",
    )

    parameters = models.TextField(
        verbose_name="Parameters provided to the API endpoint",
        help_text="",
        default=None,
        blank=True,
        null=True,
    )
    payload = models.TextField(
        verbose_name="JSON body provided as POST data",
        help_text="Use only if the endpoint accepts JSON data",
        default=None,
        blank=True,
        null=True,
    )
    headers = models.TextField(
        verbose_name="Headers sent with request",
        help_text="",
        default=None,
        blank=True,
        null=True,
    )

    json_response = models.TextField(
        verbose_name="JSON body provided as POST data",
        help_text="The full unedited response from Finti",
        default=None,
        blank=True,
        null=True,
    )

    hash_identifier = models.CharField(
        max_length=100,
        verbose_name="Unique Identifier",
        help_text="Allows a unique lookup to a specific URL and parameter set",
    )
