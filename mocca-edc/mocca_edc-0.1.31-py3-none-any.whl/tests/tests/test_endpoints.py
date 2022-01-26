import sys
from unittest import skip

from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.color import color_style
from django.test import TestCase
from django.test.utils import override_settings
from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch
from edc_adverse_event.auth_objects import TMG
from edc_appointment.constants import IN_PROGRESS_APPT, SCHEDULED_APPT
from edc_appointment.models import Appointment
from edc_auth.auth_objects import AUDITOR, CLINIC, EVERYONE, PII
from edc_dashboard.url_names import url_names
from edc_export.auth_objects import EXPORT
from edc_lab.auth_objects import LAB
from edc_sites import add_or_update_django_sites, get_sites_by_country
from edc_utils import get_utcnow
from model_bakery import baker

from mocca_screening.models.subject_screening import SubjectScreening

from ..mocca_test_case_mixin import MoccaTestCaseMixin

style = color_style()

User = get_user_model()

app_prefix = "mocca"


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
    return testcase.client.force_login(user or testcase.user)


@skip
@override_settings(SIMPLE_HISTORY_PERMISSIONS_ENABLED=True)
class AdminSiteTest(MoccaTestCaseMixin, TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser("user_login", "u@example.com", "pass")

    def test_ae(self):
        self.login(superuser=False, groups=[EVERYONE, AUDITOR])
        response = self.client.get(reverse("mocca_ae:home_url"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("edc_adverse_event:ae_home_url"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("edc_adverse_event:tmg_home_url"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("edc_data_manager:home_url"))
        self.assertEqual(response.status_code, 200)

    def test_home_everyone(self):
        self.login(superuser=False, groups=[EVERYONE])
        response = self.client.get(reverse("home_url"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Screening")
        self.assertNotContains(response, "Subjects")
        self.assertNotContains(response, "Specimens")
        self.assertNotContains(response, "Adverse&nbsp;events")
        self.assertNotContains(response, "TMG&nbsp;reports")
        self.assertNotContains(response, "Pharmacy")
        self.assertNotContains(response, "Action&nbsp;items")
        self.assertNotContains(response, "Export&nbsp;data")
        self.assertNotContains(response, "Synchronization")

        self.assertContains(response, "Switch&nbsp;sites")
        self.assertContains(response, "Log&nbsp;out")

    def test_home_auditor(self):
        self.login(superuser=False, groups=[EVERYONE, AUDITOR])
        response = self.client.get(reverse("home_url"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Screening")
        self.assertContains(response, "Subjects")
        self.assertContains(response, "Specimens")
        self.assertContains(response, "Adverse&nbsp;events")
        self.assertContains(response, "TMG&nbsp;reports")

        self.assertNotContains(response, "Pharmacy")

        self.assertContains(response, "Action&nbsp;items")

        self.assertNotContains(response, "Export&nbsp;data")
        self.assertNotContains(response, "Synchronization")

        self.assertContains(response, "Switch&nbsp;sites")
        self.assertContains(response, "Log&nbsp;out")

    def test_home_clinic(self):
        self.login(superuser=False, groups=[EVERYONE, CLINIC, PII])
        response = self.client.get(reverse("home_url"))
        self.assertContains(response, "Screening")
        self.assertContains(response, "Subjects")
        self.assertContains(response, "Specimens")
        self.assertContains(response, "Adverse&nbsp;events")
        self.assertContains(response, "TMG&nbsp;reports")
        self.assertNotContains(response, "Pharmacy")

        self.assertContains(response, "Action&nbsp;items")

        self.assertNotContains(response, "Export&nbsp;data")
        self.assertNotContains(response, "Synchronization")

        self.assertContains(response, "Switch&nbsp;sites")
        self.assertContains(response, "Log&nbsp;out")

    def test_home_export(self):
        self.login(superuser=False, groups=[EVERYONE, EXPORT])
        response = self.client.get(reverse("home_url"))
        self.assertNotContains(response, "Screening")
        self.assertNotContains(response, "Subjects")
        self.assertNotContains(response, "Specimens")
        self.assertNotContains(response, "Adverse&nbsp;events")
        self.assertNotContains(response, "TMG&nbsp;reports")
        self.assertNotContains(response, "Pharmacy")
        self.assertContains(response, "Action&nbsp;items")
        self.assertContains(response, "Export&nbsp;data")
        self.assertNotContains(response, "Synchronization")
        self.assertContains(response, "Switch&nbsp;sites")
        self.assertContains(response, "Log&nbsp;out")

    def test_home_tmg(self):
        self.login(superuser=False, groups=[EVERYONE, TMG])
        response = self.client.get(reverse("home_url"))

        self.assertContains(response, "Screening")
        self.assertContains(response, "Subjects")
        self.assertNotContains(response, "Specimens")
        self.assertContains(response, "Adverse&nbsp;events")
        self.assertContains(response, "TMG&nbsp;reports")
        self.assertNotContains(response, "Pharmacy")
        self.assertContains(response, "Action&nbsp;items")
        self.assertNotContains(response, "Export&nbsp;data")
        self.assertNotContains(response, "Synchronization")
        self.assertContains(response, "Switch&nbsp;sites")
        self.assertContains(response, "Log&nbsp;out")

    def test_home_lab(self):
        self.login(superuser=False, groups=[EVERYONE, LAB])
        response = self.client.get(reverse("home_url"))

        self.assertContains(response, "Screening")
        self.assertContains(response, "Subjects")
        self.assertContains(response, "Specimens")
        self.assertNotContains(response, "Adverse&nbsp;events")
        self.assertNotContains(response, "TMG&nbsp;reports")
        self.assertNotContains(response, "Pharmacy")
        self.assertNotContains(response, "Action&nbsp;items")
        self.assertNotContains(response, "Export&nbsp;data")
        self.assertNotContains(response, "Synchronization")
        self.assertContains(response, "Switch&nbsp;sites")
        self.assertContains(response, "Log&nbsp;out")

    def test_screening_no_pii(self):
        self.login(superuser=False, groups=[EVERYONE, CLINIC])
        home_page = self.client.get(reverse("home_url"))
        screening_page = home_page.click(description="Screening", index=1)
        self.assertNotIn("Add SubjectScreening", screening_page)

    def test_screening_form(self):
        subject_screening = baker.prepare_recipe(f"{app_prefix}_screening.subjectscreening")
        self.login(superuser=False, groups=[EVERYONE, CLINIC, PII])

        home_page = self.client.get(reverse("home_url"))
        screening_listboard_page = home_page.click(description="Screening", index=1)
        add_screening_page = screening_listboard_page.click(
            description="Add Subject Screening"
        )

        # submit blank form
        response = add_screening_page.form.submit()
        self.assertIn("Please correct the errors below", response)

        # submit completed form
        for field, _ in add_screening_page.form.fields.items():
            try:
                add_screening_page.form[field] = getattr(subject_screening, field)
            except AttributeError:
                pass
        page = add_screening_page.form.submit()

        # redirects back to listboard
        self.assertRedirects(page, reverse("mocca_dashboard:screening_listboard_url"))

        # new screened subject is available
        obj = SubjectScreening.objects.all().last()
        screening_listboard_page = home_page.click(description="Screening", index=1)
        self.assertIn(obj.screening_identifier, screening_listboard_page)

        add_subjectconsent_page = screening_listboard_page.click(
            description="Consent", index=1
        )

        self.assertEqual(add_subjectconsent_page.status_code, 200)

    def test_to_subject_dashboard(self):
        add_or_update_django_sites(apps=django_apps, sites=get_sites_by_country("uganda"))
        self.login(superuser=False, groups=[EVERYONE, CLINIC, PII])
        subject_screening = self.get_subject_screening()
        home_page = self.client.get(reverse("home_url"))
        screening_listboard_page = home_page.click(description="Screening", index=1)
        add_subjectconsent_page = screening_listboard_page.click(
            description="Consent", index=1
        )
        # submit blank form
        response = add_subjectconsent_page.form.submit()
        self.assertIn("Please correct the errors below", response)

        subject_consent = baker.make_recipe(
            "mocca_subject.subjectconsent",
            screening_identifier=subject_screening.screening_identifier,
            dob=(get_utcnow() - relativedelta(years=subject_screening.age_in_years)).date(),
            first_name="Melissa",
            last_name="Rodriguez",
            initials="MR",
            consent_datetime=get_utcnow(),
        )

        home_page = self.client.get(reverse("home_url"), user=self.user, status=200)
        screening_listboard_page = home_page.click(description="Screening", index=1)

        self.assertIn("Dashboard", screening_listboard_page)
        self.assertIn(
            f"subjectscreening_change_{subject_screening.screening_identifier}",
            screening_listboard_page,
        )

        home_page = self.client.get(reverse("home_url"), user=self.user, status=200)
        subject_listboard_page = home_page.click(description="Subjects", index=1)

        self.assertIn(subject_consent.subject_identifier, subject_listboard_page)

        href = reverse(
            "mocca_dashboard:subject_dashboard_url",
            kwargs={"subject_identifier": subject_consent.subject_identifier},
        )
        subject_dashboard_page = subject_listboard_page.click(href=href)

        self.assertEqual(subject_dashboard_page.status_code, 200)

        # on subject_dashboard
        # assert all appointment are showing
        subject_identifier = subject_consent.subject_identifier
        appointments = Appointment.objects.filter(
            subject_identifier=subject_identifier
        ).order_by("appt_datetime")
        for appointment in appointments:
            self.assertIn(appointment.visit_code, subject_dashboard_page)

        # start appointment 1000
        page = subject_dashboard_page.click(linkid="start_btn_1000")
        page.form["appt_status"] = IN_PROGRESS_APPT
        page.form["appt_reason"] = SCHEDULED_APPT
        subject_dashboard_page = page.form.submit()
        self.assertEqual(subject_dashboard_page.status_code, 302)
        self.assertEqual(
            subject_dashboard_page.url,
            f"/subject/subject_dashboard/{subject_identifier}/",
        )

        subject_dashboard_page = self.client.get(
            subject_dashboard_page.url, user=self.user, status=200
        )

        # start visit 1000
        self.assertIn(" Start ", subject_dashboard_page)
        subject_visit_page = subject_dashboard_page.click(
            linkid=(
                f"start_btn_{appointments[0].visit_code}_"
                f"{appointments[0].visit_code_sequence}"
            )
        )
        subject_visit_page.form["info_source"] = "patient"
        subject_dashboard_page = subject_visit_page.form.submit()

        url = f"/subject/subject_dashboard/{subject_identifier}/" f"{str(appointments[0].pk)}/"
        self.assertEqual(subject_dashboard_page.status_code, 302)
        self.assertEqual(subject_dashboard_page.url, url)

        subject_dashboard_page = self.client.get(
            reverse(
                "mocca_dashboard:subject_dashboard_url",
                kwargs=dict(
                    subject_identifier=subject_identifier,
                    appointment=str(appointments[0].id),
                ),
            ),
            user=self.user,
            status=200,
        )

        self.assertIn("CRFs", subject_dashboard_page)
        self.assertIn("Requisitions", subject_dashboard_page)

    def test_follow_urls(self):
        """Follows any url that can be reversed without kwargs."""
        self.login(superuser=False, groups=[EVERYONE, CLINIC, PII])
        for url_name in url_names.registry.values():
            sys.stdout.write(style.MIGRATE_HEADING(f" - '{url_name}' ...\r"))
            try:
                url = reverse(url_name)
            except NoReverseMatch:
                sys.stdout.write(
                    style.ERROR(
                        f" - '{url_name}'. Got `NoReverseMatch` "
                        f"when reversed without kwargs.\n"
                    )
                )
            else:
                response = self.client.get(url)
                if response.status_code != 200:
                    sys.stdout.write(
                        style.ERROR(f" - '{url_name}'. Got `{response.status_code}`\n")
                    )
                else:
                    sys.stdout.write(style.SUCCESS(f" - '{url_name}'->{url}\n"))
