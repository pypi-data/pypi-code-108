"""
Configuration file for the Sphinx documentation builder.
"""
# -- stdlib imports ------------------------------------------------------------
import datetime
import os
import sys
import warnings

from packaging.version import Version
from pkg_resources import get_distribution

# -- Check for dependencies ----------------------------------------------------
doc_requires = get_distribution("dkist_processing_common").requires(extras=("docs",))
missing_requirements = []
for requirement in doc_requires:
    try:
        get_distribution(requirement)
    except Exception as e:
        missing_requirements.append(requirement.name)
if missing_requirements:
    print(
        f"The {' '.join(missing_requirements)} package(s) could not be found and "
        "is needed to build the documentation, please install the 'docs' requirements."
    )
    sys.exit(1)

# -- Non stdlib imports --------------------------------------------------------
import dkist_processing_common  # NOQA
from dkist_processing_common import __version__  # NOQA

# -- Project information -------------------------------------------------------
project = "DKIST-PROCESSING-COMMON"
author = "NSO / AURA"
copyright = "{}, {}".format(datetime.datetime.now().year, author)

# The full version, including alpha/beta/rc tags
release = __version__
dkist_version = Version(__version__)
is_release = not (dkist_version.is_prerelease or dkist_version.is_devrelease)

# We want to ignore all warnings in a release version.
if is_release:
    warnings.simplefilter("ignore")

# Suppress warnings about overriding directives as we overload some of the
# doctest extensions.
suppress_warnings = [
    "app.add_directive",
]

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "matplotlib.sphinxext.plot_directive",
    "autoapi.extension",
    "sphinx_changelog",
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sunpy.util.sphinx.doctest",
    "sunpy.util.sphinx.generate",
]

autoapi_dirs = ["../dkist_processing_common"]
autoapi_template_dir = "./templates"
autoapi_ignore = ["*tests*"]
# Set this to true to aid in debugging errors/warnings
# autoapi_keep_files = True
autodoc_typehints = "description"
# WE must include the defaults if we customize otherwise the defaults get clobbered
autoapi_default_options = [
    "members",
    "undoc-members",
    "private-members",
    "show-inheritance",
    "show-module-summary",
    "special-members",
    "imported-members",
]
# Customizations we want
autoapi_custom_options = [
    "show-inheritance-diagram",
    "inherited-members",
]
autoapi_options = autoapi_default_options + autoapi_custom_options

# Add any paths that contain templates here, relative to this directory.
# templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied

# The suffix(es) of source filenames.
# You can specify multiple suffixes as a list of strings:
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# The reST default role (used for this markup: `text`) to use for all
# documents. Set to the "smart" one.
default_role = "obj"

# Disable having a separate return type row
napoleon_use_rtype = False

# Disable google style docstrings
napoleon_google_docstring = False

# -- Options for intersphinx extension -----------------------------------------
# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    "python": (
        "https://docs.python.org/3/",
        (None, "http://www.astropy.org/astropy-data/intersphinx/python3.inv"),
    ),
    "numpy": (
        "https://numpy.org/doc/stable/",
        (None, "http://www.astropy.org/astropy-data/intersphinx/numpy.inv"),
    ),
    "scipy": (
        "https://docs.scipy.org/doc/scipy/reference/",
        (None, "http://www.astropy.org/astropy-data/intersphinx/scipy.inv"),
    ),
    "matplotlib": (
        "https://matplotlib.org/",
        (None, "http://www.astropy.org/astropy-data/intersphinx/matplotlib.inv"),
    ),
    "astropy": ("https://docs.astropy.org/en/stable/", None),
    "parfive": ("https://parfive.readthedocs.io/en/stable/", None),
    "sunpy": ("http://docs.sunpy.org/en/latest/", None),
    "ndcube": ("http://docs.sunpy.org/projects/ndcube/en/latest/", None),
    "gwcs": ("http://gwcs.readthedocs.io/en/latest/", None),
    "asdf": ("http://asdf.readthedocs.io/en/latest/", None),
    "dask": ("http://dask.pydata.org/en/latest/", None),
    # dkist_processing_common depends only on dkist_processing_core for internal cross references
    "dkist_processing_core": (
        "https://dkistdc-public-documentation.readthedocs-hosted.com/projects/dkistdc-dkist-processing-core/en/latest/",
        None,
    ),
}

# -- Options for HTML output ---------------------------------------------------
# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
from dkist_sphinx_theme.conf import *

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".

# Render inheritance diagrams in SVG
graphviz_output_format = "svg"
graphviz_dot_args = [
    "-Nfontsize=10",
    "-Nfontname=Helvetica Neue, Helvetica, Arial, sans-serif",
    "-Efontsize=10",
    "-Efontname=Helvetica Neue, Helvetica, Arial, sans-serif",
    "-Gfontsize=10",
    "-Gfontname=Helvetica Neue, Helvetica, Arial, sans-serif",
]
# Use a top-to-bottom orientation for the diagrams
inheritance_graph_attrs = dict(rankdir="TB")
