# -*- coding: UTF-8 -*-
# Copyright 2017-2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


from lino.utils import Cycler
from lino.api import rt
from lino_xl.lib.vat.choicelists import VatAreas, VatRegimes, VatRules


def objects():
    qs = rt.models.contacts.Company.objects.filter(country__isnull=False)
    qs = qs.filter(vat_id="")
    for obj in qs:
        if not obj.vid_manager.origin.length:
            continue
        obj.vid_manager.generate_vid()
        yield obj

    va2regimes = dict()
    for va in VatAreas.get_list_items():
        regimes = []
        for reg in VatRegimes.get_list_items():
            if reg.is_allowed_for(va) and reg.name not in ('lu', 'de'):
                # if va.name == "national":
                #     raise Exception("20190408 ok")
                if VatRules.get_vat_rule(
                        va, vat_regime=reg, default=False):
                    regimes.append(reg)
        if len(regimes) == 0:
            raise Exception("20190408 no regimes for {}".format(va))
        va2regimes[va] = Cycler(regimes)

    if len(va2regimes) == 0:
        msg = "No VAT rules defined. "
        msg += "The VAT plugin requires a declaration plugin xxvat"
        raise Exception(msg)

    qs = rt.models.contacts.Partner.objects.filter(country__isnull=False)
    qs = qs.filter(vat_regime="")
    for obj in qs:
        va = VatAreas.get_for_country(obj.country)
        if va is None:
            raise Exception("20190408 no VAT area for {}".format(obj.country))
        regs = va2regimes.get(va)
        regs = list(regs.items)
        reg = regs.pop(0)
        if obj.vat_id:
            # prefer a reg that needs vat id
            while len(regs) and not reg.needs_vat_id:
                reg = regs.pop(0)
                # print("20200121a", reg, regs)
        else:
            while len(regs) and reg.needs_vat_id:
                reg = regs.pop(0)
                # print("20200121b", reg, regs)
        obj.vat_regime = reg
        yield obj
        # else:
        #     raise Exception("20190408 no VAT regime for {}".format(obj))
