from uuid import uuid4
from django.db import models
from django.utils.translation import pgettext_lazy
from django.conf import settings

from .query import UploadQuerySet
from .conf import settings

__all__ = 'Upload',


class Upload(models.Model):
    objects: models.Manager[UploadQuerySet] = (
        UploadQuerySet.as_manager()
    )

    class Meta:
        verbose_name = pgettext_lazy('pxd_upload', 'Upload')
        verbose_name_plural = pgettext_lazy(
            'pxd_upload', 'Uploads'
        )

    id = models.UUIDField(
        primary_key=True, default=uuid4, blank=True,
        verbose_name=pgettext_lazy('pxd_upload', 'ID'),
    )
    title = models.TextField(
        verbose_name=pgettext_lazy('pxd_upload', 'Title'),
        null=False, blank=True
    )

    file = models.FileField(
        verbose_name=pgettext_lazy('pxd_upload', 'File'),
        upload_to=settings.TO, null=False, blank=False
    )
    meta = models.JSONField(
        verbose_name=pgettext_lazy('pxd_upload', 'Metadata'),
        default=dict, null=False, blank=True
    )

    created_at = models.DateTimeField(
        verbose_name=pgettext_lazy('pxd_upload', 'Created at'),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name=pgettext_lazy('pxd_upload', 'Update at'), auto_now=True,
    )

    def __str__(self):
        return self.title or str(self.id)
