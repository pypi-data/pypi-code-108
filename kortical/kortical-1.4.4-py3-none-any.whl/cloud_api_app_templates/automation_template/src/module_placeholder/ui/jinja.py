import logging
import os
import jinja2

logger = logging.getLogger(__name__)

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
print(f"Website template directory [{template_dir}]")

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)


def get_template(name, parent=None, globals_=None):
    return env.get_template(name, parent, globals_)
