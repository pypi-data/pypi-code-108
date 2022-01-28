from code_generator.app.model import Model


class ModelCodeBlock(Model):
    code = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.code is None:
            raise Exception(f'Не задан код.')

    def __str__(self):
        return self.code.split('\n')


class TypeScriptCodeBlock(ModelCodeBlock):
    pass


class PythonCodeBlock(ModelCodeBlock):
    pass
