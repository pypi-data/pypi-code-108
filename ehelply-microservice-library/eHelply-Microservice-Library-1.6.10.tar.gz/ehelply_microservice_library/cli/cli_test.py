import math
from typing import List
import typer
import pytest
from pytest import ExitCode
import os
from pathlib import Path
import coverage
import pylint.lint

cli = typer.Typer()

LINTING_CONFIG_VERSION: str = "0.0.1"

LINTING_THRESHOLD: float = 8.0
UNIT_TEST_COVERAGE_THRESHOLD: int = 69
INTEGRATION_TEST_COVERAGE_THRESHOLD: int = 50

OMIT_PATTERNS_LINTING: List[str] = [
    "example/**/*",
    "db/alembic/**/*",
    "service_meta.py",
    "service_template/**/*"
]

OMIT_PATTERNS_TESTING: List[str] = [
    "src/example/*",
    "src/db/alembic/*",
    "src/db/*schema*.py",
    "src/db/*model*.py",
    "src/*seeders*",
    "src/service_meta.py",
    "src/service_template/*",
    "src/db/__init__.py",
    "src/service.py"
]


def lint() -> float:
    omit_files: List[str] = []

    for omit_pattern in OMIT_PATTERNS_LINTING:
        for path in Path('src').glob(omit_pattern):
            omit_files.append(str(path))

    files_to_lint: List[str] = []

    for path in Path('src').rglob("*.py"):
        if str(path) not in omit_files:
            files_to_lint.append(str(path))

    results = pylint.lint.Run(
        [
            "-r",  # generate report
            "y",  # yes
            "-s",  # generate code score
            "y",  # yes
            f"--rcfile=.pylintrc.ehelply.{LINTING_CONFIG_VERSION}",
        ] + files_to_lint,
        exit=False
    )

    linting_score = results.linter.stats.global_note

    return linting_score


def test_base(tests_dir: Path, test_results_dir: Path) -> float:
    test_results_dir.mkdir(parents=True, exist_ok=True)

    result: ExitCode = pytest.main(
        [
            "-s",
            "-v",
            "--cov-report", f"html:{str(test_results_dir)}",
            "--cov=src",
            f"{str(tests_dir)}/"
        ]
    )

    if result != ExitCode.OK and result != ExitCode.NO_TESTS_COLLECTED:
        raise typer.Exit(code=result)

    cov = coverage.Coverage()
    cov.load()

    coverage_amount: float = cov.report(
        show_missing=True,
        omit=OMIT_PATTERNS_TESTING
    )

    return coverage_amount


def unit_test() -> float:
    root_path: Path = Path(os.getcwd())

    tests_dir: Path = Path(root_path).resolve().joinpath('tests').joinpath('unit')

    test_results_dir: Path = Path(root_path).resolve().joinpath('test-results').joinpath('unit')

    return test_base(tests_dir, test_results_dir)


def integration_test():
    root_path: Path = Path(os.getcwd())

    tests_dir: Path = Path(root_path).resolve().joinpath('tests').joinpath('integration')

    test_results_dir: Path = Path(root_path).resolve().joinpath('test-results').joinpath('integration')

    return test_base(tests_dir, test_results_dir)


def migrate():
    # Run DB migrations or unit tests for features relying on DB migrations will fail
    #   Thus, failing prod build/deploys
    typer.echo("Running Migrations..")
    from alembic.config import Config
    import alembic.command

    config = Config('alembic.ini')
    config.attributes['configure_logger'] = False

    alembic.command.upgrade(config, 'head')


@cli.command()
def linting(
        ignore_final_report: bool = typer.Option(False),
        ignore_failures: bool = typer.Option(False)
):
    report: List[str] = [
        "\n",
        "REPORT"
    ]

    """
    LINTING
    """
    linting_score: float = lint()

    if linting_score < LINTING_THRESHOLD and not ignore_failures:
        raise Exception(
            f"Linting score is {round(linting_score, 2)} which is below {LINTING_THRESHOLD}. Thus, build has failed."
        )

    report.append(f" * Linting score: {round(linting_score, 2)}/10, Linting threshold: {LINTING_THRESHOLD}")

    """
    REPORTING
    """

    report.append("\n")

    if not ignore_final_report:
        for line in report:
            typer.echo(line)


@cli.command()
def units(
        ignore_final_report: bool = typer.Option(False),
        ignore_failures: bool = typer.Option(False)
):
    report: List[str] = [
        "\n",
        "REPORT"
    ]

    migrate()
    report.append(" * Database Migrations were run")

    """
    UNIT TESTING
    """

    coverage_amount: float = unit_test()
    if math.ceil(coverage_amount) < UNIT_TEST_COVERAGE_THRESHOLD and not ignore_failures:
        raise Exception(
            f"Unit test coverage is {math.ceil(coverage_amount)}% which is below {UNIT_TEST_COVERAGE_THRESHOLD}%. Thus, build has failed."
        )

    report.append(
        f" * Unit test coverage: {int(coverage_amount)}%/100%, Unit test coverage threshold: {UNIT_TEST_COVERAGE_THRESHOLD}%")

    """
    REPORTING
    """

    report.append("\n")

    if not ignore_final_report:

        for line in report:
            typer.echo(line)


@cli.command()
def integrations(
        ignore_final_report: bool = typer.Option(False),
        ignore_failures: bool = typer.Option(False)
):
    report: List[str] = [
        "\n",
        "REPORT"
    ]

    migrate()
    report.append(" * Database Migrations were run")

    """
    INTEGRATION TESTING
    """

    coverage_amount: float = integration_test()
    if math.ceil(coverage_amount) < INTEGRATION_TEST_COVERAGE_THRESHOLD and not ignore_failures:
        raise Exception(
            f"Integration test coverage is {math.ceil(coverage_amount)}% which is below {INTEGRATION_TEST_COVERAGE_THRESHOLD}%. Thus, build has failed."
        )

    report.append(
        f" * Integration test coverage: {int(coverage_amount)}%/100%, Integration test coverage threshold: {INTEGRATION_TEST_COVERAGE_THRESHOLD}%")

    """
    REPORTING
    """

    report.append("\n")

    if not ignore_final_report:
        for line in report:
            typer.echo(line)
