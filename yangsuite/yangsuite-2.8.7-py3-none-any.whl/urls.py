# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.

"""yangsuite URL Configuration..

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.apps import apps
from django.views.generic.base import RedirectView
from django.core.exceptions import ImproperlyConfigured
from yangsuite import views
from yangsuite.apps import YSAppConfig
from yangsuite.logs import get_logger

from django_registration.backends.activation.views import RegistrationView
from .forms import YsUserRegistrationForm

log = get_logger(__name__)

urlpatterns = [
    path('',
         RedirectView.as_view(pattern_name='help', permanent=False),
         name='home'),
    path('favicon.ico',
         RedirectView.as_view(url='/static/yangsuite/favicon/favicon.ico',
                              permanent=False),
         name='favicon'),

    path('accounts/profile/', views.user_profile_view, name="user_profile"),
    path('accounts/register/',
         RegistrationView.as_view(form_class=YsUserRegistrationForm),
         name="ys_user_register"),
    path('accounts/', include('django_registration.backends.activation.urls')),
    path('accounts/login/',
         auth_views.LoginView.as_view(
             extra_context={'registration_open': settings.REGISTRATION_OPEN}
         ),
         name="ys_user_login"),
    path('accounts/', include('django.contrib.auth.urls')),

    path('yangsuite/plugins/check_versions', views.check_plugins,
         name='check_versions'),
    path('yangsuite/plugins/mode', views.mode, name='mode'),
    path('yangsuite/plugins/list', views.list_plugins, name='list_plugins'),
    path('yangsuite/plugins/report', views.report_modules,
         name="report_modules"),
    path('yangsuite/plugins/update', views.update_plugins_view,
         name="update_plugins_view"),
    path('yangsuite/plugins/', views.plugins, name='plugins'),
    path('yangsuite/logs/getlog', views.get_log),
    path('yangsuite/logs/', views.log_view),
    path('admin/', admin.site.urls),
    path('help/',
         RedirectView.as_view(url='/help/yangsuite/', permanent=False),
         name="help"),
    path('help/search/', views.help_search, name="help_search"),
    path('help/search/<section>/',
         RedirectView.as_view(pattern_name='help', permanent=False)),
    path('help/search/<section>/<document>/',
         RedirectView.as_view(pattern_name='help', permanent=False)),
    path('help/<section>/', views.help_view, name="help"),
    path('help/<section>/<document>/', views.help_view, name="help"),
    path('yangsuite/eula/', views.eula, name="eula"),
    path('gtm', views.enable_gtm, name="gtm"),
    path('save_email', views.save_email, name="save_email")
]

# Dynamically load URL patterns for all installed YANG Suite apps
for ac in apps.get_app_configs():
    if not isinstance(ac, YSAppConfig):
        continue

    if ac.name == 'yangsuite':
        # Avoid recursion - don't include ourself!
        continue

    if ac.url_prefix is not None:
        log.debug("Including %s at '%s'", ac.name + '.urls', ac.url_prefix)
        try:
            urlpatterns.append(path(ac.url_prefix + "/",
                                    include(ac.name + '.urls')))
        except ImproperlyConfigured as exc:
            log.error("Unable to load urls from %s:\n%s", ac.name, exc)
