#!/usr/bin/env python3
# coding: utf-8

from __future__ import unicode_literals

import volkanic

cmddef = """
pydir       joker.superuser.tools.pydir
pyentry     joker.superuser.tools.pyentry
unsource    joker.superuser.tools.unsource
cases       joker.superuser.tools.cases
dup         joker.superuser.tools.dedup
setop       joker.superuser.tools.setop
rmdir       joker.superuser.tools.remove
apt         joker.superuser.tools.apt
url         joker.superuser.tools.urls
urls        joker.superuser.tools.urls:runloop
"""

_prog = 'python3 -m joker.superuser'
registry = volkanic.CommandRegistry.from_cmddef(cmddef, _prog)

if __name__ == '__main__':
    registry()
