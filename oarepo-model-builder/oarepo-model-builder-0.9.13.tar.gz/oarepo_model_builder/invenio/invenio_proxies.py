from .invenio_base import InvenioBaseClassPythonBuilder


class InvenioProxiesBuilder(InvenioBaseClassPythonBuilder):
    TYPE = 'invenio_proxies'
    class_config = 'proxies-current-resource'
    template = 'proxies'
