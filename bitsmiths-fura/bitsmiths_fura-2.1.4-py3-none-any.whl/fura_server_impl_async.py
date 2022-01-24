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
import mettle
import json

from mettle.lib import xMettle

from bs_fura.braze import FuraAsyncServerInterface

from .                   import fura_davcache
from .dao_async          import DaoAsync
from .err_code           import ErrCode
from .user_login_async   import UserLoginAsync
from .fura_token         import FuraToken
from .xfura              import xFura

from .auth         import factory as AuthFactory

from .db.tables   import tConfig
from .db.tables   import tFunc
from .db.tables   import tFuncGrp
from .db.tables   import tRole
from .db.tables   import tSite
from .db.tables   import tSiteCfg
from .db.tables   import tUsr
from .db.tables   import tUsrAuth
from .db.tables   import tUsrType

from bs_loco.trigger.loco_trig_async  import LocoTrigAsync

import bs_fura

from bs_fura.braze  import bAuthPolicy
from bs_fura.braze  import bRoleFuncRel
from bs_fura.braze  import ResetMethod_Couplet
from bs_fura.braze  import bUserLogin

from bs_lib.auto_transaction_async import AutoTransactionAsync
from bs_lib                        import Pod
from bs_lib                        import query_builder

from bs_audit.audit_async  import AuditAsync


