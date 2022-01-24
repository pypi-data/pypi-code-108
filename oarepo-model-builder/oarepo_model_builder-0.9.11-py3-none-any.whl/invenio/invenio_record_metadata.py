from .invenio_base import InvenioBaseClassPythonBuilder


class InvenioRecordMetadataBuilder(InvenioBaseClassPythonBuilder):
    TYPE = 'invenio_record_metadata'
    class_config = 'record-metadata-class'
    template = 'record-metadata'
