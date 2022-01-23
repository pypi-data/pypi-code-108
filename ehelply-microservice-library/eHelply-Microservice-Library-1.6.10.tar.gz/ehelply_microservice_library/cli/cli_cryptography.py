import typer
from ehelply_bootstrapper.utils.cryptography import Encryption, Hashing
from OpenSSL import crypto
from pathlib import Path
from typing import Optional

cli = typer.Typer()


def cert_gen(
        emailAddress="business@ehelply.com",
        commonName="microservice",
        countryName="CA",
        localityName="CA",
        stateOrProvinceName="SK",
        organizationName="eHelply",
        organizationUnitName="eHelply",
        serialNumber=0,
        validityStartInSeconds=0,
        validityEndInSeconds=10 * 365 * 24 * 60 * 60,
        KEY_FILE:Path=Path("private.key"),
        CERT_FILE:Path=Path("certificate.crt")
):
    # can look at generated file using openssl:
    # openssl x509 -inform pem -in selfsigned.crt -noout -text
    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 4096)
    # create a self-signed cert
    cert = crypto.X509()

    cert.get_subject().C = countryName
    cert.get_subject().ST = stateOrProvinceName
    cert.get_subject().L = localityName
    cert.get_subject().O = organizationName
    cert.get_subject().OU = organizationUnitName
    cert.get_subject().CN = commonName
    cert.get_subject().emailAddress = emailAddress

    cert.set_serial_number(serialNumber)

    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(validityEndInSeconds)

    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)

    cert.sign(k, 'sha512')

    with open(CERT_FILE, "wt") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))

    with open(KEY_FILE, "wt") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf-8"))


@cli.command()
def encrypt(
        data: str = typer.Option(..., prompt=True, help="Data to encrypt"),
        key: str = typer.Option(..., prompt=True, help="Encryption key. Must be a valid Fernet key")
):
    """
    Encrypt data using a fernet key
    """
    enc = Encryption([key.encode(Encryption.STRING_ENCODING)])
    typer.echo(enc.encrypt(data))


@cli.command()
def decrypt(
        data: str = typer.Option(..., prompt=True, help="Data to decrypt"),
        key: str = typer.Option(..., prompt=True, help="Encryption key. Must be a valid Fernet key")
):
    """
    Decrypt data using a fernet key
    """
    enc = Encryption([key.encode(Encryption.STRING_ENCODING)])
    typer.echo(enc.decrypt(data.encode(Encryption.STRING_ENCODING)))


@cli.command()
def hash(
        data: str = typer.Option(..., prompt=True, help="Data to hash"),
        timed: bool = typer.Option(False, help="Time how long it takes to create the hash"),
        cost: int = typer.Option(12, help="How many rounds to use to create the hash. The higher the number, the longer the hash will take")
):
    """
    Create a hash of data
    """
    Hashing.COST_FACTOR = cost
    hasher = Hashing()
    if timed:
        result = hasher.hash_timed(data)
    else:
        result = hasher.hash(data)
    typer.echo(result)


@cli.command()
def hash_check(
        data: str = typer.Option(..., prompt=True, help="Non hashed data to compare"),
        hash: str = typer.Option(..., prompt=True, help="The hash to compare against")
):
    """
    Compare data to a hash to verify whether they are equivalent
    """
    hasher = Hashing()
    typer.echo(hasher.check(data, hash))


@cli.command()
def generate_key():
    """
    Generate a new Fernet key
    """
    typer.echo(Encryption.generate_key())


@cli.command()
def refresh_https_certificates(
        key: Optional[Path] = typer.Option(None, help="Path to key file"),
        cert: Optional[Path] = typer.Option(None, help="Path to cert file")
):
    """
    DEPRECATED: Refresh HTTPS certificates
    """

    args: dict = {}

    if key:
        args['KEY_FILE'] = key
    if cert:
        args['CERT_FILE'] = cert

    cert_gen(**args)
    typer.echo("Complete")


if __name__ == '__main__':
    cli()
