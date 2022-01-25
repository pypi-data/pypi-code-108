from django.urls import include, path

from django_request_mapping import UrlPattern

from . import views

handler404 = 'pfx.pfxcore.views.resource_not_found'

urlpatterns = UrlPattern()
urlpatterns.register(views.AuthorRestView)
urlpatterns.register(views.PrivateEditAuthorRestView)
urlpatterns.register(views.PrivateAuthorRestView)
urlpatterns.register(views.AdminEditAuthorRestView)
urlpatterns.register(views.AdminAuthorRestView)
urlpatterns.register(views.BookRestView)
urlpatterns.register(views.BookTypeRestView)
urlpatterns.register(views.Testi18nView)
urlpatterns.register(views.TestErrorView)

urlpatterns = [
    path('api/', include(urlpatterns)),
    path('api/', include('pfx.pfxcore.urls'))
]
