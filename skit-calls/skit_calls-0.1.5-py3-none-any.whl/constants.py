"""
Common constants used by the package.

We maintain this file to make sure that we don't have inconsistencies in the
constants used. It is common to notice spelling mistakes associated with strings
additionally, we don't get IDE's to automatically suggest values.

consider:

```python
a_dict["key"]
```

and 

```
a_dict[const.KEY]
```
In the latter, a mature IDE will suggest the KEY constant, reducing time and ensuring consistency.
"""
AUTHORIZATION = "authorization"
ROUTE__CALL = "/call_report/calls/"
ROUTE__TURN = "/call_report/calls/{}/"
LIVE = "live"
SUBTESTING = "subtesting"

# ----------- Tagged calls are one of the following -----------
REPORTED = "reported"
RESOLVED = "resolved"
# but if there are no preferences, we can get
# all calls.
ALL = "all"
# ------------------------------------------------------------

# --------------------- Get call params ----------------------
START_DATE = "start"
END_DATE = "end"
LANG_CODE = "lang_code"
PAGE_SIZE = "page_size"
CALL_TYPE = "call_type"
IGNORED_CALLER_NUMBERS = "ignored_caller_numbers"
TAB = "tab"
PAGE = "page"
CUSTOM_SEARCH_KEY = "custom_search_key"
CUSTOM_SEARCH_VALUE = "custom_search_value"

# These are system generated pings and are never required
DEFAULT_IGNORE_CALLERS_LIST = ["ev-connect", "0000000000"]
# ---------------------------------------------------------

# ----------- columns in the calls+turns list -------------
TOTAL_PAGES = "total_pages"
TOTAL_ITEMS = "total_items"
ITEMS = "items"
UUID = "uuid"
CONV_UUID = "conversation_uuid"
CALL_UUID = "call_uuid"
TURNS = "turns"
CONVERSATIONS = "conversations"
PREDICTION = "prediction"
METADATA = "metadata"
DEBUG_METADATA = "debug_metadata"
CREATED_AT = "created_at"
UPDATED_AT = "updated_at"
# ---------------------------------------------------------

# ------------------------- cli -----------------------------------
DESCRIPTION = """
Skit.ai's calls library {version}.

We provide means to sample calls and conversations from a 
specified environment.

Learn about this library at: https://github.com/skit-ai/skit-calls
""".strip()
# ------------------------------------------------------------------

FILES = "files"
IN_MEMORY = "in-memory"
MEMORY_LIMIT = 10e7
DEFAULT_API_GATEWAY_URL = "https://apigateway.vernacular.ai"
DEFAULT_CALL_QUANTITY = 200
DEFAULT_TIMEZONE = "Asia/Kolkata"
