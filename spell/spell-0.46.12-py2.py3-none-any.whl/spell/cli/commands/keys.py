import os
from base64 import b64decode, b64encode
import getpass
from hashlib import sha256
import platform
import socket
import subprocess
from tempfile import NamedTemporaryFile

import click
from Cryptodome.PublicKey import RSA

from spell.cli.log import logger
from spell.cli.exceptions import api_client_exception_handler, ExitException
from spell.cli.utils import (
    prettify_time,
    tabulate_rows,
    cli_ssh_key_path,
    write_ssh_config_file,
)

try:
    from subprocess import DEVNULL  # Added in Python 3.3
except ImportError:
    DEVNULL = open(os.devnull, "wb")


def find_key_path():
    key_locs = [
        "~/.ssh/id_rsa.pub",
        "~/.ssh/id_dsa.pub",
        "~/.ssh/id_ecdsa.pub",
        "~/.ssh/id_ed25519.pub",
        "~/.ssh/identity.pub",
    ]
    key_locs = map(os.path.expanduser, key_locs)
    key_locs = list(filter(os.path.exists, key_locs))
    return key_locs[0] if key_locs else None


@click.group(
    name="keys",
    short_help="Manage public SSH keys registered with Spell",
    help="Manage public SSH keys registered with Spell",
)
@click.pass_context
def keys(ctx):
    pass


@keys.command(name="list", help="Display all your public SSH keys")
@click.pass_context
@click.option("--raw", help="display output in raw format", is_flag=True, default=False, hidden=True)
def list_keys(ctx, raw):
    client = ctx.obj["client"]
    with api_client_exception_handler():
        keys = client.get_keys()
    if len(keys) == 0:
        click.echo("There were no keys found for you.")
    else:
        data = [(k.title, prettify_time(k.created_at), k.fingerprint) for k in keys]
        tabulate_rows(data, headers=["TITLE", "ADDED", "FINGERPRINT"], raw=raw)


@keys.command(name="add", help="Add a public SSH key to your account")
@click.pass_context
@click.option(
    "-f",
    "--file",
    "file",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help="location of public key file",
    prompt="Enter the location of the file for the public key you wish to add",
    default=find_key_path,
)
@click.option(
    "-t",
    "--title",
    "title",
    type=str,
    help="title for the public key",
    prompt="Enter the title for the public key you wish to add",
    default=socket.gethostname,
)
def add(ctx, file, title):
    client = ctx.obj["client"]
    try:
        with click.open_file(file) as f:
            key_content = f.read()
    except IOError as e:
        raise ExitException("Could not read public SSH key from {}: {}".format(file, e))

    if len(key_content) == 0:
        raise ExitException('Public SSH key file "{}" is empty'.format(file))

    with api_client_exception_handler():
        key = client.new_key(title=title, key=key_content)
    logger.info("Succesfully added SSH key: {}:{}".format(key.title, key.fingerprint))


@keys.command(name="generate", help="Generate SSH key pair for your account")
@click.pass_context
@click.option(
    "-t",
    "--title",
    "title",
    type=str,
    help="title for the public key",
    default="{} Spell CLI".format(socket.gethostname()),
)
@click.option(
    "-f",
    "--force",
    "force",
    is_flag=True,
    help="overwrite local key file if it already exists",
    default=False,
)
def generate(ctx, title, force):
    config_handler = ctx.obj["config_handler"]

    # check if key already exists
    key_path = cli_ssh_key_path(config_handler)
    if os.path.isfile(key_path) and not force:
        if not click.confirm("Overwrite existing key?"):
            return

    key = RSA.generate(2048)
    public_key_str = key.publickey().exportKey("OpenSSH").decode("utf-8")

    # add public key to account
    client = ctx.obj["client"]
    client.new_key(title=title, key=public_key_str)

    write_key_to_disk(config_handler, key.exportKey().decode("utf-8"))


@keys.command(name="rm", help="Remove a public SSH key from your account")
@click.pass_context
@click.argument("title", required=False, default=None)
def remove(ctx, title):
    # get keys associated with user
    client = ctx.obj["client"]
    with api_client_exception_handler():
        keys = client.get_keys()
    if not keys:
        raise ExitException("There are no keys associated with your account.")

    # key to remove
    key = None

    # filter keys by title
    if title:
        keys = list(filter(lambda k: k.title == title, keys))
        if not keys:
            raise ExitException('Key with title "{}" not found.'.format(title))
        elif len(keys) == 1:
            key = keys[0]

    # list keys and prompt user to pick one
    if not key:

        def row(n, k):
            return (n, k.title, prettify_time(k.created_at), k.fingerprint)

        data = [row(i, keys[i]) for i in range(len(keys))]
        tabulate_rows(data, headers=["NUM", "TITLE", "ADDED", "FINGERPRINT"])
        key = keys[click.prompt("Enter number of key to remove", type=int)]

    # delete the selected key
    with api_client_exception_handler():
        client.delete_key(key.id)
    logger.info("Succesfully removed SSH public key: title={}, fingerprint={}".format(key.title, key.fingerprint))


