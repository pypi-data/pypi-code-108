#
# Created on Tue Dec 21 2021
#
# Copyright (c) 2021 Lenders Cooperative, a division of Summit Technology Group, Inc.
#
import uuid

from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.db.models import JSONField, Q, UniqueConstraint
from django.utils.translation import ugettext_lazy as _
from django_lc_utils.mixins import SoftDeleteMixin
from model_utils.models import TimeStampedModel

from los_docusign.utils.validators import validate_file_extension

numeric = RegexValidator(r"^\d*$", "Numeric Values Required")


class DocuSignUserAuth(TimeStampedModel, SoftDeleteMixin):
    class Meta:
        db_table = "docusign_client_auths"
        verbose_name = "Docusign user authentication"
        verbose_name_plural = "Docusign user authentications"

    access_token = models.TextField("Access Token")
    expires_at = models.DateTimeField("Token Expires At")
    # organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE,unique=True)
    organization_model = models.ForeignKey(
        to="contenttypes.ContentType",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("Organization Model"),
    )
    organization_pk = models.CharField(
        max_length=255, verbose_name=_("organization pk")
    )
    two_factor_enabled_flag = models.BooleanField("Two Factor Enabled?", default=False)
    docusign_api_username = models.CharField("Docusign API Username", max_length=255)
    default_user = models.BooleanField("Default User?", max_length=255, default=False)

    def save(self, *args, **kwargs):
        # Do not allow more than 1 default user
        dsua = DocuSignUserAuth.objects.filter(default_user=True).exclude(id=self.id)
        if dsua.exists():
            self.default_user = False
        super().save(*args, **kwargs)

    def __str__(self):
        if self.default_user:
            return "Default Docusign User"
        else:
            return f"Docusign User for {self.organization_pk}"


def return_slug_for_url(instance, filename):
    return "loans/{0}/files/{1}".format(instance.slug, filename)
    # return 'docusign_signed_documents/{0}/files/{1}'.format(instance.slug, filename)


class DocusignEnvelopeStageData(TimeStampedModel, SoftDeleteMixin):
    class Meta:
        db_table = "docusign_envelope_stage_datas"
        verbose_name = "Docusign Envelope Stage Data"
        verbose_name_plural = "Docusign Envelope Stage Datas"

        constraints = [
            UniqueConstraint(
                fields=["object_pk", "content_type", "phase"],
                condition=Q(is_removed=False),
                name="unique_phase_content_type",
            ),
        ]

    slug = models.UUIDField(
        default=uuid.uuid4, blank=True, editable=False, db_index=True
    )
    envelope_id = models.CharField("Envelope ID", max_length=255, db_index=True)
    record_status = models.CharField("Record Status", max_length=255)
    envelope_status = models.CharField("Envelope Status", max_length=255)
    recipient_status = models.CharField(
        "Recipient Status", max_length=255, blank=True, default=None, null=True
    )
    signed_document = models.FileField(
        "Document",
        upload_to=return_slug_for_url,
        max_length=255,
        validators=[validate_file_extension],
        blank=True,
        null=True,
    )
    envelope_response = models.CharField("Envelope Response", max_length=255)
    error_message = models.CharField(
        "Error Message", max_length=255, blank=True, null=True
    )
    docusign_user = models.ForeignKey(
        "los_docusign.DocuSignUserAuth", on_delete=models.PROTECT
    )
    # etran_loan = models.ForeignKey("loans.EtranLoan",on_delete=models.CASCADE, blank=True, null=True, related_name='envelopes')
    client_user_id = models.CharField(
        "Client User Id", max_length=255, null=True, blank=True
    )
    recipient_auth_info = JSONField(
        "Recipient Authentication Info", null=True, blank=True
    )
    content_type = models.ForeignKey(
        to="contenttypes.ContentType",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("content type"),
    )
    object_pk = models.CharField(max_length=255, verbose_name=_("object pk"))
    phase = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_("Application Phase")
    )
    current_status = JSONField(
        "Current status of the envelope received from webhook",
        blank=True,
        null=True,
        encoder=DjangoJSONEncoder,
    )

    def __str__(self):
        if self.envelope_id:
            return self.envelope_id
        else:
            return str(self.id)

    @property
    def url(self):
        try:
            return self.signed_document.url
        except:
            return ""


class DocusignOrgTemplate(TimeStampedModel, SoftDeleteMixin):
    class Meta:
        db_table = "docusign_org_templates"
        verbose_name = "Docusign Organization Template"
        verbose_name_plural = "Docusign Organization Templates"

    organization_model = models.ForeignKey(
        to="contenttypes.ContentType",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("Organization Model"),
    )
    organization_pk = models.CharField(
        max_length=255, verbose_name=_("organization pk")
    )
    docusign_template = models.ForeignKey(
        "los_docusign.DocusignTemplate", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.organization_pk}-{self.docusign_template.template_type}"


class DocusignTemplateOrgExclusion(TimeStampedModel, SoftDeleteMixin):
    class Meta:
        db_table = "docusign_template_org_exclusions"
        verbose_name = "Docusign Organization Template Exclusion"
        verbose_name_plural = "Docusign Organization Template Exclusions"
        unique_together = ["organization_pk", "document_name", "template"]

    organization_model = models.ForeignKey(
        to="contenttypes.ContentType",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("Organization Model"),
    )
    organization_pk = models.CharField(
        max_length=255, verbose_name=_("organization pk")
    )
    document_name = models.ForeignKey(
        "los_docusign.DocusignChoiceConfig", on_delete=models.CASCADE
    )
    template = models.ForeignKey(
        "los_docusign.DocusignTemplate", on_delete=models.CASCADE
    )


