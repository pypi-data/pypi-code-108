from cnvrgv2.context import Context
from cnvrgv2.modules.ssh.ssh import Ssh


class SshClient:
    def __init__(self, organization):
        self._context = Context(context=organization._context)

    def create_ssh(self, job_id):
        return Ssh(self._context, job_id)
