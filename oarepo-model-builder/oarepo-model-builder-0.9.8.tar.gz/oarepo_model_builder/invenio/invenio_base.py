from oarepo_model_builder.builders.python import PythonBuilder
from oarepo_model_builder.outputs.python import PythonOutput
from oarepo_model_builder.utils.hyphen_munch import HyphenMunch
from oarepo_model_builder.utils.jinja import package_name


class InvenioBaseClassPythonBuilder(PythonBuilder):
    class_config = None
    template = None

    def finish(self, **extra_kwargs):
        python_path = self.class_to_path(self.settings.python[self.class_config])
        self.process_template(python_path, self.template,
                              current_package_name=package_name(self.settings.python[self.class_config]),
                              **extra_kwargs)

    def process_template(self, python_path, template, **extra_kwargs):
        self.create_parent_modules(python_path)
        output: PythonOutput = self.builder.get_output(
            'python',
            python_path
        )
        context = HyphenMunch(settings=self.settings, python=self.settings.python,
                              **extra_kwargs)
        template = self.call_components('invenio_before_python_template', template, context=context)
        output.merge(
            template,
            context
        )
