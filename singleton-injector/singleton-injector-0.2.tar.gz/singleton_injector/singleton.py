class Singleton:
    def __init__(self):
        self.instances = {}

    def __call__(self, _class):
        def wrapper(*args, **kwargs):
            if _class not in self.instances:
                self.instances[_class] = _class(*args, **kwargs)
            return self.instances[_class]

        return wrapper
