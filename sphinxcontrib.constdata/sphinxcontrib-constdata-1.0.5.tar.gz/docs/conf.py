# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

from datetime import date

# -- Project information -----------------------------------------------------

project = "sphinxcontrib-constdata"
author = "Matt from Documatt"
copyright = f"{date.today().year}, {author}"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx.ext.intersphinx", "sphinx_tabs.tabs", "sphinxcontrib.constdata"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

rst_epilog = f"""
.. |project| replace:: {project}
.. |rst| replace:: reStructuredText
"""

highlight_language = "none"

nitpicky = True


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_documatt_theme"

html_logo = html_favicon = "img/logo.svg"

html_theme_options = {
    "header_text": "sphinxcontrib-constdata",
    "header_logo_style": "height: 3rem;",
    "header_text_style": "margin-left: 1rem;",
    "footer_logo_style": "height: 2rem; float: right;",
    "motto": "sphinxcontrib-constdata is the extension for Sphinx documentation projects that allows showing values, listing tables, and generating links from CSV, JSON and YAML files.",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

# -- Options for sphinxcontrib.constdata -------------------------------------

constdata_files = {
    "conf.yaml": {"id": "Variable", "link": "``{Variable}``"},
    "conf2.yaml": {"id": "Variable", "link": "``{Variable}``"},
    "menu.yaml": {"label": ":menuselection:`{Path}`"},
}

# -- Options for intersphinx -------------------------------------------------

# A link like :ref:`impossible <rstref:no-inline-element-nesting>` will link
# to the label "no-inline-element-nesting" in the doc set "rstref",
# if it exists.
intersphinx_mapping = {"rstref": ("https://restructuredtext.documatt.com", None)}

# -- Hooks -------------------------------------------------------------------


def setup(app):
    app.add_object_type(
        "confval",
        "confval",
        objname="configuration value",
        indextemplate="pair: %s; configuration value",
    )
