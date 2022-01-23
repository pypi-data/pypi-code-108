from ..builders import OutputBuilder
from ..outputs.toml import TOMLOutput
from ..utils.verbose import log


class InvenioSampleAppPoetryBuilder(OutputBuilder):
    TYPE = 'invenio_sample_app_poetry'

    def finish(self):
        super().finish()

        output: TOMLOutput = self.builder.get_output(
            'toml',
            'pyproject.toml'
        )

        output.setdefault("tool.poetry.dependencies.invenio",
                          'version', '^3.5.0a1',
                          'extras', ["base", "auth", "metadata", "files", "postgresql", "elasticsearch7"],
                          'optional', True,
                          'allow-prereleases', True
                          )

        output.setdefault("tool.poetry.dependencies.invenio-records-resources",
                          'version', '^0.17.3',
                          'optional', True,
                          'allow-prereleases', True
                          )

        output.setdefault("tool.poetry.extras", 'sample-app', ['invenio', 'invenio-records-resources'])

        if output.created:
            log(log.INFO, f"""To install the sample app, run
    poetry install -E sample-app            
            """)
