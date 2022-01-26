import os.path
from enum import IntEnum
import datetime
import ipaddress
import secrets
import sys
from typing import Optional
import re
import getpass

from OpenSSL import crypto
from OpenSSL.SSL import FILETYPE_PEM

"""
The RegEx to match a domain. Examples :
  - wiki
  - wiki.internal-domain.lan
  - *.sub.internal-domain.lan
"""
regex_domain = re.compile(r'^(\*\.)?([a-zA-Z0-9_-]+\.?)+$')

"""
The RegEx to match a Subject Alternate Name.

  - DNS: host, DNS: host2.domain.lan, IP: 10.0.0.1, IP: 2001:0db8:85a3:0000:0000:8a2e:0370:7334
"""
regex_san = re.compile(r'^(('
                       r'(DNS:[ ]?((\*\.)?([a-zA-Z0-9_-]+\.?))+)'  # DNS, see regex_domain
                       r'|'
                       r'(IP:[ ]?('  # IPv4
                       r'((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))'
                       r'|'  # or IPv6
                       r'((?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4})'
                       r')))'
                       r'(,?[ ]?))+'  # Followed by "," or ", "
                       r'(?<![ ,])$')  # But the string cannot be ending with "," or ", "

"""
The RegEx for the Common Name : host or IPv4 or IPv6
"""
regex_cn = re.compile(r'^(((\*\.)?([a-zA-Z0-9_-]+\.?)+)|'
                      r'((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))|'
                      r'((?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}))$')


def ask(prompt: str, values: Optional[list] = None, disable_show_values: bool = False, can_be_empty: bool = False,
        disable_lowering: bool = False) -> Optional[str]:
    """
    Ask the user for an input.

    The prompt is written to stdout and the value is read from stdin.

    The prompt will be like that :
        "<prompt message> : "
        "<prompt message> (<value 1>, <value 2>, <value 3>) : "

    The optional disable_show_values parameter disable showing values in the prompt.

    The optional values parameter is the fixed list of the authorized values. If defined, the prompt is asking until the
    user is entering one of these values.

    The optional can_be_empty parameter allows the user to not enter a value but send back a empty value.

    By default, the input string is lower(). If you doesn't want that, you can use the disable_lowering parameter.

    :param prompt: the prompt message
    :param values: the list of valid values
    :param disable_show_values: disable showing values
    :param can_be_empty: indicate if the response can be empty
    :param disable_lowering: disable the lower() of the response
    :return: the user response
    """
    if values:
        values = [str(v).lower() for v in values]

        if not disable_show_values:
            prompt += f' ({", ".join(values)})'

    prompt += ' : '

    while True:
        print(prompt, end='')
        answer = input().strip()
        answer_lower = answer.lower()

        if values:
            if answer_lower in values or (can_be_empty and len(answer) == 0):
                break
        else:
            if (len(answer) == 0 and can_be_empty) or len(answer) > 0:
                break

    if len(answer) == 0:
        return None

    if disable_lowering:
        return answer
    else:
        return answer_lower


class PEMFormatType(IntEnum):
    """
    The PEM type
    """
    CERT = 1
    KEY = 2
    CSR = 3


def ask_pem_format(prompt: str, pem_type: PEMFormatType) -> Optional[str]:
    """
    Ask the user for data in the PEM format.

    The targeted data is providing through the pem_type parameter.

    This function accepts multi-line PEM. The first line must be the ASCII armored definition "----- BEGIN...". This
    function will stop reading from stdin when the the "----- END..." is reached.

    The PEM data is not checked.

    :param prompt: the prompt message
    :param pem_type: the PEM format type
    :return: the entered PEM data
    """
    answer = ''

    prompt += ' :'
    print(prompt)

    if pem_type == PEMFormatType.CERT:
        re_start_line = re.compile('-----BEGIN CERTIFICATE-----')
        re_end_line = re.compile('-----END CERTIFICATE-----')
    elif pem_type == PEMFormatType.KEY:
        re_start_line = re.compile('-----BEGIN (RSA )?PRIVATE KEY-----')
        re_end_line = re.compile('-----END (RSA )?PRIVATE KEY-----')
    elif pem_type.CSR:
        re_start_line = re.compile('-----BEGIN CERTIFICATE REQUEST-----')
        re_end_line = re.compile('-----END CERTIFICATE REQUEST-----')
    else:
        raise RuntimeError(f'PEM type {pem_type} not supported')

    end_line_detected = False
    first = True
    while 1:
        try:
            line = sys.stdin.readline()
        except KeyboardInterrupt:
            break

        if first:
            first = False
            if not re_start_line.match(line.rstrip()):
                raise ValueError('No or bad start line')

        answer += line

        if re_end_line.match(line.rstrip()):
            end_line_detected = True
            break

    if not end_line_detected:
        raise ValueError('No end line detected')

    return answer


