
_registry = {}


def register(app_label, logic_class):
    if app_label in _registry:
        raise AttributeError("The \"%s\" app is already registerd by simple_perms" % app_label)
    _registry[app_label] = logic_class()


def get_app_logic(app_label):
    return _registry.get(app_label, None)
