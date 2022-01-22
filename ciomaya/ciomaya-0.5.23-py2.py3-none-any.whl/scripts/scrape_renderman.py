"""
A scraper to collect paths from Renderman nodes.
"""

from ciomaya.lib import scraper_utils, renderman_path_utils


# See https://rmanwiki.pixar.com/display/RFM22/String+tokens+in+RfM
TOKENS = (r"_MAPID_", r"<udim>", r"<frame>", r"<f\d?>", r"<aov>", r"#+")

def run(_):
    paths = scraper_utils.get_paths(renderman_path_utils.ATTRS)
    paths = scraper_utils.starize_tokens(paths, *TOKENS)
    paths = scraper_utils.expand_workspace(paths)
    paths = scraper_utils.extend_with_tx_paths(paths)
    return {"paths":paths, "env":[]}