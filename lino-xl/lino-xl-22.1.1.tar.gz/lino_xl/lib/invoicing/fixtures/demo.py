# -*- coding: UTF-8 -*-
# Copyright 2019-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import dd, rt, _


def area(name, **kwargs):
    kwargs = dd.str2kw('designation', name, **kwargs)
    # kwargs.update(designation=name)
    return rt.models.invoicing.Area(**kwargs)


def objects():
    yield area(_("First"))
    if dd.plugins.invoicing.three_demo_areas:
        yield area(_("Second"))
        yield area(_("Third"))
