"""
Fetches required data and formats output for `anyscale list` commands.
"""

import json
import time
from typing import Any, Dict, List, Optional, Tuple

import tabulate

from anyscale.cli_logger import BlockLogger
from anyscale.cloud import get_cloud_json_from_id
from anyscale.cluster_config import get_cluster_config
from anyscale.controllers.base_controller import BaseController
from anyscale.formatters import clouds_formatter
from anyscale.project import (
    get_proj_name_from_id,
    get_project_id,
    get_project_session,
    get_project_sessions,
    load_project_or_throw,
)
from anyscale.util import get_endpoint, humanize_timestamp


class ListController(BaseController):
    def __init__(
        self, log: BlockLogger = BlockLogger(), initialize_auth_api_client: bool = True
    ):
        super().__init__(initialize_auth_api_client=initialize_auth_api_client)
        self.log = log
        self.log.open_block("Output")

    def list_clouds(self, json_format: bool) -> str:
        clouds = self.api_client.list_clouds_api_v2_clouds_get().results
        output = clouds_formatter.format_clouds_output(
            clouds=clouds, json_format=json_format
        )

        return str(output)

    # TODO (jbai): This requires additional refactoring to decouple network fetching from formatting logic
    def list_projects(self, json_format: bool) -> str:
        resp = self.api_client.list_projects_api_v2_projects_get()
        projects = resp.results
        project_table = []
        project_json = []

        for project in projects:
            if json_format:
                session_list = self.api_client.list_sessions_api_v2_sessions_get(
                    project_id=project.id
                ).results
                session_record = []
                for session in session_list:
                    status = self.get_session_status_and_commands(session=session)[0]
                    session_record.append({"name": session.name, "status": status})
                project_json.append(
                    {
                        "name": project.name,
                        "sessions": session_record,
                        "url": "{}".format(get_endpoint(f"/projects/{project.id}")),
                    }
                )
            else:
                project_table.append(
                    [
                        project.name,
                        get_endpoint(f"/projects/{project.id}"),
                        project.description,
                    ]
                )

        if json_format:
            return json.dumps(project_json)
        else:
            table = tabulate.tabulate(
                project_table, headers=["NAME", "URL", "DESCRIPTION"], tablefmt="plain",
            )
            return f"Projects:\n{table}"

    # TODO (jbai): This requires additional refactoring to decouple network fetching from formatting logic
    def list_sessions(
        self, name: Optional[str], show_all: bool, json_format: bool
    ) -> str:
        project_definition = load_project_or_throw()
        project_id = get_project_id(project_definition.root)

        sessions = self.api_client.list_sessions_api_v2_sessions_get(
            project_id=project_id, name=name, active_only=not show_all
        ).results

        if json_format:
            output = self.session_list_json(sessions=sessions, project_id=project_id)
            return output

        active_project_title = f"Active project: {project_definition.root}"
        if name is None:
            table = []
            for session in sessions:
                created_at = humanize_timestamp(session.created_at)

                idle_timeout_minutes = (
                    session.idle_timeout
                )  # the constant idle_timeout specified by the user
                if idle_timeout_minutes >= 0:
                    idle_time_remaining_seconds = (
                        session.idle_time_remaining_seconds
                    )  # the remaining time to auto-suspend in seconds

                    if idle_time_remaining_seconds is not None:
                        if idle_time_remaining_seconds < 60:
                            # If we have LESS than a minute left till auto-suspend
                            idle_time_remaining_message = " ({} s left)".format(
                                idle_time_remaining_seconds
                            )
                        else:
                            # If we have MORE than a minute left till auto-suspend
                            idle_time_remaining_message = " ({} min left)".format(
                                int(round(idle_time_remaining_seconds / 60))
                            )
                    else:
                        # Even if the idle_timeout_minutes >= 0, the
                        # idle_time_remaining_seconds might still be None if
                        # the session is not in the "Running" state.
                        idle_time_remaining_message = ""

                    idle_timeout_message = "Enabled{}".format(
                        idle_time_remaining_message
                    )
                else:
                    idle_timeout_message = "Disabled"

                record = [
                    session.name,
                    " {}".format(
                        self.get_session_status_and_commands(session=session)[0]
                    ),
                    created_at,
                    idle_timeout_message,
                ]
                if show_all:
                    table.append(
                        [
                            " Y"
                            if session.state
                            in [
                                "Running",
                                "Updating",
                                "UpdatingErrored",
                                "StartingUp",
                                "StartupErrored",
                            ]
                            else " N"
                        ]
                        + record
                    )
                else:
                    table.append(record)
            if not show_all:
                table_string = tabulate.tabulate(
                    table,
                    headers=["SESSION", "STATUS", "CREATED", "AUTO-SUSPEND"],
                    tablefmt="plain",
                )
            else:
                table_string = tabulate.tabulate(
                    table,
                    headers=["ACTIVE", "SESSION", "STATUS", "CREATED", "AUTO-SUSPEND"],
                    tablefmt="plain",
                )

            return f"{active_project_title}\n{table_string}"
        else:
            sessions = [session for session in sessions if session.name == name]
            session_output_strings = []
            for session in sessions:
                resp = self.api_client.describe_session_api_v2_sessions_session_id_describe_get(
                    session_id=session.id
                )

                snapshot_table = []
                for applied_snapshot in resp.result.applied_snapshots:
                    snapshot_id = applied_snapshot.snapshot_id
                    created_at = humanize_timestamp(applied_snapshot.created_at)
                    snapshot_table.append([snapshot_id, created_at])
                session_output_strings.append(
                    tabulate.tabulate(
                        snapshot_table,
                        headers=[
                            "SNAPSHOT applied to {}".format(session.name),
                            "APPLIED",
                        ],
                        tablefmt="plain",
                    )
                )

                command_table = []
                for command in resp.results.commands:
                    created_at = humanize_timestamp(command.created_at)
                    command_table.append(
                        [
                            " ".join(
                                [command.name]
                                + [
                                    "{}={}".format(key, val)
                                    for key, val in command.params.items()
                                ]
                            ),
                            command.id,
                            created_at,
                        ]
                    )
                    session_output_strings.append(
                        tabulate.tabulate(
                            command_table,
                            headers=[
                                "COMMAND run in {}".format(session.name),
                                "ID",
                                "CREATED",
                            ],
                            tablefmt="plain",
                        )
                    )
            session_output_string = "\n".join(session_output_strings)

            return f"{active_project_title}\n{session_output_string}"

    # TODO (jbai): This requires additional refactoring to decouple network fetching from formatting logic
    def list_ips(
        self, session_name: Optional[str], json_format: bool, all_sessions: bool
    ) -> str:
        project_definition = load_project_or_throw()
        project_id = get_project_id(project_definition.root)

        if all_sessions:
            sessions = get_project_sessions(project_id, session_name, self.api_client)
            sessions = [session.name for session in sessions]
        else:
            sessions = [
                get_project_session(project_id, session_name, self.api_client).name
            ]

        output_json = []
        output_table = []
        for name in sessions:
            head_ip, worker_ips = self._get_head_and_worker_ips(session_name=name)
            if json_format:
                session = get_project_session(project_id, name, self.api_client)
                status = self.get_session_status_and_commands(session=session)[0]
                session_record = {"name": session.name, "status": status}
                project_record = {
                    "name": get_proj_name_from_id(project_id, self.api_client)
                }
                cloud_record = get_cloud_json_from_id(session.cloud_id, self.api_client)
                output_json.append(
                    {
                        "session": session_record,
                        "project": project_record,
                        "cloud": cloud_record,
                        "head-ip": head_ip,
                        "worker-ips": worker_ips,
                    }
                )
            else:
                output_table.append([name, head_ip, "head"])
                for worker_ip in worker_ips:
                    output_table.append([name, worker_ip, "worker"])

        return (
            json.dumps(output_json)
            if json_format
            else tabulate.tabulate(
                output_table,
                headers=["SESSION", "IP ADDRESS", "NODE TYPE"],
                tablefmt="plain",
            )
        )

    # TODO (jbai): Reorganize to other files
    def _get_head_and_worker_ips(self, session_name: str) -> Tuple[str, List[str]]:
        from ray.autoscaler.sdk import get_head_node_ip, get_worker_node_ips

        cluster_config = get_cluster_config(session_name, self.api_client)
        head_ip = get_head_node_ip(cluster_config)
        worker_ips = get_worker_node_ips(cluster_config)

        return head_ip, worker_ips

    # Consolidate this once this https://github.com/anyscale/product/pull/497 gets merged.
    def session_list_json(self, sessions: List[Any], project_id: str) -> str:
        output = []
        for session in sessions:
            status, commands = self.get_session_status_and_commands(session=session)
            record = {"name": session.name}
            record["status"] = status
            record["startup_error"] = (
                session.state_data.startup if session.state_data else {}
            )
            record["stop_error"] = (
                session.state_data.stopping if session.state_data else {}
            )

            record["created_at"] = time.mktime(session.created_at.timetuple())
            record["connect_url"] = session.connect_url
            record["jupyter_notebook_url"] = session.jupyter_notebook_url
            record["ray_dashboard_url"] = session.ray_dashboard_url
            record["grafana_url"] = session.metrics_dashboard_url
            if session.tensorboard_available and session.service_proxy_url:
                record["tensorboard_url"] = session.service_proxy_url
            else:
                record["tensorboard_url"] = None

            record["session_idle_timeout_minutes"] = session.idle_timeout
            record[
                "session_idle_time_remaining_seconds"
            ] = session.idle_time_remaining_seconds

            record["commands"] = commands

            record["project"] = project_id
            record["cloud"] = get_cloud_json_from_id(session.cloud_id, self.api_client)
            del record["cloud"]["config"]
            output.append(record)

        return json.dumps(output)

    def get_session_status_and_commands(
        self, session: Any
    ) -> Tuple[str, List[Dict[str, Any]]]:
        resp = self.api_client.get_session_commands_history_api_v2_session_commands_get(
            session_id=session.id
        )
        commands = []
        is_session_idle = True
        for command in resp.results:
            if command.killed_at is not None:
                command_status = "KILLED"
            elif command.finished_at is not None:
                command_status = "FINISHED"
            else:
                command_status = "RUNNING"
                is_session_idle = False

            command_record = {
                "id": command.id,
                "name": command.name,
                "created_at": humanize_timestamp(command.created_at),
                "status": command_status,
            }
            commands.append(command_record)
        status = str(session.state)
        if status == "Running":
            status = "Idle" if is_session_idle else "TASK_RUNNING"
        return status, commands
