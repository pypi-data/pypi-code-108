# Copyright 2014-2015 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Run an SMTP daemon process.

See :doc:`/plugins/smtpd`.

.. autosummary::
   :toctree:

   signals

"""


from lino.api import ad, _


class Plugin(ad.Plugin):
    "See :doc:`/dev/plugins`."

    verbose_name = _("Mail server")
