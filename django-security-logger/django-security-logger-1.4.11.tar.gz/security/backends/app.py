from importlib import import_module

from django.apps import AppConfig


def import_class(path):
    module_name, class_name = path.rsplit('.', 1)
    return getattr(import_module(module_name), class_name)


class SecurityBackend(AppConfig):

    backend_name = None
    writer = None
    reader = None
    registered_writers = {}
    registered_readers = {}

    def ready(self):
        if self.reader:
            self.reader_inst = import_class(self.reader)()
            SecurityBackend.registered_readers[self.backend_name] = self.reader_inst
        if self.writer:
            self.writer_inst = import_class(self.writer)(self.backend_name)
            SecurityBackend.registered_writers[self.backend_name] = self.writer_inst
