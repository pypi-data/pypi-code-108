# -*- coding: utf-8 -*-
from django.conf import settings as django_settings
try:
    from django.conf.urls import url
except ImportError:
    from django.conf.urls.defaults import url

if django_settings.ASKBOT_TRANSLATE_URL == True:
    from django.utils.translation import pgettext
else:
    pgettext = lambda context, value: value

from askbot.deps.django_authopenid import views as OpenidViews

urlpatterns = [
    # yadis rdf
    url(r'^yadis.xrdf$', OpenidViews.xrdf, name='yadis_xrdf'),
     # manage account registration
    url(r'^%s$' % pgettext('urls', 'signin/'), OpenidViews.signin, name='user_signin'),
    url(
        r'^%s%s$' % (pgettext('urls', 'widget/'), pgettext('urls', 'signin/')),
        OpenidViews.signin,
        {'template_name': 'authopenid/widget_signin.html'},
        name='widget_signin'
    ),
    url(r'^%s$' % pgettext('urls', 'signout/'), OpenidViews.signout, name='user_signout'),
    #this view is "complete-openid" signin
    url(
        r'^%s%s$' % (pgettext('urls', 'signin/'), pgettext('urls', 'complete/')),
        OpenidViews.complete_openid_signin,
        name='user_complete_openid_signin'),
    url(
        r'^%s%s$' % (pgettext('urls', 'signin/'), pgettext('urls', 'complete-cas/')),
        OpenidViews.complete_cas_signin,
        name='user_complete_cas_signin'),
    url(
        r'^signin/complete-oauth/',# % (pgettext('urls', 'signin/'), pgettext('urls', 'complete-oauth/')),
        OpenidViews.complete_oauth1_signin,
        name='user_complete_oauth1_signin'
    ),
    url(
        r'^signin/complete-discourse/',
        OpenidViews.complete_discourse_signin,
        name='user_complete_discourse_signin'
    ),
    url(
        r'^signin/complete-oauth2/',
        OpenidViews.complete_oauth2_signin,
        name='user_complete_oauth2_signin'
    ),
    url(r'^%s$' % pgettext('urls', 'register/'), OpenidViews.register, name='user_register'),
    url(
        r'^%s$' % pgettext('urls', 'signup/'),
        OpenidViews.signup_with_password,
        name='user_signup_with_password'
    ),
    url(
        r'change-password/',
        OpenidViews.change_password,
        name='change_password'
    ),
    url(r'^%s$' % pgettext('urls', 'logout/'), OpenidViews.logout_page, name='logout'),
    url(
        r'^%s$' % pgettext('urls', 'recover/'),
        OpenidViews.recover_account,
        name='user_account_recover'
    ),
    url(
        r'^%s$' % pgettext('urls', 'verify-email/'),
        OpenidViews.verify_email_and_register,
        name='verify_email_and_register'
    ),
    url(
        r'^delete_login_method/$',#this method is ajax only
        OpenidViews.delete_login_method,
        name ='delete_login_method'
    )
]
