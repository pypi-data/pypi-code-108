from .invenio_base import InvenioBaseClassPythonBuilder


class InvenioViewsBuilder(InvenioBaseClassPythonBuilder):
    TYPE = 'invenio_views'
    class_config = 'create_blueprint_from_app'
    template = 'views'
