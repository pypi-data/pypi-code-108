# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Proxies for accessing the currently instantiated requests extension."""

from flask import current_app
from werkzeug.local import LocalProxy

current_requests = LocalProxy(lambda: current_app.extensions["invenio-requests"])
"""Proxy for the instantiated requests extension."""

current_registry = LocalProxy(
    lambda: current_app.extensions["invenio-requests"].request_type_registry
)
"""Proxy for the instantiated request type registry."""

current_requests_service = LocalProxy(
    lambda: current_app.extensions["invenio-requests"].requests_service
)
"""Proxy to the instantiated requests service."""

current_events_service = LocalProxy(
    lambda: current_app.extensions["invenio-requests"].request_events_service
)
"""Proxy to the instantiated requests service."""

current_requests_resource = LocalProxy(
    lambda: current_app.extensions["invenio-requests"].requests_resource
)
"""Proxy to the instantiated requests resource."""
