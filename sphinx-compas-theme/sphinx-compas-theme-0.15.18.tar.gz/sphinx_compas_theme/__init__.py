import os
import sys

__version__ = '0.15.18'


def get_html_theme_path():
    theme_path = os.path.abspath(os.path.dirname(__file__))
    return [theme_path]


def get_autosummary_templates_path():
    theme_path = get_html_theme_path()[0]
    templates_path = os.path.join(theme_path, 'templates')
    return [templates_path]


def get_extensions_path():
    theme_path = get_html_theme_path()[0]
    extensions_path = os.path.join(theme_path, 'ext')
    return extensions_path


def get_html_static_path():
    theme_path = get_html_theme_path()[0]
    static_path = os.path.join(theme_path, 'shared', 'static')
    return [static_path]


def setup(app):
    if hasattr(app, 'add_html_theme'):
        theme_path = get_html_theme_path()[0]

        app.add_html_theme('compas', os.path.join(theme_path, 'compas'))
        app.add_html_theme('compaspkg', os.path.join(theme_path, 'compaspkg'))


sys.path.append(get_extensions_path())
