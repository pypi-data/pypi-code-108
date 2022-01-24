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
import string

from mettle.lib import xMettle

from bs_lib import common

from .access      import Access
from .audit       import Audit
from .auth        import factory as AuthFactory
from .dao         import Dao
from .err_code    import ErrCode
from .fura_token  import FuraToken
from .otp         import Otp
from .xfura       import xFura
from .            import util

from bs_fura.braze  import ResetMethod_Couplet

from bs_fura.db.tables import tUla


class UserLogin:
    """
    This object controls the user login authentication, and
    management of tokens.
    """

    MODULE = "[UserLogin]"

    def __init__(self, dao: Dao, site_code: str, site_id: int = None):
        """
        Constructor.

        :param dao: The fura dao object to use.
        :param site_code: Site unique code.
        :param site_id: The site id instead.
        """
        self._dao       = dao
        self._site_code = site_code
        self._site_id   = site_id or -1
        self._acc       = None
        self._usr_id    = None

        if not self._site_code and self._site_id > 0:
            st = self._dao.site_get(self._site_id)

            if not st:
                raise Exception('Site not found. [%d]' % (self._site_id))

            self._site_code = st.code
        else:
            st = self._dao.site_get(self._site_code)

            if not st:
                raise Exception('Site not found. [%s]' % (self._site_code))

            self._site_id = st.id


    def __del__(self):
        """
        Destructor.
        """
        self.clear()


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


    def clear(self):
        """
        Clear the object for reuse.
        """
        if self._acc:
            self._acc.clear_audit_hist()
            self._acc = None


    def login(self,
              usr_id     : str,
              auth_type  : str,
              auth_data  : str,
              auth_ip    : str = None,
              auth_geo   : str = None,
              token_mode : bool = False):
        """
        Does a user login, doing the authentication.

        :param usr_id: User logging in.
        :param auth_type: Auth type - see UsrAuth.auth_type_Couplet
        :param auth_data: Auth data, ie password or key or something else.
        :param authIp: Optionally give the auth ip address.
        :param auth_geo: Optionally give the auth geo location.
        :param token_mode: If true, does not suspend accounts on to many failures, but does make them wait.
        """
        self.clear()

        with Access(self._dao, self._site_code, usr_id, self.MODULE) as ac:
            if not ac.ok():
                tmp = ac._ada_lst[-1]
                ac.clear_audit_hist()
                raise xFura(tmp)

            ac.clear_audit_hist()

            self._acc = ac

            ao = AuthFactory.get_auth_object(auth_type)

            ao.initialize(self._dao, self._acc._site.id, usr_id)

            if ao.is_token_based():
                raise xMettle('Cannot login with a token based auth type')

            ec = ao.login(auth_data, auth_ip, auth_geo, token_mode)

            ao.save_user_auth()

            self._save_ula_and_raise(tUla.Action_Couplet.key_login,
                                     auth_type,
                                     ec,
                                     auth_ip,
                                     auth_geo)

            self._usr_id = usr_id


    def login_token(self,
                    auth_type   : str,
                    auth_data   : str,
                    auth_ip     : str = None,
                    auth_geo    : str = None,
                    raise_error : bool = True) -> str:
        """
        Login with a token instead of username/password.

        :param auth_type: Auth type - see UsrAuth.auth_type_Couplet
        :param auth_data: Auth data, the token to use.
        :param authIp: Optionally give the auth ip address.
        :param auth_geo: Optionally give the auth geo location.
        :param raise_error: Optinally return None if not a valid auth token.
        :return: The user id or None if not found.
        """
        au = self._dao.usrauth_by_token(self._site_code, auth_type, auth_data)

        if not au:
            if raise_error:
                raise xMettle('Invalid token.')

            return None

        with Access(self._dao, self._site_code, au.usr_id, self.MODULE) as ac:
            if not ac.ok():
                tmp = ac._ada_lst[-1]
                ac.clear_audit_hist()
                raise xFura(tmp)

            ac.clear_audit_hist()

            self._acc = ac

            ao = AuthFactory.get_auth_object(auth_type)

            ao.initialize(self._dao, self._acc._site.id, au.usr_id)

            if not ao.is_token_based():
                raise xMettle('Cannot token login with non token based authentication type')

            ec = ao.login(auth_data,
                          auth_ip,
                          auth_geo,
                          True)

            ao.save_user_auth()

            self._save_ula_and_raise(tUla.Action_Couplet.key_login,
                                     auth_type,
                                     ec,
                                     auth_ip,
                                     auth_geo)

            self._usr_id  = au.usr_id

        return au.usr_id


    def logout(self, site_id: int, usr_id: str):
        """
        Does a user login, doing the authentication.

        :param site_id:  Site id.
        :param usr_id: User logging out.
        """
        ula = tUla(
            site_id,
            '',
            datetime.datetime.now(),
            usr_id,
            ErrCode.NoError.value,
            tUla.State_Couplet.key_success,
            tUla.Action_Couplet.key_logout,
            'X',
            '',
            '')

        self._usr_id  = None
        self._site_id = -1

        self._dao.ula_save(ula)


    def gen_fura_token(self, ft: FuraToken) -> str:
        """
        Generate a web access token for the login.

        :param ft: Web token object.
        :return: The generated token.
        """
        if not self._acc:
            raise Exception("User not logged in.")

        return ft.new_usr_token(self._acc)


    def reset_auth(self,
                   usr_id       : str,
                   auth_type    : str,
                   reset_method : str,
                   otp_tags     : dict,
                   auth_ip      : str = None,
                   auth_geo     : str = None) -> str:
        """
        Preps an auth entry to being reset. Returns the reset token that must be
        used to reset the user auth entry.

        :param usr_id: User logging in.
        :param auth_type: Auth type - see UsrAuth.auth_type_Couplet
        :param reseMethod: See ResetMethod_Couplet.
        :param otp_tags: Optionally add any otp tags.
        :param auth_ip: Optionally give the auth ip address.
        :param auth_geo: Optionally give the auth geo location.
        :return: The reset token/otp.
        """
        with Access(self._dao, self._site_code, usr_id, self.MODULE) as ac:
            if not ac.ok():
                tmp = ac._ada_lst[-1]
                ac.clear_audit_hist()
                raise xFura(tmp)

            ac.clear_audit_hist()

            self._acc = ac

        ao = AuthFactory.get_auth_object(auth_type)

        if ao.is_token_based():
            raise xMettle("Auth type [%s] is token based, higher security prevents it \
from being reset manually." % (ao.auth_type_name()))

        with Otp(self._dao, self._site_id, usr_id) as otp:
            otp_str = otp.new_otp(reset_method, 'auth-reset', otp_tags)

        self._save_ula_and_raise(tUla.Action_Couplet.key_reset_auth,
                                 auth_type,
                                 ErrCode.NoError,
                                 auth_ip,
                                 auth_geo)

        return otp_str


    def req_auth_reset(self,
                       usr_who      : str,
                       targ_usr     : str,
                       auth_type    : str,
                       reset_method : str,
                       targ_addr    : str,
                       pub_safe     : bool = True,
                       is_reg       : bool = False) -> bool:
        """
        Requests a user reset url from Fura.  This uses the 'authreset.*' config values
        in the config table to generate an email and send it via a stock standard
        smpt email server to the user.

        This is used as a fallback mechenism, ideally a system using Fura should implement
        its own methods of resetting user authentication passwords/keys.

        :param usr_who: Which user is requesting this auth reset.
        :param targ_usr: The user who is having their auth reset.
        :param auth_type: The auth type being reset.
        :param reset_method: The requestion method, either email or sms.
        :param targ_addr: Optionally give the target email/sms address to send, else the
                            system will attempt to send to available user email/cell no.
        :param pub_safe: If true does not give back detailed info on why an auth request was rejected.
        :param is_reg: If true, this is customer registration instead of an authreset
        :return: True if request was successful as false.
        """
        if usr_who != targ_usr and usr_who != 'admin':
            raise xMettle('Only admin users can reset other users.')

        site_rec  = self._dao.site_get(self._site_code)

        if not site_rec:
            if pub_safe:
                self._dao.pod.log.warning('Site [%s] not found.' % self._site_code, self.MODULE)
                return False

            raise xMettle('Site [%s] not found.' % self._site_code, self.MODULE)

        usr_rec = self._dao.usr_get(site_rec.id, targ_usr)
        meth    = None

        if not usr_rec:
            if pub_safe:
                self._dao.pod.log.warning('User [%s] not found.' % targ_usr, self.MODULE)
                return False

            raise xMettle('User [%s] not found.' % targ_usr, self.MODULE)

        addr_obj = util.get_usr_loco_address(usr_rec, targ_addr)
        meth     = ResetMethod_Couplet.get_value(reset_method).lower()

        if not addr_obj or meth not in addr_obj:
            if targ_addr:
                raise xMettle('Invalid %s destination [%s]' % (
                    ResetMethod_Couplet.get_value(reset_method), str(targ_addr)), self.MODULE)

            if pub_safe:
                self._dao.pod.log.warning('User [%s] does not have any valid %s desinations.' % (
                    targ_usr, ResetMethod_Couplet.get_value(reset_method)), self.MODULE)
                return False

                raise xMettle('User [%s] does not have any valid %s destinations.' % (
                    targ_usr, ResetMethod_Couplet.get_value(reset_method)), self.MODULE)

        if meth not in ('email', 'sms'):
            if pub_safe:
                self._dao.pod.log.warning('Reset method not expected [%s]' % (reset_method))
                return False

            raise xMettle('Reset method not expected [%s]' % (reset_method), self.MODULE)

        for rem_meth in (list(addr_obj.keys())):
            if rem_meth != meth:
                addr_obj.pop(rem_meth)

        reset_url  = self._dao.read_config(site_rec.id, 'authreset.urlmask.%s' % meth, str)
        supp_email = self._dao.read_config(site_rec.id, 'authreset.support-email',     str)
        loco_type  = self._dao.read_config(site_rec.id, 'loco.usrreg' if is_reg else 'loco.authreset', str)
        otp_tags   = None

        if targ_addr:
            otp_tags = { 'addr' : targ_addr }
        elif len(addr_obj) == 1:
            otp_tags = { 'addr' : list(addr_obj.values())[0] }

        otp = self.reset_auth(targ_usr, auth_type, reset_method, otp_tags)

        tags = {
            'usr'           : usr_rec.id,
            'site'          : site_rec.code,
            'site_descr'    : site_rec.descr,
            'authtype'      : auth_type,
            'otpmethod'     : reset_method,
            'tok'           : otp,
            'otp'           : otp,
            'support_email' : supp_email,
            'newreg'        : 'yes' if is_reg else 'no',
            'mode'          : 'reg' if is_reg else 'forgot',
        }

        tags['httplink'] = string.Template(reset_url).substitute(tags)

        self._dao.pod.log.info('  - httplink: %s' % (tags['httplink']))

        meta_data = { 'site': site_rec.code, 'usr': targ_usr }

        self._dao.pod.usr_id = targ_usr

        loco_cnt = self._dao.loco_trig.trig(loco_type, addr_obj, tags, meta_data = meta_data)

        self._dao.pod.log.info('  - triggered %d notifications [%s]' % (loco_cnt, loco_type))

        return True


    def req_token_reset(self, usr_who: str, targ_usr: str, auth_type: str):
        """
        Resets a token type authentiction.

        :param usr_who: Which user is requesting this token reset.
        :param targ_usr: The user who is having their token reset.
        :param auth_type: The auth type to be reset, needs to be a token auth type.
        """
        if usr_who != targ_usr and usr_who != 'admin':
            raise xMettle('Only admin users can reset other users.')

        self.clear()

        with Access(self._dao, self._site_code, targ_usr, self.MODULE) as ac:
            if not ac.ok():
                tmp = ac._ada_lst[-1]
                ac.clear_audit_hist()
                raise xFura(tmp)

            ac.clear_audit_hist()

            self._acc = ac

        ao = AuthFactory.get_auth_object(auth_type)

        if not ao.is_token_based():
            raise xMettle("Auth type [%s] is not token based." % (ao.auth_type_name()))

        ao.initialize(self._dao, self._acc._site.id, targ_usr)

        ec = ao.set_auth_data(None, 'token')

        self._save_ula_and_raise(tUla.Action_Couplet.key_change_auth, auth_type, ec)


    def set_auth_data(self,
                      audit      : Audit,
                      usr_id     : str,
                      auth_type  : str,
                      auth_data  : str,
                      otp        : str,
                      otp_method : str,
                      auth_ip    : str = None,
                      auth_geo   : str = None):
        """
        Sets the users auth type auth data.

        :param audit: The fura audit object to use.
        :param usr_id: User logging in.
        :param auth_type: Auth type - see UsrAuth.auth_type_Couplet
        :param auth_data: The password/key auth string.
        :param otp: The otp being used, if None check is ignored.
        :param otp_method: The otp method meing used, if None check is ignored.
        :param auth_ip: Optionally give the auth ip address.
        :param auth_geo: Optionally give the auth geo location.
        """
        self.clear()

        with Access(self._dao, self._site_code, usr_id, self.MODULE) as ac:
            if not ac.ok():
                tmp = ac._ada_lst[-1]
                ac.clear_audit_hist()
                raise xFura(tmp)

            ac.clear_audit_hist()

            self._acc = ac

        ao = AuthFactory.get_auth_object(auth_type)

        ao.initialize(self._dao, self._acc._site.id, usr_id)

        ec = ao.set_auth_data(audit, auth_data, otp, otp_method)

        self._save_ula_and_raise(tUla.Action_Couplet.key_change_auth, auth_type, ec, auth_ip, auth_geo)


    def read_token(self, usr_id: str, auth_type: str) -> str:
        """
        User wants to get/read their auth token for specific auth type.

        :param usr_id: The logged in user.
        :param auth_type: The auth type to read from.
        :return: The token value.
        """
        self.clear()

        with Access(self._dao, self._site_code, usr_id, self.MODULE) as ac:
            if not ac.ok():
                tmp = ac._ada_lst[-1]
                ac.clear_audit_hist()
                raise xFura(tmp)

            ac.clear_audit_hist()

            self._acc = ac


        ao = AuthFactory.get_auth_object(auth_type)

        if not ao.is_token_based():
            raise xMettle("Auth type [%s] is not token based." % (ao.auth_type_name()))

        ao.initialize(self._dao, self._acc._site.id, usr_id)

        ec, tok = ao.read_token()

        self._save_ula_and_raise(tUla.Action_Couplet.key_change_auth, auth_type, ec)

        return tok


    def change_auth(self, usr_id: str, auth_type: str, new_data: str, old_data: str):
        """
        User wants to change their authtype value, ie their password probably.

        :param usr_id: The logged in user.
        :param auth_type: The auth type to change from.
        :param new_data: The new value.
        :param old_data: The old value for confirmation.
        """
        self._usr_id = usr_id

        ao = AuthFactory.get_auth_object(auth_type)

        if ao.is_token_based():
            raise xMettle("Auth type [%s] is token based, higher security prevents it \
from being changed manually." % (ao.auth_type_name()))


        ao.initialize(self._dao, self.get_site_id(), usr_id)

        try:
            ao.change(new_data, old_data)
        except Exception:
            self._save_ula(tUla.Action_Couplet.key_change_auth, auth_type, ErrCode.AuthInvalid)
            raise


    def get_site_id(self) -> int:
        """
        Gets the site id after logging in.
        """
        if self._site_id <= 0:
            if self._site_code:
                st = self._dao.site_get(self._site_code)

                if not st:
                    raise Exception('Site not found. [%d]' % (self._site_code))

                self._site_id = st.id

        return self._site_id


    def get_usr_id(self) -> str:
        """
        Gets the user id after logging in.
        """
        return self._usr_id


    def confirm_contact_req(self, usr_id: str, contact_addr: str):
        """
        User is requesting a contact information confirmation request.

        :param userId: The user identifier.
        :param contact_addr: Which address are they verifying.
        """
        usr_rec = self._dao.usr_get(self._site_id, usr_id)

        if not usr_rec:
            raise Exception('User not found. [site:%d, usr_id:%s]' % (self._site_code, usr_id))

        self._usr_id = usr_id
        addr_obj     = {}
        otp_method   = None

        if contact_addr == usr_rec.email1:
            if not common.dest_addr_valid_email(contact_addr):
                raise xMettle('Not a valid email address.')

            if usr_rec.email1Conf:
                raise xMettle('Already verified.')

            otp_method = ResetMethod_Couplet.key_email
        elif contact_addr == usr_rec.email2:
            if not common.dest_addr_valid_email(contact_addr):
                raise xMettle('Not a valid email address.')

            if usr_rec.email2Conf:
                raise xMettle('Already verified.')

            otp_method = ResetMethod_Couplet.key_email
        elif contact_addr == usr_rec.cellNo1:
            if not common.dest_addr_valid_sms(contact_addr):
                raise xMettle('Not a valid cell number.')

            if usr_rec.cellNo1Conf:
                raise xMettle('Already verified.')

            otp_method = ResetMethod_Couplet.key_sms
        elif contact_addr == usr_rec.cellNo2:
            if not common.dest_addr_valid_sms(contact_addr):
                raise xMettle('Not a valid cell number.')

            if usr_rec.cellNo2Conf:
                raise xMettle('Already verified.')

            otp_method = ResetMethod_Couplet.key_sms
        else:
            raise xMettle('Contact information not found. Please refresh and try again.')

        addr_obj       = { ResetMethod_Couplet.get_value(otp_method).lower() : [ contact_addr ]}
        otp_meta_data  = { 'addr': contact_addr }
        loco_cfg_id    = 'loco.confirm_addr'
        loco_type      = self._dao.read_config(usr_rec.site_id, loco_cfg_id, str)
        loco_tags      = self._dao.std_loco_tags(usr_rec)
        loco_meta_data = { 'site': self._site_code, 'usr': usr_id }

        if loco_type == 'DEADBEEF':
            self.pod.log.warning('Loco trigger is DEADBEEF, [lococFG:%s, site_id:%d, usr_id:%s] - error to be raised' % (
                loco_cfg_id, usr_rec.site_id, usr_rec.id))
            raise xMettle('Verification or confirmation of user contact information is disabled. \
Please contact your system administrator.')

        with Otp(self._dao, self._site_id, usr_id) as otp:
            otp_str = otp.new_otp(otp_method, 'confirm_contact', otp_meta_data)
            loco_tags['otp'] = otp_str

        loco_tags['contact_type'] = 'Email' if otp_method == ResetMethod_Couplet.key_email else 'Cell Number'
        loco_tags['contact_addr'] = contact_addr

        loco_cnt = self._dao.loco_trig.trig(loco_type, addr_obj, loco_tags, meta_data = loco_meta_data)

        self._dao.pod.log.info('  - triggered %d notifications [%s]' % (loco_cnt, loco_type))


    def confirm_contact(self, audit: Audit, usr_id: str, otp_str: str) -> str:
        """
        User is confirming their contact details.

        :param audit: The audit object to use.
        :param userId: The user identifier.
        :param otp_str: The otp string to verifify.
        :return: The contact number that was confirmed.
        """
        usr_rec = self._dao.usr_get(self._site_id, usr_id)

        if not usr_rec:
            raise Exception('User not found. [site:%d, usr_id:%s]' % (self._site_code, usr_id))

        self._usr_id = usr_id
        otp_meta     = {}
        ecode        = self._dao.otp_ok(otp_str, 'confirm_contact', usr_rec.site_id, usr_rec.id, otp_meta)

        if ecode != ErrCode.NoError:
            raise xMettle('Invalid OTP', errCode=ecode)

        orig         = copy.copy(usr_rec)
        contact_addr = otp_meta.get('addr')

        if not contact_addr:
            raise Exception('Internal Error. Contact address not set by OTP')

        if contact_addr == usr_rec.email1:
            usr_rec.email1Conf = True
        elif contact_addr == usr_rec.email2:
            usr_rec.email2Conf = True
        elif contact_addr == usr_rec.cellNo1:
            usr_rec.cellNo1Conf = True
        elif contact_addr == usr_rec.cellNo2:
            usr_rec.cellNo2Conf = True
        else:
            raise xMettle('Contact information not found. Please refresh and try again.')

        usr_rec.modified_by = usr_id

        self._dao.db_dao.dUsr(self._dao.pod.dbcon).update(usr_rec)

        audit.aud(usr_rec.site_id, self.MODULE, usr_rec.modified_by).diff(orig, usr_rec, 'fura.usr')

        return contact_addr


    def _save_ula_and_raise(self, action: str, auth_type: str, ec: ErrCode, auth_ip: str = None, auth_geo: str = None):
        """
        Save a user login audit record.  If the errocde is not no error
        it raises an xFura exception.

        :param action: The action being taken.
        :param auth_type: The auth type.
        :param ec: The error code.
        :param auth_ip: Optionally give the auth ip address.
        :param auth_geo: Optionally give the auth geo location.
        """
        ula = self._save_ula(action, auth_type, ec, auth_ip, auth_geo)

        if ec != ErrCode.NoError:
            raise xFura(ula)


    def _save_ula(self, action: str, auth_type: str, ec: ErrCode, auth_ip: str = None, auth_geo: str = None) -> tUla:
        """
        Save a user login audit record.  If the errocde is not no error
        it raises an xFura exception.

        :param action: The action being taken.
        :param auth_type: The auth type.
        :param ec: The error code.
        :param auth_ip: Optionally give the auth ip address.
        :param auth_geo: Optionally give the auth geo location.
        :param msg: Optinal additional error message.
        :return: The ual record created
        """
        if ec == ErrCode.NoError:
            st = tUla.State_Couplet.key_success
        elif ec in (ErrCode.AuthInvalid, ErrCode.AuthNotFound):
            st = tUla.State_Couplet.key_password_invalid
        elif ec == ErrCode.AuthEmpty:
            st = tUla.State_Couplet.key_max_attemps
        elif ec == ErrCode.AuthOTPNotFound     or\
                ec == ErrCode.AuthOTPUsed      or\
                ec == ErrCode.AuthOTPExpired   or\
                ec == ErrCode.AuthOTPInvlalid  or\
                ec == ErrCode.AuthOTPTarget    or\
                ec == ErrCode.AuthOTPTMaxFails or\
                ec == ErrCode.AuthOTPTMethod:
            st = tUla.State_Couplet.key_otp_invalid
        else:
            st = tUla.State_Couplet.key_unexpected_error

        ula = tUla(
            self.get_site_id() if not self._acc else self._acc._site.id,
            self._site_code,
            datetime.datetime.now(),
            self.get_usr_id() if not self._acc else self._acc._usr_id,
            ec.value,
            st,
            action,
            auth_type,
            '' if auth_ip  is None else auth_ip,
            '' if auth_geo is None else auth_geo)

        self._dao.ula_save(ula)

        return ula
