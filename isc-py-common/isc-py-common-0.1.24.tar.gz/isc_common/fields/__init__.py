from django.core import checks
from django.db import models


class Field(models.Field):
    def check(self, **kwargs):
        return [
            *super().check(**kwargs),
            *self._check_verbose_name(**kwargs),
        ]

    def _check_verbose_name(self, **kwargs):
        if self.verbose_name is None:
            return [
                checks.Error(
                    "Fields must define a 'verbose_name' attribute.",
                    obj=self,
                    id='fields.E120',
                )
            ]
        else:
            return []
