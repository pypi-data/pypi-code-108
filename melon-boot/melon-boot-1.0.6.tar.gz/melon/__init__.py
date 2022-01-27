# -*- encoding: utf-8 -*-
"""
@Author  : zh_o
"""
import os
from melon.utils import FileUtil


CONFIG_PATH = FileUtil.locate_file('./', 'melon.toml')
ROOT_DIR = os.path.abspath(os.path.dirname(CONFIG_PATH))
