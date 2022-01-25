import logging
import socket

import uuid

from django.db import models

log = logging.getLogger(__name__)


class Datum(models.Model):

    date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
        ordering = ['-last_modified']


class DeviceManager(models.Manager):
    def me(self):
        device, created = self.get_or_create(name=socket.gethostname())
        if created:
            log.info(f'created device {device}')
        else:
            log.debug(f'using device {device}')
        return device


class Device(models.Model):
    objects = DeviceManager()
    date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=40, unique=True)

    class Meta:
        db_table = 'device'
        ordering = ['-last_modified']

    def __str__(self):
        return self.name
