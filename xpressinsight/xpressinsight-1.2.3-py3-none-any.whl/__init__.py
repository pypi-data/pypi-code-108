"""
    Xpress Insight Python package
    =============================

    The 'xpressinsight' Python package can be used to develop Python based web
    applications for Xpress Insight.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2020-2022 Fair Isaac Corporation. All rights reserved.
"""
#

#
__version__ = '1.2.3'  #

from .exec_mode import ExecMode, ExecModeRun, ExecModeLoad
from .types import (
    AppVersion, ResultData, ResultDataDelete, Manage, Hidden,
    boolean, integer, string, real,
    Scalar, Param, Index, Series, DataFrame, Column,
)
from .app_base import AppConfig, AppBase
from .interface import (
    Attachment,
    AttachmentRules,
    AttachStatus,
    AttachTag,
    AttachTagUsage,
    AppInterface,
    ItemInfo,
    ObjSense,
    Metric,
    InterfaceError,
)
from .interface_test import (
    read_attach_info,
    write_attach_info,
)
from .repository_path import RepositoryPath
from .test_runner import create_app
