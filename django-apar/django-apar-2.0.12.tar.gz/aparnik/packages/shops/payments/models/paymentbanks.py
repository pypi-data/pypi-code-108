from azbankgateways.models import Bank
from django.db import models
from django.utils.translation import gettext_lazy as _

from .payments import Payment


class PaymentBank(models.Model):
    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        verbose_name=_('Payment')
    )
    bank_record = models.ForeignKey(
        Bank,
        on_delete=models.PROTECT,
        verbose_name=_('Bank record')
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    update_at = models.DateTimeField(auto_now=True, verbose_name=_('Update at'))

    class Meta:
        unique_together = [['bank_record']]
        verbose_name = _('Payment Bank')
        verbose_name_plural = _('Payments Bank')
