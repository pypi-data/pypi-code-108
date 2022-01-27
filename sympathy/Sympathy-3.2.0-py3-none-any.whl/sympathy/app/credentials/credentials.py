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
import dataclasses
import uuid
import contextlib
import json
from typing import Tuple, List, Optional
from Qt import QtCore, QtWidgets, QtGui
from . import keyring
from . azure.interfaces import AzureClient
from . azure.client import PublicAuthCodeClient
from . azure import token_cache as azure_token_cache
from .. import settings
from .. import messages
from .. widgets import settings_widgets as setwidgets
from .. interfaces.messages_window import MessageItemRoles as MsgRoles
from .. interfaces.messages_window import DetailsWidget
from .. interfaces.preferences import PreferenceSectionWidget
from ... platform import plugins
from ... platform import widget_library as sywidgets
from ... platform.editors import credentials as editor_credentials
from ... platform import exceptions
from ... platform.parameter_types import Connection
from ... platform import parameter_types
from ... utils import credentials as utils_credentials
from ... utils import log


core_logger = log.get_logger('core')


class Secret:
    def __init__(self, secret: str, in_sync: bool):
        self._secret = secret
        self._in_sync = False

    @property
    def value(self):
        return self._secret

    @value.setter
    def value(self, value):
        self._secret = value
        self._in_sync = False

    def save(self, service, username):
        if not self._in_sync:
            try:
                keyring.set_password(
                    service, username, self._secret)
                self._in_sync = True
            except Exception as e:
                core_logger.info('Failed to save credential: %s', e)

    def load(self, service, username):
        if not self._in_sync:
            try:
                self._secret = keyring.get_password(service, username)
                self._in_sync = True
            except Exception as e:
                core_logger.info('Failed to load credential: %s', e)

    def delete(self, service, username):
        try:
            keyring.delete_password(service, username)
        except Exception as e:
            core_logger.info('Failed to delete credential: %s', e)
        self._in_sync = False


class SettingsCredential:
    type: str = ''

    @property
    def id(self):
        raise NotImplementedError()

    @property
    def label(self):
        return f'{self.type.title()} {self.id}'

    @classmethod
    def store_id_from_id(cls, id):
        return (cls.type, id)

    @property
    def store_id(self):
        return self.store_id_from_id(self.id)

    @classmethod
    def from_settings(cls, data: dict):
        raise NotImplementedError()

    def to_settings(self):
        return {'type': self.type}

    @property
    def secret(self):
        raise NotImplementedError()

    def save(self):
        raise NotImplementedError()

    def load(self):
        raise NotImplementedError()

    def delete(self):
        raise NotImplementedError()

    @classmethod
    def credentials_from_connection(cls, connection: Connection
                                    ) -> List['SettingsCredential']:
        raise NotImplementedError()

    @classmethod
    def edit_credentials_secrets(
            cls,
            credentials: List['SettingsCredential'],
            secrets: dict) -> List['SettingsCredential']:
        """
        Edit secrets for credentials, return credentials edited.
        """
        raise NotImplementedError()

    @classmethod
    def credentials_secrets(
            cls,
            credentials: List[Tuple[bool, 'SettingsCredential']],
            include_env: bool = False
    ) -> dict:
        raise NotImplementedError()

    @classmethod
    def credentials_configuration(
            cls,
            credentials: List['SettingsCredential'],
            **kwargs
    ) -> dict:
        raise NotImplementedError()

    @classmethod
    def _secret_keys(cls) -> List[str]:
        raise NotImplementedError()

    @classmethod
    def _get_keys_or_none(cls, data: dict, keys: List[str]) -> Optional[dict]:
        res = {}
        for key in keys:
            value = data.get(key)
            if value is None:
                return
            res[key] = value
        return res

    @classmethod
    def get_env_id(cls, args: list):
        raise NotImplementedError()

    @classmethod
    def get_env_value(cls, data: dict):
        return cls._get_keys_or_none(data, cls._secret_keys())


class SecretCredential(SettingsCredential):
    type: str = 'secret'

    def __init__(self, name: str, secret: str = '', in_sync: bool = False):
        self._name = name
        self._secret = Secret(secret, in_sync)

    def _store_service(self):
        return 'Sympathy for Data Secret'

    @property
    def id(self):
        return self._name

    @property
    def name(self):
        return self.id

    @property
    def secret(self):
        return self._secret.value

    def save(self):
        self._secret.save(self._store_service(), self.id)

    def load(self):
        self._secret.load(self._store_service(), self.id)

    def delete(self):
        self._secret.delete(self._store_service(), self.id)

    @classmethod
    def _parse_secrets(cls, resource):
        return list(utils_credentials.parse_secrets(resource))

    @classmethod
    def _resource_names(cls, resource):
        return [m.group(1) for m in cls._parse_secrets(resource)]

    @classmethod
    def credentials_from_connection(
            cls,
            connection: Connection
    ) -> List[SettingsCredential]:
        return [cls(name, '')
                for name in cls._resource_names(connection.resource)]

    @classmethod
    def edit_credentials_secrets(
            cls,
            credentials: List[SettingsCredential],
            secrets) -> List[SettingsCredential]:
        res = []
        for c in credentials:
            secret = secrets.get(c.id, None)
            if secret is not None:
                c._secret.value = secret
                res.append(c)
        return res

    @classmethod
    def credentials_secrets(
            cls,
            credentials: List[Tuple[bool, 'SettingsCredential']],
            include_env: bool = False
    ) -> dict:
        res = {}
        keys = [c.store_id for _, c in credentials]
        res = dict.fromkeys([name for _, name in keys])

        for stored, credential in credentials:
            name = credential.id
            secret = None
            if stored:
                secret = credential.secret
            elif include_env:
                secret = instance().get_env(
                    credential.store_id, {}).get('secret')
            res[name] = secret
        return res

    def to_dict(self, get_secret=True):
        res = super().to_settings()
        res.update({
            'secret': self._secret.value,
            'name': self.id,
        })
        if not get_secret:
            res.pop('secret')
        return res

    @classmethod
    def from_settings(cls, data: dict):
        return cls(name=data['name'], in_sync=True)

    def to_settings(self):
        return self.to_dict(get_secret=False)

    @classmethod
    def validate_name(cls, name):
        return utils_credentials.validate_secret_name(name)

    def __eq__(self, other):
        return (self.type == other.type and
                self.id == other.id and
                self.secret == other.secret)

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def get_env_id(cls, args: list) -> Optional[Tuple[str]]:
        if len(args) == 1:
            return cls.store_id_from_id(args[0])

    @classmethod
    def _secret_keys(cls) -> List[str]:
        return ['secret']


