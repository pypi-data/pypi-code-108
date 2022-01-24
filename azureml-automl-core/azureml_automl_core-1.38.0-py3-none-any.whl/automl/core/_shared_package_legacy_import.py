# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import importlib
import os
import sys
from importlib.util import spec_from_loader
from typing import List


def handle_legacy_shared_package_imports():
    # Note: the code in the 'shared' package is used directly by some AutoML components that live in the
    # Jasmine repo. This shared package used to be importable under different namespaces.
    # For the sake of backwards compatibility (not breaking legacy code still using these imports),
    # we redirect legacy aliases to the 'shared' module they intend to reference.
    legacy_aliases = [
        "automl.client.core.common",
        "azureml.automl.core._vendor.automl.client.core.common",
    ]

    # The following two lines existed in the code before the removal of vendoring for the shared module.
    # They enable top-level importing of packages that exist under the _vendor folder.
    # For instance, they enable 'import automl', even though the automl package is inside the _vendor folder.
    vendor_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "_vendor"))
    sys.path.append(vendor_folder)

    # Add the SharedPackageMetaPathFinder to the sys.meta_path.
    # Our finder must be added at the beginning of the meta path. Otherwise, the standard system
    # importers can intercept the package import and create duplicate module objects for code from
    # the same file on disk. For instance, if
    # import azureml.automl.core.shared.x as x1
    # import automl.client.core.common.x as x2
    # x1 and x2 may not be the same exact object, and so x1 == x2 could evaluate to False.
    sys.meta_path.insert(0, SharedPackageMetaPathFinder(
        shared_pacakge_current_alias='azureml.automl.core.shared',
        shared_package_legacy_aliases=legacy_aliases))


class SharedPackageMetaPathFinder(importlib.abc.MetaPathFinder):
    """Meta path finder that redirects legacy shared package imports."""

    def __init__(
        self,
        shared_pacakge_current_alias: str,
        shared_package_legacy_aliases: List[str]
    ) -> None:
        self._shared_pacakge_current_alias = shared_pacakge_current_alias
        self._shared_package_legacy_aliases = shared_package_legacy_aliases

    def find_spec(self, fullname, path, target=None):
        """Implement find_spec method of abstract importlib.abc.MetaPathFinder base class."""
        for shared_package_legacy_alias in self._shared_package_legacy_aliases:
            if fullname.startswith(shared_package_legacy_alias):
                current_alias = fullname.replace(shared_package_legacy_alias, self._shared_pacakge_current_alias)
                loader = SharedPackageModuleLoader(current_alias, fullname)
                return spec_from_loader(fullname, loader)
        return None


class SharedPackageModuleLoader(importlib.abc.Loader):
    """Module loader for legacy shared package imports."""

    def __init__(self, current_alias, legacy_alias):
        self._current_alias = current_alias
        self._legacy_alias = legacy_alias

    def create_module(self, spec):
        return importlib.import_module(self._current_alias)

    def exec_module(self, module):
        pass
