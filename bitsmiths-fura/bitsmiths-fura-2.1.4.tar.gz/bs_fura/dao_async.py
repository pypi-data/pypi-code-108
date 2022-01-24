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
import json

from mettle.lib import xMettle

import mettle.db

from bs_lib      import common
from bs_lib      import PodAsync
from bs_lib      import query_builder

from bs_audit.audit_async import AuditAsync as BsAudit

from bs_loco.trigger.loco_trig_async  import LocoTrigAsync

import bs_fura

from .audit        import Audit
from .config_async import ConfigAsync
from .otp_async    import OtpAsync
from .             import util

from .db.tables   import tEatok
from .db.tables   import tFunc
from .db.tables   import tSite
from .db.tables   import tUla
from .db.tables   import tUsr
from .db.tables   import tUsrAuth
from .db.tables   import tUsrOtp


class DaoAsync:
    """
    Data async access object.  This class can be overloaded to do
    caching if need be in the future.
    """

    def __init__(self, pod: PodAsync, db_dao, loco_trig: LocoTrigAsync = None):
        """
        Constructor.

        :param pod: The async pod to use.
        :param dao: The dao library to use.
        :param loco_trig: Optionally provide the loco trigger to use.
        """
        self.pod        = pod

        if type(db_dao) == str:
            self.db_dao = bs_fura.dao_by_name(db_dao, 'dao_async')
        else:
            self.db_dao = db_dao

        self.cfg        = ConfigAsync()
        self.loco_trig  = loco_trig
        self.site_cache = {}


    async def initialize(self, pod: PodAsync = None):
        """
        Back to initialize functions, lol. Anyway this loads the local trigger if it
        was not already loaded.

        :param pod: Optionally set a new pod.
        """
        if pod:
            self.pod = pod

        if not self.loco_trig:
            self.loco_trig = await self._init_loco_trig()


    async def _init_loco_trig(self) -> LocoTrigAsync:
        """
        Initialize a new logo trigger from the config table.
        """
        loco_type = await self.read_config(0, 'loco.trigger.type', str)
        loco_cfg  = await self.read_config(0, 'loco.trigger.cfg',  str)
        lcfg      = None if not loco_cfg else json.loads(loco_cfg)

        from bs_loco import trigger

        return await trigger.get_trigger_async(self.pod, loco_type, lcfg)


    def dao_name(self) -> str:
        """
        Gets data access object name.

        :return: The name of the object.
        """
        return self.db_dao.__package__.split('.')[-1]


    async def eatoken_get(self, site_id: int, tok: str, lock: bool = True) -> tEatok:
        """
        Gets the elevated access token if it exists.

        :param site_id: The site id.
        :param tok: The token string.
        :param lok: Lock the record or not.
        :return: Token record if it exists else None.
        """
        fnd = self.db_dao.dEatokByTok(self.pod.dbcon)

        if not await (await fnd.exec_deft(site_id, tok)).fetch():
            return None

        dt = self.db_dao.dEatok(self.pod.dbcon)

        if not await dt.try_select_one_deft(fnd.orec.id):
            return None

        if lock:
            await dt.lock_one_deft(fnd.orec.id, self.std_db_lock())

        return dt.rec


    async def eatoken_incr_usage(self, tok_id: int):
        """
        Increment the token usage.

        :param tokId: The token id.
        """
        await self.db_dao.dEatokIncrUsage(self.pod.dbcon).exec_deft(tok_id)


    async def func_get(self, func_id: str) -> tFunc:
        """
        Gets the function record.

        :param func_id: The function id.
        :return: The func rec, None if not found.
        """
        f = self.db_dao.dFunc(self.pod.dbcon)

        if not await f.try_select_one_deft(func_id):
            return None

        return f.rec


    async def role_get(self, site_id: int, role_id: str) -> str:
        """
        Gets the users role.

        :param site_id: (int) The site id.
        :param role_id: (string) The role id.
        :return: (tRole) The role rec or None if not found.
        """
        r = self.db_dao.dRole(self.pod.dbcon)

        if not await r.try_select_one_deft(site_id, role_id):
            return None

        return r.rec


    async def rolefuncrel_get(self, site_id: int, func_id: str, role_id: str) -> bool:
        """
        Check if the role func rel exists.

        :param site_id: The site id.
        :param func_id: The func id.
        :param role_id: The role id.
        :return: True if exists else False.
        """
        rfr = self.db_dao.dRoleFuncRelExists(self.pod.dbcon)

        return await (await rfr.exec_deft(site_id, func_id, role_id)).fetch()


    async def site_get(self, site_code: "str|int") -> tSite:
        """
        Gets the site by its code or identifier.

        :param site_code: The site identifier (int) or code (str).
        :return: The site record, or None if not found.
        """
        sobj = self.site_cache.get(site_code)

        if sobj:
            return sobj

        if isinstance(site_code, int):
            s = self.db_dao.dSite(self.pod.dbcon)

            if not await s.try_select_one_deft(site_code):
                return None

            self.site_cache[s.rec.id]   = s.rec
            self.site_cache[s.rec.code] = s.rec

            return s.rec

        s = self.db_dao.dSiteByCode(self.pod.dbcon)

        if not await (await s.exec_deft(site_code)).fetch():
            return None

        self.site_cache[s.orec.id]   = s.orec
        self.site_cache[s.orec.code] = s.orec

        return s.orec


    async def usr_get(self, site_id: int, usr_id: str) -> tUsr:
        """
        Gets the user by it's id.

        :param site_id: The site id.
        :param usr_id: The user id.
        :return: The user record.
        """
        u = self.db_dao.dUsr(self.pod.dbcon)

        if not await u.try_select_one_deft(site_id, usr_id):
            return None

        return u.rec


    async def usr_search(self,
                         site_id: int,
                         usr_id: str,
                         role_list: list,
                         name_first: str,
                         name_last: str,
                         email: str,
                         cellno: str,
                         title: str,
                         usr_type: str,
                         status_list: list) -> tUsr.List:
        """
        Search for users on the given input critiera.
        """
        qry = self.db_dao.dUsrSearch(self.pod.dbcon)
        res = tUsr.List()

        qry.irec.site_id = site_id

        if usr_id:
            qry.irec.criteria += query_builder.dyn_crit(usr_id,   'u', 'id', always_like=True)

        if role_list:
            qry.irec.criteria += query_builder.dyn_list(role_list,  'u', 'role_id')

        if name_first:
            qry.irec.criteria += query_builder.dyn_crit(name_first,  'u', 'name_first', always_like=True)

        if name_last:
            qry.irec.criteria += query_builder.dyn_crit(name_last,  'u', 'name_last', always_like=True)

        if email:
            qry.irec.criteria += query_builder.dyn_crit(email,  'u', 'email1', always_like=True)

        if cellno:
            qry.irec.criteria += query_builder.dyn_crit(cellno,  'u', 'cellno1', always_like=True)

        if title:
            qry.irec.criteria += query_builder.dyn_crit(title,  'u', 'title', always_like=True)

        if usr_type:
            qry.irec.criteria += query_builder.dyn_crit(usr_type,  'u', 'usrtype_id')

        if status_list:
            qry.irec.criteria += query_builder.dyn_list(status_list,  'u', 'status')

        await qry.exec()
        await qry.fetch_all(res)

        return res


    async def usr_lock(self, site_id: int, usr_id: str) -> tUsr:
        """
        Locks the user by it's id.

        :param site_id: The site id.
        :param usr_id: The user id.
        :return: (tUser) The site record, or None if not found.
        """
        u = self.db_dao.dUsr(self.pod.dbcon)

        await u.lock_one_deft(site_id, usr_id, self.pod.std_db_lock())

        return u.rec


    async def usr_create(self, audit: BsAudit, rec: tUsr) -> tUsr:
        """
        Create a new user.

        :param audit: The audit object to use.
        :param rec: The user record to update.
        :param internal: This is an internal safe update.
        :return: The user record updated.
        """
        du = self.db_dao.dUsr(self.pod.dbcon)

        rec.modified_by = self.pod.usr_id

        await du.insert(rec)

        audit.aud(rec.site_id, __name__, rec.modified_by).diff(None, rec, 'fura.usr')

        return rec


    async def usr_update(self, audit: BsAudit, rec: tUsr, internal: bool = False) -> tUsr:
        """
        Update the user record.

        :param audit: The audit object to use.
        :param rec: The user record to update.
        :param internal: This is an internal safe update.
        :return: The user record updated.
        """
        du = self.db_dao.dUsr(self.pod.dbcon)

        await du.lock_one_deft(rec.site_id, rec.id, self.pod.std_db_lock())

        if du.rec.tm_stamp.replace(microsecond=0) != rec.tm_stamp.replace(microsecond=0):
            raise xMettle("Stale data. Please refresh and try again.")

        bef = copy.copy(du.rec)

        if bef.date_activate and bef.date_activate <= datetime.date.today():
            rec.date_activate  = bef.date_activate

        if not internal:
            rec.status      = bef.status
            rec.email1_conf  = bef.email1_conf
            rec.email2_conf  = bef.email2_conf
            rec.cellno1_conf = bef.cellno1_conf
            rec.cellno2_conf = bef.cellno2_conf
            rec.role_id      = bef.role_id

            if rec.email1 != bef.email1:
                rec.email1_conf = False

            if rec.email2 != bef.email2:
                rec.email2_conf = False

            if rec.cellno1 != bef.cellno1:
                rec.cellno1_conf = False

            if rec.cellno2 != bef.cellno2:
                rec.cellno2_conf = False

        rec.modified_by = self.pod.usr_id

        await du.update(rec)

        audit.aud(rec.site_id, __name__, rec.modified_by).diff(bef, rec, 'fura.usr')

        return rec


    async def usr_role_rel_get(self, site_id: int, usr_id: str) -> str:
        """
        Gets the users role rel id for the user.

        :param site_id: The site id.
        :param usr_id: The user id.
        :return: The role id or None if not found.
        """
        urr = self.db_dao.dUsrRoleRelByUsr(self.pod.dbcon)

        if not await (await urr.exec_deft(site_id, usr_id)).fetch():
            return None

        return urr.orec.role_id


    def std_db_lock(self, mili_seconds: int = 500, retrys: int = 10) -> mettle.db.DBLock:
        """
        Gets a lock that retries for 5 seconds before raising an exception.

        :param mili_seconds: Miliseconds between retrys
        :param retrys: Number of retrys
        :return: The db lock record.
        """
        return mettle.db.DBLock(mili_seconds, retrys)


    async def save_access_denied(self, aud: Audit):
        """
        Saves an access denied record.

        :param aud: The audit object.
        """
        if aud.func and not isinstance(aud.func, str):
            aulvl = await self.read_config(aud.site_id, 'audit.granted.level', int)

            if aud.func.audit_lvl > aulvl:
                return

        ada = self.db_dao.dAda(self.pod.dbcon)

        await ada.insert_deft(aud.site_id,
                              aud.site_code,
                              aud.tm,
                              aud.usr_id,
                              aud.ea_usr_id(),
                              aud.role_id(),
                              aud.func_id(),
                              aud.func_action(),
                              aud.src,
                              aud.short_reason())


    async def save_access_granted(self, aud: Audit):
        """
        Saves an access granted record.

        :param aud: The Audit object.
        """
        if aud.func is not None and not isinstance(aud.func, str):
            aulvl = await self.read_config(aud.site_id, 'audit.granted.level', int)

            if aud.func.audit_lvl > aulvl:
                return

        aga = self.db_dao.dAga(self.pod.dbcon)

        await aga.insert_deft(aud.site_id,
                              aud.site_code,
                              aud.tm,
                              aud.usr_id,
                              aud.ea_usr_id(),
                              aud.role_id(),
                              aud.func_id(),
                              aud.func_action(),
                              aud.src)


    async def save_usr_login_audit(self, ula: tUla):
        """
        Saves a user login audit record.

        :param ual: (tUla) Record to save.
        """
        ula = self.db_dao.dUla(self.pod.dbcon)

        await ula.insert(ula)


    async def read_config(self, site_id: int, key: str, key_type: type, fallback: bool = True) -> object:
        """
        Reads a site config value.

        :param site_id: Site id.
        :param key: The config key.
        :param key_type: The type the key must be.
        :param fallback: If true, will check the normal config table if the site cfg value is not found.
        :return: The value read.
        """
        cfg = await self.cfg.load(self, site_id, key, must_exist = False)

        if not cfg.get(key) and fallback and site_id != 0:
            cfg = await self.cfg.load(self, 0, key, must_exist = False)
            return common.read_dict(cfg, key, key_type)  # duplicate return I want exceptions raised from this here

        return common.read_dict(cfg, key, key_type)


    async def usrauth_get(self, site_id: int, usr_id: str, auth_type: str) -> tUsrAuth:
        """
        Gets a user auth record.  Note the record is locked!

        :param site_id: Site id.
        :param usr_id: The user id.
        :param auth_type: The auth type.
        :return: The record found, or None if not found.
        """
        ua = self.db_dao.dUsrAuth(self.pod.dbcon)

        if not await ua.lock_one_deft(site_id, usr_id, auth_type, self.std_db_lock(), False):
            return None

        return ua.rec


    async def usrauth_new(self, site_id: int, usr_id: str, auth_type: str) -> tUsrAuth:
        """
        Creates a new user auth record.

        :param site_id: Site id.
        :param usr_id: The user id.
        :param auth_type: The auth type.
        :return: The record created.
        """
        ua = self.db_dao.dUsrAuth(self.pod.dbcon)

        await ua.insert_deft(site_id,
                             usr_id,
                             auth_type,
                             '',
                             0,
                             '',
                             '',
                             '',
                             None,
                             None,
                             usr_id)

        return ua.rec


    async def usrauth_save(self, rec: tUsrAuth):
        """
        Saves a user auth record.

        :param rec: The auth rec to save.
        """
        ua = self.db_dao.dUsrAuth(self.pod.dbcon)

        await ua.update(rec)


    async def usrauth_by_token(self, site_code: str, auth_type: str, token: str) -> tUsrAuth:
        """
        Gets a user auth record by site, auth type and token.

        :param site_code: The site code.
        :param auth_type: The authtype to get for.
        :param token: The authdata effectively to match on.
        :return: The record.
        """
        qry = self.db_dao.dUsrAuthByToken(self.pod.dbcon)

        if not await(await qry.exec_deft(site_code, auth_type, token)).fetch():
            return None

        return qry.orec


    async def ula_save(self, rec: tUla):
        """
        Saves a new ula record.

        :param rec: The user login access record.
        """
        ul = self.db_dao.dUla(self.pod.dbcon)

        await ul.insert(rec)


    async def usrotp_get(self, site_id: int, usr_id: str) -> tUsrOtp:
        """
        Gets a user otp record.  Note the record is locked!

        :param site_id: (int) Site id.
        :param usr_id: (string) The user id.
        :return: The record found, or None if not found.
        """
        uo = self.db_dao.dUsrOtp(self.pod.dbcon)

        if not await uo.lock_one_deft(site_id, usr_id, self.std_db_lock(), False):
            return None

        return uo.rec


    async def usrotp_new(self, site_id: int, usr_id: str) -> tUsrOtp:
        """
        Creates a new user otp record.

        :param site_id: (int) Site id.
        :param usr_id: (string) The user id.
        :return: The created otp record.
        """
        uo = self.db_dao.dUsrOtp(self.pod.dbcon)

        await uo.insert_deft(site_id,
                             usr_id,
                             tUsrOtp.OtpMethod_Couplet.key_none,
                             '',
                             datetime.datetime.min,
                             False,
                             '',
                             0,
                             None)

        return uo.rec


    async def usrotp_save(self, rec: tUsrOtp):
        """
        Saves a user auth record.

        :param rec: The otp rec to save.
        """
        uo = self.db_dao.dUsrOtp(self.pod.dbcon)

        await uo.update(rec)


    async def send_loco(self, loco_cfg_id: str, urec: tUsr, add_tags: dict = None, meta_data: dict = None):
        """
        Sends a loco trigger event.

        :param loco_cfg_id: The loco config notification id type to send.
        :param urec: The user rec in question.
        :param add_tags: Optionalyl add additional tags.
        :param meta_data: Optional meta tags to add to the otp.
        """
        loco_type = await self.read_config(urec.site_id, loco_cfg_id, str)

        if loco_type == 'DEADBEEF':
            self.pod.log.warning('Loco trigger is DEADBEEF, [lococFG:%s, site_id:%d, usr_id:%s]' % (
                loco_cfg_id, urec.site_id, urec.id))
            return

        addr = util.get_usr_loco_address(urec)

        if not addr:
            self.pod.log.warning('Could not send loco trigger, user has no address info [loco:%s, site_id:%d, usr_id:%s]' % (
                loco_type, urec.site_id, urec.id))
            return

        if meta_data is None:
            meta_data = {}

        utags = await self.std_loco_tags(urec)

        meta_data['site'] = utags['site_code']
        meta_data['usr']  = urec.id

        if add_tags:
            utags.update(add_tags)

        if not self.loco_trig:
            await self.initialize()

        await self.loco_trig.trig(loco_type, addr, utags, meta_data = meta_data)


    async def std_loco_tags(self, urec: tUsr) -> dict:
        """
        Gets the stand user loco tags.

        :param urec: The user rec.
        :return: The standard tags.
        """
        st         = await self.site_get(urec.site_id)
        supp_email = await self.read_config(urec.site_id, 'authreset.support-email', str)

        return util.std_loco_tags(urec, st, supp_email)


    async def otp_send(self,
                       otp_method  : str,
                       target      : str,
                       loco_cfg_id : str,
                       site_id     : int,
                       usr_id      : str,
                       meta_data   : dict = None):
        """
        Send an OTP to a user.

        :param otp_method: The otp method
        :param loco_cfg_id: The loco notification template message to send.
        :param target: The system target of the otp.
        :param site_id: Site id.
        :param usr_id: The user id.
        :param meta_data: Optional meta data to add to the otp message.
        """
        urec = await self.usr_get(self, site_id, usr_id)

        if not urec:
            raise Exception('User not found. [site_id:%d, usr_id:%s]' % (site_id, usr_id))

        with await OtpAsync(self, site_id, usr_id) as otp:
            otp_str  = await otp.new_otp(otp_method, target, meta_data)
            otp_tags = {'otp': otp_str}

            await self.send_loco(loco_cfg_id, urec, otp_tags)


    async def otp_ok(self, otp_str: str, target: str, site_id: int, usr_id: str, out_meta_data: dict = None) -> int:
        """
        Helper wrapper to make it easier to check if otps are ok.

        :param otp_str: The otp to check.
        :param target: The target to check.
        :param site_id: Site id.
        :param usr_id: The user id.
        :param out_meta_data: If this is not none, any output metadata will be populated into this dictionary.
        :return: The ErrCode result.
        """
        with await OtpAsync(self, site_id, usr_id) as otp:
            return await otp.ok(otp_str, 'Z', target, out_meta_data)
