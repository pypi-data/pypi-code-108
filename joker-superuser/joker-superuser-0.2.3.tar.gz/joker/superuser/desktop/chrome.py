#!/usr/bin/env python3
# coding: utf-8

import os.path
import platform
import sys

from volkanic.utils import under_home_dir


def under_chrome_default_dir(*paths):
    # https://stackoverflow.com/a/13874620/2925169
    # https://newbedev.com/how-can-i-view-archived-google-chrome-history
    # -i-e-history-older-than-three-months

    if sys.platform == 'darwin':
        return under_home_dir(
            'Library/Application Support/Google/Chrome/Default', *paths,
        )
    elif sys.platform in ['linux', 'linux2']:
        return under_home_dir('.config/google-chrome/Default', *paths)
    elif sys.platform in ['win32', 'cygwin', 'msys']:
        if platform.win32_ver()[0] in ['XP', '2000']:
            return under_home_dir(
                r'Local Settings\Application Data',
                r'Google\Chrome\User Data\Default',
                *paths,
            )
        else:
            return under_home_dir(
                r'\AppData\Local\Google\Chrome\User Data\Default',
                *paths,
            )
    else:
        raise RuntimeError('current platform is not supported')


def get_chrome_history_db_files():
    paths = [
        under_chrome_default_dir('History'),
        under_chrome_default_dir('Archived History'),
    ]
    return [os.path.exists(p) for p in paths]
