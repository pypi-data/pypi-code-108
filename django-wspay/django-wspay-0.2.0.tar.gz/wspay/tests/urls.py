from django.urls import include, path

urlpatterns = [
    path('wspay/', include('wspay.urls', 'wspay'))
]
