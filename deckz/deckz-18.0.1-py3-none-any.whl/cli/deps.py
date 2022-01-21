from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, Dict, FrozenSet, Iterable, Mapping, Optional, Set, Tuple

from rich.console import Console
from rich.padding import Padding
from rich.progress import Progress, track
from rich.table import Table
from typer import Argument, Option
from yaml import safe_load as yaml_safe_load

from deckz.cli import app
from deckz.paths import GlobalPaths, Paths
from deckz.targets import Targets


@app.command()
def deps(
    section: Optional[str] = Argument(None, help="Section to study"),
    flavor: Optional[str] = Argument(None, help="Flavor to study"),
    unused: bool = Option(True, help="Display the unused flavors"),
    workdir: Path = Option(
        Path("."), help="Path to move into before running the command"
    ),
) -> None:
    """Display information about shared sections and flavors usage."""
    paths = GlobalPaths.from_defaults(workdir)
    with Progress() as progress:
        targets_progress = progress.add_task("Retrieving targets files", start=False)
        sections_progress = progress.add_task("Retrieving section files", start=False)

        targets_paths = list(paths.git_dir.glob("**/targets.yml"))
        progress.update(
            targets_progress, total=len(targets_paths), completed=len(targets_paths)
        )
        progress.start_task(targets_progress)
        ymls = paths.shared_latex_dir.glob("**/*.yml")
        section_paths = []
        for yml in ymls:
            with yml.open(encoding="utf8") as fh:
                content = yaml_safe_load(fh)
                if not isinstance(content, dict):
                    continue
                if {"title", "flavors"}.issubset(content):
                    section_paths.append(yml)

        progress.update(
            sections_progress, total=len(section_paths), completed=len(section_paths)
        )
        progress.start_task(sections_progress)

    all_targets_dependencies: Dict[str, Dict[str, Set[str]]] = defaultdict(dict)
    by_sections: DefaultDict[str, DefaultDict[str, Set[Tuple[str, str]]]] = defaultdict(
        lambda: defaultdict(set)
    )
    for targets_path in track(targets_paths, description="Processing targets files"):
        _process_targets(targets_path, all_targets_dependencies, by_sections)

    if unused:
        _print_unused_report(section_paths, by_sections, paths)
    if section is not None:
        _print_section_report(section, flavor, by_sections)


def _compute_shared_dependencies(
    dependencies: Set[Path], paths: GlobalPaths
) -> Set[str]:
    shared_dependencies = set()
    for dependency in dependencies:
        try:
            relative_dependency = dependency.relative_to(paths.shared_latex_dir)
            shared_dependencies.add(str(relative_dependency))
        except ValueError:
            pass
    return shared_dependencies


def _process_targets(
    targets_path: Path,
    all_targets_dependencies: Dict[str, Dict[str, Set[str]]],
    by_sections: Mapping[str, Mapping[str, Set[Tuple[str, str]]]],
) -> None:
    paths = Paths.from_defaults(targets_path.parent)
    targets_name = str(paths.current_dir.relative_to(paths.git_dir))
    targets = Targets.from_file(paths)
    for target in targets:
        for section_path, dependencies in target.section_dependencies.items():
            section_flavors = target.section_flavors[section_path]
            shared = False
            for dependency_path in dependencies.used:
                if _relative_to_shared_latex(paths, str(dependency_path)) is not None:
                    shared = True
                    break
            if shared:
                for section_flavor in section_flavors:
                    by_sections[section_path][section_flavor].add(
                        (targets_name, target.name)
                    )
        shared_dependencies = _compute_shared_dependencies(
            target.dependencies.used, paths
        )
        all_targets_dependencies[targets_name][target.name] = shared_dependencies


def _print_changed_report(
    touched: FrozenSet[str], all_targets_dependencies: Dict[str, Dict[str, Set[str]]]
) -> None:
    console = Console()
    console.print()
    console.print()
    console.rule("[bold]Decks affected by uncommited changes", align="left")
    console.print()
    table = Table("Deck", "Targets")
    for targets_name, targets_dependencies in all_targets_dependencies.items():
        touched_targets = []
        for target_name, target_dependencies in targets_dependencies.items():
            if touched.intersection(target_dependencies):
                touched_targets.append(target_name)
        if touched_targets:
            table.add_row(targets_name, " ".join(touched_targets))
    console.print(Padding(table if table.row_count else "None.", (0, 0, 0, 2)))


def _print_unused_report(
    section_paths: Iterable[Path],
    by_sections: Mapping[str, Mapping[str, Set[Tuple[str, str]]]],
    global_paths: GlobalPaths,
) -> None:
    console = Console()
    console.print()
    console.print()
    console.rule("[bold]Unused flavors", align="left")
    console.print()
    table = Table("Section", "Flavors")
    flavors = defaultdict(set)
    for section_path in section_paths:
        with section_path.open(encoding="utf8") as fh:
            section_config = yaml_safe_load(fh)
        section_name = "/".join(
            section_path.relative_to(global_paths.shared_latex_dir).parts[:-1]
        )
        flavors[section_name].update(section_config["flavors"])
    for section_name, section_flavors in sorted(flavors.items()):
        unused_flavors = [
            flavor
            for flavor in section_flavors
            if not by_sections[section_name][flavor]
        ]
        if unused_flavors:
            table.add_row(section_name, " ".join(sorted(unused_flavors)))
    console.print(Padding(table if table.row_count else "None.", (0, 0, 0, 2)))


def _print_section_report(
    section: str,
    flavor: Optional[str],
    by_sections: Mapping[str, Mapping[str, Set[Tuple[str, str]]]],
) -> None:
    console = Console()
    console.print()
    console.print()
    title = section
    if flavor is not None:
        title += f" {flavor}"
    console.rule(f"[bold]Decks depending on [italic]{title}", align="left")
    console.print()
    table = Table("Deck", "Targets")
    if flavor is None:
        flavors_dependencies = by_sections[section]
        for deck_path, target_name in sorted(set.union(*flavors_dependencies.values())):
            table.add_row(deck_path, target_name)
    else:
        flavors_dependencies = by_sections[section]
        for deck_path, target_name in sorted(flavors_dependencies[flavor]):
            table.add_row(deck_path, target_name)
    console.print(Padding(table if table.row_count else "None.", (0, 0, 0, 2)))


def _relative_to_shared_latex(paths: GlobalPaths, file_path: str) -> Optional[str]:
    try:
        return str((paths.git_dir / file_path).relative_to(paths.shared_latex_dir))
    except ValueError:
        return None
