import django.http as http
from rest_framework import viewsets

from masterful_gui.backend.apps.api import serializers
from masterful_gui.backend.apps.api import models
from masterful_gui.backend.apps.api import policy_search_task_scanner
from masterful_gui.backend.apps.api import dataset_spec_scanner


class PolicySearchTaskView(viewsets.ReadOnlyModelViewSet):
  serializer_class = serializers.PolicySearchTaskModelSerializer
  queryset = models.PolicySearchTask.objects.all()


class DatasetSpecView(viewsets.ReadOnlyModelViewSet):
  serializer_class = serializers.DatasetSpecModelSerializer
  queryset = models.DatasetSpec.objects.all()


def scan_view(request):
  """This performs scans on all protos supported by visualize."""
  # TODO: improve the experience. Consider reroute or surfacing
  # a template. This is not required it's just for aesthetics.
  try:
    policy_search_task_scanner.scan()
    dataset_spec_scanner.scan()
  except Exception as e:
    print(str(e))
    return http.HttpResponseServerError()

  return http.HttpResponse()
