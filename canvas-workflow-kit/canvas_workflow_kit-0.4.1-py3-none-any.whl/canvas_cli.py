#!/usr/bin/env python

import json

from os.path import join
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict, Union

from datetime import date

import arrow
import click
import requests

from canvas_workflow_kit import settings
from canvas_workflow_kit.api import fetch_patient
from canvas_workflow_kit.patient import Patient
from canvas_workflow_kit.timeframe import Timeframe
from canvas_workflow_kit.internal.string import snakecase
from canvas_workflow_kit.utils import (
    parse_class_from_python_source, load_local_patient
)

mocks_path = 'TODO'


# Utility methods -----------
#
def green(string: str) -> str:
    return click.style(string, fg='green')


def blue(string: str) -> str:
    return click.style(string, fg='blue', bold=True)


def cyan(string: str) -> str:
    return click.style(string, fg='cyan', bold=True)


def yellow(string: str) -> str:
    return click.style(string, fg='yellow', bold=True)


def red(string: str) -> str:
    return click.style(string, fg='red')


# CLI Commands -----------------------------------

@click.group()
@click.pass_context
@click.option('--use-config', required=False)
def cli(ctx, use_config='canvas_cli'):

    ctx.ensure_object(dict)
    ctx.obj['config_section'] = use_config and use_config or settings.DEFAULT_CONFIG_SECTION

    if ctx.invoked_subcommand != 'create-default-settings':
        try:
            ctx.obj['settings'] = settings.read_config(ctx.obj['config_section'])
        except (FileNotFoundError, ValueError) as e:
            raise click.ClickException(e)


@cli.command()
def create_default_settings():
    """
    Create a default settings file with placeholder text in `~/.canvas/config.ini`.
    File will only be created if it does not yet exist.
    """

    settings_path = settings.CONFIG_PATH

    if settings_path.is_file():
        raise click.ClickException(f'Settings file already exists at {settings_path}')

    settings_path.parent.mkdir(parents=True, exist_ok=True)

    click.echo(f'Writing default settings to "{settings_path}"...')

    settings_path.write_text('''[canvas_cli]
url =
api-key =
''')


@cli.command()
@click.argument('output_path')
def create(output_path: Path):
    """
    Create a new item
    """
    output_path = Path(output_path)
    if output_path.is_file():
        raise click.ClickException(f'File already exists at {output_path}')

    template_path = Path(__file__).parent / 'builtin_cqms/stub_template_user.py.txt'
    template = template_path.open('r').read()

    content = template.format(**{
        'value_sets': '*',
        'year': date.today().year,
        'class_name': "MyClinicalQualityMeasure",
        'title': "My Clinical Quality Measure",
        'description': 'Description',
        'information_link': 'https://link_to_protocol_information',
        'types': ['CQM'],
        'authors': '"Canvas Example Medical Association (CEMA)"',
        'references': '"Gunderson, Beau;  Excellence in Software Templates. 2012 Oct 20;161(7):422-34."',
        'funding_source': '',
        'denominator': 'pass',
        'numerator': 'pass'
    })
    with output_path.open('w') as output_handle:
        output_handle.write(content)

    click.echo(green(f'Successfully wrote template to {output_path.absolute()}'))


@cli.command()
@click.argument('patient-keys', nargs=-1)
@click.option('-d', '--destination', required=False, type=click.Path(),
              help="Specify a directory to store the output.")
@click.pass_context
def fixture_from_patient(ctx, patient_keys: List[str], destination: Path):
    """
    Export a fixture for the list of provided patient keys.
    Fixtures will be created with files representing the various categories.
    Eg: billingLineItems.json, conditions.json, referralReports.json ...
    """

    for patient_key in patient_keys:
        _process_fixture_from_patient(patient_key, destination)


@click.pass_context
def _process_fixture_from_patient(ctx, patient_key, output_directory):
    click.echo(f'Getting fixture from patient "{patient_key}"...')

    response_json = fetch_patient(patient_key, ctx.obj['config_section'])

    if not output_directory:
        output_directory = Path(".")

    patient = response_json['patient']
    patient_summary = f"{patient['firstName']} {patient['lastName']} {patient['birthDate'][0:4]} ({patient['sexAtBirth']})"

    output_directory = Path(output_directory) / patient_summary

    output_directory.mkdir(parents=True, exist_ok=True)
    for key, values in response_json.items():
        (output_directory / f'{snakecase(key)}.json').write_text(json.dumps(values))

    click.echo(green(f'Successfully wrote patient fixture to {output_directory.absolute()}'))


@cli.command()
@click.argument('module-path')
@click.argument('fixture-folder')
@click.option('--date')
@click.option('--start-date')
@click.option('--end-date')
@click.option('--full', flag_value='full', default=False,
              help="Show the full output returned to the application.")
def test_fixture(
    module_path: str, fixture_folder: str,
    date: str = None, start_date: str = None, end_date: str = None,
    full: bool = False
):
    """
    Test a python file with a ClinicalQualityMeasure against a fixture folder.
    """
    module_path = Path(module_path)
    try:
        Class = parse_class_from_python_source(module_path.open('r').read())
    except SyntaxError as e:
        if not e.text:
            e.text = ''
        raise SyntaxError(
            f'Could not parse python file.\n  File "{module_path.absolute()}", line {e.lineno}\n    {e.text.strip()}\nSyntaxError: {e.msg}')

    path = Path(fixture_folder)

    subdirectories = [x for x in path.iterdir() if x.is_dir()]

    if subdirectories:
        for i, fixture_folder in enumerate(subdirectories):
            if i >= 1:
                click.echo('-' * 80)
            test_fixture_directory(fixture_folder, Class, date, start_date, end_date, full)

    else:
        test_fixture_directory(path, Class, date, start_date, end_date, full)


