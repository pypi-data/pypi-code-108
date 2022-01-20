import json
from typing import Union, Dict, List
from requests import Response

import pytest
from unittest import mock

from arthurai.client.validation import validate_multistatus_response_and_get_failures


