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

import mettle.db

from bs_lib.transactionable import Transactionable

import bs_audit

from .db.tables.oaud_search import oAudSearch
from .base_audit            import BaseAudit


class Audit(BaseAudit, Transactionable):
    """
    Audit an object, has built in methods to help with auditing
    mettle generated table objects.
    """

    def __init__(self, dbcon: mettle.db.IConnect, dao_name: str):
        """
        Constructor.

        :param dbcon: Mettle db connection.
        :param dao_name: Name of dao module to use.
        """
        BaseAudit.__init__(self)

        self._dbcon   = dbcon
        self._dao     = bs_audit.dao_by_name(dao_name)


    def begin(self):
        """
        Overload the Transactionable method.
        """
        self._site_id = 0
        self._src     = None
        self._who     = None
        self._diffs.clear()


    def rollback(self):
        """
        Overload Transactionable method, undo all diff changes up to now.
        """
        self._diffs.clear()


    def commit(self) -> int:
        """
        Overload Transactionable method, saves all the audit diffs into transaction.

        :return: (int) The transaction id of the audit.
        """
        if not self._diffs:
            return 0

        if self._site_id < 1:
            raise Exception('Cannot commit audit, site id required.')

        if not self._who:
            raise Exception('Cannot commit audit, user required.')

        if not self._src:
            self._src = '<N/A>'

        total_diffs = 0

        for dobj in self._diffs:
            self._init_table_cfg(dobj['name'])
            total_diffs += self._build_diffs(dobj)

        if total_diffs < 1:
            return 0

        tran = self._dao.dTran(self._dbcon)
        aud  = self._dao.dAud(self._dbcon)
        col  = self._dao.dCol(self._dbcon)
        tbls = []

        tran.insert_deft(self._site_id, self._who, self._src)

        for dobj in self._diffs:
            diffs = dobj['diffs']

            if len(diffs) < 1:
                continue

            tobj = self._cfg.get(dobj['name'])

            kdata = dobj.get('adict')

            if kdata is None:
                kdata = dobj.get('bdict')

            aud.insert_deft(
                tran.rec.id,
                dobj['dtype'],
                dobj['name'],
                dobj['pk'],
                tobj['par'],
                self._get_key(dobj['name'], 'Foreign', tobj['pcols'], kdata))

            if dobj['name'] not in tbls:
                tbls.append(dobj['name'])

            for dcol, dcvals in dobj['diffs'].items():
                col.insert_deft(aud.rec.id, dcol, dcvals[0], dcvals[1])

        if tbls:
            self._dao.dCfgUpdLastChange(self._dbcon).exec_deft("'%s'" % "','".join(tbls))

        self._diffs.clear()

        return tran.rec.id


    def search(self,
               site_id: int,
               dt_from: datetime.datetime = None,
               dt_to:   datetime.datetime = None,
               tname:   str  = None,
               pk:      str  = None,
               usr_id:  str  = None,
               actions: list = None,
               tran_id: int  = 0) -> oAudSearch.List:
        """
        Runs a search of audit history.

        :param site_id: The site id to use.
        :param dt_from: The date time from, req if tran_id = 0.
        :param dt_to: The date time to, req if tran_id = 0.
        :param tname: Table name to search for, req if tran_id = 0.
        :param pk: The primary key of the table to search on, req if tran_id = 0.
        :param usr_id: Optionally only search for this users changes in the db.
        :param actions: Optionally give a list of actions to look for, C, U, D
        :param tran_id: The transaction to search for, 0 = ignore.
        :return: The search audit result list.
        """
        qry = self._dao.dAudSearch(self._dbcon)
        res = oAudSearch.List()

        self._prep_search(qry.irec, site_id, dt_from, dt_to, tname, pk, usr_id, actions, tran_id)

        qry.exec().fetch_all(res)

        return res


    def _init_table_cfg(self, name: str):
        """
        Initialiaze the table config.

        :param name: The table name.
        """
        tobj = self._cfg.get(name)

        if tobj:
            return tobj

        tcfg = self._dao.dCfg(self._dbcon)

        if not tcfg.select_one_deft(name):
            raise Exception('Table [%s] not found in Bitsmiths-Audit table config.' % name)

        tobj = {
            'id'    : tcfg.rec.id,
            'pk'    : tcfg.rec.col_pk.split('|'),
            'ign'   : tcfg.rec.col_ignr.split('|'),
            'par'   : tcfg.rec.par_id,
            'pcols' : tcfg.rec.par_col.split('|'),
        }

        self._cfg[tcfg.rec.id] = tobj

        return tobj
