from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import pgettext_lazy
import uuid


class Log(models.Model):
    class Meta:
        verbose_name = pgettext_lazy('pxd-actions-tracker', 'Log entry')
        verbose_name_plural = pgettext_lazy('pxd-actions-tracker', 'Log entries')
        ordering = '-created_at', 'domain'

    id = models.UUIDField(
        verbose_name=pgettext_lazy('pxd-actions-tracker', 'ID'),
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    domain = models.CharField(
        verbose_name=pgettext_lazy('pxd-actions-tracker', 'Domain'),
        max_length=1024, null=False
    )
    tracking = ArrayField(
        models.CharField(max_length=128),
        verbose_name=pgettext_lazy('pxd-actions-tracker', 'Tracking codes stack'),
        null=False, blank=True, default=list,
    )
    message = models.TextField(
        verbose_name=pgettext_lazy('pxd-actions-tracker', 'Message'),
        null=False, blank=True, default=''
    )
    detail = models.JSONField(
        verbose_name=pgettext_lazy('pxd-actions-tracker', 'Detail'),
        null=False, blank=True, default=dict
    )

    created_at = models.DateTimeField(
        verbose_name=pgettext_lazy('pxd-actions-tracker', 'Created at'),
        null=False
    )

    def __str__(self):
        return f'Log #{self.id}: {self.message}'
