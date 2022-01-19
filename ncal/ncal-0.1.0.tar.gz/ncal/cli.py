import asyncio
import datetime as dt
import logging
import time
from pathlib import Path
from typing import Callable, Coroutine, Optional

import arrow

# from notion_client import Client
import notion_client as nc
import typer
from pydantic import ValidationError

from ncal import core
from ncal.config import Settings, load_settings
from ncal.gcal_token import gcal_token

from . import __version__

app = typer.Typer(help="CLI to sync a Notion database with Google Calendar.")
state = {"verbose": False}


async def scheduler(
    timedelta: dt.timedelta, function: Callable[..., Coroutine], f_args: dict
) -> None:
    next_run = dt.datetime.now() + timedelta
    print(f"next run: {next_run}")
    while True:
        now = dt.datetime.now()
        if now >= next_run:
            await function(**f_args)
            next_run = timedelta + next_run
            print(f"next run: {next_run}")
        await asyncio.sleep(1)


async def sync(settings: Settings) -> None:
    if settings.delete_option:
        num_steps = 5
    else:
        num_steps = 4

    with typer.progressbar(
        range(num_steps + 1), label="Sychronising", show_eta=False, show_pos=True
    ) as progress:
        progress.label = "API connections"
        # Set up API connections
        service, calendar = core.setup_google_api(
            settings.default_calendar_id,
            str(settings.credentials_location),
        )
        notion = nc.Client(auth=settings.notion_api_token)
        todayDate = arrow.utcnow().isoformat()
        progress.update(1)

        progress.label = "new N->G"
        core.new_events_notion_to_gcal(
            settings.database_id,
            settings.url_root,
            settings.default_calendar_name,
            settings.calendar_dictionary,
            settings.task_notion_name,
            settings.date_notion_name,
            settings.initiative_notion_name,
            settings.extrainfo_notion_name,
            settings.on_gcal_notion_name,
            settings.gcaleventid_notion_name,
            settings.lastupdatedtime_notion_name,
            settings.calendar_notion_name,
            settings.current_calendar_id_notion_name,
            settings.delete_notion_name,
            notion,
            service,
            settings=settings,
        )
        progress.update(1)

        progress.label = "modified N->G"
        core.existing_events_notion_to_gcal(
            settings.database_id,
            settings.url_root,
            settings.default_calendar_id,
            settings.default_calendar_name,
            settings.calendar_dictionary,
            settings.task_notion_name,
            settings.date_notion_name,
            settings.initiative_notion_name,
            settings.extrainfo_notion_name,
            settings.on_gcal_notion_name,
            settings.needgcalupdate_notion_name,
            settings.gcaleventid_notion_name,
            settings.lastupdatedtime_notion_name,
            settings.calendar_notion_name,
            settings.current_calendar_id_notion_name,
            settings.delete_notion_name,
            notion,
            todayDate,
            service,
            settings=settings,
        )
        progress.update(1)

        progress.label = "modified G->N"
        core.existing_events_gcal_to_notion(
            settings.database_id,
            settings.default_calendar_name,
            settings.calendar_dictionary,
            settings.date_notion_name,
            settings.on_gcal_notion_name,
            settings.needgcalupdate_notion_name,
            settings.gcaleventid_notion_name,
            settings.lastupdatedtime_notion_name,
            settings.calendar_notion_name,
            settings.current_calendar_id_notion_name,
            settings.delete_notion_name,
            service,
            notion,
            todayDate,
            settings=settings,
        )
        progress.update(1)

        progress.label = "new G->N"
        core.new_events_gcal_to_notion(
            settings.database_id,
            settings.calendar_dictionary,
            settings.task_notion_name,
            settings.date_notion_name,
            settings.extrainfo_notion_name,
            settings.on_gcal_notion_name,
            settings.gcaleventid_notion_name,
            settings.lastupdatedtime_notion_name,
            settings.calendar_notion_name,
            settings.current_calendar_id_notion_name,
            settings.delete_notion_name,
            service,
            notion,
            settings=settings,
        )

        if settings.delete_option:
            progress.update(1)
            progress.label = "delete done pages from GCal"
            core.delete_done_pages(
                notion=notion,
                database_id=settings.database_id,
                GCalEventId_Notion_Name=settings.gcaleventid_notion_name,
                On_GCal_Notion_Name=settings.on_gcal_notion_name,
                Delete_Notion_Name=settings.delete_notion_name,
                DELETE_OPTION=settings.delete_option,
                calendarDictionary=settings.calendar_dictionary,
                Calendar_Notion_Name=settings.calendar_notion_name,
                service=service,
            )

        progress.label = "Sychronized"
        progress.update(1)
        typer.echo(f"Synchronized at UTC {arrow.utcnow()}")


async def continuous_sync(interval: dt.timedelta, settings: Settings):
    await sync(settings)
    await scheduler(interval, sync, {"settings": settings})


@app.command("sync")
def cli_sync(
    repeat: bool = typer.Option(False, "--repeat/--no-repeat", "-r"),
    seconds: int = 10,
    config_file: Optional[Path] = typer.Option(
        None, "--config-file", "-c", help="toml configuration file location"
    ),
    notion_api_token: Optional[str] = None,
    database_id: Optional[str] = None,
    url_root: Optional[str] = None,
    delete_pages: Optional[bool] = typer.Option(
        False,
        "--delete-pages/--no-delete-pages",
        "-d",
        help="delete pages which have been marked done",
    ),
):
    """
    CLI to sync a Notion database with Google Calendar.

    """
    typer.echo()
    typer.secho(
        f"Sychronize Notion <-> GCal", bg=typer.colors.GREEN, fg="white", bold=True
    )
    typer.echo()

    try:
        if config_file:
            settings = load_settings(
                config_file_path=config_file,
                notion_api_token=notion_api_token,
                database_id=database_id,
                url_root=url_root,
                delete_option=delete_pages,
            )
        else:
            settings = load_settings(
                notion_api_token=notion_api_token,
                database_id=database_id,
                url_root=url_root,
                delete_option=delete_pages,
            )
    except ValidationError:
        typer.secho(
            "no valid config provided, use --help for more information",
            bg="white",
            fg="red",
        )
        typer.echo("Required options: notion_api_token, database_id, urlRoot")
        raise typer.Exit(1)
    except FileNotFoundError:
        typer.secho(
            "invalid config-file provided, use --help for more information",
            bg="white",
            fg="red",
        )
        raise typer.Exit(1)
    logging.info(settings)

    if repeat:
        interval = dt.timedelta(seconds=seconds)
        asyncio.run(continuous_sync(interval, settings))
    else:
        asyncio.run(sync(settings))


@app.command("gcal-token")
def cli_gcal_token(client_secret_json: Path, out_file: Path = Path("token.pkl")):
    """Generate a token, which will be stored in a .pkl file"""
    gcal_token(out_file, client_secret_json)


@app.callback(invoke_without_command=True, no_args_is_help=True)
def main(
    verbose: bool = False,
    version: bool = typer.Option(None, "--version", is_eager=True),
):
    if verbose:
        state["verbose"] = True
        logging.basicConfig(level=20)
    if version:
        typer.echo(f"ncal version: {__version__}")
        raise typer.Exit()
