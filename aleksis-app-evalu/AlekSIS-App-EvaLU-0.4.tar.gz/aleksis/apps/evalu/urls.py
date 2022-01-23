from django.urls import path

from . import views

urlpatterns = [
    path("parts/", views.EvaluationPartListView.as_view(), name="evaluation_parts"),
    path("parts/create/", views.EvaluationPartCreateView.as_view(), name="create_evaluation_part"),
    path("parts/<int:pk>/", views.EvaluationPartEditView.as_view(), name="edit_evaluation_part"),
    path(
        "parts/<int:pk>/delete/",
        views.EvaluationPartDeleteView.as_view(),
        name="delete_evaluation_part",
    ),
    path("phases/", views.EvaluationPhaseListView.as_view(), name="evaluation_phases"),
    path(
        "phases/create/", views.EvaluationPhaseCreateView.as_view(), name="create_evaluation_phase"
    ),
    path("phases/<int:pk>/", views.EvaluationPhaseDetailView.as_view(), name="evaluation_phase"),
    path(
        "phases/<int:pk>/edit/",
        views.EvaluationPhaseEditView.as_view(),
        name="edit_evaluation_phase",
    ),
    path(
        "phases/<int:pk>/delete/",
        views.EvaluationPhaseDeleteView.as_view(),
        name="delete_evaluation_phase",
    ),
    path(
        "evaluations/",
        views.EvaluationPhaseOverviewView.as_view(),
        name="evaluation_phases_overview",
    ),
    path(
        "evaluations/<int:pk>/register/",
        views.RegisterForEvaluationView.as_view(),
        name="register_for_evaluation",
    ),
    path(
        "evaluations/registrations/<int:pk>/",
        views.RegistrationDetailView.as_view(),
        name="evaluation_registration",
    ),
    path(
        "evaluations/registrations/<int:pk>/manage/",
        views.ManageEvaluationProcessView.as_view(),
        name="manage_evaluation_process",
    ),
    path(
        "evaluations/groups/<int:pk>/start/",
        views.StartEvaluationForGroupView.as_view(),
        name="start_evaluation_for_group",
    ),
    path(
        "evaluations/groups/<int:pk>/stop/",
        views.StopEvaluationForGroupView.as_view(),
        name="stop_evaluation_for_group",
    ),
    path(
        "evaluations/registrations/<int:pk>/finish/",
        views.FinishEvaluationView.as_view(),
        name="finish_evaluation",
    ),
    path(
        "evaluations/registrations/<int:pk>/results/",
        views.EvaluationResultsView.as_view(),
        {"as_pdf": False},
        name="evaluation_results",
    ),
    path(
        "evaluations/registrations/<int:pk>/results/pdf/",
        views.EvaluationResultsView.as_view(),
        {"as_pdf": True},
        name="evaluation_results_as_pdf",
    ),
    path(
        "evaluations/evaluate/",
        views.EvaluationsAsParticipantListView.as_view(),
        name="evaluations_as_participant",
    ),
    path(
        "evaluations/evaluate/<int:pk>/",
        views.EvaluationFormView.as_view(),
        name="evaluate_person",
    ),
]
