# -*- coding: utf-8 -*-

project = 'toasty'
author = 'Chris Beaumont and the AAS WorldWide Telescope Team'
copyright = '2014-2020, ' + author

release = '0.dev0'  # cranko project-version
version = '.'.join(release.split('.')[:2])

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx_automodapi.automodapi',
    'sphinx_automodapi.smart_resolver',
    'numpydoc',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
language = None
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'
todo_include_todos = False

html_theme = 'bootstrap-astropy'
html_theme_options = {
    'logotext1': 'toasty',
    'logotext2': '',
    'logotext3': ':docs',
    'astropy_project_menubar': False,
}
html_static_path = ['_static']
htmlhelp_basename = 'toastydoc'

intersphinx_mapping = {
    'python': (
        'https://docs.python.org/3/',
        (None, 'http://data.astropy.org/intersphinx/python3.inv')
    ),

    'astropy': (
        'https://docs.astropy.org/en/stable/',
        None
    ),

    'numpy': (
        'https://numpy.org/doc/stable/',
        (None, 'http://data.astropy.org/intersphinx/numpy.inv')
    ),

    'PIL': (
        'https://pillow.readthedocs.io/en/stable/',
        None
    ),

    'wwt_data_formats': (
        'https://wwt-data-formats.readthedocs.io/en/stable/',
        None
    ),
}

numpydoc_show_class_members = False

nitpicky = True
nitpick_ignore = [
    ('py:class', 'ipywidgets.widgets.domwidget.DOMWidget')
]

default_role = 'obj'

html_logo = 'images/logo.png'

linkcheck_retries = 5
linkcheck_timeout = 10
