from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog

import calendarweek.django
import debug_toolbar
from ckeditor_uploader import views as ckeditor_uploader_views
from django_js_reverse.views import urls_js
from health_check.urls import urlpatterns as health_urls
from oauth2_provider.views import ConnectDiscoveryInfoView
from rules.contrib.views import permission_required
from two_factor.urls import urlpatterns as tf_urls

from . import views

urlpatterns = [
    path("", include("django_prometheus.urls")),
    path(settings.MEDIA_URL.removeprefix("/"), include("titofisto.urls")),
    path("manifest.json", views.ManifestView.as_view(), name="manifest"),
    path("serviceworker.js", views.ServiceWorkerView.as_view(), name="service_worker"),
    path("offline/", views.OfflineView.as_view(), name="offline"),
    path("about/", views.about, name="about_aleksis"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "accounts/password/change/",
        views.CustomPasswordChangeView.as_view(),
        name="account_change_password",
    ),
    path("accounts/", include("allauth.urls")),
    path(
        "accounts/social/connections/<int:pk>/delete",
        views.SocialAccountDeleteView.as_view(),
        name="delete_social_account_by_pk",
    ),
    path("admin/", admin.site.urls),
    path("admin/uwsgi/", include("django_uwsgi.urls")),
    path("data_management/", views.data_management, name="data_management"),
    path("status/", views.SystemStatus.as_view(), name="system_status"),
    path("", include(tf_urls)),
    path("celery_progress/<str:task_id>/", views.CeleryProgressView.as_view(), name="task_status"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("school_terms/", views.SchoolTermListView.as_view(), name="school_terms"),
    path("school_terms/create/", views.SchoolTermCreateView.as_view(), name="create_school_term"),
    path("school_terms/<int:pk>/", views.SchoolTermEditView.as_view(), name="edit_school_term"),
    path("persons", views.persons, name="persons"),
    path("person/", views.person, name="person"),
    path("person/create/", views.CreatePersonView.as_view(), name="create_person"),
    path("person/<int:id_>/", views.person, name="person_by_id"),
    path("person/<int:pk>/edit/", views.EditPersonView.as_view(), name="edit_person_by_id"),
    path("person/<int:id_>/delete/", views.delete_person, name="delete_person_by_id"),
    path("groups", views.groups, name="groups"),
    path("groups/additional_fields", views.additional_fields, name="additional_fields"),
    path("groups/child_groups/", views.groups_child_groups, name="groups_child_groups"),
    path(
        "groups/additional_field/<int:id_>/edit",
        views.edit_additional_field,
        name="edit_additional_field_by_id",
    ),
    path(
        "groups/additional_field/create",
        views.edit_additional_field,
        name="create_additional_field",
    ),
    path(
        "groups/additional_field/<int:id_>/delete",
        views.delete_additional_field,
        name="delete_additional_field_by_id",
    ),
    path("group/create", views.edit_group, name="create_group"),
    path("group/<int:id_>", views.group, name="group_by_id"),
    path("group/<int:id_>/edit", views.edit_group, name="edit_group_by_id"),
    path("group/<int:id_>/delete", views.delete_group, name="delete_group_by_id"),
    path("", views.index, name="index"),
    path("notifications/", views.NotificationsListView.as_view(), name="notifications"),
    path("dashboard/edit/", views.EditDashboardView.as_view(), name="edit_dashboard"),
    path(
        "notifications/mark-read/<int:id_>",
        views.notification_mark_read,
        name="notification_mark_read",
    ),
    path("groups/group_type/create", views.edit_group_type, name="create_group_type"),
    path(
        "groups/group_type/<int:id_>/delete",
        views.delete_group_type,
        name="delete_group_type_by_id",
    ),
    path("groups/group_type/<int:id_>/edit", views.edit_group_type, name="edit_group_type_by_id"),
    path("groups/group_types", views.group_types, name="group_types"),
    path("announcements/", views.announcements, name="announcements"),
    path("announcement/create/", views.announcement_form, name="add_announcement"),
    path("announcement/edit/<int:id_>/", views.announcement_form, name="edit_announcement"),
    path("announcement/delete/<int:id_>/", views.delete_announcement, name="delete_announcement"),
    path("search/searchbar/", views.searchbar_snippets, name="searchbar_snippets"),
    path("search/", views.PermissionSearchView.as_view(), name="haystack_search"),
    path("maintenance-mode/", include("maintenance_mode.urls")),
    path("impersonate/", include("impersonate.urls")),
    path(
        ".well-known/openid-configuration",
        ConnectDiscoveryInfoView.as_view(),
        name="oidc_configuration",
    ),
    path("oauth/applications/", views.OAuth2ListView.as_view(), name="oauth2_applications"),
    path(
        "oauth/applications/register/",
        views.OAuth2RegisterView.as_view(),
        name="register_oauth_application",
    ),
    path(
        "oauth/applications/<int:pk>/", views.OAuth2DetailView.as_view(), name="oauth2_application"
    ),
    path(
        "oauth/applications/<int:pk>/delete/",
        views.OAuth2DeleteView.as_view(),
        name="delete_oauth2_application",
    ),
    path(
        "oauth/applications/<int:pk>/edit/",
        views.OAuth2EditView.as_view(),
        name="edit_oauth2_application",
    ),
    path("oauth/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    path("__i18n__/", include("django.conf.urls.i18n")),
    path(
        "ckeditor/upload/",
        permission_required("core.ckeditor_upload_files_rule")(ckeditor_uploader_views.upload),
        name="ckeditor_upload",
    ),
    path(
        "ckeditor/browse/",
        permission_required("core.ckeditor_upload_files_rule")(ckeditor_uploader_views.browse),
        name="ckeditor_browse",
    ),
    path("select2/", include("django_select2.urls")),
    path("jsreverse.js", urls_js, name="js_reverse"),
    path("calendarweek_i18n.js", calendarweek.django.i18n_js, name="calendarweek_i18n_js"),
    path("gettext.js", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    path(
        "preferences/site/", views.preferences, {"registry_name": "site"}, name="preferences_site"
    ),
    path(
        "preferences/person/",
        views.preferences,
        {"registry_name": "person"},
        name="preferences_person",
    ),
    path(
        "preferences/group/",
        views.preferences,
        {"registry_name": "group"},
        name="preferences_group",
    ),
    path(
        "preferences/site/<int:pk>/",
        views.preferences,
        {"registry_name": "site"},
        name="preferences_site",
    ),
    path(
        "preferences/person/<int:pk>/",
        views.preferences,
        {"registry_name": "person"},
        name="preferences_person",
    ),
    path(
        "preferences/group/<int:pk>/",
        views.preferences,
        {"registry_name": "group"},
        name="preferences_group",
    ),
    path(
        "preferences/site/<int:pk>/<str:section>/",
        views.preferences,
        {"registry_name": "site"},
        name="preferences_site",
    ),
    path(
        "preferences/person/<int:pk>/<str:section>/",
        views.preferences,
        {"registry_name": "person"},
        name="preferences_person",
    ),
    path(
        "preferences/group/<int:pk>/<str:section>/",
        views.preferences,
        {"registry_name": "group"},
        name="preferences_group",
    ),
    path(
        "preferences/site/<str:section>/",
        views.preferences,
        {"registry_name": "site"},
        name="preferences_site",
    ),
    path(
        "preferences/person/<str:section>/",
        views.preferences,
        {"registry_name": "person"},
        name="preferences_person",
    ),
    path(
        "preferences/group/<str:section>/",
        views.preferences,
        {"registry_name": "group"},
        name="preferences_group",
    ),
    path("health/", include(health_urls)),
    path("health/pdf/", views.TestPDFGenerationView.as_view(), name="test_pdf"),
    path(
        "data_check/",
        views.DataCheckView.as_view(),
        name="check_data",
    ),
    path(
        "data_check/run/",
        views.RunDataChecks.as_view(),
        name="data_check_run",
    ),
    path(
        "data_check/<int:pk>/<str:solve_option>/",
        views.SolveDataCheckView.as_view(),
        name="data_check_solve",
    ),
    path("dashboard_widgets/", views.DashboardWidgetListView.as_view(), name="dashboard_widgets"),
    path(
        "dashboard_widgets/<int:pk>/edit/",
        views.DashboardWidgetEditView.as_view(),
        name="edit_dashboard_widget",
    ),
    path(
        "dashboard_widgets/<int:pk>/delete/",
        views.DashboardWidgetDeleteView.as_view(),
        name="delete_dashboard_widget",
    ),
    path(
        "dashboard_widgets/<str:app>/<str:model>/new/",
        views.DashboardWidgetCreateView.as_view(),
        name="create_dashboard_widget",
    ),
    path(
        "dashboard_widgets/default/",
        views.EditDashboardView.as_view(),
        {"default": True},
        name="edit_default_dashboard",
    ),
    path(
        "permissions/global/user/",
        views.UserGlobalPermissionsListBaseView.as_view(),
        name="manage_user_global_permissions",
    ),
    path(
        "permissions/global/group/",
        views.GroupGlobalPermissionsListBaseView.as_view(),
        name="manage_group_global_permissions",
    ),
    path(
        "permissions/object/user/",
        views.UserObjectPermissionsListBaseView.as_view(),
        name="manage_user_object_permissions",
    ),
    path(
        "permissions/object/group/",
        views.GroupObjectPermissionsListBaseView.as_view(),
        name="manage_group_object_permissions",
    ),
    path(
        "permissions/global/user/<int:pk>/delete/",
        views.UserGlobalPermissionDeleteView.as_view(),
        name="delete_user_global_permission",
    ),
    path(
        "permissions/global/group/<int:pk>/delete/",
        views.GroupGlobalPermissionDeleteView.as_view(),
        name="delete_group_global_permission",
    ),
    path(
        "permissions/object/user/<int:pk>/delete/",
        views.UserObjectPermissionDeleteView.as_view(),
        name="delete_user_object_permission",
    ),
    path(
        "permissions/object/group/<int:pk>/delete/",
        views.GroupObjectPermissionDeleteView.as_view(),
        name="delete_group_object_permission",
    ),
    path(
        "permissions/assign/",
        views.SelectPermissionForAssignView.as_view(),
        name="select_permission_for_assign",
    ),
    path(
        "permissions/<int:pk>/assign/",
        views.AssignPermissionView.as_view(),
        name="assign_permission",
    ),
    path("pdfs/<int:pk>/", views.RedirectToPDFFile.as_view(), name="redirect_to_pdf_file"),
]

# Use custom server error handler to get a request object in the template
handler500 = views.server_error

# Add URLs for optional features
if hasattr(settings, "TWILIO_ACCOUNT_SID"):
    from two_factor.gateways.twilio.urls import urlpatterns as tf_twilio_urls  # noqa

    urlpatterns += [path("", include(tf_twilio_urls))]

# Serve javascript-common if in development
if settings.DEBUG:
    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))

# Automatically mount URLs from all installed AlekSIS apps
for app_config in apps.app_configs.values():
    if not app_config.name.startswith("aleksis.apps."):
        continue

    try:
        urlpatterns.append(path(f"app/{app_config.label}/", include(f"{app_config.name}.urls")))
    except ModuleNotFoundError:
        # Ignore exception as app just has no URLs
        pass  # noqa
