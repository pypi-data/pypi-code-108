from enum import Enum
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class WSPayRequestStatus(Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    FAILED = 'failed'

    @classmethod
    def choices(cls):
        return [(x.name, x.value) for x in cls]


class WSPayTransaction(models.Model):
    payload = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class WSPayRequest(models.Model):
    cart_id = models.PositiveIntegerField()
    status = models.CharField(
        max_length=15, choices=WSPayRequestStatus.choices(),
        default=WSPayRequestStatus.PENDING.name
    )
    request_uuid = models.UUIDField(default=uuid.uuid4)
    response = models.TextField(null=True, blank=False)
    additional_data = models.TextField(
        null=False,
        blank=True,
        help_text=_('Use this to store any data you want to preserve when making a request')
    )
    transactions = models.ManyToManyField(to=WSPayTransaction)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
