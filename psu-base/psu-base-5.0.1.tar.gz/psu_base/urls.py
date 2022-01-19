from django.urls import path
from . import views
import django_cas_ng.views as cas_views

urlpatterns = [
    # For now, use the test page as default
    path("", views.test_status, name="index"),
    # Feature Toggles
    path("features", views.feature_list, name="features"),
    path("add_feature", views.add_feature, name="add_feature"),
    path("modify_feature", views.modify_feature, name="modify_feature"),
    path("delete_feature", views.delete_feature, name="delete_feature"),
    # Admin Scripts
    path("scripts", views.script_list, name="scripts"),
    path("add_script", views.add_script, name="add_script"),
    path("modify_script", views.modify_script, name="modify_script"),
    path("delete_script", views.delete_script, name="delete_script"),
    # Audit Events
    path("audit", views.audit_list, name="audit"),
    path("audit_xss", views.audit_xss_attempts, name="audit_xss"),
    path("audit_xss_review", views.audit_xss_review_attempt, name="audit_xss_review"),
    # Email Logs
    path("emails", views.email_list, name="emails"),
    path("display_email", views.display_email, name="display_email"),
    path("resend_email", views.resend_email, name="resend_email"),
    # Error logs
    path("errors", views.error_list, name="errors"),
    path("error_status", views.error_status, name="error_status"),
    # Testing pages
    path("test", views.test_status, name="test"),
    path("versions", views.test_versions, name="versions"),
    path("session", views.test_session, name="session"),
    path("finti", views.FintiView.as_view(), name="finti"),
    path("email", views.email_test_page, name="email"),
    # Utility Views
    path(
        "menu_options/<menu_type>",
        views.banner_menu_options,
        name="banner_menu_options",
    ),
    path("id_tag/<identifier>", views.get_id_tag, name="id_tag"),
    path("id_tag", views.get_id_tag, name="id_tag_tbd"),
    path("validate/date", views.validate_date_format, name="validate_date_format"),
    path("format/phone_number", views.format_phone_number, name="format_phone_number"),
    path("format/name", views.clean_banner_name, name="clean_banner_name"),
    path("format/chars", views.clean_banner_chars, name="clean_banner_chars"),
    path("toggle/simulation", views.toggle_simulation, name="toggle_simulation"),
    path("session/extend", views.extend_session, name="extend"),
    path("session/expired", views.end_session, name="end_session"),
    # Downtimes
    path("downtime/list", views.downtime_list, name="downtimes"),
    path("downtime/add", views.downtime_add, name="add_downtime"),
    path(
        "downtime/delete/<int:downtime_id>",
        views.downtime_delete,
        name="delete_downtime",
    ),
    path("downtime/end/<int:downtime_id>", views.downtime_end, name="end_downtime"),
    # Data Export
    path("export", views.export_all, name="export"),
    # Authentication and CAS login/logout endpoints
    path("stop_impersonating", views.stop_impersonating, name="stop_impersonating"),
    path("start_impersonating", views.start_impersonating, name="start_impersonating"),
    path("stop_proxying", views.stop_proxying, name="stop_proxying"),
    path("start_proxying", views.start_proxying, name="start_proxying"),
    path("proxy_search", views.proxy_search, name="proxy_search"),
    path("initiate_auth", views.initiate_auth, name="initiate_auth"),
    path("login", cas_views.LoginView.as_view(), name="login"),
    path("logout", cas_views.LogoutView.as_view(), name="logout"),
    # Messages
    path("messages", views.messages, name="messages"),
    # Error Pages
    path("xss", views.xss_prevention, name="xss"),
    path("xss_lock", views.xss_lock, name="xss_lock"),
    path(
        "authentication_error", views.authentication_error, name="authentication_error"
    ),
]
