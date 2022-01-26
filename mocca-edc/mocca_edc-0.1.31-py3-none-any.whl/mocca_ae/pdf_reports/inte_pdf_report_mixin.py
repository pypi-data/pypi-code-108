from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist


class InteCrfReportMixin:
    weight_model = "mocca_subject.followup"

    @property
    def unblinded(self):
        unblinding_request_model_cls = django_apps.get_model("mocca_prn.unblindingrequest")
        try:
            unblinded = unblinding_request_model_cls.objects.get(
                subject_identifier=self.subject_identifier, approved=True
            )
        except ObjectDoesNotExist:
            unblinded = False
        return unblinded
