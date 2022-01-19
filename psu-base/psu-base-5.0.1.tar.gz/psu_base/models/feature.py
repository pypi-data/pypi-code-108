from django.db import models
from psu_base.classes.Log import Log
from psu_base.classes.ConvenientDate import ConvenientDate

log = Log()


class Feature(models.Model):
    """Feature Toggles"""

    # Fields
    app_code = models.CharField(
        max_length=15,
        verbose_name="Application Code",
        help_text="Application that this feature belongs to. NULL applies to all apps (global)",
        default=None,
        blank=True,
        null=True,
    )
    default = models.CharField(
        max_length=1,
        help_text="This is the default definition of the feature (intended to be used globally)",
        default="N",
        choices=(("N", "No"), ("Y", "Yes")),
    )
    override = models.CharField(
        max_length=1,
        help_text="This overrides other definitions of the feature (intended to be used globally)",
        default="N",
        choices=(("N", "No"), ("Y", "Yes")),
    )
    feature_code = models.CharField(
        max_length=30,
        verbose_name="Feature Identifier",
        help_text="Short identifier for referencing this feature from source code",
    )
    feature_title = models.CharField(
        max_length=80,
        verbose_name="Feature Title",
        help_text="Title of the feature (displayed to users)",
    )
    feature_description = models.CharField(
        max_length=500,
        verbose_name="Feature Description",
        help_text="Optional description of the feature (displayed to users)",
        default=None,
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=1,
        help_text="Is this feature active?",
        default="L",
        choices=(("N", "No"), ("Y", "Yes"), ("L", "Limited to Admins")),
    )
    enable_date = models.DateTimeField(default=None, blank=True, null=True)
    disable_date = models.DateTimeField(default=None, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def enable_date_display(self):
        if self.enable_date:
            return ConvenientDate(self.enable_date).banner_date_time()
        else:
            return ""

    def disable_date_display(self):
        if self.disable_date:
            return ConvenientDate(self.disable_date).banner_date_time()
        else:
            return ""

    def get_status_description(self):
        if self.status == "Y":
            return "Active"
        elif self.status == "L":
            return "Limited"
        else:
            return "Inactive"

    def __str__(self):
        return f"<{self.get_status_description()} Feature: {self.feature_code}>"

    def to_dict(self):
        return {
            "id": self.id,
            "app_code": self.app_code,
            "default": self.default,
            "override": self.override,
            "feature_code": self.feature_code,
            "feature_title": self.feature_title,
            "feature_description": self.feature_description,
            "status": self.status,
            "status_description": self.get_status_description(),
            "last_updated": self.last_updated.strftime("%Y-%m-%d %H:%M:%S"),
        }


class FeatureToggle:
    """
    All features are queried once and saved in the session.
    When retrieved from the session, they are no longer model objects.
    The FeatureToggle class will represent a Feature that has been stored in the session
    """

    id: None
    app_code: None
    default: None
    override: None
    feature_code: None
    feature_title: None
    feature_description: None
    status: None
    status_description: None
    last_updated: None

    def __init__(self, feature_dict):
        self.id = feature_dict["id"]
        self.app_code = feature_dict["app_code"]
        self.default = feature_dict["default"]
        self.override = feature_dict["override"]
        self.feature_code = feature_dict["feature_code"]
        self.feature_title = feature_dict["feature_title"]
        self.feature_description = feature_dict["feature_description"]
        self.status = feature_dict["status"]
        self.status_description = feature_dict["status_description"]
        self.last_updated = feature_dict["last_updated"]
