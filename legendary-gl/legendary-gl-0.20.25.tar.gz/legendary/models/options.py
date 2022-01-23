# coding: utf-8

from asyncio import Queue as AIOQueue
from dataclasses import dataclass
from multiprocessing import Queue as MPQueue
from typing import Optional

from .manifest import Manifest
from .game import Game


@dataclass
class DownloaderManagerOptions:
    download_dir: str
    base_url: str
    cache_dir: Optional[str] = None
    resume_file: Optional[str] = None
    # queue options
    status_queue: Optional[MPQueue, AIOQueue] = None
    update_interval: float = 1.0
    # downloader options
    dl_timeout: float = 10.0
    max_workers: Optional[int] = None
    max_shared_memory: int = 1024 * 1024 * 1024


@dataclass
class DownloaderAnalysisOptions:
    manifest: Manifest
    old_manifest: Optional[Manifest] = None

    # additional features
    enable_patching: bool = True
    enable_resume: bool = True
    enable_process_opts: bool = False

    # filters
    prefix_include_filters: Optional[list] = None
    prefix_exclude_filters: Optional[list] = None
    suffix_include_filters: Optional[list] = None
    suffix_exclude_filters: Optional[list] = None
    install_tags: Optional[list] = None


@dataclass
class CorePrepareDownloadOpts:
    game: Game
    base_game: Game = None
    base_path: Optional[str] = None
    game_folder: Optional[str] = None

    # behavioural options
    force: bool = False
    repair: bool = False
    disable_delta: bool = False
    disable_https: bool = False
    repair_use_latest: bool = False

    # manifest options
    override_manifest: Optional[str] = None
    override_old_manifest: Optional[str] = None
    override_delta_manifest: Optional[str] = None
    override_base_url: Optional[str] = None
    override_platform: Optional[str] = None

    # downloader options
    preferred_cdn: Optional[str] = None
    disable_patching: bool = False
    disable_process_opts: bool = False
    status_queue: Optional[MPQueue, AIOQueue] = None
    max_shared_memory: Optional[int] = None
    max_workers: Optional[int] = None
    dl_timeout: Optional[float] = None
    # filtering
    prefix_include_filters: Optional[list] = None
    prefix_exclude_filters: Optional[list] = None
    suffix_include_filters: Optional[list] = None
    suffix_exclude_filters: Optional[list] = None


