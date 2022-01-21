"""The main OU Container Builder commandline application.

Run ``ou-container-builder --help`` for help with the command-line parameters.
"""
import click
import os
import re
import shutil
import subprocess

from jinja2 import Environment, PackageLoader
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from . import generators, packs
from .validator import validate_settings


def run_build(settings: dict, context: str, build: bool, clean: bool, tag: list) -> list:
    """Run the build process.

    This processes the ``settings``, generates the required files, and then runs the Docker build process.

    :param settings: The settings parsed from the configuration file
    :type settings: dict
    :param context: The directory within which to run the build
    :type context: str
    :param build: Whether to automatically invoke ``docker build``
    :type build: bool
    :param clean: Whether to automatically clean all generated files
    :type clean: bool
    :param tag: A list of tags to pass to docker
    :type tag: list[str]
    :return: A list with any errors that occured during processing
    :rtype: list
    """
    settings = validate_settings(settings)
    if isinstance(settings, dict):
        env = Environment(loader=PackageLoader('ou_container_builder', 'templates'),
                          autoescape=False)

        if os.path.exists(os.path.join(context, 'ou-builder-build')):
            shutil.rmtree(os.path.join(context, 'ou-builder-build'))
        os.makedirs(os.path.join(context, 'ou-builder-build'))

        # Handle base image
        if re.match(r'3\.[789]', settings['base']):
            settings['base'] = f'python:{settings["base"]}-slim-buster'

        # Handle optional packs
        if 'packs' in settings and settings['packs']:
            if 'tutorial-server' in settings['packs']:
                settings = packs.tutorial_server(context, env, settings)
            if 'mariadb' in settings['packs']:
                settings = packs.mariadb(context, env, settings)

        # Setup the generators
        if settings['type'] == 'jupyter-notebook':
            settings = generators.jupyter_notebook.setup(context, env, settings)
        elif settings['type'] == 'web-app':
            settings = generators.web_app.setup(context, env, settings)

        # Handle core packs
        if 'services' in settings:
            settings = packs.services(context, env, settings)
        if 'scripts' in settings:
            settings = packs.scripts(context, env, settings)
        settings = packs.content(context, env, settings)

        # Handle automatic hacks
        if 'packages' in settings and 'apt' in settings['packages']:
            if 'openjdk-11-jdk' in settings['packages']['apt']:
                if 'hacks' in settings:
                    if 'missing-man1' not in settings['hacks']:
                        settings['hacks'].append('missing-man1')
                else:
                    settings['hacks'] = ['missing-man1']

        settings = validate_settings(settings)
        if isinstance(settings, dict):
            # Sort package lists
            if 'packages' in settings:
                if 'apt' in settings['packages']:
                    settings['packages']['apt'].sort()
                if 'pip' in settings['packages']:
                    settings['packages']['pip'].sort()

            # Generate the Dockerfiles
            if settings['type'] == 'jupyter-notebook':
                generators.jupyter_notebook.generate(context, env, settings)
            elif settings['type'] == 'web-app':
                generators.web_app.generate(context, env, settings)

            if build:
                cmd = ['docker', 'build', context]
                if tag:
                    for t in tag:
                        cmd.append('--tag')
                        cmd.append(t)
                subprocess.run(cmd)
                if clean:
                    os.unlink(os.path.join(context, 'Dockerfile'))
                    if os.path.exists(os.path.join(context, 'ou-builder-build')):
                        shutil.rmtree(os.path.join(context, 'ou-builder-build'))
            return []
        else:
            return settings
    else:
        return settings


@click.command()
@click.option('-c', '--context',
              default='.',
              help='Context within which the container will be built',
              show_default=True)
@click.option('-b/-nb', '--build/--no-build',
              default=True,
              help='Automatically build the container',
              show_default=True)
@click.option('--clean/--no-clean',
              default=True,
              help='Automatically clean up after building the container',
              show_default=True)
@click.option('--tag',
              multiple=True,
              help='Automatically tag the generated image')
def main(context: str, build: bool, clean: bool, tag: list):
    """Build your OU Container."""
    with open(os.path.join(context, 'ContainerConfig.yaml')) as config_f:
        settings = load(config_f, Loader=Loader)
    result = run_build(settings, context, build, clean, tag)
    if result:
        click.echo(click.style('There are errors in your configuration settings:', fg='red'), err=True)
        click.echo(err=True)
        for error in settings:
            click.echo(error, err=True)


if __name__ == '__main__':
    main()
