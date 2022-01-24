from .invenio_base import InvenioBaseClassPythonBuilder


class InvenioRecordServiceBuilder(InvenioBaseClassPythonBuilder):
    TYPE = 'invenio_record_service'
    class_config = 'record-service-class'
    template = 'record-service'
