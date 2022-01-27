from .invenio_base import InvenioBaseClassPythonBuilder


class InvenioRecordResourceBuilder(InvenioBaseClassPythonBuilder):
    TYPE = 'invenio_record_resource'
    class_config = 'record-resource-class'
    template = 'record-resource'
