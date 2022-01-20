from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from reversion import set_comment
from reversion.views import RevisionMixin

from huscy.projects.models import Project
from huscy.project_ethics import serializer
from huscy.project_ethics.models import Ethic
from huscy.project_ethics.permissions import EthicsFilePermission, EthicPermission
from huscy.project_ethics.services import get_ethic_boards, get_ethic_files, get_ethics


class EthicBoardViewSet(RevisionMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                        mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    http_method_names = 'delete', 'head', 'get', 'options', 'post', 'put'
    permission_classes = (DjangoModelPermissions, )
    queryset = get_ethic_boards()
    serializer_class = serializer.EthicBoardSerializer

    def perform_create(self, serializer):
        ethic_board = serializer.save()
        set_comment(f'Created ethic board "{ethic_board.name}"')

    def perform_destroy(self, ethic_board):
        ethic_board.delete()
        set_comment(f'Deleted ethic board "{ethic_board.name}"')

    def perform_update(self, serializer):
        ethic_board = serializer.save()
        set_comment(f'Updated ethic board "{ethic_board.name}"')


class EthicViewSet(RevisionMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                   mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    http_method_names = 'delete', 'head', 'get', 'options', 'post', 'put'
    permission_classes = IsAuthenticated, EthicPermission
    serializer_class = serializer.EthicSerializer

    def initial(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        super().initial(request, *args, **kwargs)

    def get_queryset(self):
        return get_ethics(self.project)

    def perform_create(self, serializer):
        ethic = serializer.save(project=self.project)
        set_comment(f'Created ethic <ID-{ethic.id}>')

    def perform_destroy(self, ethic):
        ethic.delete()
        set_comment(f'Deleted ethic <ID-{ethic.id}>')

    def perform_update(self, serializer):
        ethic = serializer.save()
        set_comment(f'Updated ethic <ID-{ethic.id}>')


class EthicsFileViewSet(RevisionMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                        mixins.UpdateModelMixin, viewsets.GenericViewSet):
    http_method_names = 'delete', 'head', 'options', 'post', 'put'
    permission_classes = IsAuthenticated, EthicsFilePermission

    def initial(self, request, *args, **kwargs):
        self.ethics = get_object_or_404(Ethic.objects.select_related('project'),
                                        pk=self.kwargs['ethic_pk'],
                                        project=self.kwargs['project_pk'])
        super().initial(request, *args, **kwargs)

    def get_queryset(self):
        return get_ethic_files(self.ethics)

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return serializer.UpdateEthicsFileSerializer
        return serializer.EthicsFileSerializer

    def perform_create(self, serializer):
        ethics_file = serializer.save(ethic=self.ethics, creator=self.request.user)
        set_comment(f'Created ethics file <ID-{ethics_file.id}>')

    def perform_destroy(self, ethics_file):
        ethics_file.delete()
        set_comment(f'Deleted ethics file <ID-{ethics_file.id}>')

    def perform_update(self, serializer):
        ethics_file = serializer.save()
        set_comment(f'Updated ethics file <ID-{ethics_file.id}>')