class LoginCredential(SettingsCredential):
    type: str = 'login'
    in_sync: bool = False

    def __init__(self, id: str, username: str, password: str = None,
                 in_sync: bool = False):
        self._id = id
        self.username = username
        self._password = Secret(password, in_sync)

    def _store_service(self):
        return f'Sympathy for Data Login: {self.id}'

    @property
    def id(self):
        return self._id

    @property
    def password(self):
        return self._password.value

    def save(self):
        self._password.save(self._store_service(), self.username)

    def load(self):
        self._password.load(self._store_service(), self.username)

    def delete(self):
        self._password.delete(self._store_service(), self.username)

    @classmethod
    def credentials_from_connection(
            cls,
            connection: Connection
    ) -> List[SettingsCredential]:
        return [cls(connection.identifier(), '', '')]

    @classmethod
    def edit_credentials_secrets(
            cls,
            credentials: List[SettingsCredential],
            secrets: dict) -> List[SettingsCredential]:
        username = secrets.get('username', None)
        password = secrets.get('password', None)
        res = []
        if username is not None and password is not None:
            for c in credentials:
                c.username = username
                c._password.value = password
            res = credentials
        return res

    @classmethod
    def credentials_secrets(
            cls,
            credentials: List[Tuple[bool, 'SettingsCredential']],
            include_env: bool = False
    ) -> dict:
        res = {
            'username': None,
            'password': None,
        }
        for stored, credential in credentials:
            if stored:
                res['username'] = credential.username
                res['password'] = credential.password
            elif include_env:
                res.update(
                    instance().get_env(credential.store_id, {}))
        return res

    def to_dict(self, get_secret=True):
        res = super().to_settings()
        res.update({
            'resource': self.id,
            'username': self.username,
            'password': self.password,
        })
        if not get_secret:
            res.pop('password')
        return res

    @classmethod
    def from_settings(cls, data: dict):
        return cls(id=data['resource'],
                   username=data['username'],
                   in_sync=True)

    def to_settings(self):
        return self.to_dict(get_secret=False)

    def __eq__(self, other):
        return (self.type == other.type and
                self.id == other.id and
                self.username == other.username and
                self.password == other.password)

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def get_env_id(cls, args: list) -> Optional[Tuple[str]]:
        if len(args) == 1:
            return cls.store_id_from_id(args[0])

    @classmethod
    def _secret_keys(cls) -> List[str]:
        return ['username', 'password']


class UnknownCredential(SettingsCredential):

    def __init__(self, type, data, in_sync: bool = False):
        self.type = type
        self._data = data
        self._id = str(uuid.uuid4())

    @property
    def id(self):
        return self._id

    @property
    def label(self):
        return f'{self.type} Unknown'.title()

    @classmethod
    def store_id_from_id(cls, label):
        return (cls.type, label)

    def save(self):
        pass

    def load(self):
        pass

    def delete(self):
        pass

    def to_dict(self, get_secret=True):
        return self._data

    @classmethod
    def from_settings(cls, data: dict):
        return cls(data['type'], data, in_sync=True)

    def to_settings(self):
        return self._data

    def __eq__(self, other):
        return self._data == other._data

    def __ne__(self, other):
        return not self.__eq__(other)


class AzureCredential(SettingsCredential):
    type: str = 'azure'
    _auth_clients = {}

    def __init__(self,
                 client: str,
                 username: str = '',
                 userid: str = '',
                 name: str = '',
                 in_sync: bool = False):

        self._client = client
        self._username = username
        self._userid = userid
        self._name = name
        self._secret = None

    def _store_service(self):
        return azure_token_cache._service_name()

    @classmethod
    def _id_from_name_client(cls, name, client):
        name = name or ''
        client = client or ''
        return (client, name)

    @classmethod
    def store_id_from_name_client(cls, name, client):
        return cls.store_id_from_id(cls._id_from_name_client(name, client))

    @property
    def id(self):
        return self._id_from_name_client(self.name, self.client)

    @property
    def label(self):
        client = self.client_name()
        name = self.name
        return f'{self.type.title()} {client} {name}'.strip()

    @classmethod
    def from_settings(cls, data: dict):
        return cls(
            client=data['client'],
            username=data['username'],
            userid=data['userid'],
            name=data.get('name', ''),
            in_sync=True)

    def to_settings(self):
        res = super().to_settings()
        res.update({
            'client': self.client,
            'username': self.username,
            'userid': self.userid,
        })
        if self.name:
            res['name'] = self.name
        return res

    @property
    def client(self):
        return self._client or ''

    @property
    def name(self):
        return self._name or ''

    @property
    def username(self):
        return self._username or ''

    @property
    def userid(self):
        return self._userid or ''

    def azure_client(self):
        client = self.client
        return azure_clients.plugins().get(client)

    def client_name(self):
        client = self.client
        res = client.title()
        client = self.azure_client()
        if client:
            res = client.name()
        return res

    @classmethod
    def create_auth_client(cls, client_id) -> Optional[PublicAuthCodeClient]:
        if client_id not in cls._auth_clients:
            client_cls = azure_clients.plugins().get(client_id)
            if not client_cls:
                return
            client = client_cls()
            auth = PublicAuthCodeClient(client, instance().azure_token_cache)
            cls._auth_clients[client_id] = auth
        return cls._auth_clients[client_id]

    @classmethod
    def _get_client_user_secret(cls, client, userid):
        res = {}
        auth = cls.create_auth_client(client)
        if auth:
            response = auth.acquire_token_silent(userid=userid)
            if response:
                res = auth.secrets(response)
        return res

    def _get_secret(self):
        return self._get_client_user_secret(
            self.client, self.userid)

    def is_logged_in(self) -> bool:
        return bool(self._get_secret())

    @property
    def secret(self):
        return {}

    def save(self):
        pass

    def load(self):
        pass

    def delete(self):
        pass

    def to_connection(self):
        return parameter_types.Connection(
            resource=self.client,
            credentials=parameter_types.Credentials(
                mode=parameter_types.CredentialsMode.azure,
                name=self.name))

    @classmethod
    def credentials_from_connection(
            cls,
            connection: Connection
    ) -> List[SettingsCredential]:
        credential = cls(
            client=connection.resource,
            name=connection.credentials.name)
        return [credential]

    @classmethod
    def edit_credentials_secrets(
            cls,
            credentials: List[SettingsCredential],
            secrets: dict) -> List[SettingsCredential]:
        res = []
        state = secrets.get('state')
        auth = None
        if credentials:
            auth = cls._auth_clients.get(credentials[0].client)
        if 'code' in secrets and state and auth and credentials:
            response = auth.acquire_token_by_auth_code_flow(secrets)
            if response and response.get('token_type') == 'Bearer':
                # Success!
                account = auth.get_response_account(response)
                username = account.get('username', '')
                for c in credentials:
                    c._userid = account.get('home_account_id', '')
                    c._username = username
                res = credentials
        return res

    @classmethod
    def credentials_secrets(
            cls,
            credentials: List[Tuple[bool, 'SettingsCredential']],
            include_env: bool = False
    ) -> dict:
        res = {}
        if credentials:
            for stored, credential in credentials:
                if stored:
                    res.update(credential._get_secret())
                elif include_env:
                    res.update(instance().get_env(
                        credential._flat_id(credential.store_id), {}))
        return res

    @classmethod
    def credentials_configuration(
            cls,
            credentials: List['SettingsCredential'],
            port: int = None,
            **kwargs
    ) -> dict:
        user = {}
        auth = {}
        secrets = {}
        res = {'user': user, 'auth': auth, 'secrets': secrets}

        if credentials:
            for credential in credentials:
                user.update({
                    'username': credential.username,
                    'userid': credential.userid})
                auth_client = cls.create_auth_client(credential.client)
                if auth_client:
                    username = credential.username or None
                    flow = auth_client.initiate_auth_code_flow(
                        username=username,
                        port=port)

                    auth_url = flow['auth_uri']
                    state = flow['state']
                    redirect_url = flow['redirect_uri']

                    auth.update({
                        'auth_url': auth_url,
                        'state': state,
                        'redirect_url': redirect_url,
                        'login_hint': username})

        return res

    @classmethod
    def _flat_id(cls, store_id) -> Tuple[str]:
        # Change store_id to flat tuple instead!
        head, rest = store_id
        res_list = [head]
        for part in rest:
            res_list.append(part)
        return tuple(res_list)

    @classmethod
    def get_env_id(cls, args: list) -> Optional[Tuple[str]]:
        if len(args) in [1, 2]:
            client, name, *_ = args + ['']
            return cls._flat_id(cls.store_id_from_name_client(name, client))

    @classmethod
    def _secret_keys(cls) -> List[str]:
        return ['token', 'expires_on']


