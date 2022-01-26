from edc_subject_dashboard.views import SubjectDashboardView


class DashboardView(SubjectDashboardView):

    consent_model = "mocca_consent.subjectconsent"
    navbar_selected_item = "consented_subject"
    visit_model = "mocca_subject.subjectvisit"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"recruitment_clinic_name": self.get_recruitment_clinic_name()})
        return context

    def get_recruitment_clinic_name(self):
        return self.consent.get_clinic_type_display()
