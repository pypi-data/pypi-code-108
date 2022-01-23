#!/usr/bin/env python3
# coding: utf-8
import subprocess


def find_name(rootdir='.', pattern=''):
    # https://unix.stackexchange.com/questions/118959/how-to-find-files-that-contain-newline-in-filename
    subprocess.run(['find', rootdir, '-name', pattern])
