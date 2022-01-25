"""
Copyright 2021 DataRobot, Inc. and its affiliates.

All rights reserved.

DataRobot, Inc. Confidential.

This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.

The copyright notice above does not evidence any actual or intended publication of such source code.

Released under the terms of DataRobot Tool and Utility Agreement.
"""

from datarobot_bp_workshop.settings import Settings


class FriendlyRepr(object):
    def __friendly_repr__(self):
        return super(FriendlyRepr, self).__repr__()

    def __repr__(self):
        if Settings().is_dev_mode:
            return super(FriendlyRepr, self).__repr__()
        return self.__friendly_repr__()
