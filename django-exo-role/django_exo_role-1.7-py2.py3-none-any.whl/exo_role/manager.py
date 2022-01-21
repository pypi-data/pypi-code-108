from django.db import models

from .queryset import ExORoleQueryset


class ExORoleManager(models.Manager):

    queryset_class = ExORoleQueryset

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)
