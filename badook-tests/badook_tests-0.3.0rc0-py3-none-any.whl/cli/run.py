import click
import unittest
from badook_tests import BadookRuntimeTestResult
from badook_tests.context import global_context


@click.command()
@click.option(
    "--target-directory",
    "-d",
    default="./",
    help="The root of the project directory where you want to execute badook tests.",
)
@click.option('--batch/--no-batch', default=False)
@click.option('--force-pull/--no-force', default=False)
@click.option('--rerun-id')
@click.option('--file_path', '-f', default='')
def run(target_directory, batch, force_pull, rerun_id, file_path):
    global_context.track_batch = batch
    global_context.force_pull = force_pull

    pattern = 'test*.py'

    if file_path:
        if not file_path.endswith('.py'):
            file_path += '.py'

        split_paths = file_path.rsplit('/', 1)

        if len(split_paths) > 1:
            target_directory, pattern = split_paths
        else:
            target_directory = ''
            pattern = split_paths[0]

        click.secho(f'file={pattern}', fg='blue')

    suit = unittest.defaultTestLoader.discover(
        target_directory, pattern=pattern)
    click.secho(f'found {len(suit._tests)} test cases', fg='green')
    if rerun_id:
        click.secho(f'rerun id={rerun_id}', fg='blue')
        global_context.run_id = rerun_id
        global_context.rerun = True

    unittest.TextTestRunner(resultclass=BadookRuntimeTestResult).run(suit)
