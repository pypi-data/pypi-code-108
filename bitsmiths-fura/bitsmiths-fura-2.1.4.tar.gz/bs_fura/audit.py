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

# from .access     import Access
from .err_code import ErrCode

from .db.tables import tEatok
from .db.tables import tFunc
from .db.tables import tRole


class Audit:
    """
    An audit log of access for either granted or denied.
    """
    STR_NONE = '<NONE>'

    def __init__(self,
                 site_id   : str,
                 site_code : str,
                 usr_id    : str,
                 src       : str,
                 role      : tRole,
                 func      : "str|tFunc",
                 ad        : bool,
                 ec        : ErrCode = None,
                 eaktok    : tEatok = None):
        """
        Constructor.

        :param site_code: Site code.
        :param usr_id: User id.
        :param src: Source part of the system.
        :param role: Role the uer has.
        :param func:  Function requested.
        :param ad: True for granted, false for denied.
        :param ec: The err code enum as to why denied.
        :param eatok: The elevated access record.
        """
        self.tm        = datetime.datetime.now()
        self.site_id   = site_id
        self.site_code = site_code
        self.usr_id    = usr_id
        self.src       = src
        self.role      = role
        self.func      = func
        self.ad        = ad
        self.ec        = ec
        self.eatok     = eaktok


    def get_long_msg(self):
        """
        Gets the long (error) message from this audit log.

        :return: The long message.
        """
        if self.ad:
            return 'Access granted [site:%s, usr:%s, role:%s, func:%s, when:%s]' % (
                self.site_code, str(self.usr_id), self.role_id(), self.func_id(), str(self.tm))

        return 'Access denied [site:%s, usr:%s, role:%s, func:%s, reason:%s, when:%s]' % (
            self.site_code, str(self.usr_id), self.role_id(), self.func_id(), self.err_descr(), str(self.tm))


    def short_reason(self):
        if self.ad:
            return ''

        if not self.ec:
            return

        return self.ec.name


    def role_id(self):
        if not self.role:
            return self.STR_NONE

        return self.role.id


    def err_descr(self):
        if not self.ec:
            return self.STR_NONE

        return '%s (%d)' % (self.ec.name, self.ec.value)


    def func_id(self):
        if not self.func:
            return self.STR_NONE

        if isinstance(self.func, str):
            return self.func

        return self.func.id


    def func_action(self):
        if not self.func or isinstance(self.func, str):
            return '?'

        return self.func.action


    def ea_usr_id(self):
        if not self.eatok:
            return ''

        return self.eatok.usr_id


    class List(list):
        """
        List of audit objects.
        """

        def add(self,
                ac,  # : Access,
                role  : tRole,
                func  : tFunc,
                ad    : bool,
                ec    : ErrCode = None,
                eatok : tEatok = None):
            """
            Adds an audit line.

            :param ac: Access object..
            :param role: Role the uer has.
            :param func: Function requested.
            :param ad: True for granted, false for denied.
            :param ec: The err code enum as to why denied.
            """
            self.append(Audit(
                0 if not ac._site else ac._site.id,
                str(ac._site_code),
                ac._usr_id,
                ac._src,
                role,
                func,
                ad,
                ec,
                eatok))
