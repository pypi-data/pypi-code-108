#  (C) Copyright IBM Corp. 2021.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
from .utils import *

wml_credentials = get_wml_credentials()

if 'flight_url' in wml_credentials:
    url_parts = wml_credentials['flight_url'].replace('https://', '').replace('http://', '').split(':')
    location = url_parts[0]
    port = url_parts[1] if len(url_parts) > 1 else '443'

    if "FLIGHT_SERVICE_LOCATION" not in os.environ:
        os.environ['FLIGHT_SERVICE_LOCATION'] = location

    if "FLIGHT_SERVICE_PORT" not in os.environ:
        os.environ['FLIGHT_SERVICE_PORT'] = port
