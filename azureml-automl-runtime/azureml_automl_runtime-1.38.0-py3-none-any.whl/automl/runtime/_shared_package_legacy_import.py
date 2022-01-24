# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import sys

from azureml.automl.core._shared_package_legacy_import import SharedPackageMetaPathFinder


def handle_legacy_shared_package_imports():
    # Note: the code in the 'shared' package is used directly by some AutoML components that live in the
    # Jasmine repo. This shared package used to be importable under different namespaces.
    # For the sake of backwards compatibility (not breaking legacy code still using these imports),
    # we redirect legacy aliases to the 'shared' module they intend to reference.
    legacy_aliases = [
        "automl.client.core.runtime",
        "azureml.automl.runtime._vendor.automl.client.core.runtime",
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
    # import azureml.automl.runtime.shared.x as x1
    # import automl.client.core.runtime.x as x2
    # x1 and x2 may not be the same exact object, and so x1 == x2 could evaluate to False.
    sys.meta_path.insert(0, SharedPackageMetaPathFinder(
        shared_pacakge_current_alias='azureml.automl.runtime.shared',
        shared_package_legacy_aliases=legacy_aliases))
