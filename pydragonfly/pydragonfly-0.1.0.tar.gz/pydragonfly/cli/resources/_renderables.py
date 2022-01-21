# flake8: noqa: E501
from typing import Dict, List

from rich import box
from rich.console import Console, RenderGroup
from rich.emoji import Emoji
from rich.panel import Panel
from rich.table import Table

from .._utils import (
    get_datetime_text,
    get_json_syntax,
    get_status_text,
    get_success_text,
    get_weight_text,
)


def _display_single_analysis(data: Dict) -> None:
    console = Console()
    style = "[bold #31DDCF]"
    user = data["user"]
    sample = data["sample"]
    panels = [
        Panel(
            RenderGroup(
                f"[i green]{Emoji('information')} Visit the GUI page to see all info[/]",
            ),
        ),
        Panel(
            RenderGroup(
                f"{style}ID:[/] {data['id']}",
                f"{style}Date:[/] {data['created_at']}",
                f"{style}User:[/] {user['username']}",
                f"{style}Public:[/] {data['public']}",
                f"{style}Root:[/] {data['root']}",
                f"{style}URL:[/] [u cyan]{data['gui_url']}[/]",
            ),
            title="Attributes",
        ),
        Panel(
            RenderGroup(
                f"{style}Name:[/] {sample['filename']}",
                f"{style}Behaviour:[/] {sample['malware_type']} ({sample['mimetype']})",
                f"{style}Operating System:[/] {sample['os']} ({sample['arch']}, {sample['mode']})",
                f"{style}SHA256:[/] {sample['sha256']}",
                f"{style}SHA1:[/] {sample['sha1']}",
                f"{style}MD5:[/] {sample['md5']}",
            ),
            title="Sample Information",
        ),
        Panel(
            RenderGroup(
                f"{style}Status:[/] {get_status_text(data['status'], False)}",
                f"{style}Evaluation:[/] {get_status_text(data['evaluation'], False)}",
                f"{style}Weight:[/] {data['weight']}",
                f"{style}Malware Families:[/] " + ",".join(data["malware_families"]),
                f"{style}Mitre Techniques:[/] "
                + ",".join(
                    f"[link={technique['mitre_url']}]{technique['name']}[/link]"
                    for tactic in data["mitre_techniques"]
                    for technique in tactic["techniques"]
                ),
            ),
            title="Result Overview",
        ),
        Panel(
            RenderGroup(
                *[
                    RenderGroup(
                        f"{style}Report[/] - [cyan]#{report['id']} \[{report['profile']['filename']}, {report['profile']['emulator']}][/]",
                        f"\tStatus: {get_status_text(report['status'], False)}",
                        f"\tEvaluation: {get_status_text(report['evaluation'], False)}",
                        f"\tWeight: {report['weight']}",
                    )
                    for report in data["reports"]
                ]
            ),
            title="Reports",
        ),
        Panel(get_json_syntax(data), title="Raw"),
    ]
    with console.pager(styles=True):
        for p in panels:
            console.print(p)


def _generate_analysis_table(rows: List[Dict]) -> Table:
    table = Table(
        show_header=True, title="Latest Analysis", box=box.DOUBLE_EDGE, expand=True
    )
    for col in [
        "ID",
        "Created",
        "Sample",
        "Mitre\nTechniques",
        "Malware\nFamilies",
        "Status",
        "Evaluation",
        "Weight",
    ]:
        table.add_column(header=col, header_style="bold blue")
    for el in rows:
        table.add_row(
            f"[link={el['gui_url']}]{Emoji('link')} {el['id']}[/link]",
            get_datetime_text(el["created_at"]),
            f"{el['sample']['filename']}\n({el['sample']['os']}, {el['sample']['arch']}, {el['sample']['mode']})",
            ",".join(
                f"[link={tactic['mitre_url']}]{tactic['name']}[/link]"
                for tactic in el["mitre_techniques"]
            ),
            ",".join(el["malware_families"]),
            get_status_text(el["status"]),
            get_status_text(el["evaluation"]),
            get_weight_text(el["weight"]),
        )
    return table


def _generate_profile_table(rows: List[Dict]) -> Table:
    table = Table(
        show_header=True, title="Latest Profiles", box=box.DOUBLE_EDGE, expand=True
    )
    for col in ["ID", "Enabled", "Created", "Filename", "Emulator", "Content"]:
        table.add_column(header=col, header_style="bold blue")
    for el in rows:
        table.add_row(
            str(el["id"]),
            get_success_text(str(el["enabled"])),
            get_datetime_text(el["created_at"]),
            el["filename"],
            el["emulator"],
            f"[cyan]{el['read']}[/]",
        )
    return table


def _generate_rule_table(rows: List[Dict]) -> Table:
    table = Table(
        show_header=True, title="Latest Rules", box=box.DOUBLE_EDGE, expand=True
    )
    for col in [
        "ID",
        "Enabled",
        "Name",
        "Meta",
        "Mitre\nTechnique",
        "Malware\nFamily",
        "Variables",
        "Weight",
    ]:
        table.add_column(header=col, header_style="bold blue")
    for el in rows:
        table.add_row(
            str(el["id"]),
            get_success_text(str(el["enabled"])),
            el["rule"],
            get_json_syntax(el["meta_description"]) if el["meta_description"] else None,
            f"[link={el['mitre_technique']['mitre_url']}]{el['mitre_technique']['name']}[/link]"
            if el["mitre_technique"]
            else None,
            el["malware_family"],
            get_json_syntax(el["variables"]) if el["variables"] else None,
            get_weight_text(el["weight"]),
        )
    return table


def _paginate_table(generator, generate_table_fn) -> None:
    console = Console()
    for resp, page in generator:
        console.print(generate_table_fn(resp.data["results"]), justify="center")
        console.print(
            f"page: {page}, total pages: {resp.data['total_pages']}",
            justify="center",
        )
        console.input("\n[ENTER] next page [CTRL+C] abort...")
        console.clear()
