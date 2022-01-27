# This file is part of Sympathy for Data.
# Copyright (c) 2019 Combine Control Systems AB
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
import Qt.QtWidgets as QtWidgets
import Qt.QtCore as QtCore
import re
import json
import requests
from sympathy.utils import log
import sympathy.app.settings
import sympathy.app.version
import sympathy.app.user_statistics
import sympathy.app.package
import sympathy.app.widgets.settings_widgets
import sympathy.platform.widget_library as sywidgets
from sympathy.platform.hooks import request_http

core_logger = log.get_logger('core')


def _info_form_layout():
    layout = QtWidgets.QFormLayout()
    layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
    layout.setFormAlignment(QtCore.Qt.AlignLeft)
    layout.setLabelAlignment(QtCore.Qt.AlignVCenter)
    layout.setVerticalSpacing(15)
    return layout


class IssueMessage(QtWidgets.QWidget):

    _basic_email_re = re.compile('^[^@]+@[^@]+$')
    valid_changed = QtCore.Signal()
    show_data = QtCore.Signal()

    def __init__(self, subject=None, details=None, generated=False,
                 parent=None):
        super().__init__(parent=parent)

        layout = _info_form_layout()
        subject = subject or ''
        details = details or ''

        self._email = sympathy.app.widgets.settings_widgets.EmailWidget()
        self._subject = QtWidgets.QLineEdit()
        self._subject.setText(subject)
        subject_help = 'Enter issue subject'
        self._subject.setPlaceholderText(subject_help)
        self._subject.setToolTip(subject_help)
        self._details = QtWidgets.QTextEdit()
        self._details.setPlainText(details)
        self._details.setAcceptRichText(False)
        self._status_label = sywidgets.ClickableHtmlLabel()
        self._status_label.setToolTip(
            'Link to show the full data. Data included can be configured '
            'in Preferences: Privacy.\n'
            'Also displays the status: what needs to be changed before '
            'sending.')
        self._status = ''

        details_help = """Enter issue description.
- Steps to reproduce.
- Expected behavior compared to actual."""

        self._details.setToolTip(details_help)
        self._details.setPlaceholderText(details_help)

        policy = self._details.sizePolicy()
        policy.setVerticalStretch(1)
        self._details.setSizePolicy(policy)

        details_layout = QtWidgets.QVBoxLayout()
        details_info = QtWidgets.QLabel(
            'Please check that no sensitive information is included')
        details_info.setWordWrap(True)
        details_layout.addWidget(self._details)
        details_layout.addWidget(details_info)
        top, left, right, bot = details_layout.getContentsMargins()
        details_layout.setContentsMargins(top, 0, 0, bot)

        layout.addRow('Sender', self._email)
        layout.addRow('Subject', self._subject)
        layout.addRow('Details', details_layout)

        layout.addRow(self._status_label)

        self._update_status()

        self._email.textChanged.connect(self._handle_lineedit_changed)
        self._subject.textChanged.connect(self._handle_lineedit_changed)
        self._details.textChanged.connect(self._update_status)
        self._status_label.linkActivated.connect(
            self._handle_status_label_activated)

        self.setLayout(layout)

    def to_dict(self):
        return {
            'email': self._email.text().strip(),
            'subject': self._subject.text().strip(),
            'details': self._details.toPlainText()
        }

    def save(self):
        self._email.save()

    def valid(self):
        return not bool(self._status)

    def _set_status_text(self, status_text):
        self._status = status_text
        if status_text:
            status_text = f'{status_text}.'
        html = (f'<html><body>Click to show the '
                f'<a href="#show-data">full data</a>. '
                f'{status_text}'
                f'</body></html>')

        self._status_label.setText(html)
        self.valid_changed.emit()

    def _update_status(self):
        email_text = self._email.text().strip()
        status_text = ''

        email_len = len(email_text)

        if not self._basic_email_re.match(email_text):
            status_text = 'Email is invalid'
        elif email_len > 255:
            status_text = f'Email is too long: {email_len}/255'
        else:
            subject_len = len(self._subject.text().strip())
            if not subject_len:
                status_text = 'Subject is empty'
            elif subject_len > 255:
                status_text = f'Subject is too long: {subject_len}/255'
            else:
                details_len = self._details.document().characterCount() - 1
                if not details_len:
                    status_text = 'Details are empty'
                elif details_len > 2000:
                    status_text = f'Details are too long: {details_len}/2000'

        self._set_status_text(status_text)

    def _handle_lineedit_changed(self, text):
        self._update_status()

    def _handle_status_label_activated(self, link):
        if link == '#show-data':
            self.show_data.emit()


