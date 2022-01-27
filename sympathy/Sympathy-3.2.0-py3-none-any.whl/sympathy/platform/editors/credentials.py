# This file is part of Sympathy for Data.
# Copyright (c) 2020 Combine Control Systems AB
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
import Qt.QtCore as QtCore
import Qt.QtWidgets as QtWidgets
import jinja2
import logging
import os
import queue
import shutil
import tempfile
import threading
import urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import ParseResult

from sympathy.platform import widget_library as sywidgets
from sympathy.platform.parameter_types import (
    Connection, Credentials, CredentialsMode)
from sympathy.platform import os_support as oss
from sympathy.utils import prim

credentials_logger = logging.getLogger('common.credentials')


def _web_engine_view(parent):
    # Unsupported by Qt.py.
    from PySide2.QtWebEngineWidgets import QWebEngineView
    return QWebEngineView(parent=parent)


def _web_engine_profile(storage_name, parent):
    # Unsupported by Qt.py.
    from PySide2.QtWebEngineWidgets import QWebEngineProfile
    return QWebEngineProfile(storage_name)


def _web_engine_page(profile, parent):
    # Unsupported by Qt.py.
    from PySide2.QtWebEngineWidgets import QWebEnginePage
    return QWebEnginePage(profile, parent)


class StackedWidget(QtWidgets.QStackedWidget):
    def sizeHint(self):
        return self.currentWidget().sizeHint()

    def minimumSizeHint(self):
        return self.currentWidget().minimumSizeHint()


class PasswordLineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setEchoMode(self.EchoMode.Password)


class LineValueMixin:
    def __init__(self, value=None, **kwargs):
        super().__init__(**kwargs)
        self.set_value(value)

    def get_value(self):
        return self.text()

    def set_value(self, value):
        self.setText(value)

    def clear(self):
        self.setText('')


class CredentialMixin(LineValueMixin):
    type = None

    def __init__(self, value=None, parent=None):
        super().__init__(parent=parent)

        self._reset = False
        if value is None:
            self.setPlaceholderText('Not set')
        elif value:
            self.set_value(value)

        self.textEdited.connect(self._handle_value_edited)

    def _handle_value_edited(self, value):
        if not self._reset:
            self.value_edited.emit(value)

    def clear(self):
        self.from_dict({self.type: ''})

    def to_dict(self):
        return {
            self.type: self.get_value(),
        }

    def from_dict(self, data):
        try:
            self._reset = True
            self.set_value(data[self.type])
        finally:
            self._reset = False


class ShowPasswordLineEdit(QtWidgets.QWidget):
    """
    Works as a QLineEdit for passwords with a button to show the text
    temporarily. The button state is cleared on setText for convenience since
    setText in all current uses means showing a new password. This could be
    made explicit if it causes problems.

    Implements the current required subset of QLineEdit interface. Add more
    operations when needed.
    """

    textEdited = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._show_widget = sywidgets.ShowButton()
        self._show_widget.setFocusPolicy(QtCore.Qt.NoFocus)
        self._password_widget = PasswordLineEdit()
        layout.addWidget(self._password_widget)
        layout.addWidget(self._show_widget)
        self.setLayout(layout)
        self._show_widget.toggled.connect(self._handle_show_widget_toggled)
        self._password_widget.textEdited.connect(self.textEdited)

    def _handle_show_widget_toggled(self, checked=False):
        if checked:
            self._password_widget.setEchoMode(
                self._password_widget.EchoMode.Normal)
        else:
            self._password_widget.setEchoMode(
                self._password_widget.EchoMode.Password)

    def text(self):
        return self._password_widget.text()

    def setText(self, value):
        self._show_widget.setChecked(False)
        return self._password_widget.setText(value)

    def get_value(self):
        return self.text()

    def set_value(self, value):
        self.setText(value)

    def setPlaceholderText(self, text):
        self._password_widget.setPlaceholderText(text)


