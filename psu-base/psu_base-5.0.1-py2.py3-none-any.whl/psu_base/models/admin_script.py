from django.db import models
from psu_base.classes.Log import Log
import datetime

log = Log()


class AdminScript(models.Model):
    """
    Admin Script - Javascript that can be defined to run at the end of specified requests.
    Mainly used for a quick temporary fix to a production bug without a redeployment.
    Other uses could be to temporarily alter a feature for a specific user or temporarily
    disable something that does not have a feature toggle.
    """

    # Associated app
    app_code = models.CharField(
        max_length=15,
        verbose_name="Application Code",
        help_text="Application that this script belongs to. NULL applies to all apps (global)",
        default=None,
        blank=True,
        null=True,
    )

    # Who wrote this and when
    last_updated = models.DateTimeField(auto_now=True)
    developer = models.CharField(
        max_length=30,
        verbose_name="Developer",
        help_text="This developer who last modified this script",
    )

    # What does the script do
    description = models.CharField(
        max_length=100,
        verbose_name="Description of the Script",
        help_text="What does the script do. Why is it needed.",
    )

    # In what situation should this run
    target_username = models.CharField(
        max_length=30,
        verbose_name="Targeted User",
        help_text="This script will apply only to the specified user",
        default=None,
        blank=True,
        null=True,
    )
    target_url = models.CharField(
        max_length=80,
        verbose_name="Targeted User",
        help_text="This script will apply only to the specified user",
        default=None,
        blank=True,
        null=True,
    )

    # Is the script active
    enabled = models.CharField(
        max_length=1,
        help_text="Is this script enabled?",
        default="N",
        choices=(("N", "No"), ("Y", "Yes")),
    )
    eff_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    # The script
    javascript = models.CharField(
        max_length=4000,
        verbose_name="JavaScript Code",
        help_text="JavaScript code to run when page loads",
        blank=True,
        null=True,
    )

    def is_active(self):
        # Must be enabled
        if self.enabled != "Y":
            return False
        # Must be effective
        if self.eff_date and self.eff_date > datetime.datetime.now():
            return False
        # Cannot have ended
        if self.end_date and self.end_date <= datetime.datetime.now():
            return False

        return True
