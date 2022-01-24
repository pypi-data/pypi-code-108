# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Common constants for this package."""
import enum


class IOConstants:
    """Contains IO related constants."""

    JSON = 'json'
    UTF8 = 'utf-8'
    ARTIFACT_PREFIX = 'prefix'


class AssetProperties:
    """Contains constants for asset properties."""

    COMMENT = 'comment'
    UPLOAD_ID = 'upload_id'
    UPLOAD_TIME = 'upload_time'


class RAITool(enum.Enum):
    """Contains enums for different RAI tools."""

    EXPLANATIONS = 1
    FAIRNESS = 2
    COUNTERFACTUAL = 3
    CAUSAL = 4
    ERRORANALYSIS = 5


class PackageNames:
    """Constants for package names."""

    LIGHTGBM = 'lightgbm'


class LoggingConstants:
    """Constants for logging"""

    PUBLIC_API = 'PublicApi'
    REMOTE_JOB = 'RemoteJob'
