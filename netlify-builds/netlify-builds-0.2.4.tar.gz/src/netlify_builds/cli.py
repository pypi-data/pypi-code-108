import asyncio
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List, NamedTuple

import httpx
from dateutil.parser import parse
from httpx import HTTPError
from rich.console import Console
from rich.table import Table

console = Console()


class BuildRow(NamedTuple):
    team: str
    used: int
    total: int
    start_date: dt.datetime
    end_date: dt.datetime

    @property
    def percent_used(self) -> float:
        return 100 * self.used / self.total

    @property
    def percent_elapsed(self) -> float:
        return (
            100
            * (dt.datetime.now(tz=self.start_date.tzinfo) - self.start_date)
            / (self.end_date - self.start_date)
        )


def main():
    asyncio.run(run_async())


async def run_async():
    team_tokens = read_config()
    async with httpx.AsyncClient(timeout=3) as client:
        tasks = [
            make_request(client, team, token) for team, token in team_tokens.items()
        ]
        team_responses = await asyncio.gather(*tasks)
        rows = [
            parse_response(team, response_data)
            for team, response_data in team_responses
            if response_data
        ]
        print_table(rows)


def read_config():
    config_file = Path.home() / ".netlify-builds.json"
    return json.loads(config_file.read_text())


async def make_request(client, team, token):
    try:
        response = await client.get(
            f"https://api.netlify.com/api/v1/{team}/builds/status",
            headers={"content-length": "0", "authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
    except HTTPError:
        return team, None
    return team, response.json()


def parse_response(team: str, response_data: Dict[str, Any]) -> BuildRow:
    minutes = response_data["minutes"]
    start_date = parse(minutes["period_start_date"])
    end_date = parse(minutes["period_end_date"])
    used = minutes["current"]
    total = minutes["included_minutes"]
    return BuildRow(
        team=team,
        used=used,
        total=total,
        start_date=start_date,
        end_date=end_date,
    )


def print_table(rows: List[BuildRow]):
    if not rows:
        console.print("No rows to print", style="bold red")
        return

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Team", style="bold yellow")
    table.add_column("Mins", style="dim", justify="right")
    table.add_column("Start Date", style="dim")
    table.add_column("End Date", style="dim")
    table.add_column("Elapsed", justify="right")
    table.add_column("Used", justify="right")

    for build_row in rows:
        style = "red" if build_row.percent_used > build_row.percent_elapsed else "green"
        table.add_row(
            build_row.team,
            f"{build_row.used} mins",
            f"{build_row.start_date:%Y-%m-%d}",
            f"{build_row.end_date:%Y-%m-%d}",
            f"[{style}]{build_row.percent_elapsed:.1f}%[/{style}]",
            f"[{style}]{build_row.percent_used:.1f}%[/{style}]",
        )

    console.print(table)
