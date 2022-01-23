import typer
import base64

cli = typer.Typer()


@cli.command()
def encode_json_header(
        json: str = typer.Option(..., prompt=True, help="JSON string to encrypt"),
):
    json_bytes = json.encode('utf-8')
    base64_bytes = base64.b64encode(json_bytes)
    base64_str = base64_bytes.decode('utf-8')
    typer.echo(base64_str)
