from .invenio_base import InvenioBaseClassPythonBuilder


class InvenioRecordBuilder(InvenioBaseClassPythonBuilder):
    TYPE = 'invenio_record'
    class_config = 'record-class'
    template = 'record'
