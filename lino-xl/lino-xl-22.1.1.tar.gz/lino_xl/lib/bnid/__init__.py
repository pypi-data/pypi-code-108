# -*- coding: UTF-8 -*-
# Copyright 2012-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""

Read Bangladeshi national ID (NID) and/or birth certificate information and
store that data in the database.

TODO: make bnid talk to https://porichoy.gov.bd/

"""

from os.path import join
from lino.api import ad, _
from lino.utils import Cycler


class Plugin(ad.Plugin):
    """The :class:`lino.core.Plugin` for this plugin.

    .. attribute:: holder_model

        The one and only model on this site which implements
        :class:`BnIdCardHolder`.

        This is available only after site startup.

    .. attribute:: data_collector_dir

        When this is a non-empty string containing a directory name on the
        server, then Lino writes the raw data of every eid card into a
        text file in this directory.

    .. attribute:: read_only_simulate

        Whether to just simulate.

    """

    # site_js_snippets = ['bnid/eidreader.js']
    media_name = 'eidreader'
    data_collector_dir = None
    data_cache_dir = None
    eidreader_timeout = 15
    read_only_simulate = False

    simulate_eidreader_path = None
    """
    Path for eidreader simulation data.

    If given, this should be the name of a directory containing files with
    eidreader data to be used for simulation.

    """

    urlhandler_prefix = 'bnid://'
    """
    Set this to a string to be passed by the
    :func:`bnid_card_processor` Javascript function to the URL
    protocol handler responsible for running eidreader.

    Default value is ``'bid://'`` which should work in a standard
    usage.

    You can tell Lino to use another URL protocol than ``bnid`` by
    saying::

       SITE.plugins.bnid.urlhandler_prefix = 'mybnid://'

    You can disable eidreader functionality by saying::

       SITE.plugins.bnid.urlhandler_prefix = None

    """

    preprocessor_delay = 0
    """

    Time (in milliseconds) Lino should wait between opening the eidreader URL and
    sending the actions' AJAX request.

    For example on an nginx server with only one worker process, you can set
    this to make sure that the client machine has read the card data and sent it
    to the server *before* you ask the server to process that data::

        preprocessor_delay = 3000

    """

    def on_site_startup(self, kernel):

        from lino_xl.lib.bnid.mixins import BnIdCardHolder
        from lino.core.utils import models_by_base

        super(Plugin, self).on_site_startup(kernel)

        if self.data_cache_dir is None:
            self.data_cache_dir = self.site.cache_dir.child('media').child('cache').child('bnid')
            # self.data_cache_dir = join(
            #     self.site.cache_dir, 'media', 'bnidtmp')
        self.site.makedirs_if_missing(self.data_cache_dir)

        cmc = list(models_by_base(BnIdCardHolder, toplevel_only=True))
        if len(cmc) > 1:
            msg = "There must be exactly one BnIdCardHolder model " \
                  "in your Site! You have {}. ".format(cmc)
            raise Exception(msg)
        if len(cmc) == 0:
            self.site.logger.warning(
                "You have lino_xl.lib.bnid installed, "
                "but there is no implementation of BnIdCardHolder.")
            return
        self.holder_model = cmc[0]
        if self.urlhandler_prefix is not None:
            if not self.urlhandler_prefix.endswith("://"):
                msg = "Invalid urlhandler_prefix {} (must end with '://')"
                raise Exception(msg.format(self.urlhandler_prefix))

        if self.simulate_eidreader_path is not None:
            self.SIMULATION_FILES = Cycler(self.simulate_eidreader_path.listdir())

        return

    def unused_get_body_lines(self, site, request):
        if not site.use_java:
            return
        if self.url_prefix:
            return
        # p = self.build_media_url('EIDReader.jar')
        # p = self.build_media_url('eidreader.jnlp')
        p = self.build_lib_url()
        p = request.build_absolute_uri(p)
        yield '<applet name="EIDReader" code="src.eidreader.EIDReader.class"'
        # yield '        archive="%s"' % p
        yield '        codebase="%s">' % p
        # seems that you may not use another size than
        # yield '        width="0" height="0">'
        # ~ yield '<param name="separate_jvm" value="true">' # 20130913
        yield '<param name="permissions" value="all-permissions">'
        # yield '<param name="jnlp_href" value="%s">' % p
        yield '<param name="jnlp_href" value="eidreader.jnlp">'
        yield '</applet>'

    def get_patterns(self):
        # from django.conf.urls import url
        from django.urls import re_path as url
        from . import views
        urls = [ url('^eid/(?P<uuid>.+)', views.EidStore.as_view()) ]
        return urls
