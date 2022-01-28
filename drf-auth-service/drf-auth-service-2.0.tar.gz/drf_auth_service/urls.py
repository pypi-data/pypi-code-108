from django.urls import path
from rest_framework.routers import DefaultRouter

from drf_auth_service.authentication.views import EBSTokenRefreshView, TokenByCookieView
from drf_auth_service.settings import settings
from drf_auth_service.socials.views import social_login

router = DefaultRouter(trailing_slash=False)
router.register(r'services', settings.VIEWS.SERVICE_VIEWS, basename='service')
router.register(r'users', settings.VIEWS.USER_VIEWS, basename='user')
router.register(r'authentication', settings.VIEWS.AUTHENTICATION_VIEWS, basename='authentication')

urlpatterns = router.urls + [
    path('authentication/login', settings.VIEWS.AUTHENTICATION_LOGIN_VIEWS.as_view(), name='authentication-login'),
    path('authentication/oauth', social_login, name='social_login'),
    path('authentication/refresh', EBSTokenRefreshView.as_view(), name='authentication-refresh'),
    path('authentication/cookie', TokenByCookieView.as_view(), name='cookie-refresh'),
]
