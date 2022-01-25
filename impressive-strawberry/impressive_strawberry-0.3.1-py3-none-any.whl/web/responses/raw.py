"""
This module contains common HTTP responses that the app can return.
"""

import starlette.responses

NO_CONTENT = starlette.responses.Response(content=None, status_code=204)
