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

from .audit import Audit


class BaseAccess:
    """
    This class is used to determined if a user has access
    to a specific role function or not.
    """

    def __init__(self, site_code: str, usr_id: str, src: str):
        """
        Constructor.

        :param site_code: Site unique code.
        :param usr_id: User id.
        :param src: Source part of the system.
        """
        self._site_code = site_code
        self._site      = None
        self._usr_id    = usr_id
        self._role      = None
        self._src       = src
        self._aga_lst   = Audit.List()
        self._ada_lst   = Audit.List()


    def ok(self) -> bool:
        """
        Check if this access object has any problems.
        """
        return not self._ada_lst


    def clear_audit_hist(self):
        """
        Clear the audit history.
        """
        self._ada_lst.clear()
        self._aga_lst.clear()


    def get_site_id(self) -> int:
        """
        Gets the site if after successufl login.
        """
        return self._site.id
