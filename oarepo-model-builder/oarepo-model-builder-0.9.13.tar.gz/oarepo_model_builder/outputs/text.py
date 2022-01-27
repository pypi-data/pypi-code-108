from oarepo_model_builder.outputs import OutputBase


class TextOutput(OutputBase):
    TYPE = 'text'

    def begin(self):
        try:
            with self.builder.filesystem.open(self.path) as f:
                self.text = self.original_data = f.read()
        except FileNotFoundError:
            self.original_data = None
            self.text = ''

    @property
    def created(self):
        return self.original_data is None

    def finish(self):
        if self.text != self.original_data:
            with self.builder.filesystem.open(self.path, 'w') as f:
                f.write(self.text)