class SecretWidget(CredentialMixin, ShowPasswordLineEdit):
    type = 'secret'
    value_edited = QtCore.Signal(str)

    def __init__(self, value='', parent=None):
        super().__init__(value=value, parent=parent)


class UsernameWidget(CredentialMixin, QtWidgets.QLineEdit):
    type = 'username'
    value_edited = QtCore.Signal(str)

    def __init__(self, value='', parent=None):
        super().__init__(value=value, parent=parent)


class PasswordWidget(CredentialMixin, ShowPasswordLineEdit):
    type = 'password'
    value_edited = QtCore.Signal(str)

    def __init__(self, value='', parent=None):
        super().__init__(value=value, parent=parent)


class ResourceEditWidget(LineValueMixin, QtWidgets.QLineEdit):
    pass


class ResourceWidget(LineValueMixin, sywidgets.ReadOnlyLineEdit):
    pass


class NullCredentialsWidget(QtWidgets.QWidget):
    def secrets(self):
        return {}


class DenyCredentialsWidget(NullCredentialsWidget):

    def __init__(self, resource, parent=None):
        super().__init__(parent=parent)
        layout = sywidgets.FormLayout()
        self.setLayout(layout)
        deny_label = QtWidgets.QLabel(
            'Credential requests are denied by current settings')
        self.setToolTip(
            'Set to Allow in preferences to use Credentials')
        layout.addRow(deny_label)

        self._resource_widget = ResourceWidget(resource)
        layout.addRow('Resource', self._resource_widget)

    def secrets(self):
        return {}

    def set_resource(self, resource):
        self._resource_widget.set_value(resource)


class EditCredentialWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        layout = sywidgets.FormLayout()
        self.setLayout(layout)
        self._resource_widget = ResourceWidget('')
        layout.addRow('Resource', self._resource_widget)
        hline = sywidgets.HLine()
        layout.addRow(hline)
        self._connection = None

    def connection(self):
        return self._connection

    def setup(self, connection, secrets):
        self.set_connection(connection)

    def set_connection(self, connection):
        self._connection = connection
        resource = ''
        if connection is not None:
            resource = connection.identifier()
        self._resource_widget.set_value(resource)

    def secrets(self):
        raise NotImplementedError

    def set_secrets(self, secrets):
        raise NotImplementedError


