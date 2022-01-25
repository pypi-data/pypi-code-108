"""
enable the same static url (e.g. /static) search multi folders (e.g. /static /upload)
* author: City10th
* email: city10th@foxmail.com
* [github](https://github.com/city10th/samstatic_flask)
"""


__all__ = ['FlaskWithSamStatic', 'SamStatic']

from types import MethodType

from .app import FlaskWithSamStatic
from .config import Option
from .helper import set_samstatic_default_parm

class SamStatic:
    options = Option

    def __init__(self, app):
        set_samstatic_default_parm(app)

        if app.config['SAMSTATIC_ENDPOINTS'] == Option.DEACTIVE:
            return

        app.request_context = MethodType(FlaskWithSamStatic.request_context, app)
        app.get_static_endpoints = MethodType(FlaskWithSamStatic.get_static_endpoints, app)