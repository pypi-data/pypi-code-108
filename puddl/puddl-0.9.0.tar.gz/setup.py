#!/usr/bin/env python
from pathlib import Path

from setuptools import setup


def get_all_scripts():
    return [str(p) for p in Path('.').glob('bin/*')]


setup(scripts=get_all_scripts())
