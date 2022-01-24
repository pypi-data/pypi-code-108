from pathlib import Path

import click
from indico_install.utils import (
    base64file,
    convertb64,
    get_value,
    decodeb64,
)
from indico_install.cluster_manager import ClusterManager


@click.command("encode")
@click.pass_context
@click.option("--value", help="Encode this value")
@click.option(
    "--from-key",
    help="Encode this config key's value. Example: postgres.app.password",
)
@click.option("--from-file", help="Encode the contents of this file")
@click.option(
    "--save-key", help="Save the value to this key in cluster config. Example: tls.cert"
)
@click.option(
    "--stdout/--no-stdout",
    default=True,
    show_default=True,
    help="Print the encoded result to the screen",
)
def encode(
    ctx, value=None, from_key=None, save_key=None, from_file=None, stdout=True,
):
    """
    Base64 encode a string from a provided source

    value overrides from-key, which overrides from-file
    """
    cluster_manager = None
    assert any(
        [value, from_key, from_file]
    ), "Must provide one of --value, --from-key, --from-file"
    if from_key or save_key:
        cluster_manager = ClusterManager()

    if value:
        encoded_value = convertb64(value)
    elif from_key:
        keys = from_key.split(".")
        value = get_value(cluster_manager.cluster_config, keys)
        assert isinstance(value, str), f"Value of {from_key} must be a string"
        encoded_value = convertb64(value)
    else:
        assert Path(from_file).is_file(), "--from-file could not be found"
        encoded_value = base64file(from_file)

    if stdout:
        click.echo(encoded_value)

    if save_key:
        cluster_manager.lock()
        keys = save_key.split(".")
        save_value = get_value(cluster_manager.cluster_config, keys[:-1])
        save_value[keys[-1]] = encoded_value
        cluster_manager.save()
        cluster_manager.unlock()

    return encoded_value


@click.command("decode")
@click.pass_context
@click.option("--value", help="Decode this value")
@click.option(
    "--from-key",
    help="Decode this key's value in cluster config. Example: postgres.app.password",
)
@click.option("--save-file", help="Save the decoded value to this file")
@click.option(
    "--save-key", help="Save the value to this key in cluster config. Example: tls.cert"
)
@click.option(
    "--stdout/--no-stdout",
    default=True,
    show_default=True,
    help="Print the decoded result to the screen",
)
def decode(
    ctx, value=None, from_key=None, save_key=None, save_file=None, stdout=True,
):
    """
    Decode a base64-encoded string from a provided source

    value overrides from-key
    """
    cluster_manager = None
    assert any([value, from_key]), "Must provide one of --value, --from-key"
    if from_key or save_key:
        cluster_manager = ClusterManager()

    if value:
        decoded_value = decodeb64(value)
    else:
        keys = from_key.split(".")
        value = get_value(cluster_manager.cluster_config, keys)
        assert isinstance(value, str), f"Value of {from_key} must be a string"
        decoded_value = decodeb64(value)

    if stdout:
        click.echo(decoded_value)

    if save_key:
        cluster_manager.lock()
        keys = save_key.split(".")
        save_value = get_value(cluster_manager.cluster_config, keys[:-1])
        save_value[keys[-1]] = decoded_value
        cluster_manager.save()
        cluster_manager.unlock()

    if save_file:
        with open(save_file, "w") as sfile:
            sfile.write(decoded_value)

    return decoded_value
