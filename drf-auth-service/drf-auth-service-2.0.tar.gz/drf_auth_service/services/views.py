from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from drf_auth_service.common.mixins import EBSModelViewSet
from drf_auth_service.models import Service, Config
from drf_auth_service.services.permissions import SERVICE_PERMISSIONS
from drf_auth_service.settings import settings


class ServiceViewSet(EBSModelViewSet):
    serializer_class = settings.SERIALIZERS.SERVICE_SERIALIZER
    queryset = Service.objects.all()
    permission_classes_by_action = settings.PERMISSIONS.SERVICE_PERMISSIONS

    @action(detail=True, methods=['GET', 'PATCH'], url_name='configs')
    def configs(self, request, *args, **kwargs):
        service = self.get_object()

        if request.method == 'GET':
            configs = {config['key']: config['value'] for config in service.configs.all().values('key', 'value')}
            return Response(configs)

        else:
            configs = Config.objects.filter(service=service, key__in=request.data.keys())

            for config in configs:
                config.value = request.data[config.key]

            Config.objects.bulk_update(configs, ['value'])

            return Response(request.data)

    def perform_create(self, serializer):
        return serializer.save()
