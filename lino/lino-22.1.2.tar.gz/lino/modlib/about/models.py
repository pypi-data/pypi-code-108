# Copyright 2012-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import re
from html import escape
import datetime

# from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from django.conf import settings


from lino.utils.report import EmptyTable
from lino.core.utils import get_models
from lino.core import constants

from lino.utils.code import codetime
from lino.utils.diag import analyzer
from etgen.html import E

from lino.api import rt, dd

from .choicelists import TimeZones, DateFormats


def dtfmt(dt):
    if isinstance(dt, float):
        # assert dt
        dt = datetime.datetime.fromtimestamp(dt)
        # raise ValueError("Expected float, go %r" % dt)
    return gettext("%(date)s at %(time)s") % dict(
        date=dd.fds(dt.date()),
        time=settings.SITE.strftime(dt.time()))


class About(EmptyTable):
    """
    Display information about this web site.  This defines the window
    which opens via the menu command :menuselection:`Site --> About`.
    """
    label = _("About")
    help_text = _("Show information about this site.")
    required_roles = set()
    hide_top_toolbar = True
    detail_layout = dd.DetailLayout("""
    about_html
    # server_status
    """, window_size=(60, 20))

    @dd.constant()
    def about_html(cls):

        body = []

        body.append(settings.SITE.welcome_html())

        if settings.SITE.languages:
            body.append(E.p(str(_("Languages")) + ": " + ', '.join([
                lng.django_code for lng in settings.SITE.languages])))

        # print "20121112 startup_time", settings.SITE.startup_time.date()
        # showing startup time here makes no sense as this is a constant text
        # body.append(E.p(
        #     gettext("Server uptime"), ' : ',
        #     E.b(dtfmt(settings.SITE.startup_time)),
        #     ' ({})'.format(settings.TIME_ZONE)))
        if settings.SITE.is_demo_site:
            body.append(E.p(gettext(_("This is a Lino demo site."))))
        if settings.SITE.the_demo_date:
            s = _("We are running with simulated date set to {0}.").format(
                dd.fdf(settings.SITE.the_demo_date))
            body.append(E.p(s))

        feats = settings.SITE.features.features
        body.append(E.h4(str(_("Available Features:"))))
        style = "border: 1px solid black; border-radius: 2px; padding: 5px;"

        f_table_head = []
        f_table_head.append(E.th(str(_("Feature")), style=style))
        f_table_head.append(E.th(str(_("Description")), style=style))
        f_table_head.append(E.th(str(_("Status")), style=style))
        thead = E.thead(E.tr(*f_table_head))
        trs = []

        for key in feats:
            row = E.tr(E.td(key, style=style), E.td(str(feats[key]['description']), style=style),
            E.td(str(_("Active")) if key in settings.SITE.features.active_features else str(_("Inactive")), style=style))
            trs.append(row)
        tbody = E.tbody(*trs)
        body.append(E.table(thead, tbody))

        body.append(E.p(str(_("Source timestamps:"))))
        items = []
        times = []
        packages = set(['django'])

        items.append(E.li(gettext("Server timestamp"), ' : ',
            E.b(dtfmt(settings.SITE.kernel.code_mtime))))

        for p in settings.SITE.installed_plugins:
            packages.add(p.app_name.split('.')[0])
        for src in packages:
            label = src
            value = codetime('%s.*' % src)
            if value is not None:
                times.append((label, value))

        times.sort(key=lambda x: x[1])
        for label, value in times:
            items.append(E.li(str(label), ' : ', E.b(dtfmt(value))))
        body.append(E.ul(*items))
        body.append(E.p("{} : {}".format(
            _("Complexity factors"),
            ', '.join(analyzer.get_complexity_factors(dd.today())))))
        return rt.html_text(E.div(*body))

    # @dd.displayfield(_("Server status"))
    # def server_status(cls, obj, ar):
    #     st = settings.SITE.startup_time
    #     return rt.html_text(
    #         E.p(_("Running since {} ({}) ").format(
    #             st, naturaltime(st))))
