#  /************** Begin Copyright - Do not add comments here **************
#   * Licensed Materials - Property of IBM
#   *
#   *   OCO Source Materials
#   *
#   *   (C) Copyright IBM Corp. 2020, All Rights Reserved
#   *
#   * The source code for this program is not published or other-
#   * wise divested of its trade secrets, irrespective of what has
#   * been deposited with the U.S. Copyright Office.
#   ***************************** End Copyright ****************************/

class TSError(Exception):
    """
    The base time-series error which will occur if an exception is raised when using autoai_ts_libs.deps.tspy
    """
    pass


class TSErrorWithMessage(TSError):
    """
    an extension to the base time-series error which contains a message
    """
    def __init__(self, message=""):
        self._message = message

    def __str__(self):
        return self._message