class FuraServerImplAsync(FuraAsyncServerInterface):

    MODULE = '[FuraServerImpl]'

    def __init__(self, pod: Pod, dao_name: str, loco_trig: LocoTrigAsync = None):
        """
        Constructor.

        :param pod: The pod to use.
        :param dao_name: Database dao name to use.
        """
        self._shutdown = False
        self._pod      = pod
        self._log      = pod.log
        self._dao_name = dao_name
        self._dao      = DaoAsync(self._pod, bs_fura.dao_by_name(dao_name, 'dao_async'), loco_trig)
        self._audit    = None

        self._fura_token = None
        self._tok_data   = None
        self._new_token  = None


    def _shutdown_server(self):
        return self._shutdown


    def _slacktime_handler(self):
        pass


    def _construct(self):
        self._destruct()


    def _destruct(self):
        self._fura_token = None
        self._tok_data   = None
        self._new_token  = None


    async def _init_web_token(self) -> FuraToken:
        """
        Virtual method to initialize the standard web token to use for the
        fura server to use.

        :returns: the created web token.
        """
        async with AutoTransactionAsync(self._pod):
            fura_cfg = await self._dao.cfg.load(self._dao, 0, 'token.webkey')
            return FuraToken(json.loads(fura_cfg['token.webkey']))


    def _init_dav_cache(self, rpc_name, dvc):
        fura_davcache.init_davcache(dvc)


    def _has_new_rpc_token(self):
        return self._new_token


    def _set_rpc_token_data(self, tdata):
        self._new_token   = None
        self._tok_data    = tdata
        self._pod.usr_id  = ''

        if self._tok_data:
            self._pod.usr_id = self._usr_id()


    def _site_id(self):
        if not self._tok_data:
            raise Exception('Auth user required for RPC call, but no user is logged in!')

        site_id = self._tok_data.get('site')

        if not site_id or type(site_id) != int:
            raise Exception('Auth site is not set!')

        return site_id


    def _usr_id(self):
        if self._pod.usr_id:
            return self._pod.usr_id

        if not self._tok_data:
            raise Exception('Auth user required for RPC call, but no user is logged in!')

        usr_id = self._tok_data.get('usr')

        if not usr_id:
            raise Exception('Auth user is not set!')

        return usr_id


    async def _role(self):
        if not self._tok_data:
            raise Exception('Auth user required for RPC call, but no user is logged in!')

        role = self._tok_data.get('role')

        if not role:
            raise Exception('Auth role is not set!')

        return await self._dao.role_get(self._site_id(), role)


    async def get_fura_token(self):
        if not self._fura_token:
            self._fura_token = await self._init_web_token()

        return self._fura_token


    def get_dao(self):
        return self._dao


    def get_audit(self):
        if not self._audit:
            self._audit = AuditAsync(self._pod.dbcon, self._dao_name)

        return self._audit


    # ------------------------------------------------------------------------
    # SERVER INTERFACE METHODS
    # ------------------------------------------------------------------------


    async def auth_policy_read(self,
                               auth_type: str,
                               site_code: str) -> bAuthPolicy:
        async with AutoTransactionAsync(self._pod):
            site_id = 0

            if site_code:
                srec = await self._dao.site_get(site_code)

                if not srec:
                    raise Exception('Site not found [%s]' % (site_code))

                site_id = srec.id

            async with await AuthFactory.get_auth_object_async(auth_type) as auth:
                auth.initialize(self._dao, site_id, None)
                pol = await auth.get_auth_policy()

                return bAuthPolicy(auth_type, pol['descr'], pol['regex'])


    async def config_create(self, rec: tConfig) -> tConfig:
        async with AutoTransactionAsync(self.get_audit(), self._pod) as at:
            dc              = self._dao.db_dao.dConfig(self._pod.dbcon)
            rec.modified_by = self._usr_id()

            await dc.insert(rec)
            self._audit.aud(1, self.MODULE, rec.modified_by).diff(None, rec, 'fura.config')
            await at.commit()

            return rec


    async def config_read(self, cfg_id: str) -> tConfig.List :
        async with AutoTransactionAsync(self._pod):
            qry = self._dao.db_dao.dConfigSearch(self._pod.dbcon)
            res = tConfig.List()

            if cfg_id:
                qry.irec.criteria += query_builder.dyn_crit(cfg_id, 'c', 'id')

            await (await qry.exec()).fetch_all(res)

            return res


    async def config_update(self, rec: tConfig) -> tConfig:
        async with AutoTransactionAsync(self.get_audit(), self._pod) as at:
            dc              = self._dao.db_dao.dConfig(self._pod.dbcon)
            rec.modified_by = self._usr_id()

            await dc.lock_one_deft(rec.id, self._pod.std_db_lock())

            if dc.rec.tm_stamp.replace(microsecond=0) != rec.tm_stamp.replace(microsecond=0):
                raise xMettle('Stale data. Refresh and try again.', self.MODULE)

            bef = copy.copy(dc.rec)

            await dc.update(rec)
            self._audit.aud(1, self.MODULE, rec.modified_by).diff(bef, rec, 'fura.config')
            await at.commit()

            return rec


    async def config_delete(self, cfg_id: str):
        async with AutoTransactionAsync(self.get_audit(), self._pod) as at:
            dc = self._dao.db_dao.dConfig(self._pod.dbcon)
            await dc.select_one_deft(cfg_id)
            await dc.delete_one_deft(cfg_id)
            self._audit.aud(1, self.MODULE, self._usr_id()).diff(dc.rec, None, 'fura.config')
            await at.commit()


    async def func_read(self,
                        func_id: str,
                        func_grp_id: str) -> tFunc.List :
        async with AutoTransactionAsync(self._pod):
            qry = self._dao.db_dao.dFuncSearch(self._pod.dbcon)
            res = tFunc.List()

            qry.irec.site_id = self._site_id()

            if func_id:
                qry.irec.criteria += query_builder.dyn_crit(func_id,    'f', 'id')

            if func_grp_id:
                qry.irec.criteria += query_builder.dyn_crit(func_grp_id, 'f', 'funcgrp_id')

            await (await qry.exec()).fetch_all(res)

            return res


    async def func_grp_read(self, func_grp_id: str) -> tFuncGrp.List :
        async with AutoTransactionAsync(self._pod):
            qry = self._dao.db_dao.dFuncGrpSearch(self._pod.dbcon)
            res = tFuncGrp.List()

            qry.irec.site_id = self._site_id()

            if func_grp_id:
                qry.irec.criteria += query_builder.dyn_crit(func_grp_id, 'f', 'id')

            await (await qry.exec()).fetch_all(res)

            return res


    async def role_create(self, rec: tRole) -> tRole:
        async with AutoTransactionAsync(self.get_audit(), self._pod) as at:
            rl              = self._dao.db_dao.dRole(self._pod.dbcon)
            rec.site_id     = self._site_id()
            rec.modified_by = self._usr_id()

            await rl.insert(rec)
            self._audit.aud(rec.site_id, self.MODULE, rec.modified_by).diff(None, rec, 'fura.role')
            await at.commit()

            return rec


    async def role_read(self, role_id: str) -> tRole.List:
        async with AutoTransactionAsync(self._pod):
            qry = self._dao.db_dao.dRoleSearch(self._pod.dbcon)
            res = tRole.List()

            qry.irec.site_id   = self._site_id()

            if role_id:
                qry.irec.criteria += query_builder.dyn_crit(role_id, 'r', 'id')

            await (await qry.exec()).fetch_all(res)

            return res


    async def role_update(self, rec: tRole) -> tRole:
        if self._site_id() == 1 and rec.id == 'admin':
            raise xMettle('Altering the Fura.admin role is forbidden.', self.MODULE)

        async with AutoTransactionAsync(self.get_audit(), self._pod) as at:
            rl = self._dao.db_dao.dRole(self._pod.dbcon)

            await rl.lock_one_deft(self._site_id(), rec.id, self._pod.std_db_lock())

            if rl.rec.tm_stamp.replace(microsecond=0) != rec.tm_stamp.replace(microsecond=0):
                raise xMettle('Stale data. Refresh and try again.', self.MODULE)

            bef              = copy.copy(rl.rec)
            rec.site_id      = self._site_id()
            rec.modified_by  = self._usr_id()

            if rl.rec.status == tRole.Status_Couplet.key_super_user:
                rfr_list = []
                gqry = self._dao.db_dao.dRoleFuncRelByRole(self._pod.dbcon)
                dqry = self._dao.db_dao.dRoleFuncRelDeleteByRole(self._pod.dbcon)

                await (await gqry.exec_deft(self._site_id(), rl.rec.id)).fetch_all(rfr_list)

                await dqry.exec_deft(self._site_id(), rec.id)

                if len(rfr_list) > 0:
                    self._audit.diff_bulk(rfr_list, None, 'fura.rolefuncrel')

            await rl.update(rec)
            self._audit.aud(rec.site_id, self.MODULE, rec.modified_by).diff(bef, rec, 'fura.role')
            await at.commit()

            return rec


    async def role_delete(self, role_id: str):
        if self._site_id() == 1 and role_id == 'admin':
            raise xMettle('Altering the Fura.admin role is forbidden.', self.MODULE)

        async with AutoTransactionAsync(self.get_audit(), self._pod) as at:
            rl = self._dao.db_dao.dRole(self._pod.dbcon)

            await rl.lock_one_deft(self._site_id(), role_id, self._pod.std_db_lock())

            rfr_list = []
            gqry = self._dao.db_dao.dRoleFuncRelByRole(self._pod.dbcon)
            dqry = self._dao.db_dao.dRoleFuncRelDeleteByRole(self._pod.dbcon)

            await (await gqry.exec_deft(self._site_id(), rl.rec.id)).fetch_all(rfr_list)
            await dqry.exec_deft(self._site_id(), rl.rec.id)

            if len(rfr_list) > 0:
                self._audit.diff_bulk(rfr_list, None, 'fura.rolefuncrel')

            await rl.delete_one_deft(self._site_id(), role_id)
            self._audit.aud(rl.rec.site_id, self.MODULE, self._usr_id()).diff(rl.rec, None, 'fura.role')
            await at.commit()


    async def role_func_add(self,
                            role_id: str,
                            rfs: mettle.braze.StringList):
        if self._site_id() == 1 and role_id == 'admin':
            raise xMettle('Altering the Fura.admin role is forbidden.', self.MODULE)

        async with AutoTransactionAsync(self.get_audit(), self._pod) as at:
            dr     = self._dao.db_dao.dRole(self._pod.dbcon)
            df     = self._dao.db_dao.dFunc(self._pod.dbcon)
            drfr   = self._dao.db_dao.dRoleFuncRel(self._pod.dbcon)
            siteid = self._site_id()
            usrid  = self._usr_id()

            await dr.lock_one_deft(self._site_id(), role_id, self._pod.std_db_lock())

            if dr.rec.status == tRole.Status_Couplet.key_super_user:
                raise xMettle('Functions may not be added to super user roles.')

            for rf in rfs:
                if len(rf) < 1:
                    continue

                await df.select_one_deft(rf)

                if siteid != 1 and df.rec.funcgrp_id == 'FURA-ADMIN':
                    raise xMettle('FURA-ADMIN functions can only be assigned to FURA users.')

                if await drfr.try_select_one_deft(siteid, role_id, rf):
                    continue

                await drfr.insert_deft(siteid, role_id, rf, usrid)
                self._audit.aud(siteid, self.MODULE, usrid).diff(None, drfr.rec, 'fura.rolefuncrel')

            await at.commit()


    async def role_func_rem(self,
                            role_id: str,
                            rfs: mettle.braze.StringList):
        if self._site_id() == 1 and role_id == 'admin':
            raise xMettle('Altering the Fura.admin role is forbidden.', self.MODULE)

        async with AutoTransactionAsync(self.get_audit(), self._pod) as at:
            dr     = self._dao.db_dao.dRole(self._pod.dbcon)
            drfr   = self._dao.db_dao.dRoleFuncRel(self._pod.dbcon)
            siteid = self._site_id()

            self._audit.aud(siteid, self.MODULE, self._usr_id())

            await dr.lock_one_deft(self._site_id(), role_id, self._pod.std_db_lock())

            if dr.rec.status == tRole.Status_Couplet.key_super_user:
                dqry = self._dao.db_dao.dRoleFuncRelDeleteByRole(self._pod.dbcon)
                await dqry.exec_deft(self._site_id(), role_id)
                await at.commit()
                return

            for rf in rfs:
                if len(rf) < 1:
                    continue

                if rf == '*':
                    rfr_list = []
                    gqry = self._dao.db_dao.dRoleFuncRelByRole(self._pod.dbcon)
                    dqry = self._dao.db_dao.dRoleFuncRelDeleteByRole(self._pod.dbcon)

                    await (await gqry.exec_deft(self._site_id(), role_id)).fetch_all(rfr_list)
                    await dqry.exec_deft(self._site_id(), role_id)

                    if len(rfr_list) > 0:
                        self._audit.diff_bulk(rfr_list, None, 'fura.rolefuncrel')

                    break

                if await drfr.try_select_one_deft(siteid, role_id, rf):
                    await drfr.delete_one_deft(siteid, role_id, rf)
                    self._audit.diff(drfr.rec, None, 'fura.rolefuncrel')

            await at.commit()


    async def role_func_read(self,
                             role_id: str,
                             func_grp_id: str) -> bRoleFuncRel.List:
        async with AutoTransactionAsync(self._pod):
            qry = self._dao.db_dao.dRoleFuncRelSearch(self._pod.dbcon)
            res = bRoleFuncRel.List()

            qry.irec.site_id   = self._site_id()
            qry.irec.role_id   = role_id

            if func_grp_id:
                qry.irec.criteria += query_builder.dyn_crit(func_grp_id, 'fg', 'id')

            await qry.exec()

            while await qry.fetch():
                qi = bRoleFuncRel(
                    qry.orec.func_id,
                    qry.orec.func_descr,
                    qry.orec.func_action,
                    qry.orec.funcgrp_id,
                    qry.orec.func_grp_descr,
                    True)

                res.append(qi)

            return res


    async def site_cfg_create(self, rec: tSiteCfg) -> tSiteCfg:
        async with AutoTransactionAsync(self.get_audit(), self._pod) as at:
            dsc             = self._dao.db_dao.dSiteCfg(self._pod.dbcon)
            rec.site_id     = self._site_id()
            rec.modified_by = self._usr_id()

            await dsc.insert(rec)
            self._audit.aud(rec.site_id, self.MODULE, rec.modified_by).diff(None, dsc.rec, 'fura.sitecfg')
            await at.commit()

            return rec


    async def site_cfg_read(self, site_cfg_id: str) -> tSiteCfg.List:
        async with AutoTransactionAsync(self._pod):
            qry = self._dao.db_dao.dSiteCfgSearch(self._pod.dbcon)
            res = tSiteCfg.List()

            qry.irec.site_id    = self._site_id()

            if site_cfg_id:
                qry.irec.criteria += query_builder.dyn_crit(site_cfg_id, 'c', 'id')

            await (await qry.exec()).fetch_all(res)

            return res


    async def site_cfg_update(self, rec: tSiteCfg) -> tSiteCfg:
        async with AutoTransactionAsync(self.get_audit(), self._pod) as at:
            dsc = self._dao.db_dao.dSiteCfg(self._pod.dbcon)

            await dsc.lock_one_deft(self._site_id(), rec.id, self._pod.std_db_lock())

            if dsc.rec.tm_stamp.replace(microsecond=0) != rec.tm_stamp.replace(microsecond=0):
                raise xMettle('Stale data. Refresh and try again.', self.MODULE)

            bef             = copy.copy(dsc.rec)
            rec.site_id     = self._site_id()
            rec.modified_by = self._usr_id()

            await dsc.update(rec)
            self._audit.aud(rec.site_id, self.MODULE, rec.modified_by).diff(bef, rec, 'fura.sitecfg')
            await at.commit()

            return rec


    async def site_cfg_delete(self, site_cfg_id: str):
        async with AutoTransactionAsync(self.get_audit(), self._pod) as at:
            dsc = self._dao.db_dao.dSiteCfg(self._pod.dbcon)
            await dsc.select_one_deft(self._site_id(), site_cfg_id)
            await dsc.delete_one_deft(self._site_id(), site_cfg_id)
            self._audit.aud(self._site_id(), self.MODULE, self._usr_id()).diff(dsc.rec, None, 'fura.sitecfg')
            await at.commit()


    async def site_create(self,
                          site_rec: tSite,
                          admin_email: str,
                          admin_passwd: str) -> int:
        self._log.debug('site_create[%s] - start[site:%s, email:%s, passwd:***' % (
            self._usr_id(), str(site_rec), admin_email))

        async with AutoTransactionAsync(self.get_audit(), self._pod) as at:
            ds    = self._dao.db_dao.dSite(self._pod.dbcon)
            dsqry = self._dao.db_dao.dSiteByCode(self._pod.dbcon)

            if await (await dsqry.exec_deft(site_rec.code)).fetch():
                raise xMettle("A site with a site code [%s] already exists!" % (
                    site_rec.code), self.MODULE)

            site_rec.modified_by = self._usr_id()

            await ds.insert(site_rec)
            self._audit.aud(1, self.MODULE, site_rec.modified_by).diff(None, site_rec, 'fura.site')

            rl = self._dao.db_dao.dRole(self._pod.dbcon)

            await rl.insert_deft(site_rec.id,
                                 'admin',
                                 'Administrator',
                                 tRole.Status_Couplet.key_super_user,
                                 5,
                                 10,
                                 self._usr_id())

            self._audit.diff(None, rl.rec, 'fura.role')

            usr = self._dao.db_dao.dUsr(self._pod.dbcon)

            usr.rec.site_id       = site_rec.id
            usr.rec.id            = 'admin'
            usr.rec.role_id       = 'admin'
            usr.rec.status        = tUsr.Status_Couplet.key_active
            usr.rec.date_activate = datetime.date.today()
            usr.rec.email1        = 'admin_email'
            usr.rec.modified_by   = self._usr_id()
            usr.rec.usrtype_id    = 'sys'

            await usr.insert()

            self._audit.diff(None, usr.rec, 'fura.usr')

            async with UserLoginAsync(self._dao, site_rec.code) as ul:
                await ul.set_auth_data(self._audit,
                                       'admin',
                                       tUsrAuth.AuthType_Couplet.key_password,
                                       admin_passwd,
                                       None,
                                       None)

            dc = self._dao.db_dao.dSiteCfg(self._pod.dbcon)

            await dc.insert_deft(ds.rec.id, 'audit.denied.level',  'Audit Denied Level',              '100', self._usr_id())
            self._audit.diff(None, copy.copy(dc.rec), 'fura.sitecfg')
            await dc.insert_deft(ds.rec.id, 'audit.denied.age',    'Audit Denied Max Age (days)',     '90',  self._usr_id())
            self._audit.diff(None, copy.copy(dc.rec), 'fura.sitecfg')
            await dc.insert_deft(ds.rec.id, 'audit.granted.level', 'Audit Granted Level',             '100', self._usr_id())
            self._audit.diff(None, copy.copy(dc.rec), 'fura.sitecfg')
            await dc.insert_deft(ds.rec.id, 'audit.granted.age',   'Audit Granted Max Age (days)',    '90',  self._usr_id())
            self._audit.diff(None, copy.copy(dc.rec), 'fura.sitecfg')
            await dc.insert_deft(ds.rec.id, 'audit.usrlogin.age',  'Audit User Login Max Age (days)', '90',  self._usr_id())
            self._audit.diff(None, copy.copy(dc.rec), 'fura.sitecfg')

            await at.commit()

        self._log.debug('site_create[%s] - done[site_id:%d]' % (self._usr_id(), site_rec.id))

        return site_rec.id


    async def site_read(self, site_code: str) -> tSite.List:
        async with AutoTransactionAsync(self._pod):
            res = tSite.List()

            if site_code:
                qry = self._dao.db_dao.dSiteByCode(self._pod.dbcon)
                await (await qry.exec_deft(site_code)).fetch_all(res)
            else:
                qry = self._dao.db_dao.dSiteSelectAll(self._pod.dbcon)
                await (await qry.exec()).fetch_all(res)

            return res


    async def site_update(self, rec: tSite) -> tSite:
        async with AutoTransactionAsync(self.get_audit(), self._pod) as at:
            ds = self._dao.db_dao.dSite(self._pod.dbcon)

            await ds.lock_one_deft(rec.id, self._pod.std_db_lock())

            if ds.rec.tm_stamp.replace(microsecond=0) != rec.tm_stamp.replace(microsecond=0):
                raise xMettle("Stale data. Please refresh and try again.", self.MODULE)

            bef             = copy.copy(ds.rec)
            rec.modified_by = self._usr_id()
            await ds.update(rec)
            self._audit.aud(self._site_id(), self.MODULE, rec.modified_by).diff(bef, rec, 'fura.site')
            await at.commit()

            return rec


    async def site_delete(self, site_id: int):
        async with AutoTransactionAsync(self.get_audit(), self._pod) as at:
            ds = self._dao.db_dao.dSite(self._pod.dbcon)

            await ds.lock_one_deft(site_id, self._pod.std_db_lock())

            del1 = self._dao.db_dao.dEatokDeleteBySite(self._pod.dbcon)
            del2 = self._dao.db_dao.dUsrAuthDeleteBySite(self._pod.dbcon)
            del3 = self._dao.db_dao.dUsrDeleteBySite(self._pod.dbcon)
            del4 = self._dao.db_dao.dRoleFuncRelDeleteBySite(self._pod.dbcon)
            del5 = self._dao.db_dao.dRoleDeleteBySite(self._pod.dbcon)
            del6 = self._dao.db_dao.dSiteCfgDeleteBySite(self._pod.dbcon)

            await del1.exec_deft(site_id)
            await del2.exec_deft(site_id)
            await del3.exec_deft(site_id)
            await del4.exec_deft(site_id)
            await del5.exec_deft(site_id)
            await del6.exec_deft(site_id)

            await ds.deleteOne()
            self._audit.aud(self._site_id(), self.MODULE, self._usr_id()).diff(ds.rec, None, 'fura.site')
            await at.commit()


    async def user_create(self, rec: tUsr) -> tUsr:
        async with AutoTransactionAsync(self.get_audit(), self._pod) as at:
            rec.site_id = self._site_id()

            await self._dao.usr_create(self._audit, rec)

            await at.commit()

            return rec


    async def user_read(self,
                        usr_id: str,
                        usr_type: str) -> tUsr.List:
        async with AutoTransactionAsync(self._pod):
            qry = self._dao.db_dao.dUsrSearch(self._pod.dbcon)
            res = tUsr.List()

            qry.irec.site_id    = self._site_id()

            if usr_id:
                qry.irec.criteria += query_builder.dyn_crit(usr_id,   'u', 'id')

            if usr_type:
                qry.irec.criteria += query_builder.dyn_crit(usr_type, 'u', 'usrtype_id')

            await (await qry.exec()).fetch_all(res)

            return res


    async def user_update(self, rec: tUsr) -> tUsr:
        if self._site_id() == 1 and rec.id == 'admin':
            raise xMettle('Altering the Fura.admin account is forbidden.', self.MODULE)

        async with AutoTransactionAsync(self.get_audit(), self._pod) as at:
            rec.site_id = self._site_id()
            await self._dao.usr_update(self._audit, rec)
            await at.commit()

            return rec


    async def user_delete(self, usr_id: str):
        if self._site_id() == 1 and usr_id == 'admin':
            raise xMettle('Altering the Fura.admin account is forbidden.', self.MODULE)

        async with AutoTransactionAsync(self.get_audit(), self._pod) as at:
            du = self._dao.db_dao.dUsr(self._pod.dbcon)
            await du.select_one_deft(self._site_id(), usr_id)
            await du.delete_one_deft(self._site_id(), usr_id)
            self._audit.aud(self._site_id(), self.MODULE, self._usr_id()).diff(du.rec, None, 'fura.usr')
            await at.commit()


    async def user_rec(self) -> tUsr:
        async with AutoTransactionAsync(self._pod):
            return await self._dao.usr_get(self._site_id(), self._usr_id())


    async def user_funcs(self, func_prefix: str) -> mettle.braze.StringList:
        async with AutoTransactionAsync(self._pod):
            res = mettle.braze.StringList()
            qry = self._dao.db_dao.dFuncRoleFuncSearch(self._pod.dbcon)
            fp  = func_prefix.replace('*', '%').replace(' ', '%')
            fp += '%'

            await qry.exec_deft(self._site_id(), self._role().id, fp)

            while await qry.fetch():
                res.append(str(qry.orec.func_id))

            return res


    async def user_login(self, ul_rec: bUserLogin) -> int:
        async with AutoTransactionAsync(self._pod) as at:
            self._pod.usr_id = ul_rec.user_id

            try:
                async with UserLoginAsync(self._dao, ul_rec.site_code) as ul:
                    await ul.login(ul_rec.user_id, ul_rec.auth_type, ul_rec.auth_data, ul_rec.ip_addr, ul_rec.geo_loc)

                    self._new_token = ul.gen_fura_token(await self.get_fura_token())

            except xFura as xf:
                self._log.debug('userLogin Failed [%s]' % str(xf))

                if xf.get_error_code() in (ErrCode.AuthMaxFailures.value, ErrCode.AuthInvalid.value):
                    return xf.get_error_code()

                return ErrCode.AuthInvalid.value

            finally:
                await at.commit()

        return ErrCode.NoError.value


    async def user_logout(self) -> int:
        async with AutoTransactionAsync(self._pod) as at:
            try:
                async with UserLoginAsync(self._dao, None, self._site_id()) as ul:
                    await ul.logout(self._site_id(), self._usr_id())

                    if self._tok_data.get('role') is not None:
                        del self._tok_data['role']

                    self._new_token = (await self.get_fura_token()).invalidate_token(self._tok_data)

            except xFura as xf:
                self._log.debug('userLogout Failed [%s]' % str(xf))
                return xf.get_error_code()
            finally:
                await at.commit()

        return ErrCode.NoError.value


    async def user_role(self) -> tRole:
        return await self._role()


    async def user_is_super_user(self) -> bool:
        return (await self._role()).status == tRole.Status_Couplet.key_super_user


    async def user_auth_change(self,
                               auth_type: str,
                               new_data: str,
                               old_data: str):
        self._log.info('user_auth_change - start[site:%d, usr:%s, auth_type:%s]' % (
            self._site_id(), self._usr_id(), auth_type))

        async with AutoTransactionAsync(self._pod) as at:
            try:
                async with UserLoginAsync(self._dao, None, self._site_id()) as ul:
                    await ul.change_auth(self._usr_id(), auth_type, new_data, old_data)
            finally:
                await at.commit()

        self._log.info('user_auth_change - done[site:%d, usr:%s, auth_type:%s]' % (
            self._site_id(), self._usr_id(), auth_type))


    async def user_auth_reset(self,
                              site_code: str,
                              usr_id: str,
                              auth_type: str,
                              reset_method: str):
        self._log.warning('user_auth_reset - start[site:%s, usr:%s, auth_type:%s, reset_method:%s]' % (
            site_code, usr_id, auth_type, reset_method))

        self._pod.usr_id = usr_id

        async with AutoTransactionAsync(self._pod) as at:
            async with UserLoginAsync(self._dao, site_code) as ul:
                if await ul.req_auth_reset(usr_id, usr_id, auth_type, reset_method, None, True):
                    await at.commit()

        self._log.warning('user_auth_reset - done[site:%s, usr:%s, auth_type:%s, reset_method:%s]' % (
            site_code, usr_id, auth_type, reset_method))


    async def user_token_reset(self, auth_type: str):
        self._log.info('user_token_reset - start[site:%d, usr_id:%s, auth_type:%s]' % (
            self._site_id(), self._usr_id(), auth_type))

        async with AutoTransactionAsync(self._pod) as at:
            async with UserLoginAsync(self._dao, None, self._site_id()) as ul:
                await ul.req_token_reset(self._usr_id(), self._usr_id(), auth_type)

            await at.commit()

        self._log.info('user_token_reset - done[site:%d, usr_id:%s, auth_type:%s]' % (
            self._site_id(), self._usr_id(), auth_type))


    async def user_auth_reset_admin(self,
                                    usr_id: str,
                                    auth_type: str,
                                    email_addr: str):
        self._log.warning('user_auth_reset_admin - start[site:%d, loggedInUsr:%s, usr:%s, auth_type:%s, email:%s]' % (
            self._site_id(), self._usr_id(), usr_id, auth_type, email_addr))

        async with AutoTransactionAsync(self._pod) as at:
            async with UserLoginAsync(self._dao, None, self._site_id()) as ul:
                await ul.req_auth_reset(self._usr_id(),
                                        usr_id,
                                        auth_type,
                                        ResetMethod_Couplet.key_email,
                                        email_addr,
                                        False)

            await at.commit()

        self._log.warning('user_auth_reset_admin - done[site:%d, loggedInUsr:%s, usr:%s, auth_type:%s, email:%s]' % (
            self._site_id(), self._usr_id(), usr_id, auth_type, email_addr))


    async def user_token_reset_admin(self,
                                     usr_id: str,
                                     auth_type: str):
        self._log.info('user_token_reset_admin - start[site:%d, usr_id:%s, targ_usr_id:%s, auth_type:%s]' % (
            self._site_id(), self._usr_id(), usr_id, auth_type))

        async with AutoTransactionAsync(self._pod) as at:
            async with UserLoginAsync(self._dao, None, self._site_id()) as ul:
                await ul.req_token_teset(self._usr_id(), usr_id, auth_type)

            await at.commit()

        self._log.info('user_token_reset_admin - done[site:%d, usr_id:%s, targ_usr_id:%s, auth_type:%s]' % (
            self._site_id(), self._usr_id(), usr_id, auth_type))


    async def user_token_read(self,
                              auth_type: str) -> str:
        self._log.info('user_token_read - start[site:%d, usr_id:%s, auth_type:%s]' % (
            self._site_id(), self._usr_id(), auth_type))

        res = ''

        async with AutoTransactionAsync(self._pod):
            async with UserLoginAsync(self._dao, None, self._site_id()) as ul:
                res = await ul.read_token(self._usr_id(), auth_type)

        self._log.info('user_token_read - done[site:%d, usr_id:%s, auth_type:%s]' % (
            self._site_id(), self._usr_id(), auth_type))

        return res


    async def user_set_new_auth(self,
                                ul_rec: bUserLogin,
                                tok: str,
                                reset_method: str):
        async with AutoTransactionAsync(self.get_audit(), self._pod) as at:
            try:
                async with UserLoginAsync(self._dao, ul_rec.site_code, self._audit) as ul:
                    await ul.set_auth_data(self._audit,
                                           ul_rec.user_id,
                                           ul_rec.auth_type,
                                           ul_rec.auth_data,
                                           tok,
                                           reset_method,
                                           ul_rec.ip_addr,
                                           ul_rec.geo_loc)
            finally:
                await at.commit()


    async def user_activate(self, usr_id: str):
        if self._site_id() == 1 and usr_id == 'admin':
            raise xMettle('Altering the Fura.admin account is forbidden.', self.MODULE)

        async with AutoTransactionAsync(self._pod) as at:
            du = self._dao.db_dao.dUsr(self._pod.dbcon)

            await du.lock_one_deft(self._site_id(), usr_id, self._pod.std_db_lock())

            if du.rec.status == tUsr.Status_Couplet.key_active:
                return

            du.rec.status      = tUsr.Status_Couplet.key_active
            du.rec.modified_by = self._usr_id()

            await du.update()
            await at.commit()


    async def user_disable(self, usr_id: str):
        if self._site_id() == 1 and usr_id == 'admin':
            raise xMettle('Altering the Fura.admin account is forbidden.', self.MODULE)

        async with AutoTransactionAsync(self._pod) as at:
            du = self._dao.db_dao.dUsr(self._pod.dbcon)

            await du.lock_one_deft(self._site_id(), usr_id, self._pod.std_db_lock())

            if du.rec.status == tUsr.Status_Couplet.key_disabled:
                return

            du.rec.status      = tUsr.Status_Couplet.key_disabled
            du.rec.modified_by = self._usr_id()

            await du.update()
            await at.commit()


    async def user_suspend(self, usr_id: str):
        if self._site_id() == 1 and usr_id == 'admin':
            raise xMettle('Altering the Fura.admin account is forbidden.', self.MODULE)

        async with AutoTransactionAsync(self._pod) as at:
            du = self._dao.db_dao.dUsr(self._pod.dbcon)

            await du.lock_one_deft(self._site_id(), usr_id, self._pod.std_db_lock())

            if du.rec.status == tUsr.Status_Couplet.key_suspended:
                return

            du.rec.status      = tUsr.Status_Couplet.key_suspended
            du.rec.modified_by = self._usr_id()

            await du.update()
            await at.commit()


    async def user_set_role(self, usr_id: str, role_id: str) -> tUsr:
        if self._site_id() == 1 and usr_id == 'admin':
            raise xMettle('Altering the Fura.admin account is forbidden.', self.MODULE)

        async with AutoTransactionAsync(self.get_audit(), self._pod) as at:
            du = self._dao.db_dao.dUsr(self._pod.dbcon)

            await du.lock_one_deft(self._site_id(), usr_id, self._pod.std_db_lock())

            bef                = copy.copy(du.rec)
            du.rec.role_id     = role_id
            du.rec.site_id     = self._site_id()
            du.rec.modified_by = self._usr_id()

            await du.update(du.rec)
            self._audit.aud(self._site_id(), self.MODULE, du.rec.modified_by).diff(bef, du.rec, 'fura.usr')
            await at.commit()

            return du.rec


    async def user_confirm_contact(self, otp: str):
        async with AutoTransactionAsync(self.get_audit(), self._pod) as at:
            async with UserLoginAsync(self._dao, None, self._site_id()) as ul:
                try:
                    await ul.confirm_contact(self.get_audit(), self._usr_id(), otp)
                finally:
                    await at.commit()


    async def user_confirm_contact_req_otp(self, contact_addr: str):
        async with AutoTransactionAsync(self._pod) as at:
            async with UserLoginAsync(self._dao, None, self._site_id()) as ul:
                try:
                    await ul.confirm_contact_req(self._usr_id(), contact_addr)
                finally:
                    await at.commit()


    async def user_type_create(self, rec: tUsrType) -> tUsrType:
        async with AutoTransactionAsync(self.get_audit(), self._pod) as at:
            dut             = self._dao.db_dao.dUsrType(self._pod.dbcon)
            rec.modified_by = self._usr_id()

            await dut.insert(rec)
            self._audit.aud(1, self.MODULE, rec.modified_by).diff(None, rec, 'fura.usrtype')
            await at.commit()

            return rec


    async def user_type_read(self, usr_type_id: str) -> tUsrType.List:
        async with AutoTransactionAsync(self._pod):
            qry = self._dao.db_dao.dUsrTypeSearch(self._pod.dbcon)
            res = tUsrType.List()

            qry.irec.criteria += query_builder.dyn_crit(usr_type_id, 'u', 'id')
            await (await qry.exec()).fetch_all(res)

            return res


    async def user_type_update(self, rec: tUsrType) -> tUsrType:
        async with AutoTransactionAsync(self.get_audit(), self._pod) as at:
            dut             = self._dao.db_dao.dUsrType(self._pod.dbcon)
            rec.modified_by = self._usr_id()

            await dut.lock_one_deft(rec.id, self._pod.std_db_lock())

            if dut.rec.tm_stamp.replace(microsecond=0) != rec.tm_stamp.replace(microsecond=0):
                raise xMettle('Stale data. Refresh and try again.', self.MODULE)

            bef = copy.copy(dut.rec)

            await dut.update(rec)
            self._audit.aud(1, self.MODULE, rec.modified_by).diff(bef, rec, 'fura.usrtype')
            await at.commit()

            return rec


    async def user_type_delete(self, usr_type_id: str):
        async with AutoTransactionAsync(self.get_audit(), self._pod) as at:
            dut = self._dao.db_dao.dUsrType(self._pod.dbcon)
            await dut.select_one_deft(usr_type_id)
            await dut.delete_one_deft(usr_type_id)
            self._audit.aud(1, self.MODULE, self._usr_id()).diff(dut.rec, None, 'fura.usrtype')
            await at.commit()
