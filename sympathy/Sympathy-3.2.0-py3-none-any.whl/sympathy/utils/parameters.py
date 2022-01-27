# This file is part of Sympathy for Data.
# Copyright (c) 2021, Combine Control Systems AB
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
import copy

from .. platform import parameter_helper
from .. platform.parameter_helper import (
    ParameterRoot, ParameterGroup, update_list_dict)
from .. platform import parameter_types


def help_login_credential():

    return (
        'Can use the credential system for storing credentials '
        'outside of the node\'s configuration.\n'
        'For more information, see the Credentials section of the '
        'documentation.')


def help_encoding():
    return(
        'Encoding determines the translation between characters and bytes.\n'
        'Used when reading, writing files or communicating over a network.\n'
        'For more information, see the Encoding (Appendix) section of the '
        'documentation.')


def set_connection_from_string(string_parameter, connection_parameter):
    value = parameter_types.Connection(resource=string_parameter.value)
    connection_parameter.value = value


def set_string_from_connection(connection_parameter, string_parameter):
    string_parameter.value = connection_parameter.value.resource


def _with_help(description, help):
    if description:
        return f'{description}\n\n{help}'
    return help


def _with_credential_help(description):
    return _with_help(description, help_login_credential())


sqlalchemy_connection_name = 'sqlalchemy_connection'
odbc_connection_name = 'odbc_connection'
url_connection_name = 'url_connection'
azure_connection_name = 'azure_connection'


def set_sqlalchemy_connection(parameters):
    parameters.set_connection(
        sqlalchemy_connection_name, label='Engine',
        editor=parameter_helper.Editors.connection_editor(),
        description=_with_credential_help(
            'SQLAlchemy engine URL for connecting to the database'),
        value=parameter_types.Connection(
            resource='mssql+pyodbc:///'))


def set_odbc_connection(parameters):
    parameters.set_connection(
        odbc_connection_name, label='Connection string',
        description=_with_credential_help(
            'A connection string that will override other settings.'),
        editor=parameter_helper.Editors.connection_editor(),
        value=parameter_types.Connection(resource=''))


def set_url_connection(parameters, resource=''):
    parameters.set_connection(
        url_connection_name, label='URL',
        editor=parameter_helper.Editors.connection_editor(),
        description=_with_credential_help(
            'Uniform Resource Locator (URL)'),
        value=parameter_types.Connection(resource=resource))


def set_azure_connection(parameters, client, label=None, description=None):
    description = description or 'Azure credentials'
    parameters.set_connection(
        azure_connection_name, label=label,
        editor=parameter_helper.Editors.azure_connection_editor(),
        description=_with_credential_help(description),
        value=parameter_types.Connection(
            resource=client,
            credentials=parameter_types.Credentials(
                mode=parameter_types.CredentialsMode.azure)))


def encoding_editor(include=None, placeholder=None):
    options = {
        'ascii': 'US English (ASCII)',
        'iso-8859-1': 'Western Europe (ISO 8859-1)',
        'iso-8859-15': 'Western Europe (ISO 8859-15)',
        'windows-1252': 'Western Europe (Windows 1252)',
        'utf-8': 'All languages (UTF-8)',
        'utf-16-be': 'All languages (UTF-16 BE)',
        'utf-16-le': 'All languages (UTF-16 LE)',
        'utf-16': 'All languages (UTF-16)',
    }

    if include:
        options = {k: v for k, v in options.items() if k in include}
    return parameter_helper.Editors.combo_editor(
        options=options, edit=True, placeholder=placeholder)


def set_encoding(parameters,  value='utf-8', label='Encoding',
                 description=None, include=None, placeholder=None):
    parameters.set_string(
        'encoding', label=label,
        description=_with_help(description, help_encoding()),
        editor=encoding_editor(include=include, placeholder=placeholder),
        value=value)


def update_parameters(old_params, definition_params):
    """
    Update parameters of old nodes.
    """
    def default_list_params_update(old_params):
        type_ = old_params.get('type')
        if type_ == 'list':
            if bool(old_params['value']) != bool(old_params['value_names']):
                update_list_dict(old_params)
        for key in old_params:
            if isinstance(old_params[key], dict):
                default_list_params_update(old_params[key])

    def default_params_update(definition_params, old_params):
        type_ = old_params.get('type')
        for key in definition_params:
            if key == 'type':
                continue
            elif (key in ('order', 'label', 'description') and
                    key in definition_params and
                    old_params.get(key) != definition_params[key]):
                old_params[key] = definition_params[key]
            elif (type_ == 'list' and
                    key == 'list' and
                    definition_params[key] and
                    old_params.get(key) != definition_params[key]):
                old_params[key] = definition_params[key]
                list_ = old_params['list']
                old_params['value'] = [
                    list_.index(n) for n in old_params['value_names']
                    if n in list_]
            elif key not in old_params:
                old_params[key] = definition_params[key]
            elif (isinstance(definition_params[key], dict) and
                    isinstance(old_params[key], dict) and
                    not (type_ == 'json' and key == 'value')):
                default_params_update(definition_params[key], old_params[key])

    if isinstance(definition_params, ParameterGroup):
        definition_params = definition_params._parameter_dict

    # We need to make sure that definition parameters have correct values
    # for 'order'. The call to reorder will fix that, but does so by
    # mutating the parameter dictionary, so we make a copy of the
    # dictionary to avoid unwanted side-effects.
    definition_params = copy.deepcopy(definition_params)
    ParameterRoot(definition_params, gui_visitor=True).reorder()

    if isinstance(old_params, ParameterGroup):
        old_params = old_params._parameter_dict
    default_list_params_update(old_params)
    default_params_update(definition_params, old_params)
