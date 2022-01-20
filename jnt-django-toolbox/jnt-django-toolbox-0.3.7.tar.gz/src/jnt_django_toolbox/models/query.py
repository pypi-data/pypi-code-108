from django.db import models


class SQCount(models.Subquery):
    """Count items of subquery."""

    template = "(SELECT count(*) FROM (%(subquery)s) _count)"  # noqa: WPS323
    output_field = models.IntegerField()
