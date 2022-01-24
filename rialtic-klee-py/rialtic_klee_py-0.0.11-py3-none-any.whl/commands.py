import click, os, sys, traceback
from klee.internal import log, Structure
from klee import plans, test

@click.group()
def cli():
    if not os.path.exists('oim-engine.json'):
        print("This utility may only be run from within an engine's root directory.")
        sys.exit(1)
# Common Args
def shared_args(fn):
    click.argument('targets', nargs=-1)(fn)
    click.option('-p', '--plan_type', default='default', type =
        click.Choice([*plans.Options], case_sensitive=False))(fn)
    click.option('-c', '--claims-dir', default='test_claims', help='suggested location: test_claims')(fn)
    click.option('-o', '--output-dir', default='test_cases', help="suggested location: test_cases")(fn)
def test_args(fn):
    shared_args(fn)
    click.option('--pytest', default = "-vvv", help="arguments to send to pytest")(fn)
# Legacy/JSON output
@shared_args
@cli.command('build')
def BuildCommand(targets, plan_type, claims_dir, output_dir):
    structure = Structure(os.getcwd(), claims_dir, output_dir)
    structure.json_enabled = True; structure.register_instance()
    _echo('Building', targets)

    @error_logging
    def _logic():
        build_sys = plans.Options[plan_type.lower()](structure)
        build_sys.build_node_labels(targets)
# Run Tests Locally
@test_args
@cli.command('test')
def ExecLocalTest(targets, plan_type, claims_dir, output_dir, pytest):
    structure = Structure(os.getcwd(), claims_dir, output_dir)
    structure.register_instance()

    _echo('Running tests for', targets)
    if not test.PyTestUtility.env_vars_present():
        print("aborting...")
        sys.exit(1)

    @error_logging
    def _logic():
        build_sys = plans.Options[plan_type.lower()](structure)
        test_cases = build_sys.build_node_labels(targets)

        args = [x.strip() for x in pytest.split(',')]
        test.LocalTest(args).invoke_cases(test_cases)
# Run Tests Remotely
@test_args
@cli.command('smoke')
def ExecSmokeTest(targets, plan_type, claims_dir, output_dir, pytest):
    structure = Structure(os.getcwd(), claims_dir, output_dir)
    structure.register_instance(); _echo('Running smoke tests for', targets)

    @error_logging
    def _logic():
        build_sys = plans.Options[plan_type.lower()](structure)
        test_cases = build_sys.build_node_labels(targets)

        args = [x.strip() for x in pytest.split(',')]
        test.SmokeTest(args).invoke_cases(test_cases)
# Helper Functions
def _echo(what, targets):
    message = f'cli: {what} {",".join(targets) or "all"} targets\n'
    click.echo(message); log.info(message)

def error_logging(closure):
    try:
        closure()
    except:
        log.critical(traceback.format_exc())
