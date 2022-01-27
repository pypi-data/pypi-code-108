# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import os
import jinja2

import platform
import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

from sympathy.utils import prim
from sympathy.platform import feature as feature_api
from sympathy.platform import os_support as oss
from .. import config
from .. import version
from .. import settings


def _abs_license_file(lice):
    # Make license paths absolute.
    lice = dict(lice)
    localfile = lice.get('file')
    if localfile:
        if not os.path.isabs(localfile):
            localfile = os.path.abspath(
                os.path.join(prim.sympathy_path(), localfile))
        if os.path.exists(localfile):
            lice['file'] = prim.localuri(
                os.path.abspath(
                    os.path.join(prim.sympathy_path(), localfile)))
        else:
            lice['file'] = None
    else:
        lice['file'] = None
    return lice


def _license_text():
    def entrypoint_license(lice, entrypoint):
        lice = dict(lice)
        lice['file'] = os.path.abspath(os.path.join(
            entrypoint.dist.location, entrypoint.module_name,
            lice['file']))
        return _abs_license_file(lice)

    with open(os.path.join(
            settings.instance()['resource_folder'],
            'third_party.html')) as f:
        licenses_template = f.read()

    env = dict(config.active())
    env['license'] = _abs_license_file(env['license'])
    third_party = {
        'licenses': [_abs_license_file(l)
                     for l in env['third_party']['licenses']]}
    env['third_party'] = third_party

    third_party_lookup = {lice["identifier"]:
                          {package["name"]: package
                           for package in lice['packages']}
                          for lice in third_party['licenses']}
    feature_licenses = []
    env['feature_licenses'] = feature_licenses
    for entrypoint in feature_api.available_features(load=False):
        feature = entrypoint.load()
        feature_licenses.append(
            entrypoint_license(feature.license_info(), entrypoint))

        feature_third_party = dict(feature.third_party_license_info())
        for lice in feature_third_party['licenses']:
            lookup_license = third_party_lookup.get(
                lice['identifier'], {})
            packages = []
            for package in lice['packages']:
                if package['name'] not in lookup_license:
                    packages.append(package)
            if packages:
                lice = dict(lice)
                lice['packages'] = packages
                third_party['licenses'].append(lice)

    return jinja2.Template(licenses_template).render(env)


class AboutWindow(QtWidgets.QDialog):
    """Docstring for AboutWindow"""

    def __init__(self, parent=None, flags=QtCore.Qt.Widget):
        super(AboutWindow, self).__init__(parent, flags)
        self.setWindowFlags(
            self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(version.application_name())
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.setFixedSize(800, 600)

        license_info = _abs_license_file(version.license_info())

        about = jinja2.Template('''
<br/>
&copy; 2011-2021 <a href={{appurl}}>{{appcopy}}</a>
All Rights Reserved.
This software is licensed under the
{% if license_link %}
<a href="{{license_link}}">{{license_name}}</a> license.
{% else %}
{{license_name}} license.
{% endif %}
<br/><br/>
Design and programming by:
Stefan Larsson, Alexander Busck,
Krister Johansson, Erik der Hagopian,
Greger Cronquist, Magnus Sand&eacute;n,
Daniel Hedendahl, Lia Silva-Lopez,
Andreas T&aring;gerud, Sara Gustafzelius,
Samuel Genheden,
Benedikt Ziegler, and Mathias Broxvall
<br/><br/>
Please report bugs to:
<a href=mailto:{{mailsupport}}>{{mailsupport}}</a>,
contributions can be sent to:
<a href=mailto:{{mailcontrib}}>{{mailcontrib}}</a>

<br/><br/>
{{appname}} ({{edition}}) version: {{version}}<br/>
<br/>
Python version: {{python_version}}<br/>
''').render(
    appurl=version.application_url(),
    appcopy=version.application_copyright(),
    license_name=license_info['name'],
    license_link=license_info['link'],
    license_file=license_info['file'],
    mailsupport=version.email_bugs(),
    mailcontrib=version.email_contribution(),
    appname=version.application_name(),
    version=version.version,
    edition=license_info['edition'],
    python_version=platform.python_version())

        self._label = QtWidgets.QLabel(about)
        self._label.setWordWrap(True)
        self._license_view = QtWidgets.QTextBrowser()
        self._license_view.setOpenExternalLinks(False)
        self._license_view.setOpenLinks(False)
        self._license_view.setMinimumHeight(200)
        self._license_view.setReadOnly(True)

        self._button_box = QtWidgets.QDialogButtonBox()
        ok_button = self._button_box.addButton(QtWidgets.QDialogButtonBox.Ok)
        ok_button.clicked.connect(self.accept)

        self._logo = QtWidgets.QLabel('Sympathy for Data')
        self._label_font = QtWidgets.QApplication.font()
        self._label.setFont(self._label_font)
        self._label_font.setPointSize(36)
        self._logo.setFont(self._label_font)
        layout.addWidget(self._logo)
        layout.addWidget(self._label)
        layout.addWidget(self._license_view)
        layout.addWidget(self._button_box)

        self._license_view.anchorClicked.connect(self._link_clicked)
        self._set_license_html(_license_text())

    def _set_license_html(self, html):
        vscrollbar = self._license_view.verticalScrollBar()
        vscroll = vscrollbar.value()
        textcursor = self._license_view.textCursor()
        cursor_start = textcursor.selectionStart()
        cursor_end = textcursor.selectionEnd()
        self._license_view.setHtml(html)
        textcursor = self._license_view.textCursor()
        textcursor.setPosition(cursor_start)
        textcursor.setPosition(cursor_end, QtGui.QTextCursor.KeepAnchor)
        self._license_view.setTextCursor(textcursor)
        vscrollbar.setValue(vscroll)

    def _link_clicked(self, url):
        # Ensure all links open in external application, for now.
        oss.open_url(url.toString())
