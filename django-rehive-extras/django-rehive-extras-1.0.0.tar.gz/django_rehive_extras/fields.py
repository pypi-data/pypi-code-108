from django.db import models


class MoneyField(models.DecimalField):
    """
    Decimal Field for money values.
    """

    def __init__(self, verbose_name=None, name=None, max_digits=30,
            decimal_places=18, **kwargs):
        super().__init__(
            verbose_name,
            name,
            max_digits,
            decimal_places,
            **kwargs
        )
