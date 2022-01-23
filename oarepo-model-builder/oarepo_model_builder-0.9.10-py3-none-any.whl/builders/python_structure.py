from oarepo_model_builder.builders import process
from oarepo_model_builder.builders.python import PythonBuilder
from oarepo_model_builder.builders.utils import ensure_parent_modules
from oarepo_model_builder.stack import ModelBuilderStack


class PythonStructureBuilder(PythonBuilder):
    TYPE = 'python_structure'

    @process('/model')
    def model(self, stack: ModelBuilderStack):
        yield
        package_path = self.settings.package_path

        ensure_parent_modules(
            self.builder,
            self.builder.output_dir.joinpath(package_path / '__init__.py'),
            max_depth=len(package_path.parts)
        )
