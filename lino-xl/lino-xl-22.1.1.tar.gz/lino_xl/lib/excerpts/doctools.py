# -*- coding: UTF-8 -*-
# Copyright 2017-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""
Render a list of all excerpt types with pointers to demo documents.

Usage in a :rst:dir:`lino2rst` directive as follows::

   from lino_xl.lib.excerpts.doctools import show_excerpts
   print(show_excerpts())

This was used in :file:`welfare/dedocs/excerpts.rst` to generate the list of
demo excerpts. We discontinued this feature because it was of little use and
caused challenges when building the docs in a CI environment.

"""


import os
import shutil
from pathlib import Path
import rstgen
from lino.api import rt
from django.conf import settings

NEW_APPROACH = True

def show_excerpts(severe=True):
    ses = rt.login()
    # dd.logger.info("20141029 %s", settings.SITE)
    coll = {}
    demo_url = "https://weleup1.mylino.net/media/"
    # /media/cache/appypdf/excerpts.Excerpt-75.pdf

    def collect(obj):
        l = coll.setdefault(obj.excerpt_type, [])
        mf = obj.build_method.get_target(None, obj)
        if NEW_APPROACH:
            url = demo_url + ("/".join(mf.parts))
            kw = dict(owner=obj.owner, url=url, type=obj.excerpt_type)
            l.append(kw)
        else:
            tmppath  = Path(mf.name)
            if tmppath.exists():
                tail = tmppath.name
                tail = 'dl/excerpts/' + tail
                kw = dict(tail=tail)
                kw.update(type=obj.excerpt_type)
                kw.update(owner=obj.owner)
                try:
                    # dd.logger.info("20141029 copy %s to %s", tmppath, tail)
                    shutil.copyfile(tmppath, tail)
                except IOError as e:
                    kw.update(error=str(e))
                    msg = "%(type)s %(owner)s %(tail)s Oops: %(error)s" % kw
                    # raise Exception(msg)
                    kw.update(owner=msg)

                l.append(kw)

    for o in rt.models.excerpts.Excerpt.objects.order_by('excerpt_type'):
        collect(o)

    def asli(et, items):
        s = str(et)
        if NEW_APPROACH:
            s += " : " + ', '.join("`{owner} <{url}>`__".format(*kw) for kw in items)
        else:
            s += " : " + ', '.join(
                "`%(owner)s <../%(tail)s>`__" % kw % kw for kw in items)
        return s

    return rstgen.ul([asli(et, items) for et, items in sorted(coll.items())])
