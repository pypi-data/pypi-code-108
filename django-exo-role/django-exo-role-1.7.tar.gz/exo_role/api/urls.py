from django.urls import path

from .views import ExORoleListView, CertificationRoleListView, CategoryListView

app_name = 'exo-role'

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('certifications/', CertificationRoleListView.as_view(), name='certifications-list'),
    path('roles/', ExORoleListView.as_view(), name='roles-list'),

]
