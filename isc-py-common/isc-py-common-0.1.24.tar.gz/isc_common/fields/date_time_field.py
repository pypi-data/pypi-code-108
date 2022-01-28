from django.db import models


class DateTimeField(models.DateTimeField):
    def to_python(self, value):
        return super().to_python(value)
