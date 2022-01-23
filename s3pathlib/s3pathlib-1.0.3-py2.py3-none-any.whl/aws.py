# -*- coding: utf-8 -*-

from typing import Optional

try:
    import boto3
except ImportError:  # pragma: no cover
    pass
except:  # pragma: no cover
    raise


class Context:
    """
    A globally available context object managing P

    TODO: use singleton pattern to create context object
    """

    def __init__(self):
        self.boto_ses: Optional[boto3.session.Session] = None
        self._s3_client = None

        # try to create default session
        try:
            self.boto_ses = boto3.session.Session()
        except:  # pragma: no cover
            pass

    def attach_boto_session(self, boto_ses):
        """
        Attach a custom boto session.

        :type boto_ses: boto3.session.Session
        """
        self.boto_ses = boto_ses
        self._s3_client = None

    @property
    def s3_client(self):
        """
        Access the s3 client.

        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#client
        """
        if self._s3_client is None:
            self._s3_client = self.boto_ses.client("s3")
        return self._s3_client


context = Context()
