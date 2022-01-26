from django.core.exceptions import ValidationError
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from edc_randomization.site_randomizers import site_randomizers
from edc_screening.utils import get_subject_screening_model_cls
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.utils import get_subject_visit_model

from .subject_consent import SubjectConsent


def get_onschedule_model_name(instance):
    onschedule_model_name = "mocca_prn.onschedule"
    return onschedule_model_name


@receiver(
    post_save,
    weak=False,
    sender=SubjectConsent,
    dispatch_uid="subject_consent_on_post_save",
)
def subject_consent_on_post_save(sender, instance, raw, created, **kwargs):
    """Creates an onschedule instance for this consented subject, if
    it does not exist.
    """
    if not raw:
        if not created:
            _, schedule = site_visit_schedules.get_by_onschedule_model(
                get_onschedule_model_name(instance)
            )
            schedule.refresh_schedule(subject_identifier=instance.subject_identifier)
        else:
            subject_screening = get_subject_screening_model_cls().objects.get(
                screening_identifier=instance.screening_identifier
            )
            subject_screening.subject_identifier = instance.subject_identifier
            subject_screening.consented = True
            subject_screening.save_base(update_fields=["subject_identifier", "consented"])

            # randomize
            # TODO: should get randomizer name "default" from model or Consent object
            site_randomizers.randomize(
                "default",
                subject_identifier=instance.subject_identifier,
                report_datetime=instance.consent_datetime,
                site=instance.site,
                user=instance.user_created,
            )

            # put subject on primary schedule
            _, schedule = site_visit_schedules.get_by_onschedule_model(
                get_onschedule_model_name(instance)
            )
            schedule.put_on_schedule(
                subject_identifier=instance.subject_identifier,
                onschedule_datetime=instance.consent_datetime,
            )


@receiver(
    post_delete,
    weak=False,
    sender=SubjectConsent,
    dispatch_uid="subject_consent_on_post_delete",
)
def subject_consent_on_post_delete(sender, instance, using, **kwargs):
    """Updates/Resets subject screening."""
    # don't allow if subject visits exist. This should be caught
    # in the ModelAdmin delete view
    subject_visit_model_cls = get_subject_visit_model()
    if subject_visit_model_cls.objects.filter(
        subject_identifier=instance.subject_identifier
    ).exists():
        raise ValidationError("Unable to delete consent. Visit data exists.")

    _, schedule = site_visit_schedules.get_by_onschedule_model(
        get_onschedule_model_name(instance)
    )
    schedule.take_off_schedule(
        subject_identifier=instance.subject_identifier,
        offschedule_datetime=instance.consent_datetime,
    )

    # update subject screening
    subject_screening = get_subject_screening_model_cls().objects.get(
        screening_identifier=instance.screening_identifier
    )
    subject_screening.consented = False
    subject_screening.subject_identifier = subject_screening.subject_screening_as_pk
    subject_screening.save()
