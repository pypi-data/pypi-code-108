import sys
import simplejson as json
sys.path.insert(1, '/home/odoo/instance/odoo')
from odoo import release  # noqa: E402


print(json.dumps({
    'version': release.version,
    'major_version': release.major_version,
    'version_info': release.version_info}))
