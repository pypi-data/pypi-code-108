from .invenio_base import InvenioBaseClassPythonBuilder

class InvenioRecordPermissionsBuilder(InvenioBaseClassPythonBuilder):
    TYPE = 'invenio_record_permissions'
    class_config = 'record-permissions-class'
    template = 'record-permissions'
