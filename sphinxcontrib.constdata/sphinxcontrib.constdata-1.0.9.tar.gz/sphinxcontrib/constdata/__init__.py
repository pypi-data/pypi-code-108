from typing import Any, Dict

import pbr.version
from sphinx.application import Sphinx

from sphinxcontrib.constdata.domain import ConstdataDomain
from sphinxcontrib.constdata.flatfiles import cache_flatfiles, close_cachedb
from sphinxcontrib.constdata.l10n import CsvMessageCatalogBuilder
from sphinxcontrib.constdata.link_role import constdatalinknode, process_link_nodes
from sphinxcontrib.constdata.settings import (
    CONFIG_CSV_FORMAT,
    CONFIG_CSV_FORMAT_DEFAULT,
    CONFIG_FILES,
    CONFIG_FILES_ENCODING,
    CONFIG_FILES_ENCODING_DEFAULT,
    CONFIG_POT_MSG_FLAGS,
    CONFIG_POT_MSG_FLAGS_DEFAULT,
    CONFIG_ROOT,
    CONFIG_ROOT_DEFAULT,
    CONFIG_TARGET_TEMPLATE,
    CONFIG_TARGET_TEMPLATE_DEFAULT,
    CONFIG_TEMPLATES_DEFAULT,
)

if False:
    # For type annotations
    from typing import Any, Dict  # noqa

    from sphinx.application import Sphinx  # noqa

__version__ = pbr.version.VersionInfo("sphinxcontrib.constdata").version_string()
# __version__ = "0.0.0"


def setup(app: Sphinx) -> Dict[str, Any]:
    # -- Config values --------------------------------------------------------

    app.add_config_value(CONFIG_ROOT, CONFIG_ROOT_DEFAULT, "env")
    app.add_config_value(CONFIG_CSV_FORMAT, CONFIG_CSV_FORMAT_DEFAULT, "env")
    app.add_config_value(CONFIG_FILES_ENCODING, CONFIG_FILES_ENCODING_DEFAULT, "env")
    app.add_config_value(CONFIG_TARGET_TEMPLATE, CONFIG_TARGET_TEMPLATE_DEFAULT, "env")
    app.add_config_value(CONFIG_FILES, CONFIG_TEMPLATES_DEFAULT, "env")
    app.add_config_value(CONFIG_POT_MSG_FLAGS, CONFIG_POT_MSG_FLAGS_DEFAULT, "env")

    # --- Cachedb --------------------------------------------------------------
    # create cachedb & cache all found flatfiles to DB
    app.connect("builder-inited", cache_flatfiles, 200)
    app.connect("build-finished", close_cachedb)

    # -- Domain ---------------------------------------------------------------

    app.add_domain(ConstdataDomain)

    # -- Nodes ----------------------------------------------------------------

    app.add_node(constdatalinknode)

    # Replace constdatalinknode (created by :constdata:link:) to an actual Docutils
    # ref node
    app.connect("doctree-resolved", process_link_nodes)

    # -- l10n -----------------------------------------------------------------
    # Override builtin "gettext" builder
    app.add_builder(CsvMessageCatalogBuilder, override=True)

    return {"version": __version__, "parallel_read_safe": True}