def ask_date_in_future() -> datetime.date:
    """
    Ask the user for a date in the future.

    If an error is detected, the error is written on stdout and the same question is prompted again.

    :return: the date
    """
    error = True
    d = ''

    while error:
        d = ask('Enter a date in the future (DD/MM/YYYY)')

        try:
            d = datetime.datetime.strptime(d, '%d/%m/%Y').date()

            if d < datetime.date.today():
                print(f'\tThe date must be in the future')
            else:
                error = False
        except ValueError:
            print(f'\t{d} is invalid')

    return d


def ask_cn() -> str:
    """
    Ask the user for Common Name.

    The user can enter 1 host or IP.

    If an error is detected, the error is written on strerr and the same question is prompted again.

    :return: the CN
    """
    error = True
    cn = ''

    while error:
        cn = ask('Common Name')

        if not regex_cn.match(cn):
            print(f'\t{cn} is invalid')
        else:
            error = False

    return cn


def ask_hosts() -> [str]:
    """
    Ask the user for hosts.

    The user can enter 0, 1 or n hosts separated by a comma. The host value can be :
        * the hostname : wiki
        * the FQDN : wiki.internal-domain.lan
        * the * wildcard : *.sub.internal-domain.lan

    If an error is detected, the error is written on strerr and the same question is prompted again.

    :return: the hosts
    """
    error = True
    domains = set()

    while error:
        input_domains = ask('Enter alternative names separated by a comma (eg: srv.internal.lan)', can_be_empty=True)
        domains.clear()

        if not input_domains or len(input_domains) == 0:
            break

        error = False
        for d in input_domains.split(','):
            d = d.strip()

            if regex_domain.match(d):
                try:
                    ipaddress.ip_address(d)
                    error = True
                    print(f'\t{d} is an IP address')
                except ValueError:
                    domains.add(d)
            else:
                error = True
                print(f'\t{d} is invalid')

    return list(sorted(domains))


def ask_ips() -> [str]:
    """
    Ask the user for IP addresses.

    The user can enter 0, 1 or n IP addresses separated by a comma. IPv4 and IPv6 are supported.

    If an error is detected, the error is written on strerr and the same question is prompted again.

    :return: the IPs
    """
    error = True
    ips = set()

    while error:
        input_ips = ask('Enter IPs separated by a comma (eg: 10.0.0.1, 10.254.0.1)', can_be_empty=True)
        ips.clear()

        if not input_ips or len(input_ips) == 0:
            break

        error = False
        for ip in input_ips.split(','):
            ip = ip.strip()

            try:
                ipaddress.ip_address(ip)
                ips.add(ip)
            except ValueError:
                error = True
                print(f'\t{ip} is invalid')

    return list(sorted(ips))


def ask_cn_and_san() -> (str, str):
    """
    Ask the user for the CN, the alternative hosts and alternative IPS.

    :return: the CN and the build SAN
    """
    cn = ask_cn()
    alternate_hosts = ask_hosts()
    alternate_ips = ask_ips()

    try:  # CN is IP
        ipaddress.ip_address(cn)
        alternate_ips.append(cn)
    except ValueError:
        alternate_hosts.append(cn)

    san = [f'DNS:{h}' for h in alternate_hosts]
    san += [f'IP:{i}' for i in alternate_ips]
    san = ', '.join(san)

    return cn, san


def confirm(prompt: str) -> bool:
    """
    Ask user to enter Y or N (case-insensitive) to confirm an action.

    :param prompt: the prompt message
    :return: True if the answer is Y.
    """
    return ask(f'{prompt} ? [y/n]', ['y', 'n'], disable_show_values=True) == 'y'


def ask_password(prompt: str) -> str:
    """
    Ask (securely) the user to enter a password.

    :param prompt: the prompt message
    :return: the password encoded
    """
    prompt += ' : '

    return getpass.getpass(prompt)


def ask_private_key_passphrase(*args) -> str:
    """
    Ask the user for the private key passphrase.

    :param args:
    :return: the passsphrase
    """
    return ask_password('Enter the private key passphrase')


def generate_random_serial_number() -> int:
    """
    Generate (securely) a random serial number for a certificate [0, 2^64].
    
    :return: the serial number
    """
    return secrets.randbelow(2 ** 64)


def get_cert_san(cert: crypto.X509) -> Optional[str]:
    """
    Get the Subject Alternative Name from a certificate object.

    :param cert: the certificate
    :return: the SAN if defined
    """
    for i in range(0, cert.get_extension_count()):
        if cert.get_extension(i).get_short_name() == b'subjectAltName':
            return str(cert.get_extension(i)).replace('IP Address', 'IP')

    return None


def get_csr_san(csr: crypto.X509Req) -> Optional[str]:
    """
    Get the Subject Alternative Name from a certificate signing request object.

    :param csr: the certificate signing request
    :return: the SAN if defined
    """
    for ext in csr.get_extensions():
        if ext.get_short_name() == b'subjectAltName':
            return str(ext).replace('IP Address', 'IP')

    return None


def get_csr_cn(csr: crypto.X509Req) -> str:
    """
    Get the Common Name from a certificate signing request object.

    :param csr: the certificate signing request
    :return: the CN
    """
    return csr.get_subject().CN


