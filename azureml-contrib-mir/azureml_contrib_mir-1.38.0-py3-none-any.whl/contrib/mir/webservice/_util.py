# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
from pkg_resources import resource_string


mir_service_payload_template = json.loads(
    resource_string(__name__, 'data/mir_service_payload_template.json')
    .decode('ascii'))
