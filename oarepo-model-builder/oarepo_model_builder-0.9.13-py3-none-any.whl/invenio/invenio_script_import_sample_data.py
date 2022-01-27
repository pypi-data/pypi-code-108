from .invenio_base import InvenioBaseClassPythonBuilder


class InvenioScriptImportSampleDataBuilder(InvenioBaseClassPythonBuilder):
    TYPE = 'invenio_script_import_sample_data'
    class_config = 'script-import-sample-data-cli'
    template = 'script-import-sample-data'
    parent_modules = False

    def process_template(self, python_path, template, **extra_kwargs):
        super().process_template(python_path, template, **extra_kwargs)
