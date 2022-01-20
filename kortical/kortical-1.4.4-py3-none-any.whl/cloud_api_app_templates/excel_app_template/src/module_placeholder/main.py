import os
import logging
from pathlib import Path
from flask import Flask, Response
from module_placeholder.logging import logging_config
from module_placeholder.api.endpoints import register_routes

logging_config.init()

logger = logging.getLogger(__name__)


def create_app():
    current_dir = os.path.dirname(__file__)
    templates_path = os.path.join(Path(current_dir), 'templates')
    logger.info(f"Loading templates from {templates_path}")
    flask_app = Flask(__name__, template_folder=templates_path)
    register_routes(flask_app)
    return flask_app


app = create_app()
