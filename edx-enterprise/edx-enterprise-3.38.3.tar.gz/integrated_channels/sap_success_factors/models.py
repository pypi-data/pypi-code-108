"""
Database models for Enterprise Integrated Channel SAP SuccessFactors.
"""

import json
from logging import getLogger

from config_models.models import ConfigurationModel

from django.db import models
from django.utils.translation import ugettext_lazy as _

from integrated_channels.exceptions import ClientError
from integrated_channels.integrated_channel.models import EnterpriseCustomerPluginConfiguration
from integrated_channels.sap_success_factors.exporters.content_metadata import SapSuccessFactorsContentMetadataExporter
from integrated_channels.sap_success_factors.exporters.learner_data import (
    SapSuccessFactorsLearnerExporter,
    SapSuccessFactorsLearnerManger,
)
from integrated_channels.sap_success_factors.transmitters.content_metadata import (
    SapSuccessFactorsContentMetadataTransmitter,
)
from integrated_channels.sap_success_factors.transmitters.learner_data import SapSuccessFactorsLearnerTransmitter
from integrated_channels.utils import convert_comma_separated_string_to_list

LOGGER = getLogger(__name__)


class SAPSuccessFactorsGlobalConfiguration(ConfigurationModel):
    """
    The global configuration for integrating with SuccessFactors.

    .. no_pii:
    """

    completion_status_api_path = models.CharField(max_length=255)
    course_api_path = models.CharField(max_length=255)
    oauth_api_path = models.CharField(max_length=255)
    search_student_api_path = models.CharField(max_length=255)
    provider_id = models.CharField(max_length=100, default='EDX')

    class Meta:
        app_label = 'sap_success_factors'

    def __str__(self):
        """
        Return a human-readable string representation of the object.
        """
        return "<SAPSuccessFactorsGlobalConfiguration with id {id}>".format(id=self.id)

    def __repr__(self):
        """
        Return uniquely identifying string representation.
        """
        return self.__str__()


class SAPSuccessFactorsEnterpriseCustomerConfiguration(EnterpriseCustomerPluginConfiguration):
    """
    The Enterprise-specific configuration we need for integrating with SuccessFactors.

    .. no_pii:
    """

    USER_TYPE_USER = 'user'
    USER_TYPE_ADMIN = 'admin'

    USER_TYPE_CHOICES = (
        (USER_TYPE_USER, 'User'),
        (USER_TYPE_ADMIN, 'Admin'),
    )

    key = models.CharField(
        max_length=255,
        verbose_name="Client ID",
        help_text=_("OAuth client identifier.")
    )
    sapsf_base_url = models.CharField(
        max_length=255,
        verbose_name="SAP Base URL",
        help_text=_("Base URL of success factors API.")
    )
    sapsf_company_id = models.CharField(
        max_length=255, verbose_name="SAP Company ID", help_text=_("Success factors company identifier.")
    )
    sapsf_user_id = models.CharField(
        max_length=255,
        verbose_name="SAP User ID",
        help_text=_("Success factors user identifier.")
    )
    secret = models.CharField(
        max_length=255,
        verbose_name="Client Secret",
        help_text=_("OAuth client secret.")
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default=USER_TYPE_USER,
        verbose_name="SAP User Type",
        help_text=_("Type of SAP User (admin or user).")
    )
    additional_locales = models.TextField(
        blank=True,
        default='',
        verbose_name="Additional Locales",
        help_text=_("A comma-separated list of additional locales.")
    )
    show_course_price = models.BooleanField(default=False)
    transmit_total_hours = models.BooleanField(
        default=False,
        verbose_name=_("Transmit Total Hours"),
        help_text=_("Include totalHours in the transmitted completion data")
    )
    prevent_self_submit_grades = models.BooleanField(
        default=False,
        verbose_name="Prevent Learner From Self-Submitting Grades",
        help_text=_("When set to True, the integration will use the "
                    "generic edX service user ('sapsf_user_id') "
                    "defined in the SAP Customer Configuration for course completion.")
    )

    # overriding base model field, to use chunk size 1 default
    transmission_chunk_size = models.IntegerField(
        default=1,
        help_text=(
            _("The maximum number of data items to transmit to the integrated channel "
              "with each request.")
        )
    )

    def get_locales(self, default_locale=None):
        """
        Get the list of all(default + additional) locales

        Args:
            default_locale (str): Value of the default locale

        Returns:
            list: available locales
        """
        locales = []

        if default_locale is None:
            locales.append('English')
        else:
            locales.append(default_locale)

        return set(
            locales + convert_comma_separated_string_to_list(self.additional_locales)
        )

    class Meta:
        app_label = 'sap_success_factors'

    def __str__(self):
        """
        Return human-readable string representation.
        """
        return "<SAPSuccessFactorsEnterpriseCustomerConfiguration for Enterprise {enterprise_name}>".format(
            enterprise_name=self.enterprise_customer.name
        )

    def __repr__(self):
        """
        Return uniquely identifying string representation.
        """
        return self.__str__()

    @staticmethod
    def channel_code():
        """
        Returns an capitalized identifier for this channel class, unique among subclasses.
        """
        return 'SAP'

    @property
    def provider_id(self):
        '''
        Fetch ``provider_id`` from global configuration settings
        '''
        return SAPSuccessFactorsGlobalConfiguration.current().provider_id

    def get_learner_data_transmitter(self):
        """
        Return a ``SapSuccessFactorsLearnerTransmitter`` instance.
        """
        return SapSuccessFactorsLearnerTransmitter(self)

    def get_learner_data_exporter(self, user):
        """
        Return a ``SapSuccessFactorsLearnerDataExporter`` instance.
        """
        return SapSuccessFactorsLearnerExporter(user, self)

    def get_content_metadata_transmitter(self):
        """
        Return a ``SapSuccessFactorsContentMetadataTransmitter`` instance.
        """
        return SapSuccessFactorsContentMetadataTransmitter(self)

    def get_content_metadata_exporter(self, user):
        """
        Return a ``SapSuccessFactorsContentMetadataExporter`` instance.
        """
        return SapSuccessFactorsContentMetadataExporter(user, self)

    def get_learner_manger(self):
        """
        Return a ``SapSuccessFactorsLearnerManger`` instance.
        """
        return SapSuccessFactorsLearnerManger(self)

    def unlink_inactive_learners(self):
        """
        Unlink inactive SAP learners form their related enterprises
        """
        sap_learner_manager = self.get_learner_manger()
        try:
            sap_learner_manager.unlink_learners()
        except ClientError as exc:
            LOGGER.exception(
                'Failed to unlink learners for integrated channel [%s] [%s] \nError: [%s]',
                self.enterprise_customer.name,
                self.channel_code(),
                str(exc)
            )


