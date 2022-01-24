from .invenio_base import InvenioBaseClassPythonBuilder


class InvenioRecordResourceConfigBuilder(InvenioBaseClassPythonBuilder):
    TYPE = 'invenio_record_resource_config'
    class_config = 'record-resource-config-class'
    template = 'record-resource-config'
