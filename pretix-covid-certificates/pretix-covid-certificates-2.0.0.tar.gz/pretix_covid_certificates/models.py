from django.db import models
from pretix.base.models import LoggedModel


class CovidCertificateExpiry(LoggedModel):
    answer = models.ForeignKey(
        "pretixbase.QuestionAnswer",
        on_delete=models.CASCADE,
        related_name="CovidCertificateExpiry",
    )

    expiry = models.DateTimeField(db_index=True)
