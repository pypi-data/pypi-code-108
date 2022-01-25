from django.shortcuts import get_object_or_404

from mayan.apps.rest_api import generics

from .models import ImportSetup
from .permissions import (
    permission_import_setup_create, permission_import_setup_delete,
    permission_import_setup_edit, permission_import_setup_process,
    permission_import_setup_view
)
from .serializers import ImportSetupItemSerializer, ImportSetupSerializer
from .tasks import task_import_setup_populate, task_import_setup_process


class APIImportSetupClearView(generics.ObjectActionAPIView):
    """
    post: Delete all the items of the specified import setup.
    """
    lookup_url_kwarg = 'import_setup_id'
    mayan_object_permissions = {
        'POST': (permission_import_setup_process,)
    }
    queryset = ImportSetup.objects.all()

    def object_action(self, request):
        self.object.clear()


class APIImportSetupPopulateView(generics.ObjectActionAPIView):
    """
    post: Populate all the items of the specified import setup.
    """
    lookup_url_kwarg = 'import_setup_id'
    mayan_object_permissions = {
        'POST': (permission_import_setup_process,)
    }
    queryset = ImportSetup.objects.all()

    def object_action(self, request):
        task_import_setup_populate.apply_async(
            kwargs={'import_setup_id': self.object.pk}
        )


class APIImportSetupProcessView(generics.ObjectActionAPIView):
    """
    post: Process all the items of the specified import setup.
    """
    lookup_url_kwarg = 'import_setup_id'
    mayan_object_permissions = {
        'POST': (permission_import_setup_process,)
    }
    queryset = ImportSetup.objects.all()

    def object_action(self, request):
        task_import_setup_process.apply_async(
            kwargs={'import_setup_id': self.object.pk}
        )


class APIImportSetupDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    delete: Delete the selected import setup.
    get: Return the details of the selected import setup.
    patch: Edit the selected import setup.
    put: Edit the selected import setup.
    """
    lookup_url_kwarg = 'import_setup_id'
    mayan_object_permissions = {
        'DELETE': (permission_import_setup_delete,),
        'GET': (permission_import_setup_view,),
        'PATCH': (permission_import_setup_edit,),
        'PUT': (permission_import_setup_edit,)
    }
    queryset = ImportSetup.objects.all()
    serializer_class = ImportSetupSerializer

    def get_serializer(self, *args, **kwargs):
        if not self.request:
            return None

        return super().get_serializer(*args, **kwargs)


class APIImportSetupListView(generics.ListCreateAPIView):
    """
    get: Returns a list of all the import setups.
    post: Create a new import setup.
    """
    mayan_object_permissions = {'GET': (permission_import_setup_view,)}
    mayan_view_permissions = {'POST': (permission_import_setup_create,)}
    queryset = ImportSetup.objects.all()
    serializer_class = ImportSetupSerializer

    def get_serializer(self, *args, **kwargs):
        if not self.request:
            return None

        return super().get_serializer(*args, **kwargs)


# Import Setup item


class ImportSetupParentMixin:
    def get_import_setup(self):
        return get_object_or_404(
            klass=ImportSetup, pk=self.kwargs['import_setup_id']
        )

    def get_queryset(self):
        return self.get_import_setup().items.all()


class APIImportSetupItemListView(ImportSetupParentMixin, generics.ListAPIView):
    """
    get: Returns a list of all the import setup items.
    """
    mayan_object_permissions = {'GET': (permission_import_setup_view,)}
    serializer_class = ImportSetupItemSerializer

    def get_serializer(self, *args, **kwargs):
        if not self.request:
            return None

        return super().get_serializer(*args, **kwargs)


class APIImportSetupItemDetailView(
    ImportSetupParentMixin, generics.RetrieveDestroyAPIView
):
    """
    delete: Delete the selected import setup items.
    get: Return the details of the selected import setup items.
    """
    lookup_url_kwarg = 'import_setup_item_id'
    mayan_object_permissions = {
        'DELETE': (permission_import_setup_edit,),
        'GET': (permission_import_setup_view,),
    }
    serializer_class = ImportSetupItemSerializer

    def get_serializer(self, *args, **kwargs):
        if not self.request:
            return None

        return super().get_serializer(*args, **kwargs)