def azure_login_dialog(credentials, parent=None):
    res = False
    if credentials:
        # Will be only 1.
        credential = credentials[0]
        client_cls = azure_clients.plugins().get(credential.client)
        if client_cls:
            port = editor_credentials.azure_login_server().port()
            configure_secrets = (
                AzureCredential.credentials_configuration(
                    credentials, port=port))
            dialog = editor_credentials.EditAzureDialog(
                credential.to_connection(), configure_secrets, parent=parent)
            res = dialog.exec_() == QtWidgets.QDialog.Accepted
            secrets = dialog.secrets()
            AzureCredential.edit_credentials_secrets(credentials, secrets)
    return res


class MissingCredentialsMessage(messages.ResultMessage):
    _type = None

    def __init__(self, type, *, connection=None, brief=None, details=None,
                 **kwargs):
        self._type = type
        self._connection = connection

        if brief is None:
            brief = f'Missing {type.title()} Credentials'
        super().__init__(brief=brief, **kwargs)

    def connection(self):
        return self._connection

    def resource(self):
        return self._connection.resource


class CredentialsMissingMessageBuilder(messages.ErrorResultMessageBuilder):
    def __init__(self, type):
        self._type = type

    def build(self, *, error, **kwargs):
        return MissingCredentialsMessage(
            self._type, connection=error.connection, **kwargs)


class CredentialsDetails(DetailsWidget):

    def __init__(self, font, parent=None):
        super().__init__(parent=parent)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        button_layout = QtWidgets.QHBoxLayout()
        wrap_layout = QtWidgets.QVBoxLayout()
        self._label = QtWidgets.QLabel()
        self._stack = QtWidgets.QStackedWidget()
        self._deny_widget = editor_credentials.DenyCredentialsWidget('')
        self._null_widget = editor_credentials.NullCredentialsWidget()
        self._wrap_widget = QtWidgets.QWidget()
        self._ok_widget = self._create_ok_widget()
        self._create_button = QtWidgets.QPushButton(self._save_text)
        button_layout.addWidget(self._create_button)
        button_layout.addStretch()

        self._wrap_widget.setLayout(wrap_layout)
        wrap_layout.addWidget(self._ok_widget)
        wrap_layout.addLayout(button_layout)

        self._stack.addWidget(self._deny_widget)
        self._stack.addWidget(self._null_widget)
        self._stack.addWidget(self._wrap_widget)
        layout.addWidget(self._label)
        layout.addWidget(self._stack)
        self.setLayout(layout)

        self._stack.setCurrentWidget(self._null_widget)

        self._create_button.clicked.connect(
            self._handle_create_button_clicked)

    def type(self):
        assert self.type
        return self._type

    def _text(self, item):
        message = item.data(MsgRoles.message)
        brief = message.brief()
        details = message.details()

        res = ''
        if brief and details:
            res = '\n\n'.join([brief, details])
        elif brief:
            res = brief
        elif details:
            res = details

        return res

    def _create_ok_widget(self):
        return QtWidgets.QWidget()

    def _setup_connection(self, connection):
        pass

    def clear(self):
        super().clear()
        self._stack.setCurrentWidget(self._null_widget)

    def _is_denied(self):
        credential_action = settings.instance()['credential_action']
        return credential_action == settings.credential_action_deny

    def update_data(self, item):
        self.clear()
        self._item = item
        resource = item.data(MsgRoles.message).resource()
        connection = item.data(MsgRoles.message).connection()
        item_text = self._text(item)
        self._label.setText(item_text)
        item.setData(MsgRoles.text, item_text)
        self._deny_widget.set_resource(resource)

        ok = False
        if self._is_denied():
            self._stack.setCurrentWidget(self._deny_widget)
        else:
            self._setup_connection(connection)
            ok = True
            self._stack.setCurrentWidget(self._wrap_widget)

        self._create_button.setEnabled(ok)

    def _handle_create_button_clicked(self):
        pass


class SecretsMessageDetails(CredentialsDetails):
    _type = 'secrets'
    _save_text = 'Save New Secrets'

    def __init__(self, font, parent=None):
        super().__init__(font, parent=parent)
        layout = QtWidgets.QVBoxLayout()
        self._ok_widget.setLayout(layout)

    def _setup_connection(self, connection):
        secrets = instance().request_connection(connection)[1]
        self._ok_widget.setup(connection, secrets)

    def _create_ok_widget(self):
        return editor_credentials.EditSecretsWidget()

    def _handle_create_button_clicked(self):
        for name, secret in self._ok_widget.secrets().items():
            credential = SecretCredential(name, secret)
            exists = False
            if credential.store_id in instance():
                stored = instance().get_credential(credential.store_id)
                stored.load()
                if stored.secret == secret:
                    exists = True
            if not exists:
                instance().set_credential(credential.store_id, credential)
        self._remove()


class LoginMessageDetails(SecretsMessageDetails):
    _type = 'login'
    _save_text = 'Save New Login'

    def _create_ok_widget(self):
        return editor_credentials.EditLoginWidget()

    def _handle_create_button_clicked(self):
        secrets = self._ok_widget.secrets()
        credential = LoginCredential(
            self._ok_widget.connection().identifier(),
            secrets['username'],
            secrets['password'])
        instance().set_credential(credential.store_id, credential)
        self._remove()


class AzureMessageDetails(CredentialsDetails):
    _type = 'azure'
    _save_text = 'Login'

    def __init__(self, font, parent=None):
        super().__init__(font, parent=parent)
        self._auth = None
        self._client = None
        self._connection = None

    def _setup_connection(self, connection):
        self._connection = connection

    def _handle_create_button_clicked(self):
        credentials = AzureCredential.credentials_from_connection(
            self._connection)
        if azure_login_dialog(credentials, parent=self):
            for credential in credentials:
                instance().set_credential(credential.store_id, credential)
            self._remove()


