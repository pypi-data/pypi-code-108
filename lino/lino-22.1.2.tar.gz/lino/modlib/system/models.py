# -*- coding: UTF-8 -*-
# Copyright 2009-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from etgen.html import E
from django.conf import settings
from django.utils.encoding import force_str

from django.db import models
from django.utils.translation import gettext_lazy as _

from django.apps import apps ; get_models = apps.get_models

from lino.api import dd, rt
from lino.core import actions
from lino.core.utils import full_model_name
from lino.core.roles import SiteStaff
from lino.core.actors import resolve_action

from lino.modlib.printing.choicelists import BuildMethods
from lino.modlib.checkdata.choicelists import Checker


# import them here to have them on rt.models.system:
from .choicelists import YesNo, Genders, PeriodEvents, DashboardLayouts
from .mixins import Lockable


class BuildSiteCache(dd.Action):
    label = _("Rebuild site cache")
    url_action_name = "buildjs"

    def run_from_ui(self, ar):
        settings.SITE.kernel.default_renderer.build_site_cache(True)
        return ar.success(
            """\
Seems that it worked. Refresh your browser.
<br>
Note that other users might experience side effects because
of the unexpected .js update, but there are no known problems so far.
Please report any anomalies.""",
            alert=_("Success"))


if False:
    class SiteConfigManager(models.Manager):

        def get(self, *args, **kwargs):
            return settings.SITE.site_config



class SiteConfig(dd.Model):

    class Meta(object):
        abstract = dd.is_abstract_model(__name__, 'SiteConfig')
        verbose_name = _("Site configuration")

    if False:
        objects = SiteConfigManager()
        real_objects = models.Manager()

    default_build_method = BuildMethods.field(
        verbose_name=_("Default build method"),
        blank=True, null=True)

    simulate_today = models.DateField(
        _("Simulated date"), blank=True, null=True)

    site_company = dd.ForeignKey(
        "contacts.Company",
        blank=True, null=True,
        verbose_name=_("Site operator"),
        related_name='site_company_sites')


    def __str__(self):
        return force_str(_("Site Parameters"))

    def update(self, **kw):
        """
        Set some field of the SiteConfig object and store it to the
        database.
        """
        # print("20180502 update({})".format(kw))
        for k, v in kw.items():
            if not hasattr(self, k):
                raise Exception("SiteConfig has no attribute %r" % k)
            setattr(self, k, v)
        self.full_clean()
        self.save()

    def save(self, *args, **kw):
        # print("20180502 save() {}".format(dd.obj2str(self, True)))
        super(SiteConfig, self).save(*args, **kw)
        settings.SITE.clear_site_config()


def my_handler(sender, **kw):
    # print("20180502 {} my_handler calls clear_site_config()".format(
    #     settings.SITE))
    settings.SITE.clear_site_config()
    #~ kw.update(sender=sender)
    # dd.database_connected.send(sender)
    #~ dd.database_connected.send(sender,**kw)

from django.test.signals import setting_changed
from lino.core.signals import testcase_setup
setting_changed.connect(my_handler)
testcase_setup.connect(my_handler)
dd.connection_created.connect(my_handler)
models.signals.post_migrate.connect(my_handler)


# def dashboard_layouts(cls, k, layout_class, **options):
#     assert k == "detail_layout"
#     yield cls.detail_layout
#     for i in DashboardLayouts.get_list_items():
#         yield i.main


class SiteConfigs(dd.Table):

    model = 'system.SiteConfig'
    required_roles = dd.login_required(SiteStaff)
    hide_navigator = True
    allow_delete = False
    hide_top_toolbar = True

    detail_layout = dd.DetailLayout("""
    default_build_method
    # lino.ModelsBySite
    """, window_size=(60, 'auto'))

    @classmethod
    def get_default_action(cls):
        return cls.detail_action

    do_build = BuildSiteCache()

from lino.utils.report import EmptyTable


class Dashboard(EmptyTable):

    # label = _("D")
    hide_navigator = True
    required_roles = set()
    allow_delete = False
    # detail_layout = """
    # welcome_messages
    # working.WorkedHours comments.RecentComments
    # tickets.MyTicketsToWork
    # notify.MyMessages
    # """

    @classmethod
    def get_extra_layouts(cls):
        # count = 0
        for i in DashboardLayouts.get_list_items():
            yield i.value, i.main
            # print("20210530", i.value, repr(i.main))
        #     count += 1
        # assert count > 0

    @classmethod
    def get_default_action(cls):
        # raise Exception("20210530")
        # return None
        # return actions.ShowExtraDetail(None)
        # cls._bind_action("extra_"+name, a, False)
        ba = cls.get_action_by_name('extra_default')
        # assert ba is not None
        return ba

    @classmethod
    def get_detail_action(self, ar):
        u = ar.get_user()
        if u.dashboard_layout:
            return cls.get_action_by_name('extra_' + u.dashboard_layout.name)
        return cls.get_action_by_name('extra_default')

    @dd.htmlbox()
    def welcome_messages(cls, obj, ar=None):
        return settings.SITE.get_main_html(ar)
        # if ar.get_user().is_authenticated:
        #     return E.p(*settings.SITE.get_welcome_messages(ar))

    @classmethod
    def collect_extra_actions(cls):
        return settings.SITE.quicklinks.items
        # for ql in settings.SITE.quicklinks.items:
        #     yield ql.bound_action

        # for mi in settings.SITE.get_quicklinks(None).items:
        #     yield mi
        # for p in settings.SITE.sorted_plugins:
        #     for ql in p.get_quicklinks(None):
        #         yield ql
        #         # print(repr(ql))
        #         # ba = resolve_action(ql)
        #         # if ba is not None:
        #         #     yield ba


# if settings.SITE.user_model == 'users.User':
#     dd.inject_field(settings.SITE.user_model,
#                     'user_type', UserTypes.field())
#     dd.inject_field(settings.SITE.user_model, 'language', dd.LanguageField())

# @dd.receiver(dd.pre_analyze)
# def set_dashboard_actions(sender, **kw):
#     for p in settings.SITE.sorted_plugins:
#         for ql in p.get_quicklinks(None):
#             ba = resolve_action(ql)
#             Dashboard.define_action(ba.action.action_name=ba)

    # for ql in settings.SITE.get_quicklinks()
    # for m in get_checkable_models().keys():
    #     if m is None:
    #         continue
    #     assert m is not Problem
    #     m.define_action(check_data=UpdateProblemsByController(m))
    #     m.define_action(fix_problems=FixProblemsByController(m))


class BleachChecker(Checker):

    verbose_name = _("Find unbleached html content")
    model = dd.Model

    def get_checkable_models(self):

        for m in super(BleachChecker, self).get_checkable_models():
            if len(m._bleached_fields):
                yield m

    def get_checkdata_problems(self, obj, fix=False):
        t = tuple(obj.fields_to_bleach())
        if len(t):
            fldnames = ', '.join([f.name for f, old, new in t])
            yield (True, _("Fields {} have unbleached content.").format(fldnames))
            if fix:
                obj.before_ui_save(None, None)
                obj.full_clean()
                obj.save()


BleachChecker.activate()
