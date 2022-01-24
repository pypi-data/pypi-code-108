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
import random
import string

from mettle.lib import xMettle

from bs_lib.auto_transaction import AutoTransaction

from .dao          import Dao
from .errcode      import ErrCode
from .user_login   import UserLogin
from .xfura        import xFura

from .db.tables    import tToken


class TokenManager:
    """
    Controls creation, expiring and deleting of tokens for external use.
    """
    MAX_TOKENS_PER_CLIENT = 256    # this is reduced by 100 every minute
    TOK_LEN               = 64

    def __init__(self, dao: Dao):
        """
        Constructor.

        :param dao: The dao object.
        """
        self._dao = dao
        self._pod = dao.pod
        self._log = self._pod.log


    def __del__(self):
        """
        Destructor.
        """
        pass


    def __enter__(self):
        """
        On enter event.
        """
        return self


    def __exit__(self, type, value, traceback):
        """
        On exit event.
        """
        pass


    def create(self, site_code: str, usr_id: str, auth_type: str, auth_data: str) -> tuple:
        """
        Create a new token if the request information is valid

        :param site_code: The site code.
        :param usr_id: The user id to login with.
        :param auth_type: Password/ssh/etc.
        :param auth_data: The passwd/key.
        :return: (ErrorCode, Token)
        """
        self._log.debug("TokenManager.create - start [site_code:%s, usr_id:%s, auth_type:%s]" % (
            site_code, usr_id, auth_type))

        tok = None

        self._pod.dbcon.rollback()

        with UserLogin(self._dao, site_code) as ul:
            try:
                ul.login(usr_id, auth_type, auth_data, None, None, True)
            except xFura as xf:
                self._log.debug('Create token failed [%s]' % str(xf))
                return xf.get_error_code().value, None
            finally:
                self._pod.dbcon.commit()

            with AutoTransaction(self._pod) as at:
                ds    = self._dao.db_dao.dTokenSentry(self._pod.dbcon)
                dtnow = datetime.datetime.now()

                if not ds.try_select_one_deft(ul._acc._site.id):
                    ds.insert_deft(ul._acc._site.id, 0, dtnow)

                ds.lock_one_deft(ul._acc._site.id, self._pod.std_db_lock())

                if ds.rec.tokenCnt > self.MAX_TOKENS_PER_CLIENT:
                    self._log.warning("TokenManager.create - slow down boy, you gonna make a mess \
[site_code:%s, usr_id:%s]" % (site_code, usr_id))
                    return ErrCode.TokenTooMany.value, None

                dt  = self._dao.db_dao.dToken(self._pod.dbcon)
                cnt = 0

                while True:
                    cnt += 1
                    ts   = self._new_tok_str()

                    if not dt.try_select_one_deft(ul._acc._site.id, ts):
                        break

                    if cnt >= 10:
                        raise xMettle('Internal insanity detected. We are probably under \
attack by russian hackers or aliens!')

                exp = dtnow + datetime.timedelta(
                    minutes=ul._acc._role.sess_timeout if ul._acc._role.sess_timeout != 0 else 10)
                ds.rec.tokenCnt += 1

                dt.insert_deft(ul._acc._site.id, ts, usr_id, dtnow, exp, 0, usr_id)
                ds.update()

                tok = dt.rec
                at.commit()

        self._log.debug("TokenManager.create - done [tok:%s]" % str(tok))

        return ErrCode.NoError.value, tok


    def destroy(self, site_code: str, token: str) -> bool:
        """
        Destroys a token by moving it to the history table.

        :param site_code: The site code.
        :param token: Input token
        :return: True if the token was destroyed else false if it was not found or already expired.
        """
        self._log.debug("TokenManager.destroy - start [token:%s]" % token)

        dt   = self._dao.db_dao.dToken(self._pod.dbcon)
        dh   = self._dao.db_dao.dTokenHist(self._pod.dbcon)
        ds   = self._dao.db_dao.dSiteIdByCode(self._pod.dbcon)

        if not ds.exec_deft(site_code).fetch():
            self._log.debug("TokenManager.destroy - done [token:%s.%s, msg:site not found]" % (site_code, token))
            return False

        if not dt.try_select_one_deft(ds.orec.site_id, token):
            self._log.debug("TokenManager.destroy - done [token:%s.%s, msg:not found]" % (site_code, token))
            return False

        dt.lock_one_deft(ds.orec.site_id, token, self._pod.std_db_lock())

        rec = dt.rec

        dh.insert_deft(rec.site_id,
                       rec.id,
                       rec.usr_id,
                       rec.date_created,
                       rec.expires,
                       rec.msg_cnt,
                       rec.modified_by,
                       rec.tm_stamp)

        dt.delete_one_deft(rec.site_id, rec.id)

        self._log.debug("TokenManager.destroy - done [tok:%s.%s]" % (site_code, token))

        return True


    def use(self, site_code: str, token: str) -> tToken:
        """
        Use a token.

        :param site_code: The site code.
        :param token: The token in question to use.
        :return: Result token after use.
        """
        self._log.debug("TokenManager.use - start [site_code:%s, token:%s]" % (site_code, token))

        usErr = 'The given token is not valid.'

        if not site_code or not token:
            self._log.error('Site was not provided')
            raise xMettle(usErr, __name__)

        ds = self._dao.db_dao.dSiteIdByCode(self._pod.dbcon)
        dt = self._dao.db_dao.dToken(self._pod.dbcon)

        if not ds.exec_deft(site_code).fetch():
            self._log.error('Site could be be found with site_code:%s' % site_code)
            raise xMettle(usErr, __name__)

        if not dt.try_select_one_deft(ds.orec.site_id, token):
            self._log.error('Token could not be found: site:%d, token:%s' % (ds.orec.site_id, token))
            raise xMettle(usErr, __name__)

        dt.lock_one_deft(ds.orec.site_id, token, self._pod.std_db_lock())

        if not self._token_valid(dt.rec):
            self._log.error('Token is not valid: site:%d, token:%s' % (ds.orec.site_id, token))
            raise xMettle(usErr, __name__)

        dt.rec.msg_cnt += 1
        dt.update()

        self._log.debug("TokenManager.use - done [res:%s]" % str(dt.rec))

        return dt.rec


    def valid(self, site_code: str, token: str) -> bool:
        """
        Checks if a token is still valid.

        :param site_code: The site code.
        :param token: The token in question to use.
        :return: True if the token is valid.
        """
        self._log.debug("TokenManager.valid - start [site_code:%s, token:%s]" % (site_code, token))

        res = True

        if not token:
            res = False
        else:
            tdb = self._dao.db_dao.dTokenBySite(self._pod.dbcon)

            if not tdb.exec_deft(site_code, token).fetch():
                res = False
            else:
                res = self._token_valid(tdb.orec)

        self._log.debug("TokenManager.valid - done [res:%s]" % str(res))

        return res


    def archive_expired_tokens(self, date_expired: datetime.datetime) -> int:
        """
        Moves expired tokens to the archive table.

        :param date_expired: Expirey date, set to datetime.now() if you want to archive all expire tokens.
        :return: The number of tokens moved.
        """
        self._log.debug("TokenManager.archive_expired_tokens - start [date_expired:%s]" % str(date_expired))

        tdb  = self._dao.db_dao.dToken(self._pod.dbcon)
        tqry = self._dao.db_dao.dTokenExpired(self._pod.dbcon)
        hdb  = self._dao.db_dao.dTokenHist(self._pod.dbcon)
        recs = []

        tqry.exec_deft(0, date_expired).fetch_all(recs)

        for rec in recs:
            hdb.insert_deft(rec.site_id,
                            rec.id,
                            rec.usr_id,
                            rec.date_created,
                            rec.expires,
                            rec.msg_cnt,
                            rec.modified_by,
                            rec.tm_stamp)

            tdb.delete_one_deft(rec.site_id, rec.id)

        self._log.debug("TokenManager.archive_expired_tokens - done [cnt:%d]" % len(recs))

        return len(recs)


    def _new_tok_str(self) -> str:
        """
        Generates a new token string.

        :return: The new token.
        """
        return ''.join(random.SystemRandom().choice(
            string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(self.TOK_LEN))


    def _token_valid(self, tok) -> bool:
        """
        Check if a token is still valid.

        :param tok: (tToken) Token record.
        :return: True if valkd.
        """
        if tok.expires <= datetime.datetime.now():
            return False

        return True
