from datetime import datetime
from pprint import pprint
from typing import Optional

from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from edc_appointment.tests.appointment_test_case_mixin import AppointmentTestCaseMixin
from edc_constants.constants import FEMALE, NO, NOT_APPLICABLE, YES
from edc_facility.import_holidays import import_holidays
from edc_list_data.site_list_data import site_list_data
from edc_randomization.randomization_list_importer import RandomizationListImporter
from edc_randomization.site_randomizers import site_randomizers
from edc_sites import (
    add_or_update_django_sites,
    get_current_country,
    get_sites_by_country,
)
from edc_sites.tests.site_test_case_mixin import SiteTestCaseMixin
from edc_utils.date import get_utcnow
from edc_visit_schedule.constants import DAY1
from edc_visit_tracking.constants import SCHEDULED, UNSCHEDULED
from edc_visit_tracking.stubs import SubjectVisitModelStub
from model_bakery import baker

from mocca_consent.models import SubjectConsent
from mocca_screening.constants import NO_INTERRUPTION
from mocca_screening.forms import SubjectScreeningForm
from mocca_screening.import_mocca_register import import_mocca_register
from mocca_screening.mocca_original_sites import get_mocca_sites_by_country
from mocca_screening.models import MoccaRegister, SubjectScreening
from mocca_sites.sites import fqdn
from mocca_subject.models import SubjectVisit

User = get_user_model()


def age_in_years(birth_year: int) -> int:
    return datetime.now().year - birth_year


def login(testcase, user=None, superuser=None, groups=None):
    user = testcase.user if user is None else user
    superuser = True if superuser is None else superuser
    if not superuser:
        user.is_superuser = False
        user.is_active = True
        user.save()
        for group_name in groups:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
    form = testcase.app.get(reverse("home_url")).maybe_follow().form
    form["username"] = user.username
    form["password"] = "pass"
    return form.submit()


