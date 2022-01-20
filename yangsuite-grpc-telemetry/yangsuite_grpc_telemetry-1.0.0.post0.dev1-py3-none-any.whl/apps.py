# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
try:
    from yangsuite.apps import YSAppConfig
except:
    from django.apps import AppConfig as YSAppConfig


class YSGrpcTelemetryConfig(YSAppConfig):
    name = 'ysgrpctelemetry'
    """str: Python module name (mandatory)."""

    url_prefix = 'grpctelemetry'
    """str: Prefix under which to include this module's URLs."""

    verbose_name = 'gRPC Telemetry support for YANG Suite'
    """str: Human-readable application name."""

    menus = {
        'Protocols': [
            ('gRPC telemetry', ''),
        ],
    }
    """dict: Menu items ``{'menu': [(text, relative_url), ...], ...}``"""

    help_pages = [
        ('yangsuite-grpc-telemetry documentation', 'index.html')
    ]
    """list: of tuples ``('title', 'file path')``.

    The path is relative to the directory ``<app>/static/<app>/docs/``.
    """
