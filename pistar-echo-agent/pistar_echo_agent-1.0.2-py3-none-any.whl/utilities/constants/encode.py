"""
description: this module provides the constant ENCODE.
"""

import platform


class ENCODE:
    """
    description the common encoding.
    """

    UTF8 = 'utf8'
    GBK = 'gbk'
    CMD = GBK if platform.system() == 'Windows' else UTF8
