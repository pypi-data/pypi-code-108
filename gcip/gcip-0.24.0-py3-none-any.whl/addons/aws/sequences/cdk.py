from typing import Dict, Optional

from gcip.core.sequence import Sequence
from gcip.addons.aws.jobs.cdk import Diff, Deploy


class DiffDeploy(Sequence):
    def __init__(
        self,
        *stacks: str,
        toolkit_stack_name: str,
        deploy_strict: bool = True,
        wait_for_stack: bool = True,
        wait_for_stack_assume_role: Optional[str] = None,
        wait_for_stack_account_id: Optional[str] = None,
        diff_options: Optional[str] = None,
        deploy_options: Optional[str] = None,
        context: Optional[Dict[str, str]] = None,
    ):
        super().__init__()
        self.diff_job = Diff(
            *stacks,
            diff_options=diff_options,
            context=context,
        )
        self.deploy_job = Deploy(
            *stacks,
            toolkit_stack_name=toolkit_stack_name,
            wait_for_stack=wait_for_stack,
            wait_for_stack_assume_role=wait_for_stack_assume_role,
            wait_for_stack_account_id=wait_for_stack_account_id,
            strict=deploy_strict,
            deploy_options=deploy_options,
            context=context,
        )
        self.deploy_job.add_needs(self.diff_job)

        self.add_children(
            self.diff_job,
            self.deploy_job,
        )