class DocusignChoiceConfig(TimeStampedModel, SoftDeleteMixin):
    class Meta:
        db_table = "docusign_choice_configs"
        verbose_name = "Docusign Choice Config"
        verbose_name_plural = "Docusign Choice Configs"

    DOCUSIGN_TEMPLATE = "docusign_templates"
    DOCUSIGN_TEMPLATE_ORG_EXCLUSIONS = "docusign_template_org_exclulsions"

    MODEL_TYPE_CHOICES = (
        (DOCUSIGN_TEMPLATE, "docusign_templates"),
        (DOCUSIGN_TEMPLATE_ORG_EXCLUSIONS, "docusign_template_org_exclulsions"),
    )

    docusign_model = models.CharField(choices=MODEL_TYPE_CHOICES, max_length=128)
    config_key = models.CharField("Config Key", max_length=128)

    def __str__(self):
        return f"{self.docusign_model}-{self.config_key}"


class DocusignTemplate(TimeStampedModel, SoftDeleteMixin):
    class Meta:
        db_table = "docusign_templates"
        verbose_name = "Docusign Template"
        verbose_name_plural = "Docusign Templates"

    docusign_payload = models.TextField("Docusign Payload")
    # template_type = models.CharField("Template Type",max_length=32,choices=TEMPLATE_TYPE_CHOICES)
    template_type = models.ForeignKey(
        "los_docusign.DocusignChoiceConfig", on_delete=models.CASCADE
    )
    is_active = models.BooleanField("Is Active", default=True)
    is_default = models.BooleanField("Default Template", default=False)

    def save(self, *args, **kwargs):
        # Do not allow more than 1 default
        ds = DocusignTemplate.objects.filter(
            is_default=True, template_type=self.template_type
        ).exclude(id=self.id)
        if ds.exists():
            self.is_default = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.template_type.config_key


class DocusignOrgTemplateConfig(TimeStampedModel, SoftDeleteMixin):
    class Meta:
        db_table = "docusign_org_template_configs"
        verbose_name = "Docusign Organization Template Config"
        verbose_name_plural = "Docusign Organizations Templates Configs"
        unique_together = ["organization_pk", "template"]

    # organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE)
    organization_model = models.ForeignKey(
        to="contenttypes.ContentType",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("content type"),
    )
    organization_pk = models.CharField(
        db_index=True, max_length=255, verbose_name=_("object pk")
    )
    template_config = JSONField("Template Configuration")
    template = models.ForeignKey(
        "los_docusign.DocusignTemplate", on_delete=models.CASCADE
    )
    is_active = models.BooleanField("Is Active", default=True)
    is_default = models.BooleanField("Default Config", default=False)

    def save(self, *args, **kwargs):
        # Do not allow more than 1 default
        ds = DocusignOrgTemplateConfig.objects.filter(
            is_default=True, template=self.template
        ).exclude(id=self.id)
        if ds.exists():
            self.is_default = False
        super().save(*args, **kwargs)

    # def __str__(self):
    # return self.get_template_config_display()


class DocusignEnvelopeAuditLog(TimeStampedModel, SoftDeleteMixin):
    class Meta:
        db_table = "docusign_envelope_audit_log"
        verbose_name = "Docusign Envelope Audit Log"
        verbose_name_plural = "Docusign Envelopes Audits Logs"

    # etran_loan = models.ForeignKey('loans.EtranLoan',on_delete=models.SET_NULL, null=True)
    content_type = models.ForeignKey(
        to="contenttypes.ContentType",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("content type"),
    )
    object_pk = models.CharField(
        db_index=True, max_length=255, verbose_name=_("object pk")
    )
    event_received_at = models.DateTimeField(null=True, blank=True)
    envelope_id = models.CharField("Envelope ID", max_length=255)
    event_type = models.CharField(max_length=125, null=True, blank=True, db_index=True)
    event_value = models.CharField(max_length=125, null=True, blank=True, db_index=True)
    tin = models.CharField(
        "TIN",
        max_length=9,
        null=True,
        blank=True,
        db_index=True,
        validators=[
            MinLengthValidator(9, message="Business TIN must be 9 digits"),
            numeric,
        ],
    )
    remote_addr = models.GenericIPAddressField(
        blank=True, null=True, verbose_name=("remote address")
    )

    def __str__(self):
        return self.content_type + str(self.tin)

    # def set_tin(self):
    #    if self.etran_loan:
    #        self.tin = self.etran_loan.ein

    # event_type -> CALLBACK_URL, WEBHOOK
    # event_value (CALLBACK_URL)-> cancel, id_check_failed, completed, decline
    # event_value (WEBHOOK)-> completed, decline, authentication_failed
    # For repeated failing KBA
    # Add property to grant has_received_docusign_callback
    # 1. Create Envelope -> Fails (No entry in the database)
    # 2. Generate URL for signing
    #     -> error_response
    #     -> docusign_envelope_stage_data
    # In case of KBA Failure, if we don't receive the webhook notificaiton
    # -> We will get call back failure for KBA failed
    #   -> Increment docusign kba failure count in the table
    #   -> 3
    # -> Reset the application to Applicant Correction
    # -> Delete the existing envelope
