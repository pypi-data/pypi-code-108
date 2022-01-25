"""Module containing the logic for the Template application."""

from flask import Flask
from gtunrealdevice import version
from gtunrealdevice import edition


__version__ = version
__edition__ = edition


app = Flask(__name__)


class Application:
    def run(self):
        """Launch gtunrealdevice application."""
        app.run()


def execute():
    """Launch gtunrealdevice application."""
    app.run()


@app.route('/')
def index():
    return '<h1>Hello GT Unreal Device</h1>'

