# Gunicorn is not supported on Windows
import gunicorn.app.base  # type: ignore
# Needed to call gunicorn from Python (Results in import errors if removed)
# pylint: disable=unused-import
from gunicorn import glogging
from gunicorn.workers import sync  # type: ignore


class GunicornFlaskApplication(gunicorn.app.base.BaseApplication):  # pylint: disable=abstract-method
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(GunicornFlaskApplication, self).__init__()

    # Needed to load the options
    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    # Needed to overload base class
    def load(self):
        return self.application
