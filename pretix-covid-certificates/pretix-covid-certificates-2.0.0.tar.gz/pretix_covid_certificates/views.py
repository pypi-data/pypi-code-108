import json
from django import forms
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext, gettext_lazy as _, gettext_noop  # NoQA
from pretix.base.forms import SettingsForm
from pretix.base.models import Event, Question
from pretix.control.views.event import EventSettingsFormView, EventSettingsViewMixin

DEFAULT_COMBINATION_RULES = [
    (
        # Regular behaviour, either tested or vaccinated or cured
        json.dumps(
            {
                "or": [
                    {"var": "VACC"},
                    {"var": "CURED"},
                    {"var": "TESTED_PCR"},
                    {"var": "TESTED_AG_UNKNOWN"},
                    {"var": "OTHER"},
                ]
            },
            sort_keys=True,
        ),
        _("Any one of the certificate types enabled below"),
    ),
    (
        # Known as "2G+" in Germany
        json.dumps(
            {
                "and": [
                    {"or": [{"var": "VACC"}, {"var": "CURED"}, {"var": "OTHER"}]},
                    {
                        "or": [
                            {"var": "TESTED_PCR"},
                            {"var": "TESTED_AG_UNKNOWN"},
                            {"var": "OTHER"},
                        ]
                    },
                ]
            },
            sort_keys=True,
        ),
        _(
            "One immunization certificate (vaccinated or cured) PLUS one test certificate"
        ),
    ),
    (
        json.dumps(
            {
                "or": [
                    {"var": "CURED"},
                    {"and": [{"var": "VACC"}, {"var": "VACC_isBooster"}]},
                    {
                        "and": [
                            {"var": "VACC"},
                            {
                                "or": [
                                    {"var": "TESTED_PCR"},
                                    {"var": "TESTED_AG_UNKNOWN"},
                                ]
                            },
                        ]
                    },
                    {"var": "OTHER"},
                ]
            },
            sort_keys=True,
        ),
        _(
            "One immunization certificate (vaccinated or cured) PLUS one test certificate (only without booster "
            "vaccination, no test for cured attendees)"
        ),
    ),
    (
        # This is roughly what is required in the state of Baden-Wurttemberg, Germany in December 2021
        json.dumps(
            {
                "or": [
                    {
                        "and": [
                            {"var": "VACC"},
                            {
                                "!=": [{"var": "VACC_occurence_days_since"}, None]
                            },  # required because in json logic, None < 180 is true
                            {"<=": [{"var": "VACC_occurence_days_since"}, 180]},
                        ]
                    },
                    {"var": "CURED"},
                    {"and": [{"var": "VACC"}, {"var": "VACC_isBooster"}]},
                    {
                        "and": [
                            {"var": "VACC"},
                            {
                                "or": [
                                    {"var": "TESTED_PCR"},
                                    {"var": "TESTED_AG_UNKNOWN"},
                                ]
                            },
                        ]
                    },
                    {"var": "OTHER"},
                ]
            },
            sort_keys=True,
        ),
        _(
            "One immunization certificate (vaccinated or cured) PLUS one test certificate (only if vaccinated more than "
            "180 days ago and no booster vaccination, no test for cured attendees)"
        ),
    ),
    (
        json.dumps(
            {
                "or": [
                    {
                        "and": [
                            {"var": "VACC"},
                            {"!=": [{"var": "VACC_occurence_days_since"}, None]},
                            {"<=": [{"var": "VACC_occurence_days_since"}, 180]},
                        ]
                    },
                    {"var": "CURED"},
                    {
                        "and": [
                            {"var": "VACC"},
                            {
                                "or": [
                                    {"var": "TESTED_PCR"},
                                    {"var": "TESTED_AG_UNKNOWN"},
                                ]
                            },
                        ]
                    },
                    {"var": "OTHER"},
                ]
            },
            sort_keys=True,
        ),
        _(
            "One immunization certificate (vaccinated or cured) PLUS one test certificate (only if vaccinated more than "
            "180 days ago, no test for cured attendees)"
        ),
    ),
]


