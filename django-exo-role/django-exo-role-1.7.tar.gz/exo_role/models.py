from django.db import models

from model_utils.models import TimeStampedModel

from .manager import ExORoleManager
from .conf import settings  # noqa


class Category(TimeStampedModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=2, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def num_roles(self):
        return self.roles.count()


class ExORole(TimeStampedModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True)
    categories = models.ManyToManyField('Category', related_name='roles')
    description = models.TextField(blank=True, null=True)

    objects = ExORoleManager()

    class Meta:
        ordering = ['name']
        verbose_name = 'ExORole'
        verbose_name_plural = 'ExORoles'

    def __str__(self):
        return '{} - {}'.format(self.categories.first().name, self.name)


class CertificationRole(TimeStampedModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True)
    level = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'CertificationRole'
        verbose_name_plural = 'CertificationRoles'

    def __str__(self):
        return self.name