def define_san(cert_or_csr: crypto.X509 or crypto.X509Req, san: str):
    """
    Define the Subject Alternative Name for a certificate or a certificate signing request.

    :param cert_or_csr: a certificate or a certificate signing request.
    :param san: the Subject Alternative Name
    :return:
    """
    if not regex_san.match(san):
        raise ValueError(f'The SAN "{san}" is invalid')

    san_already_defined = False
    if isinstance(cert_or_csr, crypto.X509):
        if get_cert_san(cert_or_csr):
            san_already_defined = True
    else:
        if get_csr_san(cert_or_csr):
            san_already_defined = True

    if san_already_defined:
        raise RuntimeError('Cannot define SAN because the extension is already defined')

    cert_or_csr.add_extensions([
        crypto.X509Extension(b'subjectAltName',
                             False,
                             san.encode('utf8'))])

    return cert_or_csr


def validate_or_build_san(cn: str, san: Optional[str]) -> str:
    """
    Validate the Subject Alternative Name depending on the Common Name. If the SAN is empty, this function creates one
    depending of the Common Name.

    :param cn: the Common Name
    :param san: the optional Subject Alternative Name
    :return: the final Subject Alternative Name
    """
    # Checking the the CN is an IP address or a hostname
    try:
        ipaddress.ip_address(cn)
        cn_is_ip = True
    except ValueError:
        cn_is_ip = False

    if san:
        values = [val.strip().replace(' ', '') for val in san.split(',')]
    else:
        values = []

    if cn_is_ip:
        cn_san = f'IP:{cn}'
    else:
        cn_san = f'DNS:{cn}'

    if cn_san not in values:
        values.append(cn_san)

    san = ', '.join(values)

    if not regex_san.match(san):
        raise ValueError(f'The SAN "{san}" is invalid')

    return san


def get_cert_text(cert: crypto.X509) -> str:
    """
    Get the text version of a certificate object.

    :param cert: the certificate
    :return: the text version
    """
    return crypto.dump_certificate(2 ** 16 - 1, cert).decode('utf8')


def get_csr_text(csr: crypto.X509Req) -> str:
    """
    Get the text version of a certificate signing request object.

    :param csr: the certificate signing request
    :return: the text version
    """
    return crypto.dump_certificate_request(2 ** 16 - 1, csr).decode('utf8')


def get_private_key_text(key: crypto.PKey) -> str:
    """
    Get the text version of a private key object.

    :param key: the private key
    :return: the text version
    """
    return crypto.dump_privatekey(2 ** 16 - 1, key).decode('utf8')


def nb_seconds_to_date(expire_date: datetime.date) -> int:
    """
    Compute the number of seconds between now and the expired date. Note that the date is given without the time part
    so we use the current hours/minutes/seconds.

    :param expire_date: the expire date
    :return: the number of seconds
    """
    if expire_date < datetime.date.today():
        raise ValueError('The expire date is not in the future')

    expire_dt = datetime.datetime.now().replace(year=expire_date.year, month=expire_date.month, day=expire_date.day)
    return int((expire_dt - datetime.datetime.now()).total_seconds())


def print_tabulated(text: str) -> None:
    """
    Print the text with one tabulation.

    :param text: the text to print
    """

    text = '\t' + text.replace('\n', '\n\t')
    print(text)


def write_cert_pem(cert: crypto.X509, filepath: str):
    """
    Write the certificate in PEM format into the provided filepath.

    If the file already exists, a RuntimeError is raised.

    :param cert: the certificate
    :param filepath: the target filepath
    """
    if os.path.exists(filepath):
        raise RuntimeError(f'The filepath "{filepath}" already exists')

    with open(filepath, 'w') as f:
        f.write(crypto.dump_certificate(FILETYPE_PEM, cert).decode('utf8'))


def write_private_key_pem(key: crypto.PKey, filepath: str):
    """
    Write the private key in PEM format into the provided filepath.

    If the file already exists, a RuntimeError is raised.

    :param key: the private key
    :param filepath: the target filepath
    """
    if os.path.exists(filepath):
        raise RuntimeError(f'The filepath "{filepath}" already exists')

    with open(filepath, 'w') as f:
        f.write(crypto.dump_privatekey(FILETYPE_PEM, key).decode('utf8'))


def write_p12(filepath: str, passphrase: str, cert: crypto.X509, key: Optional[crypto.PKey] = None):
    """
    Write the certificate (and the private key if provided) in PKCS12 format.

    If the file already exists, a RuntimeError is raised.

    :param cert: the certificate
    :param filepath: the target filepath
    :param passphrase: the password
    """
    if os.path.exists(filepath):
        raise RuntimeError(f'The filepath "{filepath}" already exists')

    if len(passphrase) == 0:
        raise ValueError('The provided passphrase is empty')

    crypto.PKCS12()
    pfx = crypto.PKCS12()
    pfx.set_certificate(cert)

    if key:
        pfx.set_privatekey(pfx)

    pfx_data = pfx.export(passphrase)
    with open(filepath, 'wb') as f:
        f.write(pfx_data)
