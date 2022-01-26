from .glucose import Glucose


class GlucoseFollowup(Glucose):
    class Meta:
        proxy = True
        verbose_name = "Glucose: Followup"
        verbose_name_plural = "Glucose: Followup"
