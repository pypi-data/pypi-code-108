from ..builders import OutputBuilder
from ..outputs.toml import TOMLOutput


class InvenioRecordJSONSchemasPoetryBuilder(OutputBuilder):
    TYPE = 'invenio_record_jsonschemas_poetry'

    def finish(self):
        super().finish()

        output: TOMLOutput = self.builder.get_output(
            'toml',
            'pyproject.toml'
        )

        output.set(
            "tool.poetry.plugins.'invenio_jsonschemas.schemas'",
            self.settings.python.record_jsonschemas_poetry,
            self.settings.jsonschemas_package
        )
