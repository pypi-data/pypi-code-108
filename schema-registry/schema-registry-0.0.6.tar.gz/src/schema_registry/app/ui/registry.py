from typing import Optional
import typer

from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def get_namespaces(ctx: typer.Context) -> None:
    res = list(ctx.obj["registry"].namespaces)
    res.sort()
    console.print(res)


@app.command()
def get_types(ctx: typer.Context, namespace: str) -> None:
    res = list(ctx.obj["registry"].types(namespace=namespace))
    res.sort()
    console.print(res)


@app.command()
def get_schema(
    ctx: typer.Context, namespace: str, type: str, version: Optional[int] = None
) -> None:
    console.print(
        ctx.obj["registry"].get(namespace=namespace, type_name=type, version=version)
    )


@app.command()
def get_example(
    ctx: typer.Context, namespace: str, type: str, version: Optional[int] = None
) -> None:
    console.print(
        ctx.obj["registry"].example(
            namespace=namespace, type_name=type, version=version
        )
    )
