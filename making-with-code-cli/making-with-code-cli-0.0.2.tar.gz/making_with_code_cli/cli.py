import click
from pprint import pprint
from pathlib import Path
from subprocess import run
import yaml
import os
from making_with_code_cli.mwc_api import MakingWithCodeAPI as API
from making_with_code_cli.styles import (
    address,
    question,
    info,
    confirm,
)
from making_with_code_cli.settings import (
    read_settings, 
    iter_settings,
    write_settings,
)
from making_with_code_cli.cli_setup import (
    INTRO_MESSAGE,
    INTRO_NOTES,
    WORK_DIR_PERMISSIONS,
    choose_mwc_username,
    choose_work_dir,
    choose_mwc_site_url,
    choose_course,
    choose_editor,
    MWCShellConfig,
    InstallHomebrew,
    InstallXCode,
    InstallPoetry,
    WriteShellConfig,
    InstallPython3,
    InstallGit,
    InstallAtom,
    GHAuthentication,
)
from making_with_code_cli.curriculum import (
    get_curriculum,
)
from making_with_code_cli.git_backend import (
    get_backend,
)

@click.group()
def cli():
    "Command line interface for Making with Code."
    pass

#@cli.command()
def home():
    "Go to the MWC home folder"
    settings = read_settings()
    print(settings["work_dir"])
    os.chdir(settings["work_dir"])

@cli.command()
@click.option("--yes", is_flag=True, help="Automatically answer 'yes' to setup prompts")
@click.option("--teacher", is_flag=True, help="Install in teacher mode")
@click.pass_context
def setup(ctx, yes, teacher):
    """Set up the MWC command line interface"""
    settings = read_settings()
    rc_tasks = []
    click.echo(address(INTRO_MESSAGE))
    for note in INTRO_NOTES:
        click.echo(address(note, list_format=True))
    click.echo()
    #settings['mwc_username'] = choose_mwc_username(settings.get("mwc_username"))
    settings['role'] = "teacher" if teacher else "student"
    settings['work_dir'] = str(choose_work_dir(settings.get("work_dir")).resolve())
    settings['mwc_site_url'] = choose_mwc_site_url(settings.get('mwc_site_url'))
    curriculum = get_curriculum(settings)
    settings['course'] = choose_course([course['name'] for course in curriculum['courses']])
    settings['editor'] = choose_editor(settings.get('editor', 'atom'))
    if yes:
        click.echo(info("Updated settings:"))
        click.echo(info(yaml.dump(read_settings()), preformatted=True))
    else:
        click.echo(info(yaml.dump(read_settings()), preformatted=True))
        click.confirm(
            question("Do these settings look ok?"),
            abort=True
        )
    write_settings(settings)

    tasks = [
        MWCShellConfig(settings),
        InstallHomebrew(settings),
        InstallXCode(settings),
        InstallPoetry(settings),
        WriteShellConfig(settings),
        InstallPython3(settings),
        InstallGit(settings),
        InstallAtom(settings),
        GHAuthentication(settings),
    ]
    for task in tasks:
        task.run_task_if_needed()
    
    ctx.invoke(update)

@cli.command()
def update():
    """Update the MWC directory."""
    settings = read_settings()
    curr = get_curriculum(settings)
    course = [c for c in curr['courses'] if c['name'] == settings['course']][0]
    backend = course['git_backend']
    G = get_backend(backend)(settings)
    mwc_home = Path(settings["work_dir"])
    mwc_home.mkdir(mode=WORK_DIR_PERMISSIONS, parents=True, exist_ok=True)
    for course in curr['courses']:
        course_dir = mwc_home / course['slug']
        course_dir.mkdir(mode=WORK_DIR_PERMISSIONS, exist_ok=True)
        for unit in course['units']:
            unit_dir = course_dir / unit['slug']
            unit_dir.mkdir(mode=WORK_DIR_PERMISSIONS, exist_ok=True)
            for module in unit['modules']:
                module_dir = unit_dir / module['slug']
                if not module_dir.exists() and 'init_action' in module:
                    rel_dir = module_dir.resolve().relative_to(mwc_home)
                    msg = f"Initializing {module['slug']} at {rel_dir}. See {module['url']} for details."
                    click.echo(confirm(msg))
                    G.init_module(module, module_dir)