class CovidCertificatesSettingsForm(SettingsForm):
    covid_certificates_combination_rules = forms.ChoiceField(
        label=_("Check type"),
        required=False,
        widget=forms.RadioSelect,
        choices=DEFAULT_COMBINATION_RULES,
        help_text=_(
            "Every option other than the first one is only supported on pretixSCAN 1.13.1 or newer."
        ),
    )

    covid_certificates_allow_vaccinated = forms.BooleanField(
        label=_("Allow vaccinated"),
        required=False,
        help_text=_(
            "Only participants that have received the complete treatment (two doses with the exception of "
            "designated single-dose vaccines) are deemed completely vaccinated."
        ),
    )

    covid_certificates_allow_vaccinated_min = forms.IntegerField(
        label=_("Vaccinated at least"),
        required=True,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                "addon_after": _("days ago"),
                "data-display-dependency": "#id_covid_certificates_allow_vaccinated",
                "data-required-if": "#id_covid_certificates_allow_vaccinated",
            }
        ),
    )

    covid_certificates_allow_vaccinated_max = forms.IntegerField(
        label=_("Vaccinated at most"),
        required=True,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                "addon_after": _("days ago"),
                "data-display-dependency": "#id_covid_certificates_allow_vaccinated",
                "data-required-if": "#id_covid_certificates_allow_vaccinated",
            }
        ),
    )

    covid_certificates_record_proof_vaccinated = forms.BooleanField(
        label=_("Record proof"),
        required=False,
        help_text=_(
            "With this option enabled, pretixSCAN will record what kind of certificate (vaccination, "
            "recovery, PCR- or Antigen-test) has been presented by the visitor. Saving this information is "
            "highly regulated in most countries and therefore not recommended. Only enable this option if you "
            "are required by your local health authorities to collect such information."
        ),
        widget=forms.CheckboxInput(
            attrs={
                "data-display-dependency": "#id_covid_certificates_allow_vaccinated",
            }
        ),
    )

    covid_certificates_allow_cured = forms.BooleanField(
        label=_("Allow cured"),
        required=False,
        help_text=_(
            "Only participants that have gone through and recovered from a COVID-infection are deemed cured."
        ),
    )

    covid_certificates_allow_cured_min = forms.IntegerField(
        label=_("Cured at least"),
        required=True,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                "addon_after": _("days ago"),
                "data-display-dependency": "#id_covid_certificates_allow_cured",
                "data-required-if": "#id_covid_certificates_allow_cured",
            }
        ),
    )

    covid_certificates_allow_cured_max = forms.IntegerField(
        label=_("Cured at most"),
        required=True,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                "addon_after": _("days ago"),
                "data-display-dependency": "#id_covid_certificates_allow_cured",
                "data-required-if": "#id_covid_certificates_allow_cured",
            }
        ),
    )

    covid_certificates_record_proof_cured = forms.BooleanField(
        label=_("Record proof"),
        required=False,
        help_text=_(
            "With this option enabled, pretixSCAN will record what kind of certificate (vaccination, "
            "recovery, PCR- or Antigen-test) has been presented by the visitor. Saving this information is "
            "highly regulated in most countries and therefore not recommended. Only enable this option if you "
            "are required by your local health authorities to collect such information."
        ),
        widget=forms.CheckboxInput(
            attrs={
                "data-display-dependency": "#id_covid_certificates_allow_cured",
            }
        ),
    )

    covid_certificates_allow_tested_pcr = forms.BooleanField(
        label=_("Allow tested (PCR)"),
        required=False,
        help_text=_(
            "This covers exclusively participants having received a negative PCR-test."
        ),
    )

    covid_certificates_allow_tested_pcr_min = forms.IntegerField(
        label=_("PCR tested at least"),
        required=True,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                "addon_after": _("hours ago"),
                "data-display-dependency": "#id_covid_certificates_allow_tested_pcr",
                "data-required-if": "#id_covid_certificates_allow_tested_pcr",
            }
        ),
    )

    covid_certificates_allow_tested_pcr_max = forms.IntegerField(
        label=_("PCR tested at most"),
        required=True,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                "addon_after": _("hours ago"),
                "data-display-dependency": "#id_covid_certificates_allow_tested_pcr",
                "data-required-if": "#id_covid_certificates_allow_tested_pcr",
            }
        ),
    )

    covid_certificates_record_proof_tested_pcr = forms.BooleanField(
        label=_("Record proof"),
        required=False,
        help_text=_(
            "With this option enabled, pretixSCAN will record what kind of certificate (vaccination, "
            "recovery, PCR- or Antigen-test) has been presented by the visitor. Saving this information is "
            "highly regulated in most countries and therefore not recommended. Only enable this option if you "
            "are required by your local health authorities to collect such information."
        ),
        widget=forms.CheckboxInput(
            attrs={
                "data-display-dependency": "#id_covid_certificates_allow_tested_pcr",
            }
        ),
    )

    covid_certificates_allow_tested_antigen_unknown = forms.BooleanField(
        label=_("Allow tested (Antigen or unknown)"),
        required=False,
        help_text=_(
            "This covers exclusively participants having received a negative Antigen-test or any other type of "
            "test (with the exception of PCR-tests)."
        ),
    )

    covid_certificates_allow_tested_antigen_unknown_min = forms.IntegerField(
        label=_("Antigen/other tested at least"),
        required=True,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                "addon_after": _("hours ago"),
                "data-display-dependency": "#id_covid_certificates_allow_tested_antigen_unknown",
                "data-required-if": "#id_covid_certificates_allow_tested_antigen_unknown",
            }
        ),
    )

    covid_certificates_allow_tested_antigen_unknown_max = forms.IntegerField(
        label=_("Antigen/other tested at most"),
        required=True,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                "addon_after": _("hours ago"),
                "data-display-dependency": "#id_covid_certificates_allow_tested_antigen_unknown",
                "data-required-if": "#id_covid_certificates_allow_tested_antigen_unknown",
            }
        ),
    )

    covid_certificates_record_proof_tested_antigen_unknown = forms.BooleanField(
        label=_("Record proof"),
        required=False,
        help_text=_(
            "With this option enabled, pretixSCAN will record what kind of certificate (vaccination, "
            "recovery, PCR- or Antigen-test) has been presented by the visitor. Saving this information is "
            "highly regulated in most countries and therefore not recommended. Only enable this option if you "
            "are required by your local health authorities to collect such information."
        ),
        widget=forms.CheckboxInput(
            attrs={
                "data-display-dependency": "#id_covid_certificates_allow_tested_antigen_unknown",
            }
        ),
    )

    covid_certificates_allow_other = forms.BooleanField(
        label=_("Allow other forms of proof"),
        required=False,
    )

    covid_certificates_record_proof_other = forms.BooleanField(
        label=_("Record proof"),
        required=False,
        help_text=_(
            "With this option enabled, pretixSCAN will record what kind of certificate (vaccination, "
            "recovery, PCR- or Antigen-test) has been presented by the visitor. Saving this information is "
            "highly regulated in most countries and therefore not recommended. Only enable this option if you "
            "are required by your local health authorities to collect such information."
        ),
        widget=forms.CheckboxInput(
            attrs={
                "data-display-dependency": "#id_covid_certificates_allow_other",
            }
        ),
    )

    covid_certificates_record_validity_time = forms.BooleanField(
        label=_("Record validity time"),
        required=False,
        help_text=_(
            "With this option enabled, pretixSCAN will record at which the certificate becomes invalid according to "
            "the rules stated above. pretix will automatically remove the stored certificate around this time (there "
            "can be a small variance) so the person will need to show a new certificate on re-entry. All certificates "
            "where a date cannot be computed (such as non-digital certificates) will be considered valid until the end "
            "of the current day."
        ),
    )

    covid_certificates_accept_eudgc = forms.BooleanField(
        label=_("Accept EU DGC (Digital Green Certificate)"),
        required=False,
    )

    covid_certificates_accept_manual = forms.BooleanField(
        label=_("Accept manual override"),
        required=False,
        help_text=_(
            "This options allows your staff to manually set the vaccination status for a participant - for "
            "example if they present their yellow vaccination booklet or any other form of certificate which "
            "cannot be processed automatically."
        ),
    )


class CovidCertificatesSettings(EventSettingsViewMixin, EventSettingsFormView):
    model = Event
    form_class = CovidCertificatesSettingsForm
    template_name = "pretix_covid_certificates/settings.html"
    permission = "can_change_settings"

    def get_success_url(self) -> str:
        return reverse(
            "plugins:pretix_covid_certificates:settings",
            kwargs={
                "organizer": self.request.event.organizer.slug,
                "event": self.request.event.slug,
            },
        )

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)

        question, created = Question.objects.get_or_create(
            identifier="pretix_covid_certificates_question",
            event=self.request.event,
            defaults={
                "type": Question.TYPE_TEXT,
                "question": gettext("COVID Certificate Validation"),
                "required": True,
                "help_text": gettext(
                    "This question has been created automatically by the Digital COVID Certificate Validation plugin. "
                    "Please do not change its internal identifier."
                ),
                "ask_during_checkin": True,
                "hidden": True,
            },
        )

        messages.warning(
            request,
            _("Please select the products that require COVID certificate validation."),
        )

        return redirect(
            reverse(
                "control:event.items.questions.edit",
                kwargs={
                    "organizer": self.request.organizer.slug,
                    "event": self.request.event.slug,
                    "question": question.pk,
                },
            )
        )
