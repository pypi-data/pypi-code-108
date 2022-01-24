# -*- coding: UTF-8 -*-
# Copyright 2015-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.core.roles import UserRole


class LedgerPartner(UserRole):
    pass


class AccountingReader(UserRole):
    pass


class LedgerUser(AccountingReader):
    pass


class VoucherSupervisor(UserRole):
    pass


class LedgerStaff(LedgerUser, VoucherSupervisor):
    pass
