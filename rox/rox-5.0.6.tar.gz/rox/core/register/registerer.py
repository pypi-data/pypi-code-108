from rox.core.entities.rox_base import RoxBase


class Registerer:
    def __init__(self, flag_repository):
        self.flag_repository = flag_repository
        self.namespaces = set()

    def register_instance(self, container, ns):
        if ns is None:
            raise TypeError('A namespace cannot be null')

        if ns in self.namespaces:
            error_message = 'A container with the given namespace ({}) has already been registered'.format(ns)
            raise ValueError(error_message)

        self.namespaces.add(ns)

        for name, value in vars(container).items():
            if isinstance(value, RoxBase):
                self.flag_repository.add_flag(value, name if ns == '' else '%s.%s' % (ns, name))
