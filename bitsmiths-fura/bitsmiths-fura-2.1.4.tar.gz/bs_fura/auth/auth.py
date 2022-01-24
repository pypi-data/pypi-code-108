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
import time

from mettle.lib import xMettle

from bs_fura.audit     import Audit
from bs_fura.err_code  import ErrCode
from bs_fura.otp       import Otp
from bs_fura           import util

from bs_fura.db.tables import tUsrAuth

from .base_auth import BaseAuth


class Auth(BaseAuth):
    """
    Base authorize object.
    """

    def __init__(self):
        """
        Constructor.
        """
        BaseAuth.__init__(self)


    def __exit__(self, type, value, traceback):
        """
        On exit event.
        """
        self.save_user_auth()


    def login(self, data: "str|bytes", login_ip: str = None, login_geo: str = None, token_mode: bool = False) -> ErrCode:
        """
        Check if the user can log into the system.

        :param data: The password/ssk key something else to auth with.
        :param login_ip: Optionally add in the login ip address.
        :param login_geo: Optionally add the login geo location.
        :param token_mode: In token mode, going over fail counts is not an automatic failure.
        :return: The ErrCode result.
        """
        if type(data) != str:
            return ErrCode.AuthWrongType

        if not data:
            return ErrCode.AuthEmpty

        au_rec = self._auth_rec_load()

        if not token_mode and self.is_token_based():
            token_mode = True

        if au_rec is None or not au_rec.auth_data:
            return ErrCode.AuthNotFound

        if not token_mode and au_rec.fail_cnt >= self.MAX_FAIL_CNT:
            return ErrCode.AuthMaxFailures

        au_rec.last_ip  = '' if login_ip  is None else str(login_ip)
        au_rec.last_geo = '' if login_geo is None else str(login_geo)

        if not self._auth_data_for_compare(data, au_rec):
            au_rec.fail_cnt  += 1
            au_rec.last_fail  = datetime.datetime.now()

            usr_rec = self._dao.usr_get(self._site_id, self._usr_id)
            remtag  = { 'remaining' : '0' }

            if au_rec.fail_cnt < self.MAX_FAIL_CNT:
                remtag['remaining'] = str(self.MAX_FAIL_CNT - au_rec.fail_cnt)

            if usr_rec.opt_fail_login:
                self._dao.send_loco('loco.login_attempt',
                                    usr_rec,
                                    remtag)

            if token_mode and au_rec.fail_cnt >= self.MAX_FAIL_CNT:
                time.sleep(au_rec.fail_cnt)  # Fuck you brute force attacks.

            return ErrCode.AuthInvalid

        au_rec.last_succ = datetime.datetime.now()
        au_rec.fail_cnt  = 0

        return ErrCode.NoError


    def set_auth_data(self,
                      audit      : Audit,
                      data       : str,
                      otp_str    : str = None,
                      otp_method : str = None,
                      login_ip   : str = None,
                      login_geo  : str = None) -> ErrCode:
        """
        Sets a new password/key

        :param audit: The audit object to use.
        :param data: The password/ssh key something else to auth with.
        :param otp_str: If None, skips the otp check.
        :param otp_method: The otp method if an otp str is present.
        :param login_ip: Optionally add in the login ip address.
        :param login_geo: Optionally add the login geo location.
        :return: The ErrCode result.
        """
        if not isinstance(data, str):
            return ErrCode.AuthWrongType

        if not data:
            return ErrCode.AuthEmpty

        self._auth_data_ok(data)

        if otp_str:
            with Otp(self._dao, self._site_id, self._usr_id) as otp:
                out_meta = {}
                ecode   = otp.ok(otp_str, otp_method, 'auth-reset', out_meta)

                if ErrCode.NoError != ecode:
                    return ecode

                if out_meta and out_meta.get('addr') and audit:
                    urec = self._dao.usr_lock(self._site_id, self._usr_id)

                    if util.confirm_usr_addr(urec, out_meta.get('addr')):
                        self._dao.pod.usr_id = urec.id
                        self._dao.usr_update(audit, urec, True)

        au_rec = self._auth_rec_load()

        if au_rec is None:
            au_rec = self._auth_rec_new()

        au_rec.salt        = self._auth_salt_for_save(data)
        au_rec.auth_data   = self._auth_data_for_save(data, au_rec.salt)
        au_rec.last_ip     = '' if login_ip  is None else str(login_ip)
        au_rec.last_geo    = '' if login_geo is None else str(login_geo)
        au_rec.fail_cnt    = 0
        au_rec.modified_by = self._usr_id

        self.save_user_auth()

        return ErrCode.NoError


    def change(self, new_data: str, old_data: str) -> ErrCode:
        """
        Changes the existing password/key.

        :param new_data: The new password/ssh key, or something else to auth with.
        :param old_data: The old password/ssh key, or something else to auth with.
        :return: The ErrCode result.
        """
        if not isinstance(new_data, str) or not isinstance(old_data, str):
            return ErrCode.AuthWrongType

        if not new_data or not old_data:
            return ErrCode.AuthEmpty

        self._auth_data_ok(new_data)

        au_rec = self._auth_rec_load()

        if au_rec is None:
            raise xMettle('Old %s does not match.' % self.auth_type_name())

        if not self._auth_data_for_compare(old_data, au_rec):
            raise xMettle('Old %s does not match.' % self.auth_type_name())

        au_rec.salt        = self._auth_salt_for_save(new_data)
        au_rec.auth_data   = self._auth_data_for_save(new_data, au_rec.salt)
        au_rec.last_ip     = ''
        au_rec.last_geo    = ''
        au_rec.fail_cnt    = 0
        au_rec.modified_by = self._usr_id

        self.save_user_auth()

        return ErrCode.NoError


    def read_token(self) -> tuple:
        """
        Reads the token.

        returns (ErrCode, token).
        """
        if not self.is_token_based():
            raise Exception('Not a token based authenticator!')

        au_rec = self._auth_rec_load()

        if au_rec is None:
            return ErrCode.AuthNotFound, ''

        return ErrCode.NoError, au_rec.auth_data


    def save_user_auth(self):
        """
        Save the user auth update if there is one.
        """
        if not self._au_rec:
            return

        self._dao.usrauth_save(self._au_rec)
        self._au_rec = None


    def get_auth_policy(self) -> dict:
        """
        Gets the auth policy for the auth type.

        :return: Dictionary of policy items.
        """
        apDescr = self._dao.read_config(self._site_id, 'auth-policy.%s.descr' % self.auth_type(), str)
        apRegex = self._dao.read_config(self._site_id, 'auth-policy.%s.regex' % self.auth_type(), str)

        return {
            'descr' : apDescr,
            'regex' : apRegex,
        }


    def _auth_rec_load(self) -> tUsrAuth:
        """
        Loads the auth record.

        :return: The auth record or None if not found.
        """
        self._au_rec = self._dao.usrauth_get(self._site_id, self._usr_id, self.auth_type())

        return self._au_rec


    def _auth_rec_new(self) -> tUsrAuth:
        """
        Loads the auth record.

        :return: (tUsrAuth) The auth record or None if not found.
        """
        self._au_rec = self._dao.usrauth_new(self._site_id, self._usr_id, self.auth_type())

        return self._au_rec
