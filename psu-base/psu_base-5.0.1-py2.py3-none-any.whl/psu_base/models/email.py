from django.db import models
from psu_base.classes.Log import Log
from psu_base.services import utility_service

log = Log()


class Email(models.Model):
    """Record of emails sent"""

    app_code = models.CharField(
        max_length=15,
        verbose_name="Application Code",
        help_text="Application that this email belongs to.",
        blank=False,
        null=False,
    )

    url = models.CharField(
        max_length=128,
        help_text="This holds the URL from which the email was sent",
        blank=True,
        null=True,
    )

    initiator = models.CharField(
        max_length=128,
        help_text="This holds the logged-in user (which could be a provisional email address)",
        blank=True,
        null=True,
    )

    date_created = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=1,
        help_text="Indicates the status of the email (sent, failed, etc)",
        blank=False,
        null=False,
    )

    error_message = models.CharField(
        max_length=128,
        help_text="Holds any error that may have been encountered",
        blank=True,
        null=True,
    )

    subject = models.CharField(
        max_length=128, help_text="Email subject", blank=False, null=False
    )

    content = models.CharField(
        max_length=4000, help_text="Email content", blank=True, null=True
    )

    sender = models.CharField(
        max_length=128,
        help_text="Email address the email was sent from",
        blank=False,
        null=False,
    )

    to = models.CharField(
        max_length=4000,
        help_text="Email addresses the email was sent to",
        blank=True,
        null=True,
    )

    cc = models.CharField(
        max_length=4000,
        help_text="Email addresses the email was copied to",
        blank=True,
        null=True,
    )

    bcc = models.CharField(
        max_length=4000,
        help_text="Email addresses the email was blind-copied to",
        blank=True,
        null=True,
    )

    email_template = models.CharField(
        max_length=128,
        help_text="This holds the path of the template used for the email",
        blank=True,
        null=True,
    )

    context = models.CharField(
        max_length=4000,
        help_text="Email addresses the email was blind-copied to",
        blank=True,
        null=True,
    )

    max_recipients = models.IntegerField(
        help_text="The maximum number of addresses this email could have been sent to"
    )

    def get_to_list(self):
        return utility_service.csv_to_list(self.to)

    def get_cc_list(self):
        return utility_service.csv_to_list(self.cc)

    def get_bcc_list(self):
        return utility_service.csv_to_list(self.bcc)

    def get_to_csv(self):
        ll = self.get_to_list()
        return ", ".join(ll) if ll else ""

    def get_cc_csv(self):
        ll = self.get_cc_list()
        return ", ".join(ll) if ll else ""

    def get_bcc_csv(self):
        ll = self.get_bcc_list()
        return ", ".join(ll) if ll else ""
