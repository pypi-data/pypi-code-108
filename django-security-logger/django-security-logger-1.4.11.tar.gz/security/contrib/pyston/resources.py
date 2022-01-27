from security.utils import update_logged_request_data


class LogDjangoModelResourceMixin:

    log_update_obj = log_get_obj = True

    def _post_save_obj(self, obj, form, change):
        super()._post_save_obj(obj, form, change)
        if self.log_update_obj:
            update_logged_request_data(self.request, related_objects=[obj])

    def _get_obj_or_404(self, pk=None):
        obj = super()._get_obj_or_404(pk)
        if self.log_get_obj:
            update_logged_request_data(self.request, related_objects=[obj])
        return obj
