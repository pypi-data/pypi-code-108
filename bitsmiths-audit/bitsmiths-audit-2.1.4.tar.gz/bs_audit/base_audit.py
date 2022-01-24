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
import json
import uuid

import mettle.db
import mettle.io

from bs_lib     import query_builder

from .db.tables import iAudSearch


class BaseAudit:
    """
    Base audit class that has common functions
    """

    def __init__(self):
        """
        Constructor.
        """
        self._dbcon   = None
        self._dao     = None
        self._cfg     = {}
        self._diffs   = []
        self._site_id = 0
        self._src     = None
        self._who     = None


    def aud(self, site_id: int, src: str, who: str) -> "BaseAudit":
        """
        Set the source and user who is doing the changes.

        :param site_id: The site the audit is occuring for.
        :param src: The program/operation that is doing the audit.
        :param who: The user making the changes.
        :return: Returns itself for convenience.
        """
        self._site_id = site_id
        self._src    = src
        self._who    = who

        return self


    def diff(self, before: object, after: object, tbl_name: str = None) -> None:
        """
        Add a diff audit.

        :param before: The before object.
        :param after: The after object.
        :param tbl_name: Optionally specifiy the table name of before/after object
        """
        bname, bdict = self._read_object(before)
        aname, adict = self._read_object(after)

        if tbl_name is None and bname is None and aname is None:
            raise Exception('Table name not specified.')

        if not tbl_name:
            if bname and aname and bname != aname:
                raise Exception('Table names do not match [before:%s, after:%s]' % (bname, aname))

            tbl_name = bname or aname

        if not bdict and not adict:
            return

        self._diffs.append({
            'name'  : tbl_name,
            'bdict' : bdict,
            'adict' : adict,
            'diffs' : {},
            'aud'   : None,
        })


    def diff_bulk(self, before_list: list, after_list: list, tbl_name: str = None) -> None:
        """
        Bulk audits a set of items.

        :param before_list: List of before objects, can be None for bulk inserts.
        :param after_list: List of after objects, can be None for bulk delets.
        :param tbl_name: Optionally specifiy the table name of before/after objects.
        """
        if not before_list and not after_list:
            return

        if not before_list:
            for x in after_list:
                self.diff(None, x, tbl_name)
        elif not after_list:
            for x in before_list:
                self.diff(x, None, tbl_name)
        else:
            if len(before_list) != len(after_list):
                raise Exception('Before list [%d] and after list [%d] are not the same length!' % (
                    len(before_list), len(after_list)))

            idx = 0

            while idx < len(before_list):
                self.diff(before_list[idx], after_list[idx])
                idx += 1


    def _prep_search(self,
                     irec:    iAudSearch,
                     site_id: int,
                     dt_from: datetime.datetime,
                     dt_to:   datetime.datetime,
                     tname:   str,
                     pk:      str,
                     usr_id:  str,
                     actions: list,
                     tran_id: int):
        """
        Prepare the search query.

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
        irec.site_id = site_id

        if tran_id > 0:
            irec.date_from = None
            irec.date_fo   = None
            irec.criteria = query_builder.dyn_crit(tran_id, 't', 'id')
            return

        irec.date_from = dt_from
        irec.date_fo   = dt_to

        if usr_id:
            irec.criteria += query_builder.dyn_crit(usr_id, 't', 'who')

        if tname:
            irec.criteria += query_builder.dyn_crit(tname, 'a', 'tbl_id')

            if pk:
                irec.criteria += query_builder.dyn_crit(pk, 'a', 'tbl_key')

        if actions:
            irec.criteria += query_builder.dyn_list(actions, 'a', 'action')


    def _read_object(self, obj: object) -> tuple:
        """
        Attempts to read an object putting all its fields into a dictionary.

        :param obj: A class instance or dictionary.
        :return: (name, dict), note return values can be None depending on obj.
        """
        if obj is None:
            return (None, None)

        if type(obj) == dict:
            return (None, obj)

        name = None

        if isinstance(obj, mettle.io.ISerializable):
            name = obj._name()

        return (name, obj.__dict__)


    def _get_key(self, tname: str, key_type: str, cols: list, data: dict) -> str:
        """
        Gets the cols from the data.

        :param tname: Table name
        :param key_type: The key type.
        :param cols: List of key columns.
        :param data: All data columns.
        :return: Pipe delimetered cols string.
        """
        if len(cols) < 1:
            return ''

        res = ''

        for pcol in cols:
            if pcol == '':
                continue

            if pcol not in data:
                raise Exception('%s key column [%s] not found [table:%s]' % (
                    key_type, pcol, tname))

            val = data[pcol]

            if res == '':
                res = self._text_value(val, pcol)
            else:
                res += '|%s' % self._text_value(val, pcol)

        return res


    def _build_diffs(self, dobj: dict) -> int:
        """
        Work out the differenes for each dict object.

        :param dobj: Diff dictionary object.
        :return: Total diffs detected.
        """
        tobj  = self._cfg[dobj['name']]
        diff  = dobj['diffs']
        bdata = dobj['bdict']
        adata = dobj['adict']

        if bdata is None:
            dobj['dtype'] = 'C'

            for key, val in adata.items():
                if key in tobj['ign']:
                    continue

                diff[key] = ['', self._text_value(val, key)]

            for pk in tobj['pk']:
                if pk not in adata.keys():
                    raise Exception('Primary key [%s] not found for table [%s] - data[%s]' % (
                        pk, dobj['name'], str(adata)))

            dobj['pk'] = self._get_key(dobj['name'], 'Primary', tobj['pk'], adata)

        elif adata is None:
            dobj['dtype'] = 'D'

            for key, val in bdata.items():
                if key in tobj['ign']:
                    continue

                diff[key] = [self._text_value(val, key), '']

            dobj['pk'] = self._get_key(dobj['name'], 'Primary', tobj['pk'], bdata)

        else:
            dobj['dtype'] = 'U'
            read  = []

            for key, val in bdata.items():
                read.append(key)

                if key in tobj['ign']:
                    continue

                btxt = self._text_value(val, key)
                atxt = self._text_value(adata.get(key), key)

                if btxt != atxt:
                    diff[key] = [btxt, atxt]

            for key, val in adata.items():
                if key in read:
                    continue

                if key in tobj['ign']:
                    continue

                btxt = self._text_value(None, key)
                atxt = self._text_value(val, key)

                if btxt != atxt:
                    diff[key] = [btxt, atxt]

            bpk = self._get_key(dobj['name'], 'Primary', tobj['pk'], bdata)
            apk = self._get_key(dobj['name'], 'Primary', tobj['pk'], adata)

            if apk != bpk:
                raise Exception('Primary keys do not match [beforePK:%s, afterPK:%s, table:%s]' % (
                    bpk, apk, dobj['name']))

            dobj['pk'] = bpk

        return len(diff)


    def _text_value(self, val: object, pcol: str) -> str:
        """
        Gets the standard text value of the value.

        :param val: The value object.
        :param pcol: The column name.
        :return:  The text value.
        """
        if val is None:
            return ''

        if type(val) == str:
            return val[:128]

        if type(val) == int or type(val) == float or type(val) == bool:
            return str(val)

        if type(val) == datetime.date:
            if val == datetime.date.min:
                return ''

            return val.strftime('%Y-%m-%d')

        if type(val) == datetime.datetime:
            if val == datetime.datetime.min:
                return ''

            return val.strftime('%Y-%m-%d %H:%M:%S')

        if type(val) == datetime.time:
            return val.strftime('%H:%M:%S')

        if isinstance(val, dict) or isinstance(val, list):
            return json.dumps(val)[:128]

        if isinstance(val, uuid.UUID):
            return str(val)

        if type(val) == bytes or type(val) == bytearray:
            return ''

        raise Exception('Type [%s] not expected for audit purposes [column:%s].' % (
            str(type(val)), pcol))
