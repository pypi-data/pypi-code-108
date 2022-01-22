# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo Micro API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""OArepo Micro API Signal handlers."""

from flask import request_finished

from oarepo_micro_api.utils import is_api_request


@request_finished.connect
def set_no_cache_header(sender, response, **extra):
    """Sets no-cache header on all API responses."""
    if is_api_request():
        # The response may be stored by any cache, even if the response is
        # normally non-cacheable. However, the stored response MUST always
        # go through validation with the origin server first before using it.
        response.headers['Cache-Control'] = 'no-cache'
