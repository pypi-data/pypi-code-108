import click

from cnvrgv2.cli.utils import messages
from cnvrgv2.cli.utils.decorators import prepare_command


@click.group(name='experiment')
def experiment_group():
    pass


@experiment_group.command()
@click.option('-t', '--title', default=None, help=messages.EXPERIMENT_HELP_TITLE)
@click.option('-tm', '--templates', default=None, help=messages.EXPERIMENT_HELP_TEMPLATES)
@click.option('-l/-nl', '--local/--no-local', default=False, help=messages.EXPERIMENT_HELP_LOCAL)
@click.option('-c', '--command', prompt=messages.EXPERIMENT_PROMPT_COMMAND, help=messages.EXPERIMENT_HELP_COMMAND)
@click.option('-d', '--datasets', default=None, help=messages.EXPERIMENT_HELP_DATASETS)
@click.option('-v', '--volume', default=None, help=messages.EXPERIMENT_HELP_VOLUME)
@click.option('-sb/-nsb', '--sync-before/--no-sync-before', default=True, help=messages.EXPERIMENT_HELP_SYNC_BEFORE)
@click.option('-sa/-nsa', '--sync-after/--no-sync-after', default=True, help=messages.EXPERIMENT_HELP_SYNC_AFTER)
@click.option('-i', '--image', default=None, help=messages.EXPERIMENT_HELP_IMAGE)
@click.option('-gb', '--git-branch', default=None, help=messages.EXPERIMENT_HELP_GIT_BRANCH)
@click.option('-gc', '--git-commit', default=None, help=messages.EXPERIMENT_HELP_GIT_COMMIT)
@prepare_command()
def run(
    cnvrg,
    logger,
    project,
    title,
    templates,
    local,
    command,
    datasets,
    volume,
    sync_before,
    sync_after,
    image,
    git_branch,
    git_commit
):
    dataset_objects = None
    volume_object = None
    kwargs = {}
    templates_list = templates.split(",") if templates else None

    if datasets:
        dataset_names = datasets.split(",")
        dataset_objects = [cnvrg.datasets.get(ds_name) for ds_name in dataset_names]

    if volume:
        volume_object = project.volumes.get(volume)

    if image:
        image_name, image_tag = image.split(":")
        kwargs["image"] = cnvrg.images.get(name=image_name, tag=image_tag)

    if git_branch:
        kwargs["git_branch"] = git_branch

    if git_commit:
        kwargs["git_commit"] = git_commit

    experiment = project.experiments.create(
        title=title,
        templates=templates_list,
        local=local,
        command=command,
        datasets=dataset_objects,
        volume=volume_object,
        sync_before=sync_before,
        sync_after=sync_after,
        **kwargs
    )
    success_message = messages.EXPERIMENT_CREATE_SUCCESS.format(experiment.title, experiment.full_href)
    logger.log_and_echo(success_message)
