import os
import pkg_resources

PROJECT_ROOT = os.path.abspath(
    pkg_resources.resource_filename("snppy", '..')) \
    if 'PROJECT_ROOT' not in os.environ else os.environ['PROJECT_ROOT']
os.environ['PROJECT_ROOT'] = PROJECT_ROOT

os.environ['CLOUD_ROOT'] = f"gs://{os.path.basename(PROJECT_ROOT)}" \
    if 'CLOUD_ROOT' not in os.environ else os.environ['CLOUD_ROOT']

os.environ['TRACKER_PATH'] = os.path.join(
    PROJECT_ROOT, os.path.basename(PROJECT_ROOT), 'db.json')
from . import _version
__version__ = _version.get_versions()['version']
