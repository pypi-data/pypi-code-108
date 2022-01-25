# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.

"""All exceptions raised by Soufi."""


class SourceNotFound(Exception):
    """Raised when source cannot be located."""

    pass


class DownloadError(Exception):
    """Raised when source cannot be downloaded."""

    pass