class SapSuccessFactorsLearnerDataTransmissionAudit(models.Model):
    """
    The payload we sent to SuccessFactors at a given point in time for an enterprise course enrollment.

    .. no_pii:
    """

    sapsf_user_id = models.CharField(max_length=255, blank=False, null=False)
    enterprise_course_enrollment_id = models.PositiveIntegerField(blank=False, null=False, db_index=True)
    course_id = models.CharField(max_length=255, blank=False, null=False)
    course_completed = models.BooleanField(default=True)
    instructor_name = models.CharField(max_length=255, blank=True)
    grade = models.CharField(max_length=100, blank=False, null=False)
    total_hours = models.FloatField(null=True, blank=True)
    credit_hours = models.FloatField(null=True, blank=True)

    # We send a UNIX timestamp to SAPSF.
    completed_timestamp = models.BigIntegerField()

    # Request-related information.
    status = models.CharField(max_length=100, blank=False, null=False)
    error_message = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'sap_success_factors'

    def __str__(self):
        """
        Return a human-readable string representation of the object.
        """
        return (
            '<SapSuccessFactorsLearnerDataTransmissionAudit {transmission_id} for enterprise enrollment '
            '{enterprise_course_enrollment_id}, SAPSF user {sapsf_user_id}, and course {course_id}>'.format(
                transmission_id=self.id,
                enterprise_course_enrollment_id=self.enterprise_course_enrollment_id,
                sapsf_user_id=self.sapsf_user_id,
                course_id=self.course_id
            )
        )

    def __repr__(self):
        """
        Return uniquely identifying string representation.
        """
        return self.__str__()

    @property
    def provider_id(self):
        """
        Fetch ``provider_id`` from global configuration settings
        """
        return SAPSuccessFactorsGlobalConfiguration.current().provider_id

    def serialize(self, *args, **kwargs):
        """
        Return a JSON-serialized representation.

        Sort the keys so the result is consistent and testable.

        # TODO: When we refactor to use a serialization flow consistent with how course metadata
        # is serialized, remove the serialization here and make the learner data exporter handle the work.
        """
        return json.dumps(self._payload_data(), sort_keys=True)

    def _payload_data(self):
        """
        Convert the audit record's fields into SAP SuccessFactors key/value pairs.
        """
        return dict(
            userID=self.sapsf_user_id,
            courseID=self.course_id,
            providerID=self.provider_id,
            courseCompleted="true" if self.course_completed else "false",
            completedTimestamp=self.completed_timestamp,
            grade=self.grade,
            totalHours=self.total_hours,
            creditHours=self.credit_hours,
        )
