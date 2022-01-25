from oarepo_model_builder.outputs import OutputBase
from difflib import Differ


class DiffOutput(OutputBase):
    TYPE = 'diff'

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
            if self.original_data:
                lines = [
                    x[2:]
                    for x in Differ().compare(self.original_data.splitlines(), self.text.splitlines())
                    if x[0] != '?'
                ]
            else:
                lines = [self.text]

            with self.builder.filesystem.open(self.path, 'w') as f:
                f.write('\n'.join(lines))

    def write(self, text):
        self.text = text
