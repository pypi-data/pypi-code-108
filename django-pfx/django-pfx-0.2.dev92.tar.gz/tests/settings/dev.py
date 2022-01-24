"""
Development settings

Load .dev_custom if it exists for personal settings (ignored by git).
Use .dev_default directly if no.

Use: `cp dev_custom_example.py dev_custom.py to create it.`
"""

try:
    from .dev_custom import *  # noqa
except ImportError:
    from .dev_default import *  # noqa