class CredentialManager(QtCore.QObject):
    _settings_key = settings.credential_array_key

    def __init__(self):
        self._encryption = None
        self._store = {}
        self._load_settings()
        self._azure_token_cache = None
        self._environment_credentials = False
        self._environment_prefix = ''
        self._environment_dict = {}

    @property
    def azure_token_cache(self):
        # Delay until first use.
        if self._azure_token_cache is None:
            self._azure_token_cache = azure_token_cache.create()
        return self._azure_token_cache

    def set_environment_credentials(self, prefix, env, case_sensitive=True):
        def get_key(data) -> list:
            res = None
            try:
                res = json.loads(data)
            except Exception:
                pass

            if not isinstance(res, list):
                res = None
            elif not len(res):
                res = None
            return res

        def get_value(data) -> dict:
            try:
                res = json.loads(data)
            except Exception:
                res = None

            if not isinstance(res, dict):
                res = None
            return res

        def log_unsupported(key):
            core_logger.warning(
                'Environment variable matched for credentials, %s has '
                'unsupported format',
                key)

        def log_supported(key):
            core_logger.info(
                'Environment variable matched for credentials, %s was '
                'succesfully loaded',
                key)

        self._environment_credentials = True
        self._environment_case_sensitive = case_sensitive
        self._environment_prefix = prefix
        self._environment_dict.clear()

        string_credentials = utils_credentials.string_credentials_by_prefix(
            env, prefix)

        modes = self._get_os_env_modes()

        for k, v in string_credentials.items():
            key = get_key(k)
            value = get_value(v)
            if key is None or value is None:
                log_unsupported(k)
            else:
                mode, *rest = key
                if not self._environment_case_sensitive:
                    mode = mode.upper()

                info = modes.get(mode)
                if info:
                    cls = info.credential
                    env_id = cls.get_env_id(rest)
                    env_secret = cls.get_env_value(value)
                    env_id = self._get_os_env_id(env_id)
                    if env_id is None or env_secret is None:
                        log_unsupported(k)
                    else:
                        self._environment_dict[env_id] = env_secret
                        log_supported(k)

    def get_env(self, key, default=None):
        return self._environment_dict.get(self._get_os_env_id(key), default)

    def _get_os_env_id(self, key):
        if key and not self._environment_case_sensitive:
            key = tuple(k.upper() for k in key)
        return key

    def _get_os_env_modes(self):
        data = _credential_info
        if not self._environment_case_sensitive:
            data = {k.upper(): v for k, v in data.items()}
        return data

    def keys(self):
        return list(self._store.keys())

    def __contains__(self, key):
        return key in self._store

    def get(self, key, default=None):
        return self._store.get(key, default)

    def _encode_credential(self, credential_dict):
        return dict(credential_dict)

    def _decode_credential(self, credential_dict):
        return dict(credential_dict)

    def _get_stored(self, key):
        raise self._store[key]

    def get_credential(self, key):
        # Will raise KeyError if not in store.
        credential = self._store[key]
        return credential

    def _store_settings(self):
        settings.instance()[self._settings_key] = [
            credential.to_settings()
            for credential in self._store.values()]

    def _load_settings(self):
        self._store.clear()
        data = settings.instance()[self._settings_key]

        for stored in data:
            if 'type' in stored:
                type = stored['type']
                cls = _credential_info.get(type)
                if cls is None:
                    credential = UnknownCredential(type, stored)
                    self._store[credential.store_id] = credential
                else:
                    try:
                        credential = cls.credential.from_settings(stored)
                    except Exception:
                        pass
                    else:
                        self._store[credential.store_id] = credential

    def _set_stored(self, key, value):
        self._store[key] = value
        self._store_settings()

    def set_credential(self, key, credential):
        stored = self._store.get(key)
        if not (stored and stored == credential):
            # Do not replace and saved existing.
            credential.save()
            self._set_stored(key, credential)

    def _remove_stored(self, key):
        self._store.pop(key, None)
        self._store_settings()

    def remove_credential(self, key, credential=None, remove_secret=True):
        if remove_secret:
            try:
                if credential is None:
                    credential = self.get_credential(key)
                credential.delete()
            except KeyError:
                pass
        self._remove_stored(key)

    def _init_connection(self, connection: Connection):
        credential_action = settings.instance()['credential_action']
        deny = credential_action == settings.credential_action_deny
        ok = not deny
        mode = connection.credentials.mode.name
        utils_credentials.validate_mode(mode)
        return ok, mode

    def _load_stored_credentials(self, credentials: List[SettingsCredential]
                                 ) -> List[Tuple[bool, SettingsCredential]]:
        res = []
        for credential in credentials:
            store_id = credential.store_id
            if store_id in self:
                credential = self.get_credential(store_id)
                credential.load()
                res.append((True, credential))
            else:
                res.append((False, credential))
        return res

    def _as_stored_credentials(self, credentials):
        return [(True, c) for c in credentials]

    def request_connection(self, connection: Connection,
                           include_env: bool = False
                           ) -> Tuple[bool, dict]:
        """
        Returns all variables found in resource with their corresponding
        values. None in place of missing variables.
        """
        include_env &= self._environment_credentials
        res = {}
        ok, mode = self._init_connection(connection)
        if ok:
            credentials_info = _credential_info.get(mode)
            if credentials_info:
                cls = credentials_info.credential
                credentials = cls.credentials_from_connection(
                    connection)
                stored_credentials = self._load_stored_credentials(credentials)
                if credentials:
                    res = cls.credentials_secrets(
                        stored_credentials, include_env)
        return ok, res

    def edit_connection(self, connection: Connection, secrets: dict
                        ) -> Tuple[bool, dict]:
        """
        Set credentials for resource according to provided secrets.
        Returns all variables set and None in place of missing variables.
        """
        res = {}
        ok, mode = self._init_connection(connection)
        if ok:
            credentials_info = _credential_info.get(mode)

            if credentials_info:
                cls = credentials_info.credential
                credentials = cls.credentials_from_connection(
                    connection)
                for credential in cls.edit_credentials_secrets(
                        credentials, secrets):
                    self.set_credential(credential.store_id, credential)

                res = cls.credentials_secrets(
                    self._as_stored_credentials(credentials))
        return ok, res

    def configure_connection(self, connection: Connection,
                             kwargs: dict
                             ) -> Tuple[bool, dict]:
        """
        Configure new or existing credential for connection.
        """
        res = {}
        ok, mode = self._init_connection(connection)
        if ok:
            credentials_info = _credential_info.get(mode)

            if credentials_info:
                cls = credentials_info.credential
                credentials = cls.credentials_from_connection(connection)
                credentials = [self.get(c.store_id, c) for c in credentials]
                res = cls.credentials_configuration(credentials, **kwargs)
        return ok, res


