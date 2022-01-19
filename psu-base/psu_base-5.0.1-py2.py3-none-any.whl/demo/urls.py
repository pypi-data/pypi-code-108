"""demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.views.generic import RedirectView
import demo.views as demo_views
from django.urls import path, include

app_patterns = [
    # Django admin site. Probably won't use this. Our apps typically use Banner security classes.
    # Finti's sso_proxy app has JWT-specific permission endpoints that could be modified for service-to-service calls
    path('admin/', admin.site.urls),

    # PSU and CAS views are defined in psu_base app
    path('psu/', include(('psu_base.urls', 'psu_base'), namespace='psu')),
    path('accounts/', include(('psu_base.urls', 'psu_base'), namespace='cas')),

    # For now, use a simple landing page
    path('', demo_views.index),
    path('alert_message', demo_views.alert_message),

    # Landing pages for sub-app demos
    path('arrangement/landing_page', demo_views.sub_app_demo, name='arrangement'),
    path('emergency/landing_page', demo_views.sub_app_demo, name='emergency'),
    path('diploma/landing_page', demo_views.sub_app_demo, name='diploma'),

]

# On-prem apps will have additional URL context
if settings.URL_CONTEXT:
    urlpatterns = [
        path('', RedirectView.as_view(url='/'+settings.URL_CONTEXT)),
        path(settings.URL_CONTEXT + '/', include(app_patterns)),
    ]

# AWS apps will NOT have additional URL context
else:
    urlpatterns = app_patterns
