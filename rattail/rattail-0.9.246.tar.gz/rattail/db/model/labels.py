# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2022 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Data Models for Label Printing
"""

from __future__ import unicode_literals, absolute_import

import warnings

import six
import sqlalchemy as sa
from sqlalchemy.orm import object_session

from .core import Base, uuid_column
from rattail.util import load_object


@six.python_2_unicode_compatible
class LabelProfile(Base):
    """
    Represents a collection of settings for product label printing.
    """
    __tablename__ = 'label_profile'
    __versioned__ = {}

    uuid = uuid_column()

    ordinal = sa.Column(sa.Integer(), nullable=True, doc="""
    Preference ordinal number for the profile.  Profiles are typically
    sorted by this number, which means the lower the number the higher
    the preference.
    """)

    code = sa.Column(sa.String(length=30), nullable=True, doc="""
    Supposedly unique "code" for the label profile.  May be useful for
    identification of a common label type across nodes, for instance.
    """)

    description = sa.Column(sa.String(length=50), nullable=True, doc="""
    Description for the profile, to be displayed to the user.
    """)

    printer_spec = sa.Column(sa.String(length=255), nullable=True, doc="""
    Factory spec for the label printer.  This normally references some
    subclass of :class:`rattail.labels.LabelPrinter`.
    """)

    formatter_spec = sa.Column(sa.String(length=255), nullable=True, doc="""
    Factory spec for the label formatter.  This normally references some
    subclass of :class:`rattail.labels.LabelFormatter`.
    """)

    format = sa.Column(sa.Text(), nullable=True, doc="""
    Formatting template.  This is a string containing a template of
    raw printer commands, suitable for printing a single label record.

    This value is assigned to the label formatter, which uses it to
    render the final command string when printing occurs.  For more
    info see :attr:`rattail.labels.CommandFormatter.template`.
    """)

    # TODO: this should have default=True, or something?
    visible = sa.Column(sa.Boolean(), nullable=True, doc="""
    Visibility flag; set this to false to hide the profile from users.
    """)

    sync_me = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating whether this label profile should be synced across "all"
    other Rattail systems across the organization.
    """)

    def __str__(self):
        return str(self.description or '')

    def get_formatter(self, config): # pragma: no cover
        warnings.warn("method is deprecated, please use "
                      "LabelHandler.get_formatter() method instead",
                      DeprecationWarning)

        app = config.get_app()
        label_handler = app.get_label_handler()
        return label_handler.get_formatter(self, ignore_errors=True)

    def get_printer(self, config): # pragma: no cover
        warnings.warn("method is deprecated, please use "
                      "LabelHandler.get_printer() method instead",
                      DeprecationWarning)

        app = config.get_app()
        label_handler = app.get_label_handler()
        return label_handler.get_printer(self, ignore_errors=True)

    def get_printer_setting(self, name): # pragma: no cover
        warnings.warn("method is deprecated, please use "
                      "LabelHandler.get_printer_setting() method instead",
                      DeprecationWarning)

        from rattail.db.api import get_setting
        if self.uuid is None:
            return None
        session = object_session(self)
        name = 'labels.{0}.printer.{1}'.format(self.uuid, name)
        return get_setting(session, name)

    def save_printer_setting(self, name, value): # pragma: no cover
        warnings.warn("method is deprecated, please use "
                      "LabelHandler.save_printer_setting() method instead",
                      DeprecationWarning)

        from rattail.db.api import save_setting
        session = object_session(self)
        if self.uuid is None:
            session.flush()
        name = 'labels.{0}.printer.{1}'.format(self.uuid, name)
        save_setting(session, name, value)
