# Copyright (C) 2021  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from celery import shared_task

from swh.loader.package.maven.loader import MavenLoader


@shared_task(name=__name__ + ".LoadMaven")
def load_jar_file(*, url=None, artifacts=None):
    """Load jar's artifacts."""
    loader = MavenLoader.from_configfile(url=url, artifacts=artifacts)
    return loader.load()
