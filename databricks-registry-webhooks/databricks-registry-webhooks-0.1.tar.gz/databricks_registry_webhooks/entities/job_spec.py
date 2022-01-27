from databricks_registry_webhooks.entities._webhooks_base_object import _WebhooksBaseObject
from databricks_registry_webhooks.protos.webhooks_pb2 import JobSpec as ProtoJobSpec


class JobSpec(_WebhooksBaseObject):
    """
    Attributes of a Databricks Job (e.g. Job ID) for a Registry Webhook to run when one or more
    associated events occurs.
    """

    def __init__(self, job_id, access_token, workspace_url=None):
        """
        :param job_id: The ID of the Job to run.
        :param access_token: A Databricks personal access token (PAT) that can be used to execute
                             the specified Job within the specified Databricks Workspace.
                             The access token is not returned when querying Registry Webhooks.
        :param workspace_url: The URL of the Databricks Workspace to which the Job belongs. If
                              `None`, defaults to the URL of the current Databricks Workspace.
        """
        self._job_id = str(job_id)
        self._workspace_url = workspace_url
        self._access_token = access_token

    @property
    def job_id(self):
        """
        The ID of the Job to run.
        """
        return self._job_id

    @property
    def workspace_url(self):
        """
        The URL of the Databricks Workspace to which the Job belongs. If `None`, indicates that the
        Job belongs to the same workspace as the associated Registry Webhook.
        """
        return self._workspace_url

    @property
    def access_token(self):
        """
        A Databricks personal access token (PAT) that can be used to execute the specified Job
        within the specified Databricks Workspace. The access token is not returned when querying
        Registry Webhooks.
        """
        return self._access_token

    def to_proto(self):
        proto = ProtoJobSpec()
        proto.job_id = self.job_id
        proto.access_token = self.access_token
        if self.workspace_url is not None:
            proto.workspace_url = self.workspace_url
        return proto

    @classmethod
    def from_proto(cls, proto):
        return cls(
            job_id=proto.job_id,
            workspace_url=proto.workspace_url,
            access_token=proto.access_token,
        )
