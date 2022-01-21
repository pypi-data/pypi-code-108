"""Provides the main logic of the application"""
import logging
import semver

logger = logging.getLogger()


def get_current_version(tags):
    """Get the current version.

    Args:
        tags(list): list of git tags

    Returns:
        string: A version that corresponds to the tag that represents
                the last version.

    """
    versions = [tag[1:] for tag in tags]
    valid_versions = [version
                      for version
                      in versions
                      if semver.VersionInfo.isvalid(version)]
    semver_versions = [semver.VersionInfo.parse(version)
                       for version
                       in valid_versions]
    return str(max(semver_versions)) if semver_versions else "0.0.0"


def get_next_version(tags):
    """Get the next version."""
    versions = [tag[1:] for tag in tags]
    valid_versions = [version
                      for version
                      in versions
                      if semver.VersionInfo.isvalid(version)]
    semver_versions = [semver.VersionInfo.parse(version)
                       for version
                       in valid_versions]
    return (str(max(semver_versions).bump_patch())
            if semver_versions
            else "0.1.0")
