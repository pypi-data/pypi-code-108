from .invenio_base import InvenioBaseClassPythonBuilder


class InvenioRecordServiceConfigBuilder(InvenioBaseClassPythonBuilder):
    TYPE = 'invenio_record_service_config'
    class_config = 'record-service-config-class'
    template = 'record-service-config'
