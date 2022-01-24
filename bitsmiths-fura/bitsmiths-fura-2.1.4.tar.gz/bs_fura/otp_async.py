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
import copy
import datetime
import random
import string

# from .dao_async        import DaoAsync
from .err_code   import ErrCode


class OtpAsync:
    """
    This class handles all async otp operations.
    """
    METHOD_EMAIL  = 'E'
    METHOD_SMS    = 'S'
    MIN_OTP_LEN   = 4
    MIN_TIMEOUT   = 1
    MAX_OTP_FAILS = 3


    def __init__(self,
                 dao,  # : DaoAsync,
                 site_id : int,
                 usr_id  : str):
        """
        Constructor.

        :param dao: The fura async DAO object.
        :param site_id: The site identifier.
        :param usr_id: The usr identifier.
        """
        self._dao      = dao
        self._site_id  = site_id
        self._usr_id   = usr_id
        self._usr_otp  = None


    async def __aenter__(self):
        """
        On enter event.
        """
        return self


    async def __aexit__(self, type, value, traceback):
        """
        On exit event.
        """
        pass


    async def new_otp(self, otp_method: str, target: str, meta_data: dict = None) -> str:
        """
        Generate a new otp for the given otp method.

        :param otp_method: The reset method requested.
        :param target: The target the otp is for.
        """
        otp_str     = await self.generate_otp(self._site_id, otp_method)
        otp_timeout = await self.get_otp_timeout(self._site_id, otp_method)

        self._usr_otp = await self._dao.usrotp_get(self._site_id, self._usr_id)

        if not self._usr_otp:
            self._usr_otp = await self._dao.usrotp_new(self._site_id, self._usr_id)

        self._usr_otp.otp_method  = otp_method
        self._usr_otp.otp         = otp_str
        self._usr_otp.expire      = datetime.datetime.now() + datetime.timedelta(minutes = otp_timeout)
        self._usr_otp.used        = False
        self._usr_otp.target      = target or ''
        self._usr_otp.fail_cnt    = 0
        self._usr_otp.meta_data   = meta_data

        await self._dao.usrotp_save(self._usr_otp)

        return otp_str


    async def ok(self, otp_str: str, otp_method: str, target: str, out_meta_data: dict = None) -> int:
        """
        Checks if the otp is valid or ok.

        :param otp_str: The otp to check.
        :param otp_method: The method to check.
        :param target: The target to check.
        :param out_meta_data: If read ok and this is not None, will populate the otp meta data into here.
        :return: The ErrCode result.
        """
        self._usr_otp = await self._dao.usrotp_get(self._site_id, self._usr_id)

        if not self._usr_otp:
            self._dao.pod.log.warning('No OTP record found [site_id:%d, usr_id:%s, target:%s]' % (
                self._site_id, self._usr_id, target))
            return ErrCode.AuthOTPNotFound

        if self._usr_otp.expire != datetime.datetime.min and self._usr_otp.expire < datetime.datetime.now():
            return self._log_otp_error(ErrCode.AuthOTPExpired, 'OTP has expired')

        if self._usr_otp.otp != otp_str:
            self._usr_otp.fail_cnt += 1
            await self._dao.usrotp_save(self._usr_otp)
            return self._log_otp_error(ErrCode.AuthOTPInvlalid, 'Invalid OTP: "%s"' % (otp_str))

        # TODO, consider making this a config param check in required in the future
        # if self._usr_otp.otp_method != otp_method:
        #     self._usr_otp.fail_cnt += 1
        #     self._dao.usrotp_save(self._usr_otp)
        #     return self._log_otp_error(ErrCode.AuthOTPTMethod, 'Invalid Mehod: "%s"' % (otp_method))

        if self._usr_otp.target != target:
            self._usr_otp.fail_cnt += 1
            await self._dao.usrotp_save(self._usr_otp)
            return self._log_otp_error(ErrCode.AuthOTPTarget, 'Invalid target: "%s"' % (target))

        if self._usr_otp.used:
            return self._log_otp_error(ErrCode.AuthOTPUsed, 'OTP already used')

        if self._usr_otp.fail_cnt >= self.MAX_OTP_FAILS:
            return self._log_otp_error(ErrCode.AuthOTPTMaxFails, 'Max failures reached')

        if self._usr_otp.meta_data and out_meta_data:
            out_meta_data.update(self._usr_otp.meta_data)

        self._usr_otp.used = True
        await self._dao.usrotp_save(self._usr_otp)
        self._dao.pod.log.info('OTP used ok [%s]' % (str(self._usr_otp)))

        return ErrCode.NoError


    async def generate_otp(self, site_id, otp_method) -> str:
        """
        Generates a new otp string for the given method.

        :param site_id: For which fura site.
        :param otp_method: The reset method requested.
        :return: The otp
        """
        if otp_method == self.METHOD_EMAIL:
            otp_len  = await self._dao.read_config(site_id, 'otp.email.length',  int)
            otp_cont = await self._dao.read_config(site_id, 'otp.email.content', str)
        elif otp_method == self.METHOD_SMS:
            otp_len  = await self._dao.read_config(site_id, 'otp.sms.length',  int)
            otp_cont = await self._dao.read_config(site_id, 'otp.sms.content', str)
        else:
            raise Exception('OTP method not expected [%s]' % (otp_method))

        if otp_len < self.MIN_OTP_LEN:
            raise Exception('Miniumum OTP length is [%d]' % (self.MIN_OTP_LEN))

        if otp_cont == 'alpha':
            otp = ''.join(random.SystemRandom().choice(
                string.ascii_uppercase +
                string.ascii_lowercase) for _ in range(otp_len))
        elif otp_cont == 'numeric':
            otp = ''.join(random.SystemRandom().choice(
                string.digits) for _ in range(otp_len))
        elif otp_cont == 'alphanumeric':
            otp = ''.join(random.SystemRandom().choice(
                string.ascii_uppercase +
                string.ascii_lowercase +
                string.digits) for _ in range(otp_len))
        else:
            raise Exception('Otp content type not exepcted [%s]' % (otp_cont))

        return otp


    async def get_otp_timeout(self, site_id, otp_method) -> int:
        """
        Generates a new otp string for the given method.

        :param site_id: For which fura site.
        :param otp_method: The reset method requested.
        :return: The otp
        """
        if otp_method == self.METHOD_EMAIL:
            tout = await self._dao.read_config(site_id, 'otp.email.timeout', int)
        elif otp_method == self.METHOD_SMS:
            tout = await self._dao.read_config(site_id, 'otp.sms.timeout', int)
        else:
            raise Exception('OTP method not expected [%s]' % (otp_method))

        if tout < self.MIN_TIMEOUT:
            return self.MIN_TIMEOUT

        return tout


    def _log_otp_error(self, ecode: int, msg: str) -> int:
        """
        Log an otp error without showing the otp str.

        :param ecode: The error code to return.
        :param msg: The message to log.
        :return: The ecode param.
        """
        rec = copy.copy(self._usr_otp)

        rec.otp = '****'

        self._dao.pod.log.warning('%s - [%s]' % (msg, str(rec)))

        return ecode
