# -*- coding: UTF-8 -*-
# Copyright 2011-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import datetime

from etgen.html import E, tostring

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext

from lino.api import dd, rt, _
from lino.core.roles import SiteAdmin
from lino.core import auth, layouts
from lino.core.actions import SubmitInsert


def send_welcome_email(ar, obj, recipients):
    sender = settings.SERVER_EMAIL
    subject = _("Welcome on {site}").format(
        site=settings.SITE.title or settings.SITE.verbose_name)
    body = obj.get_welcome_email_body(ar)
    rt.send_email(subject, sender, body, recipients)

class CheckedSubmitInsert(SubmitInsert):
    """Like the standard :class:`lino.core.actions.SubmitInsert`, but
    checks certain things before accepting the new user.

    """
    def run_from_ui(self, ar, **kw):
        obj = ar.create_instance_from_request()
        qs = obj.__class__.objects.filter(username=obj.username)
        if len(qs) > 0:
            msg = _("The username {} is taken. "
                    "Please choose another one").format(obj.username)

            ar.error(msg)
            return

        def ok(ar2):
            SubmitInsert.run_from_ui(self, ar, **kw)
            # self.save_new_instance(ar2, obj)
            ar2.success(_("Your request has been registered. "
                          "An email will shortly be sent to {0}"
                          "Please check your emails.").format(
                              obj.email))
            # ar2.set_response(close_window=True)
            # logger.info("20140512 CheckedSubmitInsert")

        ok(ar)


class VerifyUser(dd.Action):
    """Enter your verification code."""
    label = _("Verify")
    # http_method = 'POST'
    # select_rows = False
    # default_format = 'json'
    required_roles = set([])
    # required_roles = dd.login_required(SiteAdmin)
    # show_in_bbar = False
    # show_in_workflow = True
    parameters = dict(
        email=models.EmailField(_('e-mail address')),
        verification_code=models.CharField(
            _("Verification code"), max_length=50))
    params_layout = """
    email
    # instruct
    verification_code
    """
    # def get_action_title(self, ar):
    #     return _("Register new user")

    # @dd.constant()
    # def instruct(self, *args):
    #     return _("Enter the verification code you received.")

    def get_action_permission(self, ar, obj, state):
        if obj.is_verified():
            # print("20210712 False (is verified)")
            return False
        # print("20210712 True")
        return super(
            VerifyUser, self).get_action_permission(ar, obj, state)

    def run_from_ui(self, ar, **kw):
        assert len(ar.selected_rows) == 1
        user = ar.selected_rows[0]
        pv = ar.action_param_values
        # qs = rt.models.users.User.objects.exclude(verification_code='')
        # try:
        #     user = qs.get(email=pv.email)
        # except Exception:
        #     msg = _("Invalid email address")
        #     return ar.error(msg)
        if user.is_verification_code_expired():
            msg = _("Verification code expired")
            return ar.error(msg)
        if user.verification_code != pv.verification_code:
            msg = _("Invalid verification code")
            return ar.error(msg)
        UserTypes = rt.models.users.UserTypes
        ut = UserTypes.get_by_name(dd.plugins.users.user_type_verified)
        user.user_type = ut
        user.verification_code = ''
        user.save()
        ar.success(_("User {} is now verified.").format(user))


class MySettings(dd.Action):
    label = _("My settings")
    select_rows = False
    show_in_bbar = False
    # http_method = "POST"
    default_format = None

    def run_from_ui(self, ar, **kw):
        # assert len(ar.selected_rows) == 1
        # user = ar.selected_rows[0]
        # raise PermissionError("20210811")
        user = ar.get_user()
        ar.goto_instance(user)


