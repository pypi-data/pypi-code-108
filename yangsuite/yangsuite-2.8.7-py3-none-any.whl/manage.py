#! /usr/bin/env python
# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.

"""Start the yangsuite server."""
import os
import sys
import logging


if __name__ == "__main__":
    log = logging.getLogger(__name__)
    log.info('trying to create Django settings')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                          "yangsuite.settings.develop")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django    # noqa: F401 - this is intentionally 'unused'
        except ImportError:
            log.error("Couldn't import Django.")
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)
