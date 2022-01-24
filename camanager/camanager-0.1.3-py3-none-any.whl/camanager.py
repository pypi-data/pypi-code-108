
import os
import sys
import datetime
from typing import Optional
import re

from peewee import DatabaseError
from OpenSSL import crypto
from OpenSSL.SSL import FILETYPE_PEM

from .models import CA, Config, ConfigType, Certificate, CRL, database, DATABASE_FILENAME
from .utils import ask_pem_format, ask_private_key_passphrase, get_csr_san, generate_random_serial_number, \
     get_cert_text, get_csr_text, define_san, PEMFormatType, validate_or_build_san, regex_domain, confirm, ask, \
     ask_password, ask_date_in_future, nb_seconds_to_date, print_tabulated, \
     get_csr_cn, write_cert_pem, write_private_key_pem, write_p12, ask_cn_and_san

"""
Valid key sizes
"""
VALID_KEY_SIZES = [1024, 2048, 4096, 8192]

"""
Valid hash algorithms
"""
VALID_HASH_ALGOS = ['sha1', 'sha256', 'sha512']


class CAManager:
    """
    Certificate Authority Manager
    """
    def __init__(self):
        """
        Constructor.

        By default, the manager is not loaded. This is useful for the first start because the vault must be created.
        """
        self.ca_name = 'Default'

        # Containing the Certificate Authority when loaded from the vault
        self.ca = None

    def create_vault(self, vault_password: Optional[str] = None) -> None:
        """
        Setup the vault for the first use.

        The vault cannot be existing. The user is prompted to enter :
            - a password to encrypt the vault
            - the CA certificate
            - the CA key (and the password protecting the key if any)
        """
        if os.path.isfile(DATABASE_FILENAME):
            sys.stderr.write(f'Vault "{DATABASE_FILENAME}" is already existing\n')
            exit(-1)

        vault_password = ask_password('Enter the password that will be used to encrypt the CA vault')
        vault_password_confirm = ask_password('Confirm it')

        if vault_password != vault_password_confirm:
            sys.stderr.write(f'The two provided passwords are not matching\n')
            exit(-1)

        database.init(DATABASE_FILENAME, passphrase=vault_password)

        with database:
            # Create table
            database.create_tables([CA, Certificate, CRL, Config])

            # Read CA pem from stdin
            try:
                pem_ca_cert = ask_pem_format('Paste your CA certificate in PEM format', PEMFormatType.CERT)
                ca_cert = crypto.load_certificate(FILETYPE_PEM, pem_ca_cert.encode('utf8'))
            except ValueError:
                sys.stderr.write(f'Invalid PEM certificate')
                exit(-1)
            except crypto.Error as e:
                sys.stderr.write(f'Invalid PEM certificate. OpenSSL returns with an error.')
                exit(-1)

            # Read CA key from stdin
            try:
                pem_ca_key = ask_pem_format('Paste your CA key in PEM format', PEMFormatType.KEY)
                ca_key = crypto.load_privatekey(FILETYPE_PEM, pem_ca_key.encode('utf8'),
                                                passphrase=ask_private_key_passphrase)
            except ValueError:
                sys.stderr.write(f'Invalid PEM key')
                exit(-1)
            except crypto.Error as e:
                sys.stderr.write(f'Invalid PEM key. OpenSSL returns with an error.')
                exit(-1)

            # Check CA cert and key correspondence
            if crypto.dump_publickey(FILETYPE_PEM, ca_cert.get_pubkey()) != crypto.dump_publickey(FILETYPE_PEM, ca_key):
                sys.stderr.write(f'The certificate and the private key are not corresponding')
                exit(-1)

            # Create the CA in the database
            CA.create(
                name=self.ca_name,
                cert=pem_ca_cert,
                key=pem_ca_key,
            )

            # Create the config
            Config.create(
                name='default_key_size',
                type=ConfigType.INT,
                value=4096
            )

            Config.create(
                name='default_hash_algo',
                type=ConfigType.STRING,
                value='sha256'
            )

            Config.create(
                name='default_validity_seconds',
                type=ConfigType.INT,
                value=3 * 365 * 24 * 60 * 60  # 3 years
            )

        print('The vault has been successfully created.')

    def load(self):
        """
        Load the vault.

        The password is asking.
        """
        if not os.path.isfile(DATABASE_FILENAME):
            sys.stderr.write('The vault doesn\'t exist yer. Please run with --setup to initialize it.\n')
            exit(-1)

        # Ask the vault password and initialize the database with it
        database.init(DATABASE_FILENAME, passphrase=ask_password('Enter the CA vault password'))

        try:
            database.get_tables()
        except DatabaseError as exc:
            if exc.args[0] == 'file is not a database':
                database.init(None)

                sys.stderr.write('The provided password is incorrect\n')
                exit(-1)
            else:
                raise exc

    @database.connection_context()
    def list(self, all_certificates: bool = False, only_soon_expired: bool = False):
        """
        Print the list of managed certificates.

        :param all_certificates: also the revoked/expired/renewed certificates
        :param only_soon_expired: only the soon expired certificates
        """
        if all_certificates and only_soon_expired:
            raise RuntimeError('Cannot use all and only_soon_expired')

        certs = Certificate.select()

        if only_soon_expired:
            now = datetime.datetime.now()
            next_month = now + datetime.timedelta(days=31)

            certs = certs.where((Certificate.is_renewed == False) & (Certificate.not_after >= now) &
                                (Certificate.not_after <= next_month) & (Certificate.is_revoked == False))
        elif not all_certificates:
            certs = certs.where((Certificate.is_revoked == False) & (Certificate.is_renewed == False) &
                                (Certificate.not_after > datetime.datetime.now()))

        nb_certs_found = certs.count()

        if nb_certs_found == 0:
            print('No certificate found')
        else:
            print(f'{nb_certs_found} {"certificate" if nb_certs_found < 2 else "certificates"} found :')

            for c in certs.iterator():
                print(f'\t{c}')

    def generate_new_cert(self, cn: Optional[str] = None, san: Optional[str] = None, keysize: Optional[int] = None,
                          hashalgo: Optional[str] = None, expire_date: Optional[str] = None) -> None:
        """
        Generate a new certificate.

        The method accepts parameter that are only be processed if the "cn" is defined. If none of the parameters are
        supplied, the method is interactive and asks the user for the information.

        :param cn: the Common Name
        :param san: Subject Alternative Name
        :param keysize: the keysize
        :param hashalgo: the hash algorithm
        :param expire_date: the expire date
        """

        if not cn:  # The CN is not defined, we're going into interactive mode
            if not confirm(f'Use default params ({self._get_config("default_key_size")} bits - '
                           f'{self._get_config("default_hash_algo")})'):
                keysize = int(ask('Key size', values=VALID_KEY_SIZES))
                hashalgo = ask('Hash algorithm', values=VALID_HASH_ALGOS)

            cn, san = ask_cn_and_san()

            nb_days = self._get_config("default_validity_seconds")
            not_after = datetime.date.today() + datetime.timedelta(seconds=nb_days)
            if not confirm(f'Use the default validity (will expire on {not_after.strftime("%d/%m/%Y")}'):
                expire_date = ask_date_in_future()

        try:
            cert, certificate = self._generate_signed_cert(cn, san, keysize, hashalgo, expire_date, ask_confirm=True)

            print('Certificate successfully created !\n')

            print(get_cert_text(cert), end='')
            print(certificate.cert)
            print(certificate.key)
        except (ValueError, RuntimeError) as e:
            sys.stderr.write(f'Error: {e}.\n')
            sys.stderr.write(f'The certificate cannot be created.\n')
            exit(-1)

    def sign_csr(self, csr_filepath: Optional[str] = None, cn: Optional[str] = None, san: Optional[str] = None,
                 expire_date: Optional[str] = None) -> None:
        """
        Sign a certificate.

        If the filepath is not provided, the content is read from stdin.

        The method accepts parameter that will override the CSR content.

        :param csr_filepath: the Certificate Signing Request filepath
        :param cn: the Common Name
        :param san: Subject Alternative Name
        :param expire_date: the expire date
        """

        if csr_filepath:
            if not os.path.exists(csr_filepath):
                sys.stderr.write(f'The file "{csr_filepath}" doesn\'t exist\n')
                exit(-1)

            with open(csr_filepath, 'rb') as f:
                csr_content = f.read()
        else:
            csr_content = ask_pem_format('Paste your CSR in PEM format', PEMFormatType.CSR).encode('utf8')

        csr = None
        try:
            csr = crypto.load_certificate_request(FILETYPE_PEM, csr_content)
        except ValueError:
            sys.stderr.write(f'Invalid PEM CSR')
            exit(-1)
        except crypto.Error as e:
            sys.stderr.write(f'Invalid PEM CSR. OpenSSL returns with an error.')
            exit(-1)

        print('You\'re going to process the following Certificate Signing Request :\n')
        print_tabulated(get_csr_text(csr))

        default_cn = get_csr_cn(csr)
        default_san = get_csr_san(csr)

        print('\nThis CSR apply to :')
        print(f'\tCommon Name : {default_cn}')
        print(f'\tSubject Alternative Name : {default_san if default_san else "*** not defined ***"}\n')

        print('Please note that the CN will automatically be added to the SAN if it is missing.\n')

        if not cn and not san:
            if confirm(f'Do you want to overwrite theses values'):
                cn, san = ask_cn_and_san()

        if cn and cn != default_cn or san and san != default_san:
            print('\nYou will overwrite the following values :')

            if cn and cn != default_cn:
                print(f'\tCommon Name : {cn}')

            if san and san != default_san:
                print(f'\tSubject Alternative Name : {san}')

        try:
            print('')
            cert, certificate = self._sign_csr(csr, overwrite_cn=cn, overwrite_san=san, ask_confirm=True)

            print('Certificate successfully signed !\n')

            print(get_cert_text(cert), end='')
            print(certificate.cert)

        except (ValueError, RuntimeError) as e:
            sys.stderr.write(f'Error: {e}.\n')
            sys.stderr.write(f'The certificate cannot be signed.')

    @database.connection_context()
    def renew(self, target_certificate: str):
        """
        Renew a certificate.

        :param target_certificate: CN or ID of the certificate
        """
        certificate = self.select_certificate(target_certificate)
        certificate.load_cert()
        pub_key = certificate.cert_obj.get_pubkey()

        # Generate CSR
        req = crypto.X509Req()
        req.get_subject().CN = certificate.cn
        req.set_pubkey(pub_key)

        # Define the SAN
        define_san(req, certificate.san)

        try:
            # Sign the CSR
            signed_cert, vault_certificate = self._sign_csr(req, ask_confirm=True, disable_cert_existence_check=True)

            # Set the previous certificate as renewed
            certificate.is_renewed = True
            certificate.save()

            # Save the private key for the new certificate
            vault_certificate.key = certificate.key
            vault_certificate.save()

            print('Certificate renewed successfully !\n')

            vault_certificate.load_cert()
            print(get_cert_text(vault_certificate.cert_obj), end='')
            print(vault_certificate.cert)

        except (ValueError, RuntimeError) as e:
            sys.stderr.write(f'Error: {e}.\n')
            sys.stderr.write(f'The certificate cannot be renewed.\n')
            exit(-1)

    def export(self, target_certificate: str, output_format: str, out_path: Optional[str]):
        """
        Export the certificate and its private key if available.

        If the output_format is "pem", the data is exported to a file if the out_path is provided (the file extension
        .pem is added for the certificate and .key for the key). If no out_path is provided, the data is printed to
        stdout.

        If the output_format is "p12", the data is exported to the out_path. If the out_path doesn't have the ".p12"
        extension, this method add the extension. The p12_passphrase must be provided.

        :param target_certificate: the certificate CN or ID
        :param output_format: the output format : "pem" or "p12"
        :param out_path: the output path
        """
        if output_format not in ('pem', 'p12'):
            raise ValueError(f'Output format "{output_format}" not supported')

        certificate = self.select_certificate(target_certificate)

        print(f'You\'re going to export the certificate {certificate}...')

        p12_passphrase = None
        if output_format == 'p12':
            p12_passphrase = ask_password('Enter the password that will be used protect the .p12')
            p12_passphrase_confirm = ask_password('Confirm it')

            if p12_passphrase != p12_passphrase_confirm:
                sys.stderr.write(f'The two provided passwords are not matching\n')
                exit(-1)

        try:
            self._export(certificate, output_format, out_path, p12_passphrase)
        except RuntimeError as e:
            sys.stderr.write(f'Error: {str(e)}\n')
            exit(-1)

    def _export(self, certificate: Certificate, output_format: str, out_path: Optional[str],
                p12_passphrase: Optional[str] = None):
        """
        Export the certificate and its private key if available.

        If the output_format is "pem", the data is exported to a file if the out_path is provided (the file extension
        .pem is added for the certificate and .key for the key). If no out_path is provided, the data is printed to
        stdout.

        If the output_format is "p12", the data is exported to the out_path. If the out_path doesn't have the ".p12"
        extension, this method add the extension. The p12_passphrase must be provided.

        :param certificate: the certificate
        :param output_format: the output format : "pem" or "p12"
        :param out_path: the output path
        :param p12_passphrase: the P12 passphrase
        """
        output_format = output_format.lower()
        if output_format not in ('pem', 'p12'):
            raise ValueError(f'Output format "{output_format}" not supported')

        if output_format == 'p12' and not out_path:
            raise ValueError('For the p12 format, the out_path must be specified')

        if output_format == 'p12' and not p12_passphrase:
            raise ValueError('For the p12 format, the p12_passphrase must be specified')

        certificate.load_cert()

        if certificate.key:
            certificate.load_key()

        if output_format == 'pem':
            if out_path:
                out_path_cert = out_path + '.pem'
                out_path_key = out_path + '.key'

                if os.path.exists(out_path_cert):
                    raise RuntimeError(f'The output certificate file "{out_path_cert}" already exists')

                if certificate.key:
                    if os.path.exists(out_path_key):
                        raise RuntimeError(f'The output private key file "{out_path_key}" already exists')

                write_cert_pem(certificate.cert_obj, out_path_cert)

                if certificate.key:
                    write_private_key_pem(certificate.key_obj, out_path_key)

                if certificate.key:
                    print(f'The certificate and its private key have been exported to {out_path}[.pem|.key]')
                else:
                    print(f'The certificate has been exported to {out_path}.pem. There is no private key linked.')
            else:
                print(certificate.cert)

                if certificate.key:
                    print(certificate.key)
                else:
                    print('There is no private key linked.')
        else:
            if not out_path.endswith('.p12'):
                out_path += '.p12'

            write_p12(out_path, p12_passphrase, certificate.cert_obj, certificate.key_obj)

            if certificate.key:
                print(f'The certificate and its private key have been exported to {out_path}')
            else:
                print(f'The certificate has been exported to {out_path}. There is no private key linked.')

        certificate.clear_key()

    def _load_ca(self):
        """
        Load the Certificate Authority from the vault
        """
        if self.ca:
            return

        self.ca = CA.get(CA.name == self.ca_name)
        if not self.ca:
            raise RuntimeError(f'Cannot find the CA with the name "{self.ca_name}"')

        self.ca.load_cert()

    def _get_ca_key(self) -> crypto.PKey:
        """
        Get the CA private key. If the key is passphrase protected, the user is prompted to enter it.
        After the key is retrieved, the CA key object is cleared from the self.ca.

        :return: the CA private key
        """

        if not self.ca:
            self._load_ca()

        self.ca.load_key()
        ca_key = self.ca.key_obj
        self.ca.clear_key()

        return ca_key

    def _get_config(self, config_name: str):
        """
        Get the value from a config parameter.

        The value is casted to the right type depending of the config parameter type in the vault.

        :param config_name: the config name
        :return: the value in int, string or bytes
        """
        c = Config.get_by_id(config_name)
        if not c:
            raise RuntimeError(f'The config name "{config_name}" is unknown')

        if c.type == ConfigType.INT:
            return int(c.value)
        elif c.type == ConfigType.STRING:
            return c.value
        elif c.type == ConfigType.BINARY:
            return c.value.decode('utf8')
        else:
            raise NotImplementedError(f'Config type "{c.type}" not implemented')

    @database.connection_context()
    def select_certificate(self, search_term: str) -> Certificate:
        """
        Select a certificate by specifying a search term or by giving the certificate ID.

        :param search_term: CN part or ID
        :return: the certificate
        """
        if re.match('^[0-9]+$', search_term):
            certificate = Certificate.get_by_id(int(search_term))
        else:
            now = datetime.datetime.now()
            certificates = Certificate.\
                select().where((Certificate.cn.contains(search_term)) & (Certificate.is_renewed == False) &
                               ((Certificate.is_revoked == False) & (Certificate.not_after >= now)))

            if certificates.count() == 1:
                certificate = certificates[0]
            else:
                if certificates.count() == 0:
                    print('No certificate found for this search. Listing all certificates :')
                    certificates = Certificate.select().where((Certificate.is_renewed == False) &
                                                      (Certificate.not_after > datetime.datetime.now()) &
                                                      (Certificate.is_revoked == False))
                else:
                    print(f'{certificates.count()} certificates found :')

                valid_ids = []
                for c in certificates:
                    valid_ids.append(c.id)
                    print_tabulated(str(c))

                print('')
                target_certificate = ask('Please enter the ID of one of these certificates', values=valid_ids)
                certificate = Certificate.get_by_id(int(target_certificate))

        return certificate

    @database.connection_context()
    def _sign_csr(self, csr: crypto.X509Req, overwrite_hashalgo: str = None, overwrite_cn: Optional[str] = None,
                  overwrite_san: Optional[str] = None, overwrite_expire: Optional[str] = None,
                  ask_confirm: bool = False, disable_cert_existence_check: bool = False) -> (crypto.X509, Certificate):
        """
        Sign the Certificate Signing Request with the Certificate Authority.

        The overwrite_hashalgo parameter can be used to overwrite the default hash algorithm.
        The overwrite_cn parameter can be used to overwrite the Common Name in the CSR.
        The overwrite_san parameter can be used to overwrite the Subject Alternative Name in the CSR.
        The overwrite_expire parameter can be used to overwrite the expire date (must be in the future).

        The SAN must always include an entry matching the CN. If the CSR doesn't contain a SAN, this method create it.

        A unique (and non already used) serial number is assigned to the certificate. The certificate is valid for time
        configured in the Config<default_validity_seconds>.

        This method save the certificate in the vault. Note that the private key is not saved because not known. The
        calling function must update the vault with the private key if needed.

        This method returns a tuple :
            * the certificate object
            * the certificate model instance

        :param csr: the Certificate Signing Request
        :param overwrite_hashalgo: the optional hash algorithm. See AVALAIBLE_HASHALGO.
        :param overwrite_cn: the optional Command Name that must be used
        :param overwrite_san: the optional Subject Alternative Name that must be used
        :param overwrite_expire: the optional expired date
        :param ask_confirm: the optional flag to print the CSR and ask the confirmation before continuing
        :param disable_cert_existence_check: disable the certificate existing check
        :return: (the OpenSSL certificate object, the Certificate model instance)
        """
        final_cn = overwrite_cn if overwrite_san else csr.get_subject().CN
        if not regex_domain.match(final_cn):
            raise ValueError(f'CN "{final_cn}" is invalid')

        final_san = validate_or_build_san(final_cn, overwrite_san if overwrite_san else get_csr_san(csr))

        if overwrite_hashalgo and overwrite_hashalgo not in VALID_HASH_ALGOS:
            raise ValueError(f'The hash algorithm "{overwrite_hashalgo}" is invalid')
        hashlago = overwrite_hashalgo if overwrite_hashalgo else self._get_config('default_hash_algo')

        if overwrite_expire:
            try:
                if not isinstance(overwrite_expire, datetime.date):
                    overwrite_expire = datetime.datetime.strptime(overwrite_expire, '%d/%m/%Y').date()

                if overwrite_expire < datetime.date.today():
                    raise ValueError(f'The expire date is not in the future')
            except ValueError:
                raise ValueError(f'The expire date "{overwrite_expire}" is invalid')
        not_after = nb_seconds_to_date(overwrite_expire) if overwrite_expire else \
            self._get_config('default_validity_seconds')

        if not disable_cert_existence_check:
            # Check if a certificate with the same CN already exists
            c = Certificate.select().where((Certificate.cn == final_cn) &
                                           (Certificate.is_renewed == False) &
                                           (Certificate.not_after > datetime.datetime.now()) &
                                           (Certificate.is_revoked == False))

            assert c.count() < 2, 'Critical error : there is more that one actual certificate matching this CN'

            if c.count() == 1:
                raise RuntimeError(f'The following certificate is matching this CN and it\'s not expired, revoked or '
                                   f'renewed : {c[0]}')

        # Generate unique serial number
        is_serial_validated = False
        serial_number_float64 = None
        serial_number_hex = None
        while not is_serial_validated:
            serial_number_float64 = generate_random_serial_number()
            serial_number_hex = serial_number_float64.to_bytes(8, 'big').hex(':')

            # We ensure that the random serial number is not already used
            is_serial_validated = Certificate.select().where(Certificate.serial == serial_number_hex).count() == 0

        # Load CA
        self._load_ca()

        # Generate the final certificate
        cert = crypto.X509()
        cert.set_version(2)

        cert.set_serial_number(serial_number_float64)
        cert.get_subject().CN = final_cn

        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(not_after)

        cert.set_issuer(self.ca.cert_obj.get_subject())
        cert.set_pubkey(csr.get_pubkey())

        define_san(cert, final_san)

        if ask_confirm:
            print('You are about to sign the following certificate :')
            print_tabulated(get_cert_text(cert))

            if not confirm('Do you want to sign it'):
                exit(0)

        cert.sign(self._get_ca_key(), hashlago)

        # Persist
        c = Certificate.create(
            cn=final_cn,
            san=final_san,
            created_timestamp=datetime.datetime.now().replace(microsecond=0),
            not_after=datetime.datetime.strptime(cert.get_notAfter().decode('utf8'), '%Y%m%d%H%M%SZ'),
            serial=serial_number_hex,
            cert=crypto.dump_certificate(FILETYPE_PEM, cert).decode('utf8'),
            key=None,
            is_revoked=False,
            is_renewed=False,
        )

        return cert, c

    @database.connection_context()
    def _generate_signed_cert(self, cn: str, san: Optional[str] = None, overwrite_keysize: int = None,
                              overwrite_hashalgo: str = None, overwrite_expire: Optional[str] = None,
                              ask_confirm: bool = False) -> (crypto.X509, Certificate):
        """
        Generate a Certificate and signed it with the Certificate Authority.

        The cn parameter is the Common Name. See Utils.regex_domain for valid values.
        The optional san parameter is the Subject Alternative Name. If not defined, the SAN will be generate by this
        method.

        The overwrite_keysize parameter can be used to overwrite default key size. See AVALAIBLE_KEYSIZES.
        The overwrite_hashalgo parameter can be used to overwrite the default hash algorithm.
        The overwrite_expire parameter can be used to overwrite the number of days of validity.

        The SAN must always include an entry matching the CN. If the CSR doesn't contain a SAN, this method create it.

        A unique (and non already used) serial number is assigned to the certificate. The certificate is valid for time
        configured in the Config<default_validity_seconds>.

        This method save the certificate in the vault. Note that the private key is not saved because not known. The
        calling function must update the vault with the private key if needed.

        This method returns a tuple :
            * the certificate object
            * the certificate model instance

        :param cn: the Common Name
        :param san: the optional Subject Alternative Name
        :param overwrite_keysize: the optional key size. See AVALAIBLE_KEYSIZES for valid values
        :param overwrite_hashalgo: the optional hash algorithm. See AVALABILE_HASHALGOS
        :param overwrite_expire: the optional number of days of validity that must be used
        :param ask_confirm: the optional flag to print the CSR and ask the confirmation before continuing
        :return: (the OpenSSL certificate object, the Certificate model instance)
        """
        if not regex_domain.match(cn):
            raise ValueError(f'CN "{cn}" is invalid')

        san = validate_or_build_san(cn, san)

        if overwrite_keysize and overwrite_keysize not in VALID_KEY_SIZES:
            raise ValueError(f'The key size "{overwrite_keysize}" is invalid')
        overwrite_keysize = overwrite_keysize if overwrite_keysize else self._get_config('default_key_size')

        if overwrite_hashalgo and overwrite_hashalgo not in VALID_HASH_ALGOS:
            raise ValueError(f'The hash algorithm "{overwrite_hashalgo}" is invalid')
        hashalgo = overwrite_hashalgo if overwrite_hashalgo else self._get_config('default_hash_algo')

        # Generate key
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, overwrite_keysize)

        # Generate CSR
        req = crypto.X509Req()
        req.get_subject().CN = cn
        req.set_pubkey(key)
        req.sign(key, hashalgo)

        # Define the SAN
        define_san(req, san)

        # Sign the CSR
        signed_cert, vault_certificate = self._sign_csr(req,
                                                        overwrite_hashalgo=hashalgo,
                                                        overwrite_expire=overwrite_expire,
                                                        ask_confirm=ask_confirm)

        # Save the private key into the vault
        vault_certificate.key = crypto.dump_privatekey(FILETYPE_PEM, key).decode('utf8')
        vault_certificate.save()

        return signed_cert, vault_certificate