class SendWelcomeMail(dd.Action):
    label = _("Welcome mail")
    if True:  # #1336
        show_in_bbar = True
        show_in_workflow = False
    else:
        show_in_bbar = False
        show_in_workflow = True
    button_text = "\u2709"  # ✉
    # required_roles = dd.login_required(SiteAdmin)

    def get_action_permission(self, ar, obj, state):
        if not obj.email:
            return False
        user = ar.get_user()
        if user != obj:
            if not user.user_type.has_required_roles([SiteAdmin]):
                return False
        return super(
            SendWelcomeMail, self).get_action_permission(ar, obj, state)

    def run_from_ui(self, ar, **kw):
        assert len(ar.selected_rows) == 1
        obj = ar.selected_rows[0]

        if (dd.plugins.users.allow_online_registration and not obj.is_verified()
            and obj.is_verification_code_expired()):
            obj.email_changed(ar)
            # obj.email_changed method() resets the verification_code and sent time.
            obj.full_clean()
            obj.save()

        recipients = ["{} <{}>".format(obj, obj.email)]

        def ok(ar):
            send_welcome_email(ar, obj, recipients)

            msg = _("Welcome mail has been sent to {}.").format(
                ', '.join(recipients))
            ar.success(msg, alert=True)

        msg = _("Send welcome mail to {} ?").format(', '.join(recipients))
        return ar.confirm(ok, msg)



class ChangePassword(dd.Action):
    # button_text = u"\u205C"  # DOTTED CROSS (⁜)
    # button_text = u"\u2042"  # ASTERISM (⁂)
    button_text = "\u2731" # 'HEAVY ASTERISK' (✱)
    # icon_name = "disk"
    label = _("Change password")

    parameters = dict(
        current=dd.PasswordField(_("Current password"), blank=True),
        new1=dd.PasswordField(_("New password"), blank=True),
        new2=dd.PasswordField(_("New password again"), blank=True)
    )
    params_layout = """
    current
    new1
    new2
    """

    # def get_action_permission(self, ar, obj, state):
    #     user = ar.get_user()
    #     # print("20160825", obj, user)
    #     if obj.id != user.id and \
    #        not user.user_type.has_required_roles([SiteAdmin]):
    #         return False
    #     return super(
    #         ChangePassword, self).get_action_permission(ar, obj, state)

    def run_from_ui(self, ar, **kw):

        pv = ar.action_param_values
        if pv.new1 != pv.new2:
            ar.error("New passwords didn't match!")
            return
        done_for = []
        for obj in ar.selected_rows:
            if ar.get_user().user_type.has_required_roles([SiteAdmin]) \
               or not obj.has_usable_password() \
               or obj.check_password(pv.current):
                obj.set_password(pv.new1)
                obj.full_clean()
                obj.save()
                done_for.append(str(obj))
            else:
                ar.info("Incorrect current password for %s." % obj)

        # if ar.request is not None:
        #     auth.login(ar.request, obj)
        msg = _("New password has been set for {}.").format(
            ', '.join(done_for))
        ar.success(msg, alert=True)


class SignOut(dd.Action):
    label = _("Sign out")
    select_rows = False
    default_format = 'ajax'
    show_in_bbar = False

    def run_from_ui(self, ar, **kw):
        # print(20170921, ar.request)
        user = ar.get_user()
        auth.logout(ar.request)
        ar.success(
            _("User {} logged out.").format(user),
            goto_url=ar.renderer.front_end.build_plain_url())

# from lino.core.fields import DisplayField, DummyField

# class SocialAuthField(DisplayField):

#     def value_from_object(self, obj, ar=None):
#         elems = []
#         elems.append(E.a("foo"))
#         return E.p(elems)

# def social_auth_field():
#     if settings.SITE.social_auth_backends:
#         return SocialAuthField()
#     return DummyField()

def validate_sessions_limit(request):
    if dd.plugins.users.active_sessions_limit == -1:
        return
    qs = rt.models.sessions.Session.objects.filter(
        expire_date__gt=timezone.now())
    if request.session.session_key:
        qs = qs.exclude(session_key=request.session.session_key)
    if qs.count() >= dd.plugins.users.active_sessions_limit:
        raise Warning(
            _("There are more than {} active user sessions. Please try again later.").format(
                dd.plugins.users.active_sessions_limit))

