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

from .base_access   import BaseAccess
# from .dao_async      import DaoAsync
from .err_code      import ErrCode
from .xfura         import xFura

from .db.tables   import tRole
from .db.tables   import tSite
from .db.tables   import tUsr


class AccessAsync(BaseAccess):
    """
    This class is used to determined if a user has access
    to a specific role function or not.
    """

    def __init__(self,
                 dao,  # : DaoAsync,
                 site_code : str,
                 usr_id    : str,
                 src       : str):
        """
        Constructor.

        :param dao: The fura dao object to use.
        :param siteCode: Site unique code.
        :param usr_id: User id.
        :param src: Source part of the system.
        """
        BaseAccess.__init__(self, site_code, usr_id, src)

        self._dao = dao


    async def __aenter__(self):
        """
        On enter event.
        """
        if not await self._site_ok():
            return self

        if not await self._usr_ok():
            return self

        return self


    async def __aexit__(self, type, value, traceback):
        """
        On exit event.
        """
        await self._persist_aga()
        await self._persist_ada()


    async def required(self, func: str, eatok: str = None):
        """
        This behaved like the access method, except it raises an (xFura) exception an
        if the access is not granted.

        :param func: The function id in question.
        :param eatok: Elevated access token, optional.
        """
        if not await self.access(func, eatok):
            raise xFura(self._ada_lst[-1])


    async def access(self, func: str, eatok: str = None, ignore_ada: bool = False) -> bool:
        """
        Check if user has access to a function.

        :param func: The function id in question.
        :param eatok: Elevated access token, optional.
        :param ignore_ada: If true, ignores any existing ada errors and checkes anyway.
        :return: True if access is allowed is ok else false.
        """
        if not ignore_ada and not self.ok():
            return False

        if not self._role:
            self._ada_lst.add(self, None, func, False, ErrCode.UserHasNoRole)

        frec = await self._dao.func_get(func)

        if not frec:
            self._ada_lst.add(self, self._role, func, False, ErrCode.FuncNotfound)
            return False

        if eatok is not None:
            ea = await self._dao.eatoken_get(self._site.id, eatok)

            if not ea:
                self._ada_lst.add(self, self._role, frec, False, ErrCode.EaTokNotFound, ea)
                return False

            if ea.grant_usr_id != self._usr_id:
                self._ada_lst.add(self, self._role, frec, False, ErrCode.EaTokWrongUser, ea)
                return False

            if ea.func_id != func:
                self._ada_lst.add(self, self._role, frec, False, ErrCode.EaTokWrongFunc, ea)
                return False

            if ea.max_usages > 0 and ea.usages >= ea.max_usages:
                self._ada_lst.add(self, self._role, frec, False, ErrCode.EaTokMaxUses, ea)
                return False

            if ea.expires < datetime.datetime.now():
                self._ada_lst.add(self, self._role, frec, False, ErrCode.EaTokExpired, ea)
                return False

            eausr = await self._dao.usr_get(self._site.id, ea._usr_id)
            earl  = await self._dao.role_get(self._site.id, eausr.role_id)

            if not earl:
                self._ada_lst.add(self, None, frec, False, ErrCode.UserHasNoRole, ea)
                return False

            if earl.rec.status == tRole.Status_Couplet.key_disabled:
                self._ada_lst.add(self, earl.rec, frec, False, ErrCode.RoleDisabled, ea)

            if earl.rec.status != tRole.Status_Couplet.key_super_user and\
               not await self._dao.rolefuncrel_get(self._site.id, frec.id, earl.rec.id):
                self._ada_lst.add(self, earl.rec, frec, False, ErrCode.AccessDenied, ea)
                return False

            self._aga_lst.add(self, earl.rec, frec, True, None, ea)

            await self._dao.eatoken_incr_usage(ea.id)
        else:
            if self._role.status != tRole.Status_Couplet.key_super_user and\
               not await self._dao.rolefuncrel_get(self._site.id, frec.id, self._role.id):
                self._ada_lst.add(self, self._role, frec, False, ErrCode.AccessDenied)
                return False

            self._aga_lst.add(self, self._role, frec, True, None)

        return True


    async def _site_ok(self) -> bool:
        """
        Check if the site is valid.

        :return: True if site is ok.
        """
        st = await self._dao.site_get(self._site_code)

        if not st:
            self._ada_lst.add(self, None, None, False, ErrCode.SiteNotFound)
            return False

        self._site      = st
        self._site_code = st.code

        if st.status != tSite.Status_Couplet.key_active:
            self._ada_lst.add(self, None, None, False, ErrCode.SiteDisabled)
            return False

        return True


    async def _usr_ok(self):
        """
        Check if the user is valid.

        :return: True if site is ok.
        """
        usr = await self._dao.usr_get(self._site.id, self._usr_id)

        if not usr:
            self._ada_lst.add(self, None, None, False, ErrCode.UserNotFound)
            return False

        if usr.status != tUsr.Status_Couplet.key_active:

            if usr.status == tUsr.Status_Couplet.key_suspended:
                self._ada_lst.add(self, None, None, False, ErrCode.UserSuspended)
                return False

            if usr.status == tUsr.Status_Couplet.key_expired:
                self._ada_lst.add(self, None, None, False, ErrCode.UserExpired)
                return False

            if usr.status == tUsr.Status_Couplet.key_deleted:
                self._ada_lst.add(self, None, None, False, ErrCode.UserDeleted)
                return False

            self._ada_lst.add(self, None, None, False, ErrCode.UserDisabled)
            return False

        self._role = await self._dao.role_get(self._site.id, usr.role_id)

        if not self._role:
            self._ada_lst.add(self, None, None, False, ErrCode.UserHasNoRole)
            return False

        if self._role.status != tRole.Status_Couplet.key_active:
            if self._role.status != tRole.Status_Couplet.key_super_user:
                self._ada_lst.add(self, self._role, None, False, ErrCode.RoleDisabled)
                return False

        return True


    async def _persist_aga(self):
        """
        Save the access granted audit history.
        """
        for aga in self._aga_lst:
            await self._dao.save_access_granted(aga)

        self._aga_lst.clear()


    async def _persist_ada(self):
        """
        Save the access denied audit history.
        """
        for ada in self._ada_lst:
            await self._dao.save_access_denied(ada)

        self._ada_lst.clear()
