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

from bs_lib.sentinel_thread  import SentinelThread
from bs_lib.auto_transaction import AutoTransaction


class TokenSentryPluggin(SentinelThread):
    """
    Pluggin for the sentinel that expires old tokens, and reduces
    the token count over a periodical basis.
    """

    COOLDOWN_TIME  = 60.0  # 1 minute
    COOLDOWN_COUNT = 100

    def __init__(self):
        """
        Constructor.
        """
        super().__init__('tokensentry')


    def pod_required(self) -> bool:
        return True


    def process(self):
        """
        Main process method.
        """
        dtnow = datetime.datetime.now()

        self._cooldown_sentry(dtnow)

        if self._shutdown:
            return

        self._archive_tokens(dtnow)


    def _cooldown_sentry(self, currtime: datetime.datetime):
        """
        Cools the sentry down allowing more tokens to be generated.

        :param currtime: (datetime) The time to cooldown from.
        """
        with AutoTransaction(self._pod) as at:
            poll_time = currtime - datetime.timedelta(seconds=self.COOLDOWN_TIME)
            cool_qry  = self._pod.dao.dTokenSentryCooldown(self._pod.dbcon)
            all_cool  = []

            cool_qry.exec_deft(poll_time).fetch_all(all_cool)

            if len(all_cool) < 1:
                return

        if self._shutdown:
            return

        dts = self._pod.dao.dTokenSentry(self._pod.dbcon)

        for x in all_cool:
            with AutoTransaction(self._pod) as at:

                dts.lock_one_deft(x.siteId, self._pod.std_db_lock())

                diff = currtime - dts.rec.last_poll
                tots = diff.total_seconds()

                while tots >= self.COOLDOWN_TIME and dts.rec.token_cnt > 0:
                    tots                 -= self.COOLDOWN_TIME
                    dts.rec.token_cnt -= self.COOLDOWN_COUNT

                if dts.rec.token_cnt < 0:
                    dts.rec.token_cnt = 0

                dts.rec.last_poll = currtime

                self._log.info(' - Cooled token sentry, before[%s] -> after[%s]' % (str(x), str(dts.rec)))

                dts.update()
                at.commit()

                if self._shutdown:
                    break


    def _archive_tokens(self, currtime: datetime.datetime):
        """
        Archive expired tokens.

        :param currtime: (datetime) The time to archive from.
        """
        with AutoTransaction(self._pod) as at:
            exp_qry = self._pod.dao.dTokenExpired(self._pod.dbcon)
            all_exp = []

            exp_qry.exec_deft(0, currtime).fetch_all(all_exp)

        if len(all_exp) < 1:
            return

        self._log.debug('Expiring [%d] tokens' % len(all_exp))

        dtok  = self._pod.dao.dToken(self._pod.dbcon)
        dhist = self._pod.dao.dTokenHist(self._pod.dbcon)
        cnt   = 0

        if len(all_exp) > 1000:
            all_exp = all_exp[:1000]

        if self._shutdown:
            return

        with AutoTransaction(self._pod) as at:
            for exp in all_exp:
                cnt  += 1
                dhist.insert_deft(exp.siteId,
                                  exp.id,
                                  exp.usr_id,
                                  exp.date_created,
                                  exp.expires,
                                  exp.msg_cnt,
                                  exp.modified_by,
                                  exp.tm_stamp)

                dtok.delete_one_deft(exp.siteId, exp.id)

                if self._shutdown:
                    break

            at.commit()

        self._log.info('Archived [%d] tokens.' % cnt)
