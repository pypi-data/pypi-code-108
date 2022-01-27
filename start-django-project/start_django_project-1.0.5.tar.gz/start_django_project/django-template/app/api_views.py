
from rest_framework import viewsets
from .serializers import MyUserSerializer
from rest_framework.permissions import IsAdminUser

from .models import MyUser

class MyUserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]

    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer