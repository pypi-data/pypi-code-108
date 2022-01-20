import logging
from module_placeholder.ui import jinja
from module_placeholder.authentication import safe_api_call
from module_placeholder.config import read_config

logger = logging.getLogger(__name__)

template = jinja.get_template('index.html')

config = read_config("config.yml")
api_key = config['api_key']


def register_routes(app):

    @app.route('/', methods=['get'])
    @safe_api_call
    def get_index():
        return template.render(api_key=api_key)
