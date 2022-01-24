from ..builders import OutputBuilder
from ..outputs.toml import TOMLOutput


class InvenioRecordResourcePoetryBuilder(OutputBuilder):
    TYPE = 'invenio_record_resource_poetry'

    def finish(self):
        super().finish()

        output: TOMLOutput = self.builder.get_output(
            'toml',
            'pyproject.toml'
        )

        register_function = self.settings.python.create_blueprint_from_app.rsplit('.', maxsplit=1)

        output.set("tool.poetry.plugins.'invenio_base.api_blueprints'",
                   self.settings.python.record_resource_blueprint_name,
                   f'{register_function[0]}:{register_function[-1]}'
                   )
