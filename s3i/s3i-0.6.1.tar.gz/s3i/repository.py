from s3i.ditto_manager import DittoManager


class Repository(DittoManager):
    """Class Directory contains functions to query things in S3I Repository """

    def __init__(self, s3i_repo_url, token):
        """
        Constructor

        :param s3i_repo_url: url of S3I Repository
        :type s3i_repo_url: str
        :param token: id token obtained from S3I IdP
        :type token: str
        """
        super().__init__(s3i_repo_url, token)