def _credentials_denied_message(node, resource):
    level = messages.Levels.error
    brief = (
        f'Denied credential request for resource: {resource}\n\n'
        'To allow use of credentials, '
        'open:\n  Preferences -> Credentials, and change '
        'When Requested to Allow.')
    return messages.NodeMessage(
        id=(0, resource, node.full_uuid), node=node, level=level,
        brief=brief)


def create_right_stretch_layout(widget):
    layout = QtWidgets.QHBoxLayout()
    layout.addWidget(widget)
    layout.addStretch()
    return layout


class NewCredentialWidget(QtWidgets.QWidget):

    create = QtCore.Signal(SettingsCredential)
    cancel = QtCore.Signal()
    type_changed = QtCore.Signal(str)

    type = 'unknown'

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = sywidgets.FormLayout()
        layout.setContentsMargins(0, 0, 0, 0)

    def setup(self):
        pass

    def clear(self):
        self._type_widget.clear()

    def accept(self):
        pass

    def reject(self):
        self.cancel.emit()

    def _create_form_layout(self):
        layout = sywidgets.FormLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        return layout

    def _create_type_widget(self):
        self._type_widget = ChoiceWidget(
            self.type, {t: t.title() for t in credential_types()})
        self._type_widget.changed.connect(self.type_changed)
        return self._type_widget

    def _create_button_box(self):
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        self._ok_button = button_box.button(QtWidgets.QDialogButtonBox.Ok)
        self._ok_button.setText("Create")
        button_box.button(QtWidgets.QDialogButtonBox.Cancel).setText("Cancel")

        self._ok_button.setEnabled(False)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        return button_box

    def _key_ok(self, key):
        keys = self.parentWidget().parentWidget().keys()
        return key not in keys


class NewLoginWidget(NewCredentialWidget):

    create = QtCore.Signal(LoginCredential)

    type = 'login'

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = self._create_form_layout()

        button_box = self._create_button_box()
        self._type_widget = self._create_type_widget()

        self._resource_widget = QtWidgets.QLineEdit()
        self._resource_widget.setToolTip('Name to identify this login')
        self._username_widget = editor_credentials.UsernameWidget('')
        self._password_widget = editor_credentials.PasswordWidget('')
        self._status_widget = QtWidgets.QLabel()

        layout.addRow('Type', self._type_widget)
        layout.addRow('Name', self._resource_widget)
        layout.addRow('Username', self._username_widget)
        layout.addRow('Password', self._password_widget)
        layout.addRow('Status', self._status_widget)
        layout.addRow(button_box)

        self.setLayout(layout)

        self._resource_widget.textChanged.connect(
            self._handle_resource_changed)

    def setup(self):
        self._handle_resource_changed(self._resource_widget.text())

    def clear(self):
        super().clear()
        self._resource_widget.setText('')
        self._username_widget.setText('')
        self._password_widget.setText('')

    def _to_credential(self):
        return LoginCredential(
            self._resource_widget.text(),
            self._username_widget.get_value(),
            self._password_widget.get_value())

    def accept(self):
        self.create.emit(self._to_credential())

    def _handle_resource_changed(self, resource):
        status = ''
        ok = self._key_ok(LoginCredential.store_id_from_id(resource))
        if not ok:
            status = 'Resource already exists'
        self._status_widget.setText(status)
        self._ok_button.setEnabled(ok)


class NewAzureWidget(NewCredentialWidget):

    create = QtCore.Signal(AzureCredential)

    type = 'azure'

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = self._create_form_layout()

        button_box = self._create_button_box()
        self._type_widget = self._create_type_widget()
        named_clients = {
            k: p().name() for k, p in azure_clients.plugins().items()}
        self._client_widget = ChoiceWidget('', named_clients)
        self._type_widget.changed.connect(self.type_changed)

        self._name_widget = QtWidgets.QLineEdit()
        self._name_widget.setToolTip('Name to identify this login')
        self._username_widget = ChoiceWidget('', {})
        self._status_widget = QtWidgets.QLabel()
        self._accounts = {}
        self._is_logged_in = False

        layout.addRow('Type', self._type_widget)
        layout.addRow('Name', self._name_widget)
        layout.addRow('Username', self._username_widget)
        layout.addRow('Client', self._client_widget)
        layout.addRow('Status', self._status_widget)
        layout.addRow(button_box)

        self.setLayout(layout)

        self._name_widget.textChanged.connect(self._handle_changed)
        self._client_widget.changed.connect(self._handle_login_changed)
        self._username_widget.changed.connect(self._handle_login_changed)

    def setup(self):
        accounts = instance().azure_token_cache.find_accounts()
        accounts = {account['home_account_id']: account['username']
                    for account in accounts}
        accounts[''] = ''
        accounts = dict(sorted(accounts.items()))
        self._accounts = accounts
        self._username_widget.setup('', accounts)
        self._handle_changed()

    def clear(self):
        super().clear()
        self._client_widget.clear()
        self._name_widget.setText('')

    def _to_credential(self):
        client = self._client_widget.get() or ''
        userid = self._username_widget.get() or ''
        username = self._accounts.get(userid, '')
        return AzureCredential(
            client,
            username=username,
            userid=userid,
            name=self._name_widget.text())

    def accept(self):
        credential = self._to_credential()
        if self._is_logged_in:
            self.create.emit(credential)
        else:
            ok = azure_login_dialog([credential], parent=self)
            if ok:
                self.create.emit(credential)

    def _handle_login_changed(self):
        credential = self._to_credential()
        username = self._username_widget.get()
        self._is_logged_in = False
        if username:
            self._is_logged_in = credential.is_logged_in()
        self._handle_changed()

    def _handle_changed(self):
        client = self._client_widget.get() or ''
        name = self._name_widget.text()
        status = ''
        ok = True

        if client:
            store_id = AzureCredential.store_id_from_name_client(name, client)
            if not self._key_ok(store_id):
                ok = False
                status = f'Name already exists for {client}'
        else:
            ok = False
            status = 'No client is set'

        if ok:
            if self._is_logged_in:
                status = 'Logged in'
            else:
                status = 'Not logged in'

        self._status_widget.setText(status)
        self._ok_button.setEnabled(ok)


class ExistingCredentialWidget(QtWidgets.QWidget):

    credential_changed = QtCore.Signal(SettingsCredential, bool)
    remove = QtCore.Signal()

    def __init__(self, parent=None):
        self._block_changed_value = False
        super().__init__(parent=parent)

    @contextlib.contextmanager
    def _block_changed(self):
        # Prevent modification when widget updates due to selecting
        # new credential element.
        orig = self._block_changed_value
        try:
            self._block_changed_value = True
            yield
        finally:
            self._block_changed_value = orig

    def _setup(self, credential):
        pass

    def setup(self, credential):
        with self._block_changed():
            self._setup(credential)

    def _clear(self):
        pass

    def clear(self):
        with self._block_changed():
            self._clear()

    def _credential_changed(self, credential, changed):
        if not self._block_changed_value:
            self.credential_changed.emit(credential, changed)

    def _create_form_layout(self):
        layout = sywidgets.FormLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        return layout

    def _create_button_box(self, extra_buttons=None):
        button = QtWidgets.QDialogButtonBox.Cancel
        buttons = button
        if extra_buttons:
            buttons |= extra_buttons
        button_box = QtWidgets.QDialogButtonBox(buttons)
        button_box.button(button).setText("Remove")
        button_box.rejected.connect(self.remove)
        return button_box


