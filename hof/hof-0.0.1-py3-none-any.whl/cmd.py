import os
import datetime
import click
import pybaseball as pb
from rich.console import Console
from rich.table import Table
import pandas as pd

# consts
PWD = os.getcwd()
CONSOLE = Console()


def __create_table(df: pd.DataFrame) -> Table:
    """create table object to print.

    Args:
        df (pd.DataFrame): data converted to table.

    Returns:
        Table: table object to print.
    """
    table = Table(show_header=True, header_style="bold magenta")
    for col in df.columns:
        table.add_column(col)
    for row in df.values:
        row = tuple(map(str, row))
        table.add_row(*row)
    return table


def __hof() -> pd.DataFrame:
    """get hof data as pd.DataFrame.

    Returns:
        pd.DataFrame: hof.
    """
    return pd.read_csv(f"{PWD}/data/hof.csv")


def __hof_inducted_yes() -> pd.DataFrame:
    """get data inducted to hof.

    Returns:
        pd.DataFrame: data inducted to hof.
    """
    df = __hof()
    return df[df["INDUCTED"] == "Y"]


def __save(df: pd.DataFrame):
    """save data as csv.

    Args:
        df (pd.DataFrame): data to save.
    """
    df.to_csv(f"{PWD}/data/hof.csv", index=False)


@click.group()
def hof():
    """root command.
    """
    pass


@hof.command()
def init():
    """initialize hof data.
    """
    people = pb.people()
    hof = pb.hall_of_fame()
    hof = hof.merge(people, on="playerID")[
        list(hof.columns) + ["nameFirst", "nameLast", "nameGiven"]
    ]
    hof = hof.fillna(0)
    hof["name"] = hof["nameFirst"] + " " + hof["nameLast"]
    hof = hof[
        [
            "yearID",
            "votedBy",
            "ballots",
            "needed",
            "votes",
            "inducted",
            "category",
            "name",
        ]
    ].rename(columns={"yearID": "year"})
    hof.columns = map(str.upper, hof.columns)
    __save(hof)
    CONSOLE.print("[bold blue]Done![/bold blue] :sparkles:")


@hof.command()
@click.option("--category", "-C", type=str, help="hof category.")
@click.option("--votedby", "-V", type=str, help="voted by who.")
@click.option("--head", type=int, help="line number to show from head.")
@click.option("--tail", type=int, help="line number to show from tail.")
def show(category:str, votedby:str, head:int, tail:int):
    """show hof data.

    Args:
        category (str): player / manager / pioneer/executive
        votedby (str): bbwaa / veterans
        head (int): line number to show from head.
        tail (int): line number to show from tail.
    """
    hof = __hof_inducted_yes()
    if category:
        hof = hof[hof["CATEGORY"].str.lower() == category.lower()]
    if votedby:
        hof = hof[hof["VOTEDBY"].str.lower() == votedby.lower()]
    if head:
        hof = hof.head(head)
    if tail:
        hof = hof.tail(tail)
    table = __create_table(hof)
    CONSOLE.print(table)


@hof.command()
@click.option("--name", "-N", required=True, type=str, help="name you want to add.")
def add(name: str):
    """add someone to hof.

    Args:
        name ([str]): name you want to add.
    """
    hof = __hof_inducted_yes()
    row = pd.DataFrame(
        [
            [
                datetime.datetime.now().date().strftime("%Y"),
                "prs-watch/hof",
                "500.0",
                "500.0",
                "500.0",
                "Y",
                "Player",
                name,
            ]
        ],
        columns=hof.columns,
    )
    hof = pd.concat([hof, row])
    __save(hof)
    CONSOLE.print("[bold blue]Success![/bold blue] :sparkles:")
    CONSOLE.print(f"You just added [bold blue]{name}[/bold blue] to HoF!")


@hof.command()
@click.option(
    "--name",
    "-N",
    required=True,
    type=str,
    help="name who you want to remove from hof.",
)
def remove(name: str):
    """remove someone from hof.

    Args:
        name (str): name you want to remove.
    """
    hof = hof = __hof_inducted_yes()
    hof = hof[hof["NAME"].str.lower() != name]
    __save(hof)
    CONSOLE.print("[bold red]Removed![/bold red] :skull:")
    CONSOLE.print(f"[bold red]{name}[/bold red] is no longer on hof..")


@hof.command()
def destroy():
    """destroy hof.
    """
    hof = pd.read_csv(f"{PWD}/data/hof.csv")
    hof = hof.drop(range(len(hof)))
    hof.to_csv(f"{PWD}/data/hof.csv", index=False)
    CONSOLE.print("[bold red]Done![/bold red] :bomb:")
    CONSOLE.print("Goodbye baseball.. :hand:")
    CONSOLE.print(__create_table(hof))
