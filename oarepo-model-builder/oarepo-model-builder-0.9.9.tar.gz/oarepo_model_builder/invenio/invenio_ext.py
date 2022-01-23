from .invenio_base import InvenioBaseClassPythonBuilder


class InvenioExtBuilder(InvenioBaseClassPythonBuilder):
    TYPE = 'invenio_ext'
    class_config = 'ext-class'
    template = 'ext'

