#    See the NOTICE file distributed with this work for additional information
#    regarding copyright ownership.
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#        http://www.apache.org/licenses/LICENSE-2.0
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


import logging
import os
from email.mime.text import MIMEText
from smtplib import SMTP

import deprecation
import pkg_resources
import pwd

# retro compatibility, force import methods from actual perl_utils module
from ensembl.production.core.perl_utils import \
    dict_to_perl_string as pdict_to_perl_string, \
    perl_string_to_python as pperl_string_to_python, \
    escape_perl_string as pescape_perl_string, \
    list_to_perl_string as plist_to_perl_string

__version__ = pkg_resources.require("ensembl-prodinf-core")[0].version


@deprecation.deprecated(deprecated_in="2.0.2", removed_in="3.0.0",
                        current_version=__version__,
                        details="Use the ensembl.production.core.perl_utils.perl_string_to_python instead")
def perl_string_to_python(s):
    return pperl_string_to_python(s)


@deprecation.deprecated(deprecated_in="2.0.2", removed_in="3.0.0",
                        current_version=__version__,
                        details="Use the ensembl.production.core.perl_utils.dict_to_perl_string instead")
def dict_to_perl_string(input_dict):
    return pdict_to_perl_string(input_dict)


@deprecation.deprecated(deprecated_in="2.0.2", removed_in="3.0.0",
                        current_version=__version__,
                        details="Use the ensembl.production.core.perl_utils.list_to_perl_string instead")
def list_to_perl_string(input_list):
    return plist_to_perl_string(input_list)


@deprecation.deprecated(deprecated_in="2.0.2", removed_in="3.0.0",
                        current_version=__version__,
                        details="Use the ensembl.production.core.perl_utils.escape_perl_string instead")
def escape_perl_string(s):
    return pescape_perl_string(s)


def get_default_user():
    """Method to obtain the current user. This can be complicated when running Docker containers"""
    default_user = None
    for name in ('LOGNAME', 'USER', 'LNAME', 'USERNAME'):
        user = os.environ.get(name)
        if user:
            default_user = user
            break
    if not default_user:
        default_user = pwd.getpwuid(os.getuid()).pw_name
    return default_user


def send_email(**kwargs):
    """ Utility method for sending an email"""
    logger = kwargs.get('logger', logging)
    from_address = kwargs.get('from_email_address', 'ensembl-production@ebi.ac.uk')
    msg = MIMEText(kwargs['body'])
    msg['Subject'] = kwargs['subject']
    msg['From'] = from_address
    msg['To'] = kwargs['to_address']
    smtp_server = kwargs.get('smtp_server', 'localhost')
    to_address = kwargs['to_address']
    logger.debug(
        'sendmail server: {} - Message from: {}, to: {}, subject: {}'.format(smtp_server, from_address, to_address,
                                                                             msg['Subject']))
    s = SMTP(smtp_server)
    s.sendmail(from_address, (to_address,), msg.as_string())
    s.quit()


def json_decode_error_context(error):
    beg = max(0, error.pos - 25)
    end = min(len(error.doc), error.pos + 25)
    return f"{error}. --> {error.doc[beg:end]} <--"
