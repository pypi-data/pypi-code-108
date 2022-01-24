from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from model_utils.models import TimeStampedModel

from openlxp_notifications.management.utils.notification import \
    email_verification


class ReceiverEmailConfiguration(TimeStampedModel):
    """Model for Receiver Email Configuration """

    email_address = models.EmailField(
        max_length=254,
        help_text='Enter email personas addresses to send log data',
        unique=True)

    def get_absolute_url(self):
        """ URL for displaying individual model records."""
        return reverse('Configuration-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id}'

    def save(self, *args, **kwargs):
        email_verification(self.email_address)
        return super(ReceiverEmailConfiguration, self).save(*args, **kwargs)


class SenderEmailConfiguration(TimeStampedModel):
    """Model for Sender Email Configuration """

    sender_email_address = models.EmailField(
        max_length=254,
        help_text='Enter sender email address to send log data from')

    def save(self, *args, **kwargs):
        if not self.pk and SenderEmailConfiguration.objects.exists():
            raise ValidationError('There is can be only one '
                                  'SenderEmailConfiguration instance')
        return super(SenderEmailConfiguration, self).save(*args, **kwargs)


class EmailConfiguration(TimeStampedModel):
    """Model for Email Configuration """

    LOG_TYPE_CHOICES = (
        ('attachment', 'ATTACHMENT'),
        ('message', 'MESSAGE'),
    )

    Subject = models.CharField(max_length=200,
                               default='OpenLXP Conformance Alerts')

    Email_Content = models.TextField(max_length=200, null=True, blank=True)

    Signature = models.TextField(max_length=200)

    Email_Us = models.EmailField(max_length=254,
                                 help_text='Enter email address')

    FAQ_URL = models.CharField(max_length=200)

    Unsubscribe_Email_ID = models.EmailField(max_length=254,
                                             help_text='Enter email address')
    Logs_Type = models.CharField(max_length=200, choices=LOG_TYPE_CHOICES,
                                 help_text='Check readme files of the '
                                           'components before choosing the '
                                           ' log type')

    HTML_File = models.FileField(upload_to='HTML_Files',
                                 help_text='Check sample HTML files in the '
                                           'readme files of the components')

    def get_absolute_url(self):
        """ URL for displaying individual model records."""
        return reverse('Configuration-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id}'

    def save(self, *args, **kwargs):
        if not self.pk and EmailConfiguration.objects.exists():
            raise ValidationError('There is can be only one '
                                  'EmailConfiguration instance')
        return super(EmailConfiguration, self).save(*args, **kwargs)
