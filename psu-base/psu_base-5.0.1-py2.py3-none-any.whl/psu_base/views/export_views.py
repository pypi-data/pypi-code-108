# backup_views.py
#
#   Used for exporting data from AWS database into fixtures for development instances
#

from psu_base.services import utility_service, auth_service
from psu_base.decorators import require_authority
from django.http import HttpResponse
from psu_base.classes.Log import Log
import sys
import inspect
from django.db import models
from django.core import serializers
from django.apps import apps

log = Log()
allowable_role_list = "developer"


@require_authority(allowable_role_list)
def export_all(request):
    """
    Export all model instances
    """
    # Get a list of apps to export models for
    installed_apps = utility_service.get_setting("INSTALLED_APPS")
    exportable_apps = []
    for aa in installed_apps:
        if aa.startswith("django.contrib"):
            continue
        if aa in ["django_cas_ng", "crequest", "sass_processor"]:
            continue
        exportable_apps.append(aa)
    log.info(f"Exportable apps: {exportable_apps}")

    # Get a list of models from each app
    app_models = {}
    for app_name in exportable_apps:
        log.info(f"Getting models for: {app_name}")
        app_models[app_name] = []
        try:
            model_list = inspect.getmembers(
                sys.modules[f"{app_name}.models"], inspect.isclass
            )
            log.info(f"Potential models: {model_list}")
            for mm in model_list:
                try:
                    model_name = mm[0]
                    log.info(f"Getting details for: {app_name}")
                    this_model = apps.get_model(app_name, model_name)
                    if issubclass(this_model, models.Model):
                        app_models[app_name].append(model_name)
                except Exception as ee:
                    log.info(f"Not a model: {mm}")
        except Exception as ee:
            log.warning(f"Unable to export from {app_name}: {ee}")
    log.info(f"Models to be exported: {app_models}")

    # Export models to a file
    response = HttpResponse(content_type="text/plain")
    response["Content-Disposition"] = 'attachment; filename="model_export.yaml"'
    YAMLSerializer = serializers.get_serializer("yaml")
    yaml_serializer = YAMLSerializer()
    # with open("file.yaml", "w") as out:
    for app_name, model_list in app_models.items():
        for model_name in model_list:
            ExportableModel = apps.get_model(app_name, model_name)
            yaml_serializer.serialize(ExportableModel.objects.all(), stream=response)

    auth_service.audit_event("EXPORT", comments="Database exported to yaml file")
    return response
