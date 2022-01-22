# -*- coding: utf-8 -*-


from django.db import models
from django.db.models.signals import post_save
from aparnik.contrib.users.models import PhoneField
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.text import Truncator

from aparnik.contrib.basemodels.models import BaseModel, BaseModelManager
from aparnik.contrib.notifications.models import Notification

User = get_user_model()


# Create your models here.
class ContactUsManager(BaseModelManager):
    def get_queryset(self):
        return super(ContactUsManager, self).get_queryset()

    def active(self):
        return self.get_queryset().filter(is_active=True)


class ContactUs(BaseModel):
    website = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Website')
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Address')
    )

    phone = PhoneField(
        mobile=True,
        blank=True,
        null=True,
        verbose_name=_('Phone Number')
    )

    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name=_('Email')
    )

    first_name = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_('First name')
    )

    last_name = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_('Last name')
    )

    title = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Title')
    )

    content = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Content'),
    )

    is_active = models.BooleanField(
        verbose_name=_('Is Active'),
        default=True
    )

    objects = ContactUsManager()

    def save(self, *args, **kwargs):

        return super(ContactUs, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(ContactUs, self).__init__(*args, **kwargs)

    def __str__(self):
        return '%s %s' % (self.id, self.title)

    class Meta:
        # ordering = ['latitude', 'longitude']
        verbose_name = _('Contact Us')
        verbose_name_plural = _('Contact Us')

    def get_api_uri(self):
        return reverse('aparnik-api:contactus:details', args=[self.id])

    def get_title(self):
        return self.title

    @property
    def fullname(self):
        """

        :return: fullname
        """
        return '{} {}'.format(self.first_name, self.last_name)


def post_save_constact_us_receiver(sender, instance, created, *args, **kwargs):
    if created:
        from .tasks import send_contact_us_message
        send_contact_us_message.delay(instance.pk)


post_save.connect(post_save_constact_us_receiver, sender=ContactUs)
