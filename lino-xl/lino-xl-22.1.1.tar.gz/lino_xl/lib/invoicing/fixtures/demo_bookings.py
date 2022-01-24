# -*- coding: UTF-8 -*-
# Copyright 2016-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import datetime
from lino_xl.lib.cal.choicelists import DurationUnits
from lino.api import dd, rt
from lino.utils import ONE_DAY

Plan = rt.models.invoicing.Plan
Area = rt.models.invoicing.Area


def objects():
    # vt = dd.plugins.invoicing.get_voucher_type()
    # jnl_list = vt.get_journals()
    # if len(jnl_list) == 0:
    #     return
    from lino_xl.lib.ledger.roles import LedgerStaff
    accountants = LedgerStaff.get_user_profiles()
    users = rt.models.users.User.objects.filter(
        language=dd.get_default_language(), user_type__in=accountants)
    if users.count() == 0:
        return
    ses = rt.login(users.first().username)

    for area in Area.objects.all():
        min_date = None
        today = datetime.date(dd.plugins.ledger.start_year, 1, 1)
        while today < dd.demo_date(-60):
            max_date = DurationUnits.months.add_duration(today, 1) - ONE_DAY
            plan = Plan.run_start_plan(ses.get_user(), today=today, area=area)
            # 20210804
            # plan = Plan.run_start_plan(
            #     ses.get_user(), today=today, area=area,
            #     min_date=min_date, max_date=max_date)
            yield plan
            plan.fill_plan(ses)
            # for i in plan.items.all()[:9]:
            # print("20210801 {} : create {} invoices".format(today, plan.items.count()))
            for i in plan.items.all():
                yield i.create_invoice(ses)
                # obj = i.create_invoice(ses)
                # if obj is not None:
                #     yield obj
                # else:
                #     msg = "create_invoice failed for {}".format(i)
                #     raise Exception(msg)
            min_date = max_date + ONE_DAY
            today = DurationUnits.months.add_duration(today, 1)
