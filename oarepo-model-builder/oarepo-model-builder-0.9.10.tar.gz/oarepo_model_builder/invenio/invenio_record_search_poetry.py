from ..builders import OutputBuilder
from ..outputs.toml import TOMLOutput


class InvenioRecordSearchPoetryBuilder(OutputBuilder):
    TYPE = 'invenio_record_search_poetry'

    def finish(self):
        super().finish()

        output: TOMLOutput = self.builder.get_output(
            'toml',
            'pyproject.toml'
        )

        output.set(
            "tool.poetry.plugins.'invenio_search.mappings'",
            self.settings.python.record_mapping_poetry,
            self.settings.mapping_package
        )
