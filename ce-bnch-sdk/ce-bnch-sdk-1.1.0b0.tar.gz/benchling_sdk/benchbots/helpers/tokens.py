import keyring
import typer

KEYRING_NAME = "benchling-sdk/api_keys"


def api_key_from_prompt_or_keyring(hostname: str, reset_api_key: bool) -> str:
    if reset_api_key:
        api_key = None
    else:
        api_key = keyring.get_password(KEYRING_NAME, hostname)

    if api_key is None:
        api_key = typer.prompt(f"Enter your API key for {hostname}", hide_input=True)
        if typer.confirm("Do you want to store the API key in your keyring?", default=True):
            keyring.set_password(KEYRING_NAME, hostname, api_key)
    else:
        typer.echo(f"Using {hostname} API key from keyring")

    return api_key