class SenderThread(QtCore.QThread):
    succeeded = QtCore.Signal(bool)

    def __init__(self, url, headers, data, timeout, parent=None):
        self._url = url
        self._headers = headers
        self._data = data
        self._timeout = timeout
        super().__init__(parent=parent)

    def run(self):
        try:
            r = request_http.value.post(
                url=self._url,
                data=json.dumps(self._data),
                headers=self._headers,
                timeout=self._timeout)

            # Accepted means no mail sent (due to limits).
            self.succeeded.emit(r.status_code in [
                requests.codes.ok, requests.codes.accepted])
        except Exception as e:
            core_logger.info(
                'Failed reporting issue to %s.: %s', self._url, e)

            self.succeeded.emit(False)


class IssueReportSender(QtWidgets.QDialog):
    finished = QtCore.Signal()

    def __init__(self, subject=None, details=None, generated=False,
                 parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle('Report issue')
        self.setMinimumWidth(600)
        layout = QtWidgets.QVBoxLayout()
        self._issue = IssueMessage(
            subject=subject, details=details, generated=generated)
        buttons = QtWidgets.QDialogButtonBox()
        layout.addWidget(self._issue)
        layout.addWidget(buttons)

        self._send = QtWidgets.QPushButton('Send')
        self._sending = False
        buttons.addButton(self._send,
                          QtWidgets.QDialogButtonBox.ActionRole)
        cancel = buttons.addButton(QtWidgets.QDialogButtonBox.Cancel)
        self._enable_send()

        self._issue.valid_changed.connect(self._enable_send)
        self._issue.show_data.connect(self._show_data_dialog)
        self._send.clicked.connect(self._send_issue_report)
        cancel.clicked.connect(self.reject)

        self.setLayout(layout)
        self.save()

    def _issue_dict(self):
        return {'issue': self._issue.to_dict()}

    def save(self):
        self._data = self._issue_dict()

    def _enable_send(self):
        if not self._sending:
            self._send.setEnabled(self._issue.valid())

    def _show_data_dialog(self):

        data = sympathy.app.package.Collect.to_dict_from_settings()
        data = sympathy.app.package.Collect.pretty_dict(data)
        data.update(self._issue_dict())
        dialog = sympathy.app.package.JsonDialog(data, parent=self)
        dialog.setWindowTitle('Showing full data')
        dialog.exec_()

    def _send_issue_report(self):
        def build_data(data, issues):
            res = dict(data)
            res.update(issues)
            python_dict = data['python']
            python_packages_dict = data['python_packages']

            system_dict = data['system']
            res['python_hash'] = sympathy.app.user_statistics.basic_hash(
                python_dict)
            res['python_packages_hash'] = (
                sympathy.app.user_statistics.basic_hash(
                    python_packages_dict))
            res['system_hash'] = sympathy.app.user_statistics.basic_hash(
                system_dict)
            return res

        self._send.setText('Sending...')
        self._send.setEnabled(False)
        self._sending = True

        data = build_data(
            sympathy.app.package.Collect.to_dict_from_settings(),
            self._issue_dict())

        # Expected by server, modify is no longer possible => False.
        data['issue_modified'] = False
        data['python_modified'] = False
        data['system_modified'] = False

        self._sender = SenderThread(
            f'{sympathy.app.user_statistics.api_url()}/issue/',
            headers=sympathy.app.user_statistics.api_headers(),
            data=data,
            timeout=2.0)

        self._sender.finished.connect(self._sender_finished)
        self._sender.succeeded.connect(self._sender_succeeded)
        self._sender.start()

    def _sender_succeeded(self, ok):
        self._sending = False
        if ok:
            self._issue.save()
            self.accept()
        else:
            self._send.setText('Failed, retry sending?')
            self._enable_send()

    def _sender_finished(self):
        self._sending = False
        self._sender.wait()
        self._sender = None
