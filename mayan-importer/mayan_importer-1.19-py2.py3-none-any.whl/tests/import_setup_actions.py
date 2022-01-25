from ..classes import ImportSetupActionBackend


class TestImportSetupAction(ImportSetupActionBackend):
    label = 'test import setup action'

    def get_form_schema(self, **kwargs):
        kwargs.pop('import_setup')

        return super().get_form_schema(**kwargs)
