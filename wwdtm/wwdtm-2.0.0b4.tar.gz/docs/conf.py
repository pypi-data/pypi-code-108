# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
#
# Copyright (c) 2018-2021 Linh Pham
# wwdtm is released under the terms of the Apache License 2.0
import os
import sys

from pallets_sphinx_themes import ProjectLink  # type: ignore

sys.path.insert(0, os.path.abspath('../'))

project = "wwdtm"
copyright = "2021 Linh Pham"
author = "Linh Pham"

extensions = [
    "pallets_sphinx_themes",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "sphinx_copybutton",
    "sphinx_toolbox.more_autodoc.typehints",
    "sphinx_autodoc_typehints",
]

templates_path = [
    "_templates",
]

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    ".git",
    "venv",
]

html_theme = "flask"

html_context = {
    "project_links": [
        ProjectLink("Source Code", "https://github.com/questionlp/wwdtm"),
        ProjectLink("Stats API", "https://api.wwdt.me/"),
        ProjectLink("Stats Page", "https://stats.wwdt.me/"),
        ProjectLink("Graphs Site", "https://graphs.wwdt.me/"),
        ProjectLink("Reports Site", "https://reports.wwdt.me/"),
    ]
}

html_sidebars = {
    "index": [
        "globaltoc.html",
        "project.html",
        "searchbox.html",
    ],
    "**": [
        "globaltoc.html",
        "localtoc.html",
        "relations.html",
        "project.html",
        "searchbox.html"
    ],
}

html_static_path = [
    "_static",
]

html_css_files = [
    "css/custom.css",
]

html_show_sourcelink = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

always_document_param_types = True
