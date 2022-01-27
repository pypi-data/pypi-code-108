import click
import json
import logging.config
import os
import sys

from cfde_submit import CfdeClient, CONFIG, exc, version

DEFAULT_STATE_FILE = os.path.expanduser("~/.cfde_client.json")
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version=version.__version__, message="%(version)s")
def cli():
    """Client to interact with the DERIVA Action Provider and associated Flows."""
    pass


@cli.command()
@click.argument("data-path", nargs=1, type=click.Path(exists=True))
@click.option("--dcc-id", "--dcc", default=None, show_default=True)
@click.option("--catalog", default=None, show_default=True)
@click.option("--disable-validation", is_flag=True, default=False, show_default=True)
@click.option("--schema", default=None, show_default=True)
@click.option("--output-dir", default=None, show_default=True, type=click.Path(exists=False))
@click.option("--delete-dir/--keep-dir", is_flag=True, default=False, show_default=True)
@click.option("--ignore-git/--handle-git", is_flag=True, default=False, show_default=True)
@click.option("--dry-run", is_flag=True, default=False, show_default=True)
@click.option("--test-submission", "--test-sub", "--test-drive", is_flag=True, default=False,
              show_default=True)
@click.option("--verbose", "-v", is_flag=True, default=False, show_default=True)
@click.option("--server", default=None)
@click.option("--globus", is_flag=True, default=False)
@click.option("--bag-kwargs-file", type=click.Path(exists=True), default=None)
@click.option("--client-state-file", type=click.Path(exists=True), default=None)
def run(data_path, dcc_id, catalog, schema, output_dir, delete_dir, ignore_git, dry_run,
        test_submission, verbose, server, globus, disable_validation, bag_kwargs_file,
        client_state_file):
    """Start the Globus Automate Flow to ingest CFDE data into DERIVA."""

    # Set log levels
    if verbose:
        set_log_level("DEBUG")
    else:
        log_level = os.environ.get("CFDE_SUBMIT_LOGGING")
        if log_level:
            set_log_level(log_level)

    # Read state file
    if not client_state_file:
        client_state_file = DEFAULT_STATE_FILE
    try:
        with open(client_state_file) as f:
            state = json.load(f)
        logger.debug("Loaded previous state")
    except FileNotFoundError:
        state = {}
        logger.debug("No previous state found")

    # Read bag_kwargs_file if provided
    if bag_kwargs_file:
        with open(bag_kwargs_file) as f:
            bag_kwargs = json.load(f)
    else:
        bag_kwargs = {}

    # Determine DCC ID
    # If user supplies DCC as option, will always use that
    # If supplied DCC is different from previously saved DCC, prompt to save,
    # unless user has not saved DCC or disabled the save prompt
    logger.debug("Determining DCC")
    state_dcc = state.get("dcc_id")
    never_save = state.get("never_save")

    if not never_save and dcc_id is not None and state_dcc is not None and state_dcc != dcc_id:
        logger.debug("Saved DCC '{}' mismatch with provided DCC '{}'".format(state_dcc, dcc_id))
        save_dcc = yes_or_no(f'Would you like to save {dcc_id} as your default DCC ID (instead of '
                             f'"{state_dcc}")?')
        if save_dcc:
            state['dcc_id'] = dcc_id
        else:
            disable_prompt = yes_or_no("Would you like to disable this prompt permanently?")
            if disable_prompt:
                state["never_save_dcc"] = True

    elif dcc_id is None and state_dcc is not None:
        dcc_id = state_dcc
        print("Using saved DCC '{}'".format(dcc_id))

    elif dcc_id is None and state_dcc is None:
        logger.debug("No saved DCC ID found and no DCC provided")
        dcc_id = input("Please enter the CFDE identifier for your "
                       "Data Coordinating Center: ").strip()
        save_dcc = yes_or_no(f'Thank you. Would you like to save {dcc_id} for future submissions?')
        if save_dcc:
            state["dcc_id"] = dcc_id
            logger.debug("DCC ID '{}' will be saved if the Flow initialization is successful and "
                         "this is not a dry run".format(dcc_id))
    try:
        logger.debug("Initializing Flow")
        cfde = CfdeClient()
        login_user()
        logger.debug("CfdeClient initialized, starting Flow")
        package_name = os.path.basename(os.path.normpath(data_path))
        resp = yes_or_no(f"Submit datapackage '{package_name}' using {dcc_id}?")
        if resp:
            start_res = cfde.start_deriva_flow(data_path, dcc_id=dcc_id, catalog_id=catalog,
                                               schema=schema, output_dir=output_dir,
                                               delete_dir=delete_dir,
                                               handle_git_repos=(not ignore_git), server=server,
                                               dry_run=dry_run, test_sub=test_submission,
                                               globus=globus, disable_validation=disable_validation,
                                               **bag_kwargs)
        else:
            exit_on_exception("Aborted. No data submitted.")
    except (exc.SubmissionsUnavailable, exc.InvalidInput, exc.ValidationException,
            exc.EndpointUnavailable, FileExistsError) as e:
        exit_on_exception(e)
    except Exception as e:
        exit_on_exception(repr(e))
    else:
        if not start_res["success"]:
            print("Error during Flow startup: {}".format(start_res["error"]))
        else:
            print(start_res["message"])
            if not dry_run:
                state["service_instance"] = cfde.service_instance
                state["flow_id"] = start_res["flow_id"]
                state["flow_instance_id"] = start_res["flow_instance_id"]
                state["http_link"] = start_res["http_link"]
                state["globus_web_link"] = start_res["globus_web_link"]
                with open(client_state_file, 'w') as out:
                    json.dump(state, out)
                logger.debug("State saved to '{}'".format(client_state_file))