class ExistingUnknownWidget(ExistingCredentialWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = self._create_form_layout()
        label = QtWidgets.QLabel('Existing Unknown')
        layout.addRow(label)
        self.setLayout(layout)


class ExistingSecretWidget(ExistingCredentialWidget):

    credential_changed = QtCore.Signal(SecretCredential, bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = self._create_form_layout()

        label = QtWidgets.QLabel('Existing Secret')

        button_box = self._create_button_box()

        self._name_widget = editor_credentials.ResourceWidget()
        self._name_widget.setToolTip('Name to identify this secret')
        self._secret_widget = editor_credentials.SecretWidget('')

        layout.addRow(label)

        layout.addRow('Name', self._name_widget)
        layout.addRow('Secret', self._secret_widget)
        layout.addRow(button_box)
        self.setLayout(layout)

        self._secret_widget.value_edited.connect(self._handle_secret_changed)

    def _handle_secret_changed(self):
        credential = SecretCredential(
            self._name_widget.text(),
            self._secret_widget.text())
        self._credential_changed(credential, True)

    def _setup(self, credential):
        self._name_widget.setText(credential.id)
        self._secret_widget.from_dict(credential.to_dict())

    def _clear(self):
        self._name_widget.setText('')
        self._secret_widget.clear()


class ExistingLoginWidget(ExistingCredentialWidget):

    credential_changed = QtCore.Signal(LoginCredential, bool)
    remove = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = self._create_form_layout()

        label = QtWidgets.QLabel('Existing Login')

        button_box = self._create_button_box()

        self._resource_widget = editor_credentials.ResourceWidget('')
        self._resource_widget.setToolTip('Name to identify this login')
        self._username_widget = editor_credentials.UsernameWidget('')
        self._password_widget = editor_credentials.PasswordWidget('')

        layout.addRow(label)

        layout.addRow('Name', self._resource_widget)
        layout.addRow('Username', self._username_widget)
        layout.addRow('Password', self._password_widget)
        layout.addRow(button_box)
        self.setLayout(layout)

        self._username_widget.value_edited.connect(
            self._handle_username_changed)
        self._password_widget.value_edited.connect(
            self._handle_password_changed)

    def _handle_username_changed(self):
        self._handle_changed(False)

    def _handle_password_changed(self):
        self._handle_changed(True)

    def _handle_changed(self, secret_changed):
        credential = LoginCredential(
            self._resource_widget.text(),
            self._username_widget.text(),
            self._password_widget.get_value())
        self._credential_changed(credential, secret_changed)

    def _setup(self, credential):
        self._resource_widget.setText(credential.id)
        self._username_widget.setText(credential.username)
        self._password_widget.from_dict(credential.to_dict())

    def _clear(self):
        self._resource_widget.setText('')
        self._username_widget.setText('')
        self._password_widget.clear()


class ExistingAzureWidget(ExistingCredentialWidget):

    credential_changed = QtCore.Signal(AzureCredential, bool)
    remove = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = self._create_form_layout()

        label = QtWidgets.QLabel('Existing Azure')

        button_box = self._create_button_box(QtWidgets.QDialogButtonBox.Apply)

        self._name_widget = editor_credentials.ResourceWidget()
        self._name_widget.setToolTip('Name to identify this login')
        self._username_widget = ChoiceWidget('', {})
        self._client_widget = editor_credentials.ResourceWidget()
        self._client_widget.setToolTip('Client')
        self._status_widget = QtWidgets.QLabel()
        self._login_button = button_box.button(
            QtWidgets.QDialogButtonBox.Apply)
        layout.addRow(label)
        self._login_button.setText('Edit Login')
        self._credential = None
        self._login_button.setEnabled(False)

        layout.addRow('Name', self._name_widget)
        layout.addRow('Username', self._username_widget)
        layout.addRow('Client', self._client_widget)
        layout.addRow('Status', self._status_widget)
        layout.addRow(button_box)

        self.setLayout(layout)
        self._login_button.clicked.connect(self._handle_edit_login)
        self._username_widget.changed.connect(self._handle_changed)

    def _setup(self, credential):
        self._credential = credential
        self._name_widget.setText(credential.name)
        self._client_widget.setText(credential.client_name())
        self._setup_login(credential)
        accounts = instance().azure_token_cache.find_accounts()
        accounts = {account['home_account_id']: account['username']
                    for account in accounts}
        accounts[credential.userid] = credential.username
        accounts[''] = ''
        accounts = dict(sorted(accounts.items()))
        self._accounts = accounts
        self._username_widget.setup(credential.userid, accounts)
        self._update_login()

    def _setup_login(self, credential):
        tooltip = ''
        azure_client = credential.azure_client()
        ok = azure_client is not None
        if not ok:
            tooltip = 'Can not login to unknown client'
        self._login_button.setToolTip(tooltip)
        self._login_button.setEnabled(ok)

    def _clear(self):
        self._client_widget.setText('')
        self._name_widget.setText('')

    def _to_credential(self):
        userid = self._username_widget.get()
        username = self._accounts.get(userid, '')
        return AzureCredential(
            client=self._credential.client,
            username=username,
            userid=userid,
            name=self._credential.name)

    def _update_login(self):
        username = self._username_widget.get()
        status = 'Not logged in'
        if username and self._to_credential().is_logged_in():
            status = 'Logged in'
        self._status_widget.setText(status)

    def _handle_changed(self):
        credential = self._to_credential()
        self.credential_changed.emit(credential, True)
        self._update_login()

    def _handle_edit_login(self):
        credential = self._to_credential()

        ok = azure_login_dialog(
            [credential], parent=self)
        if ok:
            self._username_widget.setCurrentText(credential.username)
            self.credential_changed.emit(credential, True)
            self._update_login()


class ChoiceWidget(QtWidgets.QComboBox):
    changed = QtCore.Signal(str)
    key_role = QtCore.Qt.UserRole

    def __init__(self, choice, choices, parent=None):
        super().__init__(parent=parent)
        self._setup(choice, choices)
        self.clear()

    def get(self):
        return self.itemData(self.currentIndex(), role=self.key_role)

    def _setup(self, choice, choices):
        super().clear()
        self._choice = choice
        self._choices = dict(choices)
        if self._choice not in choices:
            self._choices[self._choice] = self._choice.title()

        self._choice_to_index = dict(
            zip(self._choices, range(len(self._choices))))
        self._index_to_choice = list(self._choices)

        for i, (t, n) in enumerate(self._choices.items()):
            self.addItem(n)
            self.setItemData(i, t, role=self.key_role)
        self.setCurrentIndex(self._choice_to_index[choice])

    def setup(self, choice, choices):
        with self._block_changed():
            self._setup(choice, choices)

    @contextlib.contextmanager
    def _block_changed(self):
        try:
            self.currentIndexChanged.disconnect(self._handle_choice_changed)
        except Exception:
            pass
        try:
            yield
        finally:
            self.currentIndexChanged.connect(self._handle_choice_changed)

    def clear(self):
        with self._block_changed():
            self.setCurrentIndex(self._choice_to_index[self._choice])

    def _handle_choice_changed(self, index):
        self.changed.emit(self._index_to_choice[index])


class ClientsWidget(QtWidgets.QListWidget):
    key_role = QtCore.Qt.UserRole
    changed = QtCore.Signal()

    def __init__(self, clients, parent=None):
        super().__init__(parent=parent)
        self.setup(clients)
        self.itemChanged.connect(self._handle_changed)

    def _handle_changed(self, *args):
        self.changed.emit()

    def _items(self):
        return [self.item(row) for row in range(self.count())]

    def setup(self, clients):
        super().clear()
        self._clients = dict(clients)
        self._type_to_index = dict(zip(
            self._clients, range(len(self._clients))))
        self._index_to_type = list(self._clients)

        for i, (c, n) in enumerate(self._clients.items()):
            item = QtWidgets.QListWidgetItem(n)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setData(self.key_role, c)
            self.addItem(item)
        self.set([])
        self.clearSelection()

    def get(self):
        return [item.data(self.key_role) for item in self._items()
                if item.checkState() == QtCore.Qt.Checked]

    def set(self, selected):
        states = {False: QtCore.Qt.Unchecked, True: QtCore.Qt.Checked}

        for item in self._items():
            state = states[item.data(self.key_role) in selected]
            item.setCheckState(state)

    def selected(self):
        return [
            item.data(self.key_role) for item in self.selectedItems()]

    def clear(self):
        self.set([])
        self.clearSelection()


class NewSecretWidget(NewCredentialWidget):

    create = QtCore.Signal(SecretCredential)

    type = 'secret'

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = self._create_form_layout()

        self._type_widget = self._create_type_widget()

        self._name_widget = QtWidgets.QLineEdit()
        self._name_widget.setToolTip('Name to identify this secret')
        self._secret_widget = editor_credentials.SecretWidget('')
        self._status_widget = QtWidgets.QLabel()

        button_box = self._create_button_box()

        layout.addRow('Type', self._type_widget)
        layout.addRow('Name', self._name_widget)
        layout.addRow('Secret', self._secret_widget)
        layout.addRow('Status', self._status_widget)
        layout.addRow(button_box)

        self.setLayout(layout)

        self._name_widget.textChanged.connect(self._handle_name_changed)

    def setup(self):
        self._handle_name_changed(self._name_widget.text())

    def clear(self):
        super().clear()
        self._name_widget.setText('')
        self._secret_widget.setText('')

    def _to_credential(self):
        return SecretCredential(
            self._name_widget.text(), self._secret_widget.get_value())

    def accept(self):
        self.create.emit(self._to_credential())

    def reject(self):
        self.cancel.emit()

    def _handle_name_changed(self, name):
        ok = SecretCredential.validate_name(name)
        status = ''
        if ok:
            ok = self._key_ok(SecretCredential.store_id_from_id(name))
            if not ok:
                status = 'Name already exists'
        else:
            status = 'Invalid name'
        self._status_widget.setText(status)
        self._ok_button.setEnabled(ok)


class CredentialSectionWidget(PreferenceSectionWidget):
    """docstring for PreferenceSectionWidget"""

    _name = 'Credentials'
    _apply_order = 10000

    _action_choice = settings.credential_action_choice

    store_id_role = QtCore.Qt.UserRole
    credential_role = QtCore.Qt.UserRole + 1
    dirty_role = QtCore.Qt.UserRole + 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._remove_set = set()

        layout = QtWidgets.QVBoxLayout()

        self._no_credential_widget = QtWidgets.QWidget()

        self._type_new_widgets = {}
        self._type_existing_widgets = {}

        for type_, info in _credential_info.items():
            new_widget = info.new_widget()
            existing_widget = info.existing_widget()

            self._type_new_widgets[type_] = new_widget
            self._type_existing_widgets[type_] = existing_widget

        existing_unknown = ExistingUnknownWidget()
        self._type_existing_widgets['unknown'] = existing_unknown

        items_layout = QtWidgets.QHBoxLayout()
        select_layout = QtWidgets.QVBoxLayout()
        general_layout = self._layout = self._create_layout()
        credential_layout = QtWidgets.QVBoxLayout()

        self._credential_widget = QtWidgets.QStackedWidget()
        items_layout.addLayout(select_layout)
        items_layout.addLayout(credential_layout)

        self._credential_widget.addWidget(self._no_credential_widget)
        for new_widget in self._type_new_widgets.values():
            self._credential_widget.addWidget(new_widget)
        for existing_widget in self._type_existing_widgets.values():
            self._credential_widget.addWidget(existing_widget)

        hline = sywidgets.HLine()
        credential_layout.addWidget(self._credential_widget)
        credential_layout.addStretch()
        items_layout.setContentsMargins(0, 0, 0, 0)

        layout.addLayout(general_layout)
        layout.addWidget(hline)
        layout.addLayout(items_layout)

        self._current_credential = None

        self._credential_filter = sywidgets.ClearButtonLineEdit(
            placeholder='Filter', clear_button=True)

        select_width = 200

        self._credential_filter.setMaximumWidth(select_width)

        self._credential_list = QtWidgets.QListView()
        self._credential_model = QtGui.QStandardItemModel()
        self._credential_list.setMaximumWidth(select_width)
        self._search_model = sywidgets.OrderedSearchFilterModel(
            self._credential_list)
        self._search_model.setSourceModel(self._credential_model)
        self._credential_list.setModel(self._search_model)

        self._create_button = QtWidgets.QPushButton('Create New Credential')
        self._create_button.setMaximumWidth(select_width)

        self._action_combo = setwidgets.StringComboBox(
            'credential_action', settings.credential_action_choice)

        general_layout.addRow('When requested', self._action_combo)
        select_layout.addWidget(self._credential_filter)
        select_layout.addWidget(self._credential_list)
        select_layout.addWidget(self._create_button)

        self.setLayout(layout)

        self._credential_list.selectionModel().selectionChanged.connect(
            self._handle_credential_list_index_changed)

        for existing_widget in self._type_existing_widgets.values():
            existing_widget.remove.connect(self._handle_remove)

        self._create_button.clicked.connect(self._handle_create_button_clicked)

        for new_widget in self._type_new_widgets.values():
            new_widget.create.connect(self._handle_create)
            new_widget.cancel.connect(self._handle_cancel)
            new_widget.type_changed.connect(self._handle_type_changed)

        for existing_widget in self._type_existing_widgets.values():
            existing_widget.credential_changed.connect(
                self._handle_credential_changed)
        self._credential_filter.textChanged.connect(
            self._handle_filter_text_changed)

    def _get_credential(self, item):
        credential = item.data(self.credential_role)
        if item.data(self.dirty_role) is False:
            credential.load()
        return credential

    def _remove_credential(self, item):
        key = item.data(self.store_id_role)
        self._remove_set.add(key)

    def _handle_remove(self):
        for item in self._selected_items():
            self._remove_credential(item)
            self._credential_model.takeRow(
                item.row())

    def _handle_create_button_clicked(self):
        self._credential_list.clearSelection()
        for new_widget in self._type_new_widgets.values():
            new_widget.clear()
        for new_widget in self._type_new_widgets.values():
            new_widget.setup()
        self._credential_widget.setCurrentWidget(
            self._new_credential_widget('login'))
        self._create_button.setEnabled(False)

    def _handle_create(self, credential):
        self._create_button.setEnabled(True)
        item = self._create_item(credential.store_id, credential, dirty=True)
        self._add_item(item)

        self._credential_list.selectionModel().clear()

        self._credential_list.selectionModel().setCurrentIndex(
            self._search_model.mapFromSource(item.index()),
            QtCore.QItemSelectionModel.Select)

    def _handle_cancel(self):
        self._create_button.setEnabled(True)
        self._credential_widget.setCurrentWidget(self._no_credential_widget)

    def _new_credential_widget(self, text):
        widget = self._type_new_widgets.get(text)
        if widget:
            return widget
        assert False, 'Unknown type'

    def _existing_credential_widget(self, text):
        widget = self._type_existing_widgets.get(text)
        if not widget:
            widget = self._type_existing_widgets['unknown']
        return widget

    def _handle_type_changed(self, text):
        widget = self._new_credential_widget(text)
        widget.clear()
        self._credential_widget.setCurrentWidget(
            widget)

    def _handle_credential_list_index_changed(self, selected, deselected):
        new = None

        self._create_button.setEnabled(True)

        new_indices = selected.indexes()
        old_indices = deselected.indexes()

        if new_indices and new_indices[0].isValid():
            new = self._credential_model.itemFromIndex(
                self._search_model.mapToSource(new_indices[0]))

        if old_indices and old_indices[0].isValid():
            # old = self._credential_model.itemFromIndex(
            #     self._search_model.mapToSource(old_indices[0]))
            pass

        for existing_widget in self._type_existing_widgets.values():
            existing_widget.clear()

        selection = new is not None
        if selection:
            credential = self._get_credential(new)
            widget = self._existing_credential_widget(credential.type)
            self._credential_widget.setCurrentWidget(widget)
            widget.setup(credential)
        else:
            self._credential_widget.setCurrentWidget(
                self._no_credential_widget)

    def _handle_credential_changed(self, credential, changed):
        for item in self._selected_items():
            self._set_item_data(item, self.credential_role, credential)
            self._set_item_data(item, self.dirty_role, True)

    def _handle_filter_text_changed(self, text):
        self._search_model.set_filter(text)

    def _selected_items(self):
        return [self._credential_model.itemFromIndex(
            self._search_model.mapToSource(index))
                for index in self._credential_list.selectedIndexes()]

    def _set_item_data(self, item, role, data):
        item.setData(data, role)

    def _create_item(self, label, credential, dirty):
        item = QtGui.QStandardItem(credential.label)
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
        self._set_item_data(item, self.store_id_role, credential.store_id)
        self._set_item_data(item, self.credential_role, credential)
        self._set_item_data(item, self.dirty_role, dirty)
        return item

    def _add_item(self, item):
        self._credential_model.appendRow(item)
        if not self._selected_items():
            if self._search_model.rowCount():
                self._credential_list.setCurrentIndex(
                    self._search_model.index(0, 0))

    def update_data(self):
        try:
            self._credential_list.selectionModel().selectionChanged.disconnect(
                self._handle_credential_list_index_changed)

            self._remove_set.clear()
            self._credential_model.clear()
            self._create_button.setEnabled(True)
            credentials_ = instance()

            for store_id in credentials_.keys():
                credential = credentials_.get_credential(store_id)
                item = self._create_item(
                    credential.label, credential, dirty=False)
                self._add_item(item)

            self._credential_widget.setCurrentWidget(
                self._no_credential_widget)
            self._credential_list.clearSelection()
        finally:
            self._credential_list.selectionModel().selectionChanged.connect(
                self._handle_credential_list_index_changed)

    def keys(self):
        res = []
        for i in range(self._credential_model.rowCount()):
            item = self._credential_model.item(i)
            key = item.data(self.store_id_role)
            res.append(key)
        return res

    def save(self):
        self._action_combo.save()

        try:
            self._credential_list.selectionModel().selectionChanged.disconnect(
                self._handle_credential_list_index_changed)

            credentials_ = instance()
            for key in self._remove_set:
                credentials_.remove_credential(key)

            for i in range(self._credential_model.rowCount()):
                item = self._credential_model.item(i)
                if item.data(self.dirty_role):
                    credential = item.data(self.credential_role)
                    key = item.data(self.store_id_role)
                    instance().set_credential(key, credential)

            self._remove_set.clear()
            self._credential_model.clear()

        finally:
            self._credential_list.selectionModel().selectionChanged.connect(
                self._handle_credential_list_index_changed)


@dataclasses.dataclass
class CredentialInfo:
    credential: SettingsCredential
    message_details: DetailsWidget
    new_widget: QtWidgets.QWidget
    existing_widget: QtWidgets.QWidget
    exception: exceptions.SyCredentialError
    type: str = None


secrets_info = CredentialInfo(
    credential=SecretCredential,
    message_details=SecretsMessageDetails,
    new_widget=NewSecretWidget,
    existing_widget=ExistingSecretWidget,
    exception=exceptions.SySecretCredentialError,
    type='secret'
)


login_info = CredentialInfo(
    credential=LoginCredential,
    message_details=LoginMessageDetails,
    new_widget=NewLoginWidget,
    existing_widget=ExistingLoginWidget,
    exception=exceptions.SyLoginCredentialError
)


azure_info = CredentialInfo(
    credential=AzureCredential,
    message_details=AzureMessageDetails,
    new_widget=NewAzureWidget,
    existing_widget=ExistingAzureWidget,
    exception=exceptions.SyAzureCredentialError
)


azure_clients = plugins.Plugin(
    'sympathy.credential.azure.plugins',
    AzureClient
)


_credential_info = {}


def details_widgets():
    return [info.message_details for info in _credential_info.values()]


def credential_types():
    # Get rid of duplicate secrets_info.
    return {id(v): v.type or k
            for k, v in _credential_info.items()}.values()


def register_credential_info(type, credential_info):
    _credential_info[type] = credential_info
    builder = CredentialsMissingMessageBuilder(type)

    messages.register_error_result_message_builder(
        credential_info.exception, builder)


register_credential_info('login', login_info)
register_credential_info('secrets', secrets_info)
register_credential_info('azure', azure_info)
# Setup synonym.
_credential_info['secret'] = _credential_info['secrets']
_instance = None


def instance():
    global _instance
    if _instance is None:
        _instance = CredentialManager()
    return _instance
