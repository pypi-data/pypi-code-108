"""Utilities for Azure integration.

This module does not assume that the Azure Python SDK is installed (no Azure top-level import) and
can be safely imported without testing for the presence of the SDK.
"""

import os
from typing import Dict, Optional, Tuple


def test_for_azure_libs() -> bool:
    """Emit a warning if the Azure Python SDK is not installed.

    Return:
        true if the Azure Python SDK is installed.
    """
    try:
        return True
    except ImportError as e:
        import warnings

        warnings.warn(
            f"Azure Python SDK not found ({str(e)}). The SDK is required for the Azure integration. You can install the Azure extras with: pip install terality[azure]"
        )
        return False


def parse_azure_filesystem(
    fs_url: str, storage_options: Optional[Dict] = None
) -> Tuple[str, str, str]:
    """Return a tuple (storage account name, container name, blob name) from a Azure Datalake Gen2 filesystem URL.

    Mimics the implementation from adlfs (https://github.com/dask/adlfs), supporting only Gen2 storage.
    Pattern: "abfs://{container}/{path}", account_name in storage_options.
    Unlike abfs, for simplicy, we treat the path as either a folder name, or a file name (no support for globs)
    """
    if storage_options is None:
        storage_options = {}
    storage_account_name = storage_options.get("account_name")
    if storage_account_name is None:
        storage_account_name = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME")
    if storage_account_name is None:
        raise ValueError(
            "Azure storage account name not set. Set the `storage_options` parameter to a dictionary containing the key `account_name`."
        )
    if fs_url.startswith("abfs://"):
        container, path = fs_url[len("abfs://") :].split("/", maxsplit=1)
    elif fs_url.startswith("az://"):
        container, path = fs_url[len("az://") :].split("/", maxsplit=1)
    else:
        raise ValueError(f"Unsupported filesystem scheme: '{fs_url}'")
    return storage_account_name, container, path
