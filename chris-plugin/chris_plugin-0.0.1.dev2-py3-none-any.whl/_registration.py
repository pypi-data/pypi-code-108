"""
A mechanism for passing the plugin's arguments to the ``chris_plugin_info`` tool.
"""

import argparse
from chris_plugin.types import ChrisPluginType
from dataclasses import dataclass
from typing import Optional


@dataclass
class PluginDetails:
    """
    Metadata about a *ChRIS* plugin which cannot be inferred from ``setup.py``
    """
    parser: argparse.ArgumentParser
    type: ChrisPluginType
    category: str
    icon: str
    title: Optional[str]
    min_number_of_workers: int
    max_number_of_workers: int
    min_memory_limit: str
    max_memory_limit: str
    min_cpu_limit: str
    max_cpu_limit: str
    min_gpu_limit: int
    max_gpu_limit: int


_memory: list[PluginDetails] = []


class PluginSingletonException(Exception):
    pass


def register(details: PluginDetails):
    if _memory:
        raise PluginSingletonException('singleton already registered')
    _memory.append(details)


def get_registered() -> PluginDetails:
    if not _memory:
        raise PluginSingletonException('No decorated @chris_plugin main function')
    return _memory[0]
