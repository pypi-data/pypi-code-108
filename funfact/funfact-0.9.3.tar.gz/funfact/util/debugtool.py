#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from inspect import currentframe, getframeinfo


class _FILE:
    def __str__(self):
        return str(getframeinfo(currentframe().f_back).filename)


class _LINE:
    def __str__(self):
        return str(getframeinfo(currentframe().f_back).lineno)


__FILE__ = _FILE()
__LINE__ = _LINE()


def _print(self, *args):
    print(
        '%24s' % os.path.basename(
            os.path.normpath(
                getframeinfo(currentframe().f_back).filename
            )
        ),
        '%4d' % getframeinfo(currentframe().f_back).lineno,
        self.indent[-1],
        *args
    )