@cli.command()
@click.option("--flow-id", default=None, show_default=True)
@click.option("--flow-instance-id", default=None, show_default=True)
@click.option("--raw", is_flag=True, default=False)
@click.option("--client-state-file", type=click.Path(exists=True), default=None)
def status(flow_id, flow_instance_id, raw, client_state_file):
    """Check the status of a Flow."""
    login_user(quiet=True)
    if not flow_id or not flow_instance_id:
        if not client_state_file:
            client_state_file = DEFAULT_STATE_FILE
        try:
            with open(client_state_file) as f:
                client_state = json.load(f)
            flow_id = flow_id or client_state.get("flow_id")
            flow_instance_id = flow_instance_id or client_state.get("flow_instance_id")
            if not flow_id or not flow_instance_id:
                raise ValueError("flow_id or flow_instance_id not found")
        except (FileNotFoundError, ValueError):
            print("Flow not started and flow-id or flow-instance-id not specified")
            return
    try:
        cfde = CfdeClient()
        if cfde.service_instance != "prod":
            click.secho(f"Running on service '{cfde.service_instance}'", fg="yellow")
        status_res = cfde.check_status(flow_id, flow_instance_id, raw=True)
    except Exception as e:
        if raw:
            err = repr(e)
        else:
            err = str(e)
        print("Error checking status for Flow '{}': {}".format(flow_instance_id, err))
        return
    else:
        if raw:
            print(json.dumps(status_res, indent=4, sort_keys=True))
        else:
            print(status_res["clean_status"])


def login_user(force_login=False, no_browser=False, no_local_server=False, quiet=False):
    """
    Arguments:
        force_login -- Force a login flow with Globus Auth, even if tokens are valid
        no_browser -- Disable automatically opening a browser for login
        no_local_server -- Disable local server for automatically copying auth code
    """
    cfde = CfdeClient()
    if not quiet and cfde.service_instance != "prod":
        click.secho(f"Running on service '{cfde.service_instance}'", fg="yellow")

    try:
        if not cfde.is_logged_in():
            cfde.login(force=force_login, no_browser=no_browser, no_local_server=no_local_server)
            click.secho("You are authenticated and your tokens have been cached.", fg='green')
        cfde.check()
    except exc.CfdeClientException as ce:
        exit_on_exception(ce)


@cli.command()
@click.option("--force-login", is_flag=True, default=False, show_default=True)
@click.option("--no_browser", is_flag=True, default=False)
@click.option("--no_local_server", is_flag=True, default=False)
def login(force_login, no_browser, no_local_server):
    """Perform the login step (which saves credentials) by initializing
    a CfdeClient. The Client is then discarded.
    """
    logger.debug(f'Logged in? {CfdeClient().is_logged_in()}')
    if CfdeClient().is_logged_in():
        click.secho("You are already logged in")
    else:
        login_user(force_login, no_browser, no_local_server)


@cli.command()
def logout():
    """Log out and revoke your tokens."""
    cfde = CfdeClient()
    if cfde.is_logged_in():
        cfde.logout()
        click.secho("You have been logged out", fg='green')
    else:
        click.secho("You are not logged in")


@cli.command()
def reset():
    """ Reset cfde-submit configuration """
    remove = yes_or_no("Would you like to reset your cfde-submit settings and submit history?")
    if remove:
        if os.path.exists(DEFAULT_STATE_FILE):
            os.remove(DEFAULT_STATE_FILE)
        else:
            sys.exit("No cfde-submit settings exist, skipping")


def set_log_level(level):
    """ Reconfigure logging to a specific log level """
    log_config = CONFIG["LOGGING"].copy()
    log_config["handlers"]["console"]["level"] = level
    log_config["loggers"]["cfde_submit"]["level"] = level
    logging.config.dictConfig(log_config)
    global logger
    logger = logging.getLogger(__name__)


def yes_or_no(question):
    """ Ask the user a yes or no question. Returns True for yes, False for no """
    suffix = " (y/n)? > "
    question = question.rstrip()
    answer = input(question + suffix).lower().strip()
    if answer in ["y", "ye", "yes"]:
        return True
    elif answer in ["n", "no"]:
        return False
    else:
        print("Please answer with 'y' or 'n'\n")
        return yes_or_no(question)


def exit_on_exception(e):
    """ Print an exception and exit with an error """
    sys.exit(click.style(str(e), fg='red'))
