from rest_framework import generics

from .serializers import ExORoleSerializer, CertificationRoleSerializer, CategorySerializer
from ..models import ExORole, CertificationRole, Category


class ExORoleListView(generics.ListAPIView):
    queryset = ExORole.objects.all()
    serializer_class = ExORoleSerializer


class CertificationRoleListView(generics.ListAPIView):
    queryset = CertificationRole.objects.all()
    serializer_class = CertificationRoleSerializer


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
