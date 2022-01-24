# **************************************************************************** #
#                           This file is part of:                              #
#                                BITSMITHS                                     #
#                           https://bitsmiths.co.za                            #
# **************************************************************************** #
#  Copyright (C) 2015 - 2021 Bitsmiths (Pty) Ltd.  All rights reserved.        #
#   * https://bitbucket.org/bitsmiths_za/bitsmiths                             #
#                                                                              #
#  Permission is hereby granted, free of charge, to any person obtaining a     #
#  copy of this software and associated documentation files (the "Software"),  #
#  to deal in the Software without restriction, including without limitation   #
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,    #
#  and/or sell copies of the Software, and to permit persons to whom the       #
#  Software is furnished to do so, subject to the following conditions:        #
#                                                                              #
#  The above copyright notice and this permission notice shall be included in  #
#  all copies or substantial portions of the Software.                         #
#                                                                              #
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  #
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    #
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL     #
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  #
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING     #
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER         #
#  DEALINGS IN THE SOFTWARE.                                                   #
# **************************************************************************** #
import datetime

from bs_lib import common

from .db.tables import tSite
from .db.tables import tUsr


def get_usr_loco_address(urec: tUsr, targ_addr: str = None) -> dict:
    """
    Gets the users avialble address for loco correspondence.

    :param urec: The tUsr record.
    :param targ_addr: Optionally specify and overload address.
    :return: The address object.
    """
    addr  = {}
    email = []
    sms   = []

    if targ_addr:
        if common.dest_addr_valid_email(targ_addr):
            email.append(targ_addr)
        elif common.dest_addr_valid_sms(targ_addr):
            sms.append(targ_addr)
    else:
        if common.dest_addr_valid_email(urec.id):
            email.append(urec.id)

        if common.dest_addr_valid_email(urec.email1) and urec.email1 not in email:
            email.append(urec.email1)

        if common.dest_addr_valid_email(urec.email2) and urec.email2 not in email:
            email.append(urec.email2)

        if common.dest_addr_valid_sms(urec.cellno1) and urec.cellno1 not in sms:
            sms.append(urec.cellno1)

        if common.dest_addr_valid_sms(urec.cellno2) and urec.cellno2 not in sms:
            sms.append(urec.cellno2)

    if email:
        addr['email'] = email

    if sms:
        addr['sms'] = sms

    return addr


def confirm_usr_addr(urec: tUsr, targ_addr: str) -> bool:
    """
    Confirms a user address.

    :param urec: The tUsr record.
    :param targ_addr: The address to confirm.
    :return: True if the address was confirmed, false if it was already ok not confirmed.
    """
    if not targ_addr:
        return False

    if urec.email1 == targ_addr:
        if not urec.email1_conf:
            urec.email1_conf = True
            return True

    if urec.email2 == targ_addr:
        if not urec.email2_conf:
            urec.email2_conf = True
            return True

    if urec.cellno1 == targ_addr:
        if not urec.cellno1_conf:
            urec.cellno1_conf = True
            return True

    if urec.cellno2 == targ_addr:
        if not urec.cellno2_conf:
            urec.cellno2_conf = True
            return True

    return False


def std_loco_tags(urec: tUsr, srec: tSite, supp_email: str) -> dict:
    """
    """
    parts = []

    if urec.title:
        parts.append(urec.title)

    if urec.name_first:
        parts.append(urec.name_first)

    if urec.name_last:
        parts.append(urec.name_last)

    name  = 'Anonymous' if not parts else ' '.join(parts)

    dtnow = datetime.datetime.now()

    return {
        'usr_id'        : urec.id,
        'site_code'     : srec.code if srec else '',
        'site_id'       : urec.site_id,
        'role_id'       : urec.role_id,
        'site_descr'    : srec.descr if srec else '[UNKNOWN]',
        'name'          : name,
        'datetime'      : dtnow.strftime('%4Y-%m-%d %H:%M:%S'),
        'date'          : dtnow.strftime('%4Y-%m-%d'),
        'support_email' : supp_email,
    }
