from pbr import version

__all__ = ["version_info", "version_string"]

version_info = version.VersionInfo("monasca-predictor")
version_string = version_info.version_string()