def test_fixture_directory(
    fixture_folder: Path, Class: type,
    date: str = None, start_date: str = None, end_date: str = None,
    full: bool = False
):
    # 2. load JSON folder of fixture data
    fixture_title = f"Fixture: {yellow(fixture_folder.name)}"

    click.echo(fixture_title)

    patient = load_local_patient(Path(fixture_folder))

    if date:
        date = arrow.get(date)
    else:
        date = arrow.now()

    if start_date:
        start_date = arrow.get(start_date)
    else:
        start_date = arrow.now().shift(years=-1)

    if end_date:
        end_date = arrow.get(end_date)
    else:
        end_date = arrow.now()

    timeframe = Timeframe(start=start_date, end=end_date)

    # 3. instantiate module
    protocol = Class(patient=patient, date=date, timeframe=timeframe)
    results = protocol.compute_results()

    # 4. return results
    recommendations = getattr(results, 'recommendations', None)
    if not recommendations:
        click.echo(red("No recommendations"))

    elif full:
        recommendations = [vars(r) for r in recommendations]
        click.echo(json.dumps(vars(results), indent=2))
    else:
        for r in recommendations:
            click.echo(cyan(r.__class__.__name__))
            for attr in ('title', 'key', 'button'):
                if hasattr(r, attr):
                    click.echo(f' {blue(attr.capitalize())}: {getattr(r, attr)}')


@cli.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--force', default=False, is_flag=True, help="Allow the version to be overridden.")
@click.pass_context
def upload(ctx, filename: Path, force=False):
    """
    Upload a ClinicalQualityMeasure to the server
    """

    if not filename.endswith('.py'):
        raise click.ClickException(f'Only python files with a .py extension can be uploaded.')

    filename_path = Path(filename)

    click.echo(f'Uploading {filename_path.name}...')

    with filename_path.open() as f:
        contents = f.read()

    files = {'file': filename_path.open('rb')}

    # Send additional data with GET.  Using POST messes up the file upload.
    force_str = ''
    if force:
        force_str = '?force=1'

    response = requests.post(join(
        ctx.obj["settings"]["url"], f'api/PatientProtocol/upload/'
    ) + force_str, files=files, headers={
        'Authorization': ctx.obj['settings']['api_key'],
        'Content-Length': str(len(contents)),
        'Content-Disposition': f'attachment; filename="{filename_path.name}"'
    })

    if response.status_code == 201 and response.json().get('status') == 'success':
        version = response.json().get('data', {}).get('version')
        version_str = ''
        if version:
            version_str = f'Version {version}'
        click.echo(green(f'Upload successful.  {version_str} set to latest version.'))
    else:
        raise click.ClickException(response.text)


@cli.command()
@click.argument('module-name')
def set_active(module_name: str):
    """
    Set a protocol to active on the server
    """
    click.echo(f'Setting {module_name} as active...')
    _set_active(True, module_name)


@cli.command()
@click.argument('module-name')
def set_inactive(module_name: str):
    """
    Set a protocol to inactive on the server
    """
    click.echo(f'Setting {module_name}" as inactive...')
    _set_active(False, module_name)


@click.pass_context
def _set_active(ctx, is_active: bool, module_name: str):
    response = requests.post(join(
        ctx.obj["settings"]["url"], f'api/PatientProtocol/set_active/'
    ), data={
        'is_active': is_active and 1 or 0,
        'module_name': module_name,
    }, headers={
        'Authorization': ctx.obj['settings']['api_key'],
    })
    if response.status_code == 200:
        click.echo(green(response.json().get('data', {}).get('detail')))
    else:
        raise click.ClickException(response.text)


@cli.command()
@click.argument('module-name')
@click.pass_context
def list_versions(ctx, module_name: str):
    """
    List the available versions on the server.
    """
    response = requests.get(join(
        ctx.obj["settings"]["url"], f'api/PatientProtocol/version/{module_name}/'
    ), headers={
        'Authorization': ctx.obj['settings']['api_key'],
    })

    if response.status_code == 200:
        is_active = response.json().get('is_active')
        active_version = response.json().get('active_version')

        color_method = green if is_active else red

        click.echo("Is Active: " + color_method(is_active))
        click.echo("Active version: " + green(active_version))
        click.echo("Versions: ")

        for version in response.json().get('versions', []):
            version_number = version.get('version')
            def color_method(x): return x
            if version_number == active_version:
                color_method = green

            click.echo(color_method(f' {version_number}: {version.get("changelog")}'))

    else:
        raise click.ClickException(response.text)


@cli.command()
@click.argument('module-name')
@click.argument('version')
@click.pass_context
def set_version(ctx, module_name: str, version: str):
    """
    Set a protocol's active version on the server.
    The protocol upload may still need to be made active after changing the version.
    """
    response = requests.post(join(
        ctx.obj["settings"]["url"], f'api/PatientProtocol/version/{module_name}/'
    ), data={
        'version': version,
    }, headers={
        'Authorization': ctx.obj['settings']['api_key'],
    })
    if response.status_code == 200:
        click.echo(green(response.json().get('data', {}).get('detail')))
    else:
        raise click.ClickException(response.text)


if __name__ == '__main__':
    cli()
