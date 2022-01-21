from django.urls import path, include

urlpatterns = [
    path('api/', include('exo_role.api.urls')),
]