class EditSecretsWidget(EditCredentialWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._secret_widgets = {}

    def secrets(self):
        return {k: v.get_value() for k, v in
                self._secret_widgets.items()}

    def set_secrets(self, secrets):
        for k, widget in self._secret_widgets.items():
            widget.set_value(secrets.get(k, ''))

    def setup(self, connection, secrets):
        old = self._connection
        super().setup(connection, secrets)

        if old is not None:
            self._old_widgets = []
            for k, widget in self._secret_widgets.items():
                widget.deleteLater()
                self._old_widgets.append(widget)
                self.layout().removeRow(widget)
            self._secret_widgets.clear()

        if self._connection is not None:
            for k, v in secrets.items():
                widget = SecretWidget(v)
                self._secret_widgets[k] = widget
                self.layout().addRow(k, widget)


class EditLoginWidget(EditCredentialWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._password_widget = PasswordWidget('')
        self._username_widget = UsernameWidget('')
        layout = self.layout()
        layout.addRow('Username', self._username_widget)
        layout.addRow('Password', self._password_widget)

    def secrets(self):
        return {
            'username': self._username_widget.get_value(),
            'password': self._password_widget.get_value(),
        }

    def set_secrets(self, secrets):
        self._username_widget.set_value(secrets.get('username', ''))
        self._password_widget.set_value(secrets.get('password', ''))

    def setup(self, connection, secrets):
        super().setup(connection, secrets)
        self.set_secrets(secrets)


def url_query_to_dict(url: ParseResult) -> dict:
    return dict(urllib.parse.parse_qsl(url.query))


class AzureLoginRequestHandler(BaseHTTPRequestHandler):
    """
    Handles the response from an Azure browser login. The login response
    is sent as a GET request to the redirect URI.

    A successful login will contain `code` and an invalid one should contain
    `error`. `state` should be included in both cases.
    """
    _success_template = """<html>
    <body style="font-family:helvetica;">
    <div align="center">
    <h1><img src="application.png" width="100" height="100" alt="" /></h1>
    <h1 style="color: #31c331;">Login success</h1>
    <p style="font-size: 16px;" align="center">You can close this page and go back to Sympathy for Data.</p>
    </div>
    </body>
</html>
"""

    _error_template = """<html>
    <body style="font-family:helvetica;">
    <div align="center">
    <h1><img src="application.png" width="100" height="100" alt="" /></h1>
    <h1 style="color: #fb1c1c;">Login failure</h1>
    <p style="font-size: 20px;" align="center">Login failed due to an error: {{ error }}. Description: {{ error_description }}. Address: {{ error_uri }}.
    <br/>
    <p style="font-size: 16px;" align="center">You can close this page and go back to Sympathy for Data.</p>
    </div>
    </body>
</html>
"""

    _unknown_page = """<html>
    <body style="font-family:helvetica;">
    <div align="center">
    <h1><img src="application.png" width="100" height="100" alt="" /></h1>
    <h1 style="color: #fb1c1c;">Login failure</h1>
    <p style="font-size: 20px;" align="center">Login failed due to unhandled query, missing both code and error.</p>
    <br/>
    <p style="font-size: 16px;" align="center">You can close this page and go back to Sympathy for Data.</p>
    </div>
    </body>
</html>
"""

    # Share only explicit, safe resources.
    _icon_resources = {
        '/favicon.ico': ('image/x-icon', 'favicon.ico'),
        '/application.png': ('image/png', 'application.png'),
    }

    def _send_content(self, content_type, content):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        query = url_query_to_dict(parsed)
        if parsed.path == '/':
            return self._get_query(query)
        elif parsed.path in self._icon_resources:
            content_type, iconname = self._icon_resources[parsed.path]
            filename = os.path.join(prim.icons_path(), iconname)
            with open(filename, 'rb') as f:
                self._send_content(content_type, f.read())

    def _get_query(self, query):
        code = query.get('code')
        error = query.get('error')
        page = self._unknown_page
        self.server.set_login(query)

        if code or error:
            if code:
                template = self._success_template
            elif error:
                template = self._error_template

            env = jinja2.Environment()
            page = env.from_string(template).render(query)

        self._send_content('text/html', page.encode("utf-8"))

    def log_message(self, format, *args):
        credentials_logger.debug(format, *args)


class AzureLoginServer(ThreadingHTTPServer):
    """
    Simple HTTP server for handling a single login (GET request to
    the redirect URI). The `code` is not sensitive so HTTP should be
    sufficient.

    Handles requests using AzureLoginRequestHandler.
    """

    daemon_threads = True
    block_on_close = False

    def __init__(self, server_address, queue):
        super().__init__(server_address, AzureLoginRequestHandler)
        self._queue = queue

    def set_login(self, login):
        self._queue.put_nowait(login)

    def handle_timeout(self):
        raise TimeoutError('No login before timeout.')


class QueueWaiter(QtCore.QObject):
    """
    Poll queue and put results into the event loop.
    """
    result = QtCore.Signal(object)

    def __init__(self, queue, interval, parent=None):
        super().__init__(parent=parent)
        self._queue = queue
        self._timer = QtCore.QTimer()
        self._timer.setInterval(interval)
        self._timer.timeout.connect(self._check_queue)

    def _check_queue(self):
        try:
            while True:
                self.result.emit(self._queue.get_nowait())
        except queue.Empty:
            pass

    def start(self):
        self._timer.start()

    def stop(self):
        self._timer.stop()


class AzureLoginServerThread(threading.Thread):
    """
    AzureLoginServer waiting for a single login in a thread.
    Eventual result will be available in `queue`.
    """
    def __init__(self, queue, **kwargs):
        self._queue = queue
        self._port = None
        self._port_ready = threading.Event()
        super().__init__(daemon=True, kwargs=kwargs)

    def run(self):
        try:
            self._run()
        finally:
            self._port_ready.set()

    def _run(self):
        try:
            server = AzureLoginServer(('127.0.0.1', 0), self._queue)
            port = server.server_address[1]
            self._port = port
            self._port_ready.set()
            server.serve_forever()
        finally:
            self.server_close()

    def stop(self):
        super().shutdown()
        self.join(0)
        if self.is_alive():
            self._stop_server()
            self.join()

    def port(self):
        if self.is_alive():
            self._port_ready.wait()
        return self._port


class AzureLoginServerWaiter(QtCore.QObject):

    result = QtCore.Signal(object)

    def __init__(self, interval=100, parent=None):
        super().__init__(parent=parent)
        self._queue = queue.Queue()
        self._waiter = QueueWaiter(self._queue, interval, parent=parent)
        self._thread = AzureLoginServerThread(self._queue)
        self._waiter.result.connect(self.result)

    def start(self):
        self._waiter.start()
        self._thread.start()

    def stop(self):
        self._waiter.stop()
        self._thread.stop()

    def port(self):
        return self._thread.port()


_azure_login_server = None


def azure_login_server():
    global _azure_login_server
    if _azure_login_server is None:
        _azure_login_server = AzureLoginServerWaiter()
        _azure_login_server.start()
    return _azure_login_server


class AzureLoginWidget(QtWidgets.QWidget):
    finished = QtCore.Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = QtWidgets.QVBoxLayout()
        self._redirect_url = None
        view = _web_engine_view(parent=self)
        # Use separate cache folder for each login.
        # This helps with changing it, otherwise it will re-use the existing.
        # Could also help with issues from multiple WebEngines using the same
        # folder.
        profile = view.page().profile()
        profile.setHttpCacheType(profile.NoCache)
        profile.setPersistentCookiesPolicy(profile.NoPersistentCookies)
        temp_root = os.path.join(tempfile.gettempdir(), 'Sympathy', 'Azure')
        os.makedirs(temp_root, exist_ok=True)
        self._temp = tempfile.mkdtemp(dir=temp_root)
        profile.setPersistentStoragePath(self._temp)
        self._view = view

        layout.addWidget(view)
        self.setLayout(layout)
        self._view_running = False
        view.urlChanged.connect(self._view_url_changed)
        view.loadStarted.connect(self._view_load_started)
        self._result = None
        policy = self.sizePolicy()
        policy.setHorizontalPolicy(QtWidgets.QSizePolicy.Expanding)
        policy.setVerticalPolicy(QtWidgets.QSizePolicy.Expanding)
        self.setSizePolicy(policy)

    def _view_url_changed(self, url):
        url = urllib.parse.urlparse(url.toString())
        if self.same_resource(url, self._redirect_url) and self._view_running:
            self._result = url_query_to_dict(url)
            self._view_done()
            self.finished.emit(self._result)

    def _view_load_started(self):
        pass

    def _view_done(self):
        if self._view_running:
            self._view_running = False
            self._view.urlChanged.disconnect(self._view_url_changed)
            self._view.loadStarted.disconnect(self._view_load_started)
            self._view.stop()

    def setup(self, auth_url, redirect_url):
        self._result = None
        self._view_running = True
        self._redirect_url = urllib.parse.urlparse(redirect_url)
        self._view.load(auth_url)

    def cleanup(self):
        if self._temp:
            shutil.rmtree(self._temp, ignore_errors=True)
            self._temp = None

    def result(self):
        return self._result

    @staticmethod
    def same_resource(url1: ParseResult, url2: ParseResult) -> bool:
        def resource(url):
            return (url.scheme, url.netloc, url.port, url.path or '/')

        return resource(url1) == resource(url2)

    def minimumSizeHint(self):
        return QtCore.QSize(600, 600)


class ExternalBrowserWidget(QtWidgets.QLabel):
    finished = QtCore.Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent=None)
        self._state = None
        self._auth_url = None
        self.linkActivated.connect(self._handle_link_activated)

    def setup(self, auth_url, state):
        self._state = state
        self._auth_url = auth_url
        if auth_url:
            parsed = urllib.parse.urlsplit(auth_url)
            query = url_query_to_dict(parsed)
            query['prompt'] = 'login'
            parsed = parsed._replace(query=urllib.parse.urlencode(query))
            auth_url = urllib.parse.urlunsplit(parsed)

            self.setText(
                '<html><body>'
                f'<h1>Click to login in an <a href="{auth_url}">'
                'external browser</a></h1>'
                '<p>The link can also be copied into an existing browser '
                'using the right-click context menu.</p>'
                '</body></html>')
        else:
            self.setText(
                '<html><body>'
                '<h1>Failed to Login\n</h1>'
                '<p>Could not create link to open in an external browser.</p>'
                '</body></html>'
                )

    def cleanup(self):
        pass

    def _handle_login_result(self, value):
        if value:
            if 'state' in value and self._state == value.get('state'):
                self.finished.emit(value)
            else:
                self.setText(
                    '<html><body>'
                    'Failed to Login'
                    '</body></html>'
                )

    def _handle_link_activated(self, link):
        oss.open_url(link)

    def result(self):
        return self._result


class EditAzureWidget(EditCredentialWidget):

    finished = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._choice = QtWidgets.QComboBox()
        self._choice.addItems(['Internal browser', 'External browser'])
        self._internal_widget = AzureLoginWidget(parent=self)
        self._external_widget = ExternalBrowserWidget(parent=self)
        self._login_widget = StackedWidget(parent=self)
        self._login_widget.addWidget(self._internal_widget)
        self._login_widget.addWidget(self._external_widget)
        self._secrets = {'state': None, 'code': None}
        layout = self.layout()
        layout.insertRow(0, 'Login', self._choice)
        layout.addRow(self._login_widget)
        self._external_widget.finished.connect(self._handle_finished)
        self._internal_widget.finished.connect(self._handle_finished)
        self._choice.currentIndexChanged.connect(self._choice_index_changed)

    def secrets(self):
        return self._secrets

    def set_secrets(self, secrets):
        old_code = self._secrets.get('code')
        if not old_code:
            self._secrets = secrets

    def setup(self, connection, secrets):
        super().setup(connection, secrets)
        auth = secrets['auth']
        self._secrets = {'state': auth['state'], 'code': None}
        self._internal_widget.setup(auth['auth_url'], auth['redirect_url'])
        self._external_widget.setup(auth['auth_url'], auth['state'])

    def cleanup(self):
        self._internal_widget.cleanup()
        self._external_widget.cleanup()

    def _choice_index_changed(self, index):
        self._login_widget.setCurrentIndex(index)
        widget = self._login_widget.currentWidget()
        widget.adjustSize()
        self.adjustSize()
        self.parent().adjustSize()

    def _handle_finished(self, value):
        code = value.get('code')
        if code:
            self._secrets['code'] = code
            self._secrets['state'] = value.get('state')

        self.finished.emit()


class EditCredentialsDialog(QtWidgets.QDialog):
    _title = 'Unknown'

    def __init__(self, connection, secrets, parent=None):
        super().__init__(parent=parent)
        layout = QtWidgets.QVBoxLayout()
        self._connection = connection
        self._secrets = secrets
        self.setLayout(layout)
        self.setWindowTitle(self._title)
        self._edit_widget = self._editor_cls()
        self._setup_editor(connection, secrets)
        layout.addWidget(self._edit_widget)
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok |
            QtWidgets.QDialogButtonBox.Cancel)
        self._button_box = button_box
        self._add_stretch()

        layout.addWidget(button_box)

        policy = QtWidgets.QSizePolicy()
        policy.setHorizontalStretch(1)
        policy.setHorizontalPolicy(QtWidgets.QSizePolicy.Preferred)
        policy.setVerticalPolicy(QtWidgets.QSizePolicy.Maximum)
        self.setSizePolicy(policy)

        self._ok_button = button_box.button(
            QtWidgets.QDialogButtonBox.Ok)
        self._cancel_button = button_box.button(
            QtWidgets.QDialogButtonBox.Cancel)

        self._ok_button.clicked.connect(self.accept)
        self._cancel_button.clicked.connect(self.reject)

        self.setMinimumWidth(400)

    def _add_stretch(self):
        pass

    def _editor_cls(self) -> EditCredentialWidget:
        raise NotImplementedError

    def _setup_editor(self, connection, secrets):
        self._edit_widget.setup(connection, secrets)

    def secrets(self):
        return self._edit_widget.secrets()


