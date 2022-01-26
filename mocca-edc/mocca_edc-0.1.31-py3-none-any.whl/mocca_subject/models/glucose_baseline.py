from .glucose import Glucose


class GlucoseBaseline(Glucose):
    class Meta:
        proxy = True
        verbose_name = "Glucose: Baseline"
        verbose_name_plural = "Glucose: Baseline"
