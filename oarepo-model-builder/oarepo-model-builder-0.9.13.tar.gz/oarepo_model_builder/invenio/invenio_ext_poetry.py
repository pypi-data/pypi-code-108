from ..builders import OutputBuilder
from ..outputs.toml import TOMLOutput


class InvenioExtPoetryBuilder(OutputBuilder):
    TYPE = 'invenio_ext_poetry'

    def finish(self):
        super().finish()

        output: TOMLOutput = self.builder.get_output(
            'toml',
            'pyproject.toml'
        )

        ext_class = self.settings.python.ext_class.rsplit('.', maxsplit=1)

        output.set("tool.poetry.plugins.'invenio_base.api_apps'",
                   self.settings.package,
                   f'{ext_class[0]}:{ext_class[-1]}'
                   )
