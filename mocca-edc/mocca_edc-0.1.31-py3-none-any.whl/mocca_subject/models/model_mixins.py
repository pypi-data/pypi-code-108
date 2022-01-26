from django.conf import settings
from django.db import models
from edc_constants.choices import YES_NO, YES_NO_NA
from edc_constants.constants import NO, NOT_APPLICABLE
from edc_model import models as edc_models
from edc_model.utils import estimated_date_from_ago


class ReviewModelMixin(models.Model):

    care_delivery = models.CharField(
        verbose_name=(
            "Was care for this `condition` delivered in an integrated care clinic today?"
        ),
        max_length=25,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
        help_text="Select `not applicable` if site was not selected for integrated care.",
    )

    care_delivery_other = models.TextField(
        verbose_name="If no, please explain", null=True, blank=True
    )

    class Meta:
        abstract = True


class ComplicationsBaselineModelMixin(models.Model):

    stroke = models.CharField(
        verbose_name="Stroke",
        max_length=25,
        choices=YES_NO,
        null=True,
        blank=False,
    )

    stroke_ago = edc_models.DurationYMDField(
        verbose_name="If yes, how long ago",
        null=True,
        blank=True,
    )

    stroke_estimated_date = models.DateField(
        verbose_name="Estimated date of stroke",
        null=True,
        blank=True,
        editable=False,
    )

    # heart_attack
    heart_attack = models.CharField(
        verbose_name="Heart attack / heart failure",
        max_length=25,
        choices=YES_NO,
        null=True,
        blank=False,
    )

    heart_attack_ago = edc_models.DurationYMDField(
        verbose_name="If yes, how long ago",
        null=True,
        blank=True,
    )

    heart_attack_estimated_date = models.DateField(
        verbose_name="Estimated date of heart attack / heart failure",
        null=True,
        blank=True,
        editable=False,
    )

    # renal
    renal_disease = models.CharField(
        verbose_name="Renal (kidney) disease",
        max_length=25,
        choices=YES_NO,
        null=True,
        blank=False,
    )

    renal_disease_ago = edc_models.DurationYMDField(
        verbose_name="If yes, how long ago",
        null=True,
        blank=True,
    )

    renal_disease_estimated_date = models.DateField(
        verbose_name="Estimated date of renal_disease",
        null=True,
        blank=True,
        editable=False,
    )
    # vision
    vision = models.CharField(
        verbose_name="Vision problems (e.g. blurred vision)",
        max_length=25,
        choices=YES_NO,
        null=True,
        blank=False,
    )

    vision_ago = edc_models.DurationYMDField(
        verbose_name="If yes, how long ago",
        null=True,
        blank=True,
    )

    vision_estimated_date = models.DateField(
        verbose_name="Estimated date of vision problems",
        null=True,
        blank=True,
        editable=False,
    )

    # numbness
    numbness = models.CharField(
        verbose_name="Numbness / burning sensation",
        max_length=25,
        choices=YES_NO,
        null=True,
        blank=False,
    )

    numbness_ago = edc_models.DurationYMDField(
        verbose_name="If yes, how long ago",
        null=True,
        blank=True,
    )

    numbness_estimated_date = models.DateField(
        verbose_name="Estimated date of numbness",
        null=True,
        blank=True,
        editable=False,
    )

    # foot ulcers
    foot_ulcers = models.CharField(
        verbose_name="Foot ulcers",
        max_length=25,
        choices=YES_NO,
        null=True,
        blank=False,
    )

    foot_ulcers_ago = edc_models.DurationYMDField(
        verbose_name="If yes, how long ago",
        null=True,
        blank=True,
    )

    foot_ulcers_estimated_date = models.DateField(
        verbose_name="Estimated date of foot ulcers",
        null=True,
        blank=True,
        editable=False,
    )
    #
    complications = models.CharField(
        verbose_name="Are there any other major complications to report?",
        max_length=25,
        choices=YES_NO,
        default=NO,
    )

    complications_other = models.TextField(
        null=True,
        blank=True,
        help_text="Please include dates",
    )

    def save(self, *args, **kwargs):
        complications = [
            "stroke",
            "heart_attack",
            "renal_disease",
            "vision",
            "numbness",
            "foot_ulcers",
        ]
        for complication in complications:
            setattr(
                self,
                f"{complication}_estimated_date",
                estimated_date_from_ago(self, f"{complication}_ago"),
            )
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        verbose_name = "Complications: Baseline"
        verbose_name_plural = "Complications: Baseline"