class EditSecretsDialog(EditCredentialsDialog):
    _title = 'Edit Secrets'

    def __init__(self, connection, secrets, parent=None):
        super().__init__(connection, secrets, parent=parent)

    def _add_stretch(self):
        self.layout().addStretch()

    def _editor_cls(self):
        return EditSecretsWidget(parent=self)


class EditLoginDialog(EditSecretsDialog):
    _title = 'Edit Login'

    def _editor_cls(self):
        return EditLoginWidget(parent=self)


class EditAzureDialog(EditCredentialsDialog):
    _title = 'Edit Azure Login'

    def __init__(self, connection, secrets, parent=None):
        super().__init__(connection, secrets, parent=parent)
        self._edit_widget.finished.connect(self.accept)
        self.finished.connect(self._handle_finished)
        self._ok_button.setVisible(False)
        azure_login_server().result.connect(self._handle_server_result)

    def _editor_cls(self):
        return EditAzureWidget(parent=self)

    def _handle_finished(self, result):
        self._edit_widget.cleanup()

    def _handle_server_result(self, result):
        result_state = result.get('state')
        secrets_state = self._secrets.get('auth', {}).get('state')
        if result_state == secrets_state:
            self._edit_widget.set_secrets(result)
            if self._edit_widget.secrets().get('code'):
                self._handle_finished(result)
                self.accept()


