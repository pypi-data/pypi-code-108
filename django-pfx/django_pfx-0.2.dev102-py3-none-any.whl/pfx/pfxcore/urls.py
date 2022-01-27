from django_request_mapping import UrlPattern

from . import views

urlpatterns = UrlPattern()
urlpatterns.register(views.LocaleRestView)
urlpatterns.register(views.AuthenticationView)
urlpatterns.register(views.SignupView)
urlpatterns.register(views.ForgotenPasswordView)
