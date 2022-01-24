class ModelPreprocessor:
    def __init__(self, builder: 'oarepo_model_builder.builder.ModelBuilder'):
        self.builder = builder

    def transform(self, schema, settings):
        pass

    def set(self, settings, name, callable=None):
        if callable:
            if not settings.get(name):
                settings[name] = callable()
            return

        def w(func):
            if not settings.get(name):
                settings[name] = func()

        return w
