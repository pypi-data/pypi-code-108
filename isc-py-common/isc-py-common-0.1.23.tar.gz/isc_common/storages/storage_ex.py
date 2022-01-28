from django.apps import apps
from django.core.files.storage import Storage


class StorageEx(Storage):
    def _get_model_cls(self, model_class_path):
        app_label, model_name = model_class_path.rsplit('.', 1)
        model = apps.get_model(app_label, model_name)
        return model
