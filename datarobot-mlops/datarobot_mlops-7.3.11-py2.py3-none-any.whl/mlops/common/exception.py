#  Copyright (c) 2019 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2019.
#
#  DataRobot, Inc. Confidential.
#  This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.
#  The copyright notice above does not evidence any actual or intended publication of
#  such source code.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.

class DRCommonException(Exception):
    def __init__(self, *args, **kwargs):
        super(DRCommonException, self).__init__(args, kwargs)


class DRConfigKeyNotFound(DRCommonException):
    def __init__(self, *args, **kwargs):
        super(DRConfigKeyNotFound, self).__init__(args, kwargs)


class DRConfigKeyAlreadyAssigned(DRCommonException):
    def __init__(self, *args, **kwargs):
        super(DRConfigKeyAlreadyAssigned, self).__init__(args, kwargs)


class DRUnsupportedType(DRCommonException):
    def __init__(self, *args, **kwargs):
        super(DRUnsupportedType, self).__init__(args, kwargs)


class DRAlreadyInitialized(DRCommonException):
    def __init__(self, *args, **kwargs):
        super(DRAlreadyInitialized, self).__init__(args, kwargs)


class DRApiException(DRCommonException):
    def __init__(self, *args, **kwargs):
        super(DRApiException, self).__init__(args, kwargs)


class DRSpoolerException(DRCommonException):
    def __init__(self, *args, **kwargs):
        super(DRSpoolerException, self).__init__(args, kwargs)


class DRConnectedException(DRCommonException):
    def __init__(self, *args, **kwargs):
        super(DRConnectedException, self).__init__(args, kwargs)