class ComplicationsFollowupMixin(models.Model):

    # stroke
    stroke = models.CharField(verbose_name="Stroke", max_length=25, choices=YES_NO)

    stroke_date = models.DateField(
        verbose_name="If yes, date",
        null=True,
        blank=True,
        help_text="If exact date not known, see SOP on how to estimate a date.",
    )

    # heart_attack
    heart_attack = models.CharField(
        verbose_name="Heart attack / heart failure",
        max_length=25,
        choices=YES_NO,
    )

    heart_attack_date = models.DateField(
        verbose_name="If yes, date",
        null=True,
        blank=True,
        help_text="If exact date not known, see SOP on how to estimate a date.",
    )

    # renal
    renal_disease = models.CharField(
        verbose_name="Renal (kidney) disease",
        max_length=25,
        choices=YES_NO,
    )

    renal_disease_date = models.DateField(
        verbose_name="If yes, date",
        null=True,
        blank=True,
        help_text="If exact date not known, see SOP on how to estimate a date.",
    )
    # vision
    vision = models.CharField(
        verbose_name="Vision problems (e.g. blurred vision)",
        max_length=25,
        choices=YES_NO,
    )

    vision_date = models.DateField(
        verbose_name="If yes, date",
        null=True,
        blank=True,
        help_text="If exact date not known, see SOP on how to estimate a date.",
    )

    # numbness
    numbness = models.CharField(
        verbose_name="Numbness / burning sensation",
        max_length=25,
        choices=YES_NO,
    )

    numbness_date = models.DateField(
        verbose_name="If yes, date",
        null=True,
        blank=True,
        help_text="If exact date not known, see SOP on how to estimate a date.",
    )

    # foot ulcers
    foot_ulcers = models.CharField(
        verbose_name="Foot ulcers",
        max_length=25,
        choices=YES_NO,
    )

    foot_ulcers_date = models.DateField(
        verbose_name="If yes, date",
        null=True,
        blank=True,
        help_text="If exact date not known, see SOP on how to estimate a date.",
    )
    #
    complications = models.CharField(
        verbose_name="Are there any other major complications to report?",
        max_length=25,
        choices=YES_NO,
        default=NO,
    )

    complications_other = models.TextField(
        null=True,
        blank=True,
        help_text="Please include dates",
    )

    class Meta:
        abstract = True
        verbose_name = "Complications: Followup"
        verbose_name_plural = "Complications: Followup"


class DrugRefillModelMixin(models.Model):

    rx_other = models.CharField(
        verbose_name="If other, please specify ...",
        max_length=150,
        null=True,
        blank=True,
    )

    rx_modified = models.CharField(
        verbose_name=(
            "Was the patient’s prescription changed "
            "at this visit compared with their prescription "
            "at the previous visit?"
        ),
        max_length=25,
        choices=YES_NO,
    )

    modifications = models.ManyToManyField(
        f"{settings.LIST_MODEL_APP_LABEL}.RxModifications",
        verbose_name="Which changes occurred?",
        blank=True,
    )

    modifications_other = models.CharField(
        verbose_name="If other, please specify ...",
        max_length=150,
        null=True,
        blank=True,
    )

    modifications_reason = models.ManyToManyField(
        f"{settings.LIST_MODEL_APP_LABEL}.RxModificationReasons",
        verbose_name="Why did the patient’s previous prescription change?",
        blank=True,
    )

    modifications_reason_other = models.CharField(
        verbose_name="If other, please specify ...",
        max_length=150,
        null=True,
        blank=True,
    )

    return_in_days = models.IntegerField(
        verbose_name=(
            "In how many days has the patient been asked "
            "to return to clinic for a drug refill?"
        )
    )

    class Meta:
        abstract = True


class HivMedicationsModelMixin(models.Model):
    refill_hiv = models.CharField(
        verbose_name="Is the patient filling / refilling HIV medications?",
        max_length=25,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
        help_text=(
            "Select `not applicable` if subject has not "
            "been diagnosed and prescribed medication for HIV infection."
        ),
    )

    class Meta:
        abstract = True


class HtnMedicationsModelMixin(models.Model):
    refill_htn = models.CharField(
        verbose_name="Is the patient filling / refilling Hypertension medications?",
        max_length=25,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
        help_text=(
            "Select `not applicable` if subject has not "
            "been diagnosed and prescribed medication for Hypertension."
        ),
    )

    class Meta:
        abstract = True


class DmMedicationsModelMixin(models.Model):
    refill_dm = models.CharField(
        verbose_name="Is the patient filling / refilling Diabetes medications?",
        max_length=25,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
        help_text=(
            "Select `not applicable` if subject has not "
            "been diagnosed and prescribed medication for Diabetes."
        ),
    )

    class Meta:
        abstract = True


class CholMedicationsModelMixin(models.Model):
    refill_chol = models.CharField(
        verbose_name="Is the patient filling / refilling Cholesterol medications?",
        max_length=25,
        choices=YES_NO_NA,
        default=NOT_APPLICABLE,
        help_text=(
            "Select `not applicable` if subject has not "
            "been diagnosed and prescribed medication for Cholesterol."
        ),
    )

    class Meta:
        abstract = True
