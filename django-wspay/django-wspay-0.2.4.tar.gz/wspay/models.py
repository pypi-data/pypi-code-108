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


class TransactionHistory(models.Model):
    payload = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Transaction(models.Model):
    request_uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    stan = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    approval_code = models.CharField(max_length=10)
    ws_pay_order_id = models.CharField(max_length=50)
    transaction_datetime = models.DateTimeField()
    authorized = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    voided = models.BooleanField(default=False)
    refunded = models.BooleanField(default=False)
    can_complete = models.BooleanField(default=False)
    can_void = models.BooleanField(default=False)
    can_refund = models.BooleanField(default=False)
    expiration_date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    history = models.ManyToManyField(to=TransactionHistory)


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
    transaction = models.OneToOneField(
        to=Transaction, null=True, blank=True, on_delete=models.PROTECT
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
