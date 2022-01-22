import os
import pyhelios

from typer import Typer, Argument, Option, Context
from typing import List, Optional

_help = f"{pyhelios.__description__} Command Line Interface (CLI)"
app = Typer(help=_help, epilog=f"Report bugs to {pyhelios.__maintainers__[0]}")


@app.command()
def coverage(
    cov_file: str = Argument(..., metavar="", help="The coverage file"),
    output_dir: str = Argument(..., metavar="", help="LaTeX files output directory"),
):
    """Parse the coverage files and generate LaTeX files"""
    from pyhelios.coverage import Coverage

    Coverage(cov_file, output_dir)


@app.command()
def doxygen(
    xml_dir: str = Argument(..., metavar="", help="XML Doxygen output directory"),
    output_dir: str = Argument(..., metavar="", help="LaTeX files output directory"),
):
    """Parse XML Doxygen files and generate LaTeX files"""
    from pyhelios.documentation import Doxygen

    Doxygen(xml_dir, output_dir)


@app.command()
def plot(
    toml: str = Argument(..., metavar="*.toml", help="TOML configuration file"),
    tmp: str = Option(
        "", "--tmp", "-t", metavar="", help="LaTeX template file", show_default=False
    ),
    output_directory: str = Option(
        ".",
        "--output-directory",
        "-o",
        metavar="*",
        help="Figures output directory",
        show_default=False,
    ),
):
    """PUblication REady PLOT (PuRePlot)"""
    from pyhelios.plot import Plot

    Plot(toml, tmp, OutputDir=output_directory)


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def python(ctx: Context):
    """Helios Python interpreter"""
    from pyhelios.python import ipython

    ipython(ctx.args)


@app.command()
def render(
    template: str = Argument(..., metavar="*", help="Jinja2 template file"),
    toml: List[str] = Argument(..., metavar="*.toml", help="TOML configuration files"),
    output: str = Option(
        "render.out",
        "--output",
        "-o",
        metavar="*",
        help="Rendered output file",
        show_default=False,
    ),
):
    """Render a Jinja2 template file"""
    import flatdict
    import pyhelios.toml
    import pyhelios.template

    data = dict()
    for t in toml:
        d = pyhelios.toml.read(t)
        data = {**d, **data}
    data = flatdict.FlatDict(data, delimiter="_")
    pyhelios.template.render(template, output, dict(data))


@app.command()
def run(
    cmd: str = Argument(..., metavar="", help="Command"),
    stdin: Optional[List[str]] = Option(
        [], "--stdin", "-s", metavar="", help="Standard input list for the command"
    ),
    directory: str = Option(
        ".", "--dir", "-d", metavar="", help="Directory where is launched the command"
    ),
    shell: bool = Option(False, help="Shell execution"),
):
    """Run the command"""
    import pyhelios.exe

    stdout, stderr = pyhelios.exe.run(
        cmd, stdin="\n".join(stdin) + "\n", directory=directory, shell=shell
    )
    print(stderr) if stderr else print(stdout)


@app.command()
def version():
    """Show the version"""
    import pyhelios

    print(f"{pyhelios.__name__} {pyhelios.__version__}")


if __name__ == "__main__":
    app()
