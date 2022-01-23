from ..builders import OutputBuilder
from ..outputs.toml import TOMLOutput


class InvenioRecordMetadataModelsPoetryBuilder(OutputBuilder):
    TYPE = 'invenio_record_metadata_models_poetry'

    def finish(self):
        super().finish()

        output: TOMLOutput = self.builder.get_output(
            'toml',
            'pyproject.toml'
        )

        metadata_package = self.settings.python.record_metadata_class.rsplit('.', maxsplit=1)[0]

        output.set(
            "tool.poetry.plugins.'invenio_db.models'",
            self.settings.python.record_schema_metadata_poetry,
            metadata_package
        )
