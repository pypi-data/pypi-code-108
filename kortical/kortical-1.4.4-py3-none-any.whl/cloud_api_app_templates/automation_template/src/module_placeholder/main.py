import os
import logging
from pathlib import Path
from flask import Flask
from module_placeholder.logger import logging_config
from module_placeholder.api import endpoints
from module_placeholder.ui import index

logging_config.init()

logger = logging.getLogger(__name__)


def create_app():
    current_dir = os.path.dirname(__file__)
    static_path = os.path.join(Path(current_dir), 'ui', 'static')
    flask_app = Flask(__name__, static_url_path=static_path)
    endpoints.register_routes(flask_app)
    index.register_routes(flask_app)
    return flask_app


app = create_app()
