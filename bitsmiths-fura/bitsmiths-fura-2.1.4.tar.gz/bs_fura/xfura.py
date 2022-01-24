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

from .audit           import Audit
from .err_code        import ErrCode
from .db.tables.ula   import tUla

from mettle.lib import xMettle


class xFura(xMettle):
    """
    The base exception class for Fura.
    """

    def __init__(self, obj):
        """
        Constructor.

        :param obj: Access denied audit reason.
        """
        self._obj  = obj

        if isinstance(obj, Audit):
            xMettle.__init__(self, obj.get_long_msg(), obj.src, obj.ec)
        elif isinstance(obj, tUla):
            xMettle.__init__(self, ErrCode(obj.err_code).name, 'Fura.UserLogin', obj.err_code)
        else:
            xMettle.__init__(self, 'Unexpected exception', __name__, ErrCode.UnexpectedError)
