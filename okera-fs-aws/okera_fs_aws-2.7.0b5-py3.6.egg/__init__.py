# Copyright Okera Inc.
#
#
#
# pylint: disable=wrong-import-order
from . import _version
__version__ = _version.get_versions()['version']

from okera_fs_aws.plugin.aws import awscli_initialize

