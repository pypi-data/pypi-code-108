from .invenio_base import InvenioBaseClassPythonBuilder


class InvenioConfigBuilder(InvenioBaseClassPythonBuilder):
    TYPE = 'invenio_config'
    class_config = 'config-dummy-class'
    template = 'config'