def add_form_row(layout, label, widget):
    label_widget = QtWidgets.QLabel(label)
    hlayout = QtWidgets.QHBoxLayout()
    hlayout.addWidget(label_widget)
    hlayout.addWidget(widget)
    hlayout.setStretchFactor(widget, 1)
    layout.addLayout(hlayout)
    return hlayout, label


def _form_layout():
    layout = QtWidgets.QVBoxLayout()
    return layout


def create_button_box():
    box = QtWidgets.QDialogButtonBox()
    return box


def standard_button_box(dialog):
    box = create_button_box()
    box.addButton(QtWidgets.QDialogButtonBox.Ok)
    box.addButton(QtWidgets.QDialogButtonBox.Cancel)
    box.accepted.connect(dialog.accept)
    box.rejected.connect(dialog.reject)
    return box


class ParameterCredentialWidget(QtWidgets.QWidget):
    changed = QtCore.Signal()
    request_edit_dialog = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def load(self, credentials: Credentials):
        raise NotImplementedError()

    def credential(self):
        raise NotImplementedError()

    def action(self) -> QtWidgets.QAction:
        raise NotImplementedError()

    def mode(self):
        raise NotImplementedError()

    def create_edit_dialog(self, connection: Connection, secrets: dict
                           ) -> QtWidgets.QWidget:
        raise NotImplementedError()

    def can_edit(self):
        return False

    def set_can_edit(self, value):
        pass


