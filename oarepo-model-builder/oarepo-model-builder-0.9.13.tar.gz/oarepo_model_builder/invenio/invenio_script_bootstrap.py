from oarepo_model_builder.builders import OutputBuilder
from jinja2 import Environment, FunctionLoader, pass_context

from oarepo_model_builder.builders.utils import ensure_directory
from oarepo_model_builder.templates import templates


class InvenioScriptBootstrapBuilder(OutputBuilder):
    TYPE = 'invenio_script_bootstrap'

    def finish(self):
        context = {
            'settings': self.schema.settings
        }

        env = Environment(
            loader=FunctionLoader(lambda tn: templates.get_template(tn, context['settings'])),
            autoescape=False,
        )

        ensure_directory(self.builder, 'scripts')
        output = self.builder.get_output('diff', 'scripts/bootstrap.sh')
        output.write(env.get_template('script-bootstrap').render(context))
        output.make_executable()