def get_social_auth_links_func(content_header, flex_row):
    def text_fn(*args):
        elems = [E.div(
            E.hr(style="width: -moz-available; margin-right: 1ch;"),
            E.span(content_header, style="white-space: nowrap;"),
            E.hr(style="width: -moz-available; margin-left: 1ch;"),
            style='display: flex;')]
        elems.append(E.br())
        links = []
        for name, href in settings.SITE.get_social_auth_links(chunks=True):
            anchor = E.a(E.span(" " + name, CLASS='pi pi-' + name) , href=href)
            style = "padding: 1ch; margin: 2px; border: 2px solid gray; border-radius: 6px;"
            if flex_row:
                el = E.div(anchor, style=style)
            else:
                el = E.span(anchor, style=style)
            links.append(el)
        elems.append(E.div(*links, style="text-align: center;"))
        return tostring(E.div(*elems))
    return text_fn

class SignIn(dd.Action):
    label = _("Sign in")
    select_rows = False
    parameters = dict(
        username=dd.CharField(_("Username")),
        password=dd.PasswordField(_("Password"), blank=True),
        social_auth_links=dd.Constant(
            get_social_auth_links_func(gettext("Or sign in with"), flex_row=True))
    )
    if not settings.SITE.has_feature('third_party_authentication'):
        parameters['social_auth_links'] = dd.DummyField()

    params_layout = dd.Panel("""
    login_panel:50 social_auth_links:50
    """, #label_align=layouts.LABEL_ALIGN_LEFT, window_size=(50, 9),
    login_panel="""
    username
    password
    """)

    http_method = "POST"
    # show_in_bbar = False

    def run_from_ui(self, ar, **kw):
        # ipdict = dd.plugins.ipdict
        # print("20210212 SignIn.run_from_ui()", ipdict.ip_records)
        validate_sessions_limit(ar.request)
        pv = ar.action_param_values
        user = auth.authenticate(
            ar.request, username=pv.username, password=pv.password)
        if user is None:
            ar.error(_("Failed to log in as {}.".format(pv.username)))
        else:
            # user.is_authenticated:
            auth.login(ar.request, user)
            ar.success(
                _("Now logged in as {}").format(user),
                close_window=True,
                goto_url=ar.renderer.front_end.build_plain_url())

class CreateAccount(dd.Action):
    label = _("Create Account")
    select_rows = False
    parameters = dict(
        first_name=dd.CharField(_("First Name")),
        last_name=dd.CharField(_("Last Name")),
        username=dd.CharField(_("Username")),
        email=dd.CharField(_("Email")),
        password=dd.PasswordField(_("Password"), blank=True),
        social_auth_links=dd.Constant(
            get_social_auth_links_func(gettext("Create account with"), flex_row=False))
    )
    if not settings.SITE.has_feature('third_party_authentication'):
        parameters['social_auth_links'] = dd.DummyField()

    params_layout = """
    first_name last_name
    username
    email
    password
    social_auth_links
    """
    http_method = "POST"
    # show_in_bbar = False

    def run_from_ui(self, ar, **kw):
        # validate_sessions_limit(ar.request)
        pv = ar.action_param_values
        User = rt.models.users.User
        qs = User.objects.filter(username=pv['username'])
        if len(qs) > 0:
            msg = _("The username {} is taken. "
                    "Please choose another one").format(pv.username)
            ar.error(msg)
            return

        UserTypes = rt.models.users.UserTypes
        ut = UserTypes.get_by_name(dd.plugins.users.user_type_new)
        pv.pop('social_auth_links')
        obj = User.objects.create_user(user_type=ut, **pv)
        obj.on_create(ar)
        obj.full_clean()
        obj.save()

        ar.selected_rows = [obj]
        recipients = ["{} <{}>".format(obj, obj.email)]
        send_welcome_email(ar, obj, recipients)

        rt.models.about.About.sign_in.run_from_ui(ar)


class SignInWithSocialAuth(SignIn):
    # 20171207 nice as an example of a action dialog window with a
    # HtmlBox, but we don't currently use it.
    parameters = dict(
        social_auth_links=dd.HtmlBox(
            # _("Other authentications"),
            default=E.div(*settings.SITE.get_social_auth_links())),
        # social_auth_links=dd.Constant(
        #     settings.SITE.get_social_auth_links),
        # social=social_auth_field(),
        username=dd.CharField(_("Username")),
        password=dd.PasswordField(_("Password"), blank=True)
    )
    # params_layout = dd.ActionParamsLayout("""
    params_layout = dd.Panel("""
    username
    password
    social_auth_links
    """, label_align="left", window_size=(60,10))