class NoParameterCredentialWidget(ParameterCredentialWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._action = sywidgets.create_action(
            text='No credentials',
            icon_name='actions/key-slash.svg',
            tooltip_text='Use resource as is, with no credentials')

    def load(self, credentials: Credentials):
        pass

    def credential(self):
        return Credentials()

    def action(self) -> QtWidgets.QAction:
        return self._action

    def mode(self):
        return None

    def create_edit_dialog(self, connection, secrets):
        raise NotImplementedError()


class LoginParameterCredentialWidget(ParameterCredentialWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = sywidgets.FormLayout()
        layout.setContentsMargins(0, 0, 0, 5)
        layout.setVerticalSpacing(5)
        self.setLayout(layout)
        self._name_widget = QtWidgets.QLineEdit()
        self._name_widget.setPlaceholderText('Optional resource name')
        login_name_tooltip = (
            'Optional resource name used instead of the resource itself '
            'for storing and loading login credentials.\n\n'
            'It can be used to share the same login for multiple resources '
            'or to allow different logins.\nFor example, if the resource '
            'is http://example.com/path it might be useful to set the name '
            'to\nhttp://example.com and use that in each node where you '
            'want to access http://example.com.')
        self._name_widget.setToolTip(login_name_tooltip)
        layout.addRow('Name', self._name_widget)
        login_label = layout.labelForField(self._name_widget)
        login_label.setToolTip(login_name_tooltip)
        button_box = create_button_box()
        self._edit_button = button_box.addButton(
            'Edit Login', button_box.ActionRole)
        self._edit_button.setToolTip(
            'Edit the credentials used for this resource '
            '(username and password).\n'
            'Note that logins are shared between all nodes that use '
            'login credentials.\n\n'
            'Credentials are only stored on your system and are not part of '
            'the node\'s configuration.')
        layout.addRow(None, button_box)
        self.set_can_edit(False)

        self._name_widget.textChanged.connect(self.changed)

        self._edit_button.clicked.connect(
            self._handle_edit_button_clicked)

        self._action = sywidgets.create_action(
            text='Login credentials',
            icon_name='actions/user-key-4.svg',
            tooltip_text='Use resource with login credentials')

    def mode(self):
        return CredentialsMode.login

    def action(self):
        return self._action

    def load(self, credentials: Credentials):
        self._name_widget.setText(credentials.name)

    def credential(self):
        return Credentials(
            mode=CredentialsMode.login,
            name=self._name_widget.text())

    def create_edit_dialog(self, connection, secrets, parent=None
                           ) -> QtWidgets.QWidget:
        return EditLoginDialog(connection, secrets, parent=parent)

    def _handle_edit_button_clicked(self, checked):
        self.request_edit_dialog.emit()


class SecretsParameterCredentialWidget(ParameterCredentialWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = sywidgets.FormLayout()
        layout.setContentsMargins(0, 0, 0, 5)
        layout.setVerticalSpacing(5)

        self.setLayout(layout)
        button_box = create_button_box()
        self._edit_button = button_box.addButton(
            'Edit Secrets', button_box.ActionRole)
        self._edit_button.setToolTip(
            'Edit the secret credentials used for this resource. '
            'Secrets are variables in the resource, '
            'written inside angular brackets.\nFor example, username and '
            'password in "http://<username>:<password>@example.com".\nNote '
            'that secrets are shared between all nodes that use secret '
            'credentials.\n\n'
            'Credentials are only stored on your system and are not part of '
            'the node\'s configuration.')

        self.set_can_edit(False)
        layout.addRow(button_box)
        self._edit_button.clicked.connect(
            self._handle_edit_button_clicked)

        self._action = sywidgets.create_action(
            text='Secret credentials',
            icon_name='actions/mask-key-3.svg',
            tooltip_text='Use resource with secret credentials')

    def action(self):
        return self._action

    def mode(self):
        return CredentialsMode.secrets

    def load(self, credentials: Credentials):
        pass

    def credential(self):
        return Credentials(
            mode=CredentialsMode.secrets)

    def create_edit_dialog(self, connection, secrets, parent=None):
        return EditSecretsDialog(connection, secrets, parent=parent)

    def _handle_edit_button_clicked(self, checked):
        self.request_edit_dialog.emit()

    def can_edit(self):
        return self._can_edit

    def set_can_edit(self, value):
        self._can_edit = value
        self._edit_button.setEnabled(value)
