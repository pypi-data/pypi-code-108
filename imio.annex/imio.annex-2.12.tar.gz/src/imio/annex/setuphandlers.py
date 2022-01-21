# -*- coding: utf-8 -*-


def post_install(context):
    """Post install script"""
    if context.readDataFile('imioannex_default.txt') is None:
        return
