#  Copyright (c) 2019 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2021.
#
#  DataRobot, Inc. Confidential.
#  This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.
#  The copyright notice above does not evidence any actual or intended publication of
#  such source code.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.

from enum import Enum


class DatasetSourceType(Enum):
    """
    Dataset association type.
    Used to mark uploaded dataset as TRAINING or SCORING
    for a deployment within DataRobot MLOps.
    """
    TRAINING = "training"
    SCORING = "scoring"


class HTTPStatus:
    OK = 200
    ACCEPTED = 202
    NO_CONTENT = 204
    SEE_OTHER = 303
    NOT_FOUND = 404
    GONE = 410
    IN_USE = 422
    SERVICE_UNAVAIL = 503
