import json
from shlex import quote
import subprocess
import sys
import tempfile
from typing import Any, List, Tuple

import click

import anyscale
from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.models.execute_interactive_command_options import (
    ExecuteInteractiveCommandOptions,
)
from anyscale.cluster_config import get_cluster_config
from anyscale.controllers.base_controller import BaseController
from anyscale.project import get_project_id, get_project_session, load_project_or_throw
import anyscale.shared_anyscale_utils.conf as shared_anyscale_conf
from anyscale.shared_anyscale_utils.util import execution_log_name


from anyscale.cluster_config import (  # noqa: N812 isort: skip
    add_anyscale_exec_node_provider as _DO_NOT_USE_add_anyscale_node_provider,
)


def rsync(*args: Any, **kwargs: Any) -> None:
    from ray.autoscaler.sdk import rsync as ray_rsync

    ray_rsync(*args, **kwargs)


class ExecController(BaseController):
    def __init__(
        self, log: BlockLogger = BlockLogger(), initialize_auth_api_client: bool = True
    ):
        super().__init__(initialize_auth_api_client=initialize_auth_api_client)
        self.log = log

    def anyscale_exec(
        self,
        session_name: str,
        screen: bool,
        tmux: bool,
        port_forward: Tuple[int],
        sync: bool,
        stop: bool,
        terminate: bool,
        commands: List[str],
    ) -> None:
        message = (
            "Warning: `anyscale exec` has been deprecated. Please use `anyscale job submit` "
            "to run your script as a job in a cluster."
        )
        self.log.warning(message)
        import ray.scripts.scripts as autoscaler_scripts

        if screen and tmux:
            raise click.ClickException(
                "--screen and --tmux cannot both be specified. Please only specify one."
            )

        session_name, session_id = self._get_session_name_and_id(session_name)

        # Create a placeholder session command ID
        session_command = self.api_client.execute_interactive_command_api_v2_sessions_session_id_execute_interactive_command_post(
            session_id=session_id,
            execute_interactive_command_options=ExecuteInteractiveCommandOptions(
                shell_command=" ".join(commands)
            ),
        ).result
        session_command_id = session_command.command_id
        directory_name = session_command.directory_name
        dns_address = session_command.dns_address

        remote_command = self._generate_remote_command(
            session_command_id, commands, directory_name, stop, terminate
        )

        if tmux:
            wrapped_cmd = [
                "tmux",
                "new",
                "-d",
                "-s",
                session_command_id,
                "bash",
                "-c",
                quote(remote_command + "exec bash"),
            ]
            remote_command = " ".join(wrapped_cmd)
        if screen:
            wrapped_cmd = [
                "screen",
                "-L",
                "-dm",
                "bash",
                "-c",
                quote(remote_command + "exec bash"),
            ]
            remote_command = " ".join(wrapped_cmd)

        cluster_config = get_cluster_config(session_name, self.api_client)
        cluster_config = _DO_NOT_USE_add_anyscale_node_provider(
            cluster_config, dns_address
        )

        with tempfile.NamedTemporaryFile(mode="w") as config_file:
            json.dump(cluster_config, config_file)
            config_file.flush()
            config_file_path = config_file.name

            # Rsync file mounts if sync flag is set
            if sync:
                rsync(
                    cluster_config, source=None, target=None, down=False,
                )

            command = [
                sys.executable,
                autoscaler_scripts.__file__,
                "exec",
                config_file_path,
                remote_command,
                "--cluster-name",
                "{}".format(cluster_config["cluster_name"]),
            ]
            for port in list(port_forward):
                command.extend(["-p", str(port)])
            command_lst = [c for c in command if c]

            subprocess.check_call(command_lst, env=anyscale.ANYSCALE_ENV)  # noqa: B1

        if tmux or screen:
            launched_in_mode = "tmux" if tmux else "screen"
            run_cmd = "tmux attach" if tmux else "screen -xRR"
            self.log.info(
                "Command launched in {mode}, log into the cluster using `anyscale ssh {name}` and run `{run_cmd}` to check on the status.".format(
                    mode=launched_in_mode, name=session_name, run_cmd=run_cmd
                )
            )

    def _get_session_name_and_id(self, session_name: str) -> Tuple[str, str]:
        project_definition = load_project_or_throw()
        project_id = get_project_id(project_definition.root)
        session = get_project_session(project_id, session_name, self.api_client)

        return session.name, session.id

    def _generate_remote_command(
        self,
        session_command_id: str,
        commands: List[str],
        directory_name: str,
        stop: bool,
        terminate: bool,
    ) -> str:
        # Save the PID of the command so we can kill it later.
        shell_command_prefix = (
            "echo $$ > {execution_log_name}.pid; "
            "export ANYSCALE_HOST={anyscale_host}; "
            "export ANYSCALE_SESSION_COMMAND_ID={session_command_id}; ".format(
                execution_log_name=execution_log_name(session_command_id),
                anyscale_host=shared_anyscale_conf.ANYSCALE_HOST,
                session_command_id=session_command_id,
            )
        )

        # Note(simon): This section is largely similar to the server side exec command but simpler.
        # We cannot just use the server command because we need to buffer the output to
        # user's terminal as well and handle interactivity.
        redirect_to_dev_null = "&>/dev/null"
        shell_command = shell_command_prefix + " ".join(commands)
        remote_command = (
            "touch {execution_log_name}.out; "
            "touch {execution_log_name}.err; "
            f"cd {directory_name}; "
            "script -q -e -f -c {shell_command} {execution_log_name}.out; "
            "echo $? > {execution_log_name}.status; "
            "ANYSCALE_HOST={anyscale_host} anyscale session "
            "upload_command_logs --command-id {session_command_id} {redirect_to_dev_null}; "
            "ANYSCALE_HOST={anyscale_host} anyscale session "
            "finish_command --command-id {session_command_id} {stop_cmd} {terminate_cmd} {redirect_to_dev_null}; ".format(
                directory_name=directory_name,
                execution_log_name=(execution_log_name(session_command_id)),
                anyscale_host=shared_anyscale_conf.ANYSCALE_HOST,
                session_command_id=session_command_id,
                stop_cmd="--stop" if stop else "",
                terminate_cmd="--terminate" if terminate else "",
                shell_command=quote(shell_command),
                redirect_to_dev_null=redirect_to_dev_null,
            )
        )

        return remote_command
