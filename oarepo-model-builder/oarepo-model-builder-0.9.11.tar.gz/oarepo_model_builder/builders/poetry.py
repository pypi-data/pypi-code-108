from ..builders import OutputBuilder
from ..outputs.toml import TOMLOutput
from ..utils.verbose import log


class PoetryBuilder(OutputBuilder):
    TYPE = 'poetry'

    def finish(self):
        super().finish()

        output: TOMLOutput = self.builder.get_output(
            'toml',
            'pyproject.toml'
        )

        output.setdefault("tool.poetry",
                          "name", self.settings.package_base.replace('_', '-'),
                          "version", "0.0.1",
                          "description", f"A sample application for {self.settings.package}",
                          "authors", [])

        output.setdefault("build-system",
                          "requires", ['poetry-core>=1.0.0'],
                          "build-backend", "poetry.core.masonry.api")

        output.setdefault("tool.poetry.dependencies", "python", "^3.9")

        if 'runtime-dependencies' in self.schema.schema:
            output.table("tool.poetry.dependencies")
            for dep, value in self.schema.schema.runtime_dependencies.items():
                if isinstance(value, str):
                    value = {'version': value}
                output.setdefault("tool.poetry.dependencies." + dep, *sum((list(x) for x in value.items()), []))

        if 'dev-dependencies' in self.schema.schema:
            output.table("tool.poetry.dev-dependencies")
            for dep, value in self.schema.schema.dev_dependencies.items():
                if isinstance(value, str):
                    value = {'version': value}
                output.setdefault("tool.poetry.dev-dependencies." + dep, *sum((list(x) for x in value.items()), []))

        if output.created:
            log(log.INFO, f"""To install the sample app, run
    poetry install -E sample-app            
            """)
