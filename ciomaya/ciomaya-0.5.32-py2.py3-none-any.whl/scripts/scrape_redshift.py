from ciomaya.lib import scraper_utils
import pymel.core as pm
from ciomaya.lib import software
"""
A scraper to collect paths from Redshift nodes.
"""


ATTRS = {
    "redshift4Maya": {
        "RedshiftBokeh": [
            "dofBokehImage"
        ],
        "RedshiftCameraMap":
        [
            "tex0"],
        "RedshiftDomeLight":
        [
            "tex0",
            "tex1"
        ],
        "RedshiftEnvironment": [
            "tex0",
            "tex1",
            "tex2",
            "tex3",
            "tex4"
        ],

        "RedshiftIESLight":
        [
            "profile"
        ],
        "RedshiftLensDistortion":
        [
            "LDimage"
        ],
        "RedshiftLightGobo":
        [
            "tex0"
        ],
        "RedshiftNormalMap":
        [
            "tex0"
        ],
        "RedshiftOptions": [
            "irradianceCacheFilename",
            "irradiancePointCloudFilename",
            "photonFilename",
            "subsurfaceScatteringFilename"
        ],
        "RedshiftPostEffects": [
            "clrMgmtOcioFilename",
            "lutFilename"
        ],
        "RedshiftProxyMesh":
        [
            "computedFileNamePattern"
        ],
        "RedshiftSprite":
        [
            "tex0"
        ],
        "RedshiftVolumeShape": [
            "computedFileNamePattern"
        ]
    }
}

TOKENS = (r"<UDIM>", r"<f\d?>",r"<Frame>" , r"#+")


def run(_):
    if not software.detect_redshift():
        return

    paths = scraper_utils.get_paths(ATTRS)
    paths += _scrape_proxies()
    paths = scraper_utils.starize_tokens(paths, *TOKENS)
    paths = scraper_utils.expand_env_vars(paths)
    paths = scraper_utils.expand_workspace(paths)
    return {"paths":paths, "env":[]}

def _scrape_proxies():
    result = []
    for node in  pm.ls(type="RedshiftProxyMesh"):
        path = node.attr("computedFileNamePattern").get()
        if path:
            for contained_path in pm.mel.eval( 'rsProxy -q -dependencies "{}"'.format(path)) or []:
                result.append({"path":contained_path, "proxy_node": node.name()})
    return result
