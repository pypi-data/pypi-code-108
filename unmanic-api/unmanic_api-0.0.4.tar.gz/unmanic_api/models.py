"""Models for Unmanic."""

from dataclasses import dataclass
import datetime
from typing import List

from .exceptions import UnmanicError


@dataclass(frozen=True)
class Worker:
    """
    Object holding worker information from Unmanic.

    Attributes:

    id: The worker id.

    name: The worker name.

    idle: Whether the worker is idle.

    paused: Whether the worker is paused.

    start_time: The start time of the worker.

    current_file: The current file being processed.

    current_task: The current task being processed.
    """

    id: str
    name: str
    idle: bool
    paused: bool
    start_time: datetime
    current_file: str
    current_task: int

    @staticmethod
    def from_dict(data: dict):
        return Worker(
            id=data.get("id"),
            name=data.get("name"),
            idle=data.get("idle"),
            paused=data.get("paused"),
            start_time=datetime.datetime.fromtimestamp(
                int(float(data.get("start_time")))),
            current_file=data.get("current_file"),
            current_task=data.get("current_task"),
        )

@dataclass(frozen=True)
class TaskQueue:
    """
    Object holding task queue information from Unmanic.

    Attributes:

    recordsTotal: The total number of records.

    recordsFiltered: The number of records after filtering.

    results: The list of tasks.
    """

    recordsTotal: int
    recordsFiltered: int
    results: List

    @staticmethod
    def from_dict(data: dict):
        return TaskQueue(
            recordsTotal=data.get("recordsTotal"),
            recordsFiltered=data.get("recordsFiltered"),
            results=[PendingTask.from_dict(pending_task) for pending_task in data.get("results")],
        )

@dataclass(frozen=True)
class PendingTask:
    """
    Object holding pending task information from Unmanic.

    Attributes:

    id: The task id.

    abspath: The absolute path of the file.

    priority: The priority of the task.

    type: The type of the task.

    status: The status of the task.
    """

    id: int
    abspath: str
    priority: int
    type: str
    status: str

    @staticmethod
    def from_dict(data: dict):
        return PendingTask(
            id=data.get("id"),
            abspath=data.get("abspath"),
            priority=data.get("priority"),
            type=data.get("type"),
            status=data.get("status"),
        )

@dataclass(frozen=True)
class Settings:
    """
    Object holding settings from Unmanic.

    Attributes:

    ui_port: The port Unmanic is running on.

    config_path: The path to the Unmanic configuration file.

    log_path: The path to the Unmanic log file.

    plugins_path: The path to the Unmanic plugins directory.

    userdata_path: The path to the Unmanic userdata directory.

    debugging: Whether Unmanic is running in debug mode.

    library_path: The path to the Unmanic library directory.

    enabled_library_scanner: Enable periodic library scans.

    schedule_full_scan_minutes: The number of minutes between full library scans.

    follow_symlinks: Follow symlinks on library scans.

    concurrent_file_testers: The number of file testers to run concurrently.

    run_full_scan_on_start: Run a one off library scan on startup.

    enable_inotify: Enable the library file monitor.

    clear_pending_tasks_on_restart: Clear all pending tasks on startup.

    number_of_workers: The number of workers to run.

    cache_path: The path to the Unmanic cache directory.

    installation_name: The name of the Unmanic installation.

    distributed_worker_count_target: The target number of distributed workers.
    """

    ui_port: int
    config_path: str
    log_path: str
    plugins_path: str
    userdata_path: str
    debugging: bool
    library_path: str
    enable_library_scanner: bool
    schedule_full_scan_minutes: int
    follow_symlinks: bool
    concurrent_file_testers: int
    run_full_scan_on_start: bool
    enable_inotify: bool
    clear_pending_tasks_on_restart: bool
    number_of_workers: int
    cache_path: str
    installation_name: str
    distributed_worker_count_target: int

    @staticmethod
    def from_dict(data: dict):
        return Settings(
            ui_port=data.get("ui_port"),
            config_path=data.get("config_path"),
            log_path=data.get("log_path"),
            plugins_path=data.get("plugins_path"),
            userdata_path=data.get("userdata_path"),
            debugging=data.get("debugging"),
            library_path=data.get("library_path"),
            enable_library_scanner=data.get("enable_library_scanner"),
            schedule_full_scan_minutes=data.get("schedule_full_scan_minutes"),
            follow_symlinks=data.get("follow_symlinks"),
            concurrent_file_testers=data.get("concurrent_file_testers"),
            run_full_scan_on_start=data.get("run_full_scan_on_start"),
            enable_inotify=data.get("enable_inotify"),
            clear_pending_tasks_on_restart=data.get(
                "clear_pending_tasks_on_restart"),
            number_of_workers=data.get("number_of_workers"),
            cache_path=data.get("cache_path"),
            installation_name=data.get("installation_name"),
            distributed_worker_count_target=data.get(
                "distributed_worker_count_target"),
        )