def remove_cli_key(ctx):
    key_path = cli_ssh_key_path(ctx.obj["config_handler"])
    if not os.path.isfile(key_path):
        return
    try:
        remote_key = get_remote_key(ctx, key_path)
        if remote_key:
            client = ctx.obj["client"]
            client.delete_key(remote_key.id)
    finally:
        remove_key_from_agent(key_path)
        os.remove(key_path)


# Remove local key from SSH agent
#
# ssh-add -d only works with a public key file, so one is generated using a
# temporary file.
def remove_key_from_agent(path):
    try:
        subprocess.check_call(["ssh-add", "-l"], stdout=DEVNULL, stderr=DEVNULL)
    except Exception:
        return  # ssh-add is broken or missing
    with open(path, "r") as key_file:
        key = RSA.importKey(key_file.read())
    with NamedTemporaryFile() as pub_key_file:
        pub_key_file.write(key.publickey().exportKey("OpenSSH"))
        pub_key_file.flush()
        subprocess.call(["ssh-add", "-d", pub_key_file.name], stdout=DEVNULL, stderr=DEVNULL)


def get_remote_key(ctx, local_key_path):
    # Calculate fingerprint of local key
    with open(local_key_path, "r") as key_file:
        key = RSA.importKey(key_file.read())
    pub_key_str = key.publickey().exportKey("OpenSSH").decode()
    pub_key_bytes = b64decode(pub_key_str.split()[1])
    fingerprint = b64encode(sha256(pub_key_bytes).digest()).decode()[:-1]
    fingerprint = "SHA256:" + fingerprint

    # Get list of keys associated with Spell account
    client = ctx.obj["client"]
    keys = client.get_keys()

    # Return matching remote key
    keys = list(filter(lambda k: k.fingerprint == fingerprint, keys))
    return keys[0] if keys else None


def write_key_to_disk(config_handler, key):
    """
    Writes a key (and SSH config file) to the Spell config directory.
    """
    # if the spell dir doesn't exist yet, create it
    # this may happen if the client is using an access token for authentication
    if not os.path.exists(config_handler.spell_dir):
        os.mkdir(config_handler.spell_dir)

    # write key to spell directory
    key_path = cli_ssh_key_path(config_handler)
    with os.fdopen(os.open(key_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "w") as key_file:
        # key_file.write(pem.decode("utf-8"))
        key_file.write(key)

    # write ssh config file
    write_ssh_config_file(config_handler)

    # set permissions for windows compat
    if platform.system() == "Windows":
        user = getpass.getuser()
        set_windows_sshkey_permissions(key_path, user)


def set_windows_sshkey_permissions(key_path, user):
    import ntsecuritycon
    import win32security

    # get the access control lists for the key file
    security_descriptor = win32security.GetNamedSecurityInfo(
        key_path,
        win32security.SE_FILE_OBJECT,
        win32security.DACL_SECURITY_INFORMATION,
    )
    dacl = security_descriptor.GetSecurityDescriptorDacl()

    # delete all existing access control entries
    while dacl.GetAceCount():
        dacl.DeleteAce(0)

    # set up new access control list with single user
    acl_entries = [
        {
            "AccessMode": win32security.GRANT_ACCESS,
            "AccessPermissions": ntsecuritycon.GENERIC_ALL,
            "Inheritance": win32security.NO_INHERITANCE,
            "Trustee": {
                "TrusteeType": win32security.TRUSTEE_IS_USER,
                "TrusteeForm": win32security.TRUSTEE_IS_NAME,
                "Identifier": user,
            },
        },
    ]
    dacl.SetEntriesInAcl(acl_entries)

    # update security of file
    win32security.SetNamedSecurityInfo(
        key_path,
        win32security.SE_FILE_OBJECT,
        win32security.DACL_SECURITY_INFORMATION
        | win32security.PROTECTED_DACL_SECURITY_INFORMATION
        | win32security.UNPROTECTED_DACL_SECURITY_INFORMATION,
        None,
        None,
        dacl,
        None,
    )


def maybe_write_private_ssh_key_to_disk(ctx):
    """
    Does the public SSH key file (used to connect to GitLab) exists on the host?

    If yes verify its authenticity (via fingerprint) and if it is valid do nothing.

    If it does not exist, and the SPELL_INTERNAL_SSH_KEY envar is set, the host is a workspace or
    workflow. Decode the envar (expected to be the base64 encoding of a private key stored in the
    PEM file format) and write it to disk. This enables the use of these commands from within the
    run, and so this function should be executed immediately before any operations that sync code
    to GitLab.
    """
    config_handler = ctx.obj["config_handler"]
    local_key = cli_ssh_key_path(config_handler)
    matching_remote_key = os.path.isfile(local_key) and get_remote_key(ctx, local_key)

    if not matching_remote_key and os.environ.get("SPELL_RUN", False) and "SPELL_INTERNAL_SSH_KEY" in os.environ:
        pem = b64decode(os.environ["SPELL_INTERNAL_SSH_KEY"]).decode("utf-8")
        write_key_to_disk(config_handler, pem)