class MoccaTestCaseMixin(AppointmentTestCaseMixin, SiteTestCaseMixin):
    fqdn = fqdn

    default_sites = get_sites_by_country("uganda")

    site_names = [s.name for s in default_sites]

    import_randomization_list = True

    subject_visit_model_cls = SubjectVisit

    mocca_sites = []

    changelist_url_name = "mocca_screening_admin:mocca_screening_moccaregister_changelist"

    @classmethod
    def setUpTestData(cls):
        add_or_update_django_sites(sites=get_sites_by_country("uganda"))
        site_list_data.initialize()
        site_list_data.autodiscover()
        import_holidays(test=True)
        # GroupPermissionsUpdater(codenames_by_group=get_codenames_by_group(), verbose=True)
        if cls.import_randomization_list:
            randomizer_cls = site_randomizers.get("default")
            RandomizationListImporter(
                randomizer_cls=randomizer_cls, verbose=False, sid_count_for_tests=2
            )
        cls.mocca_sites = get_mocca_sites_by_country(country=get_current_country())
        import_mocca_register()

    def setUp(self):
        self.user = User.objects.create_superuser("user_login", "u@example.com", "pass")

    def login(self, **kwargs):
        return login(self, **kwargs)

    # def login(self, user=None, superuser=None, groups=None):
    #     user = self.user if user is None else user
    #     superuser = True if superuser is None else superuser
    #     if not superuser:
    #         user.is_superuser = False
    #         user.is_active = True
    #         user.save()
    #         for group_name in groups:
    #             group = Group.objects.get(name=group_name)
    #             user.groups.add(group)
    #     return self.client.force_login(user or self.user)

    def get_mocca_register(self, gender: str) -> MoccaRegister:
        mocca_study_identifiers = SubjectScreening.objects.values_list(
            "mocca_study_identifier", flat=True
        )
        return MoccaRegister.objects.filter(
            gender=gender or FEMALE, mocca_site__name__in=self.mocca_sites
        ).exclude(mocca_study_identifier__in=mocca_study_identifiers)[0]

    def get_subject_screening_form_data(
        self, mocca_register: Optional[MoccaRegister] = None, gender: Optional[str] = None
    ) -> dict:
        if not mocca_register:
            mocca_register = self.get_mocca_register(gender)

        return {
            "screening_consent": YES,
            "report_datetime": get_utcnow(),
            "mocca_participant": YES,
            "mocca_register": mocca_register,
            "mocca_site": str(mocca_register.mocca_site.id),
            "mocca_study_identifier": mocca_register.mocca_study_identifier,
            "initials": mocca_register.initials,
            "gender": mocca_register.gender,
            "birth_year": mocca_register.birth_year,
            "age_in_years": age_in_years(mocca_register.birth_year),
            "care": YES,
            "care_facility_location": YES,
            "icc_since_mocca": NO_INTERRUPTION,
            "icc": YES,
            "icc_not_in_reason": NOT_APPLICABLE,
            "unsuitable_for_study": NO,
            "unsuitable_agreed": NOT_APPLICABLE,
            "consent_ability": YES,
            "willing_to_consent": YES,
            "pregnant": NO if mocca_register.gender == FEMALE else NOT_APPLICABLE,
            "requires_acute_care": NO,
        }

    def get_subject_screening(
        self,
        report_datetime: Optional[datetime] = None,
        eligibility_datetime: Optional[datetime] = None,
        gender: Optional[str] = None,
        **kwargs
    ) -> SubjectScreening:
        data = self.get_subject_screening_form_data(gender=gender)
        data.update(report_datetime=report_datetime or get_utcnow(), **kwargs)
        form = SubjectScreeningForm(data=data, instance=None)
        form.is_valid()
        try:
            form.save()
        except ValueError:
            pprint(form._errors)
            raise

        subject_screening = SubjectScreening.objects.get(
            screening_identifier=form.instance.screening_identifier
        )

        self.assertTrue(subject_screening.eligible)

        if eligibility_datetime:
            subject_screening.eligibility_datetime = eligibility_datetime
            subject_screening.save()

        return subject_screening

    @staticmethod
    def get_subject_consent(subject_screening, consent_datetime=None, **kwargs):
        options = dict(
            user_created="erikvw",
            user_modified="erikvw",
            screening_identifier=subject_screening.screening_identifier,
            initials=subject_screening.initials,
            dob=get_utcnow().date() - relativedelta(years=subject_screening.age_in_years),
            site=subject_screening.site,
            consent_datetime=consent_datetime or get_utcnow(),
        )
        options.update(**kwargs)
        return baker.make_recipe("mocca_consent.subjectconsent", **options)

    def get_subject_visit(
        self,
        visit_code=None,
        visit_code_sequence=None,
        subject_screening=None,
        subject_consent=None,
        reason=None,
        appointment=None,
        appt_datetime=None,
    ):
        reason = reason or SCHEDULED
        if not appointment:
            subject_screening = subject_screening or self.get_subject_screening()
            subject_consent = subject_consent or self.get_subject_consent(subject_screening)
            appointment = self.get_appointment(
                subject_identifier=subject_consent.subject_identifier,
                visit_code=visit_code or DAY1,
                visit_code_sequence=(
                    visit_code_sequence if visit_code_sequence is not None else 0
                ),
                reason=reason,
                appt_datetime=appt_datetime,
            )
        return self.subject_visit_model_cls.objects.create(
            appointment=appointment, reason=reason
        )

    def get_next_subject_visit(
        self,
        subject_visit: SubjectVisitModelStub = None,
        reason=None,
        appt_datetime=None,
    ) -> SubjectVisitModelStub:
        visit_code = (
            subject_visit.appointment.visit_code
            if reason == UNSCHEDULED
            else subject_visit.appointment.next.visit_code
        )
        # visit_code_sequence will increment in get_subject_visit
        visit_code_sequence = (
            subject_visit.appointment.visit_code_sequence if reason == UNSCHEDULED else 0
        )
        return self.get_subject_visit(
            visit_code=visit_code,
            visit_code_sequence=visit_code_sequence,
            reason=reason,
            appt_datetime=appt_datetime,
            subject_screening=SubjectScreening.objects.get(
                subject_identifier=subject_visit.subject_identifier
            ),
            subject_consent=SubjectConsent.objects.get(
                subject_identifier=subject_visit.subject_identifier
            ),
        )
