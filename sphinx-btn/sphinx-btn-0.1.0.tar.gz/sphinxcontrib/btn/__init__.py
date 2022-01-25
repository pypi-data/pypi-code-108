__version__ = "0.1.0"
__author__ = "Pierrick Rambaud"
__email__ = "pierrick.rambaud49@gmail.com"

from . import btn


def setup(app):
    """Install the plugin.

    :param app: Sphinx application context.
    """

    # download the font to the output folder
    app.connect("builder-inited", btn.download_font_assets)

    # create the node
    app.add_node(btn.btn, **btn._NODE_VISITORS)

    # create the role
    app.add_role("btn", btn.btn_role)

    return
