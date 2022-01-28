import socket
from datetime import datetime

from .schemas import ExtensionFields, MandatoryFields


class Fields:

    BASE_HEADER_TPL = 'CEF:{Version}|{DeviceVendor}|{DeviceProduct}|' \
                      '{DeviceVersion}|{DeviceEventClassID}|{Name}|{Severity}|'
    EXTENSIONS_TPL = '{ext}={value} '

    def __init__(self, syslog_flag: bool = False, **fields):
        self._syslog_flag = syslog_flag

        self.mandatory = {}
        self.extensions = {}
        self.custom = {}

        for key, value in fields.items():
            if key in MandatoryFields.__fields__:
                self.mandatory[key] = value
            elif key in ExtensionFields.__fields__:
                self.extensions[key] = value
            else:
                self.custom[key] = value

    @property
    def all(self):
        return {**self.mandatory, **self.extensions, **self.custom}

    def render(self):
        syslog_header = self.render_syslog_header()
        base_header = self.render_base_header()
        extensions = self.render_extensions()
        return syslog_header + base_header + extensions

    def validate(self):
        fields = self._calculate_dynamic_fields(**self.all)

        MandatoryFields(**fields)
        ExtensionFields(**fields)

    def render_syslog_header(self):

        # Workaround for mac systems (https://bugs.python.org/issue35164)
        # To set hostname use: sudo scutil --set HostName `hostname`
        try:
            hostname = socket.getfqdn()
        except socket.gaierror:
            hostname = 'localhost'

        header = ''

        if self._syslog_flag:
            timestamp = datetime.utcnow().isoformat() + '+00:00'
            header = f'{timestamp} {hostname} '

        return header

    def render_base_header(self):
        escaped = self._escape_base_fields(**self.mandatory)
        return self.BASE_HEADER_TPL.format(**escaped)

    def render_extensions(self):
        ext_string = ''
        escaped_ext = self._escape_extensions_fields(**self.extensions)
        escaped_custom = self._escape_extensions_fields(**self.custom)

        for ext, value in {**escaped_ext, **escaped_custom}.items():
            ext_string += self.EXTENSIONS_TPL.format(ext=ext, value=value)

        return ext_string.rstrip(' ')

    def _escape_base_fields(self, **fields):
        fields = self._calculate_dynamic_fields(**fields)

        for key, value in fields.items():
            if isinstance(value, str):
                value = value.replace('\r\n', '')
                value = value.replace('\r', '')
                value = value.replace('\n', '')
                value = value.replace('\\', '\\\\')
                value = value.replace('|', r'\|')
                fields[key] = value

        return fields

    def _escape_extensions_fields(self, **fields):
        fields = self._calculate_dynamic_fields(**fields)
        fields = self._replace_none_with_empty(**fields)

        for key, value in fields.items():
            if isinstance(value, str):
                value = value.replace('\\', '\\\\')
                value = value.replace('=', r'\=')
                fields[key] = value

        return fields

    def _replace_none_with_empty(self, **fields):
        for key, value in fields.items():
            if value is None:
                fields[key] = ''
        return fields

    def _calculate_dynamic_fields(self, **fields):
        for key, value in fields.items():

            if not isinstance(value, (bool, int, str, list,
                                      tuple, set, dict, type(None))):
                fields[key] = str(value)

        return fields
