from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView, \
    RetrieveUpdateDestroyAPIView
from rest_framework.permissions import ( AllowAny, IsAuthenticated )

from aparnik.contrib.users.api.permissions import IsAdminPermission
from .serializers import ContactUsDestailSerializer
from ..models import ContactUs


class ContactUsListAPIView(ListAPIView):
    serializer_class = ContactUsDestailSerializer
    permission_classes = [IsAdminPermission]
    queryset = ContactUs.objects.active().order_by('-update_at')


class ContactUsDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ContactUsDestailSerializer
    permission_classes = [IsAdminPermission]
    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    def get_queryset(self):
        return ContactUs.objects.active()


class ContactUsCreateAPIView(CreateAPIView):
    serializer_class = ContactUsDestailSerializer
    permission_classes = [AllowAny]
    queryset = ContactUs.objects.active()
