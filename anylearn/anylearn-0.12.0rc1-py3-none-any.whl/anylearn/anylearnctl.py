import json
from pathlib import Path
import time

import click

from anylearn.applications.hpo import run_hpo, run_hpo_trial
from anylearn.applications.quickstart import quick_train
from anylearn.config import AnylearnConfig
from anylearn.utils.errors import AnyLearnException, AnyLearnMissingParamException


@click.group()
@click.version_option()
def cli():
    pass


@cli.command()
@click.argument("cluster_address")
# TODO: implement API token auth and replace the basic auth below
@click.argument("username")
@click.argument("password")
@click.argument("search_space_file")
@click.option(
    "-f", "--foreground",
    is_flag=True,
    default=False,
    help="""Run HPO in foreground mode with log print in terminal.
    """
)
@click.option(
    "--algorithm-dir",
    default=None,
    help="""Local algorithm folder absolute path.
    """
)
@click.option(
    "--algorithm-entrypoint",
    default=None,
    help="""Entrypoint command of algorithm. 
    Required when using local algorithm.
    """
)
@click.option(
    "--algorithm-output",
    default=None,
    help="""Model saving path of algorithm. 
    Required when using local algorithm.
    """
)
@click.option(
    "--dataset-dir",
    default=None,
    help="""Local dataset folder absolute path.
    """
)
@click.option(
    "--project-name",
    default=None,
    help="""Name of project to assemble all HPO trials.
    """
)
@click.option(
    "--dataset-hyperparam-name",
    default="dataset",
    help="""Parameter name to pass dataset into algorithm.
    """
)
@click.option(
    "--gpu-num",
    default=1,
    help="""Number of GPU claimed for trial.
    """
)
@click.option(
    "--hpo-max-runs",
    default=10,
    help="""Max number of trials to run in HPO
    """
)
@click.option(
    "--hpo-max-duration",
    default="24h",
    help="""Max duration of HPO, string finished by time unit: 's', 'm', 'h'.
    """
)
@click.option(
    "--hpo-tuner-name",
    default="TPE",
    help="""Name of HPO tuner supported by NNI.
    """
)
@click.option(
    "--hpo-mode",
    default="maximize",
    help="""Optimization mode either 'maximize' or 'minimize'.
    """
)
@click.option(
    "--hpo-port",
    default=31889,
    help="""Port to bind HPO process (NNI) and hence its web view.
    """
)
def hpo(
    cluster_address,
    username,
    password,
    foreground,
    algorithm_dir,
    dataset_dir,
    algorithm_entrypoint,
    algorithm_output,
    search_space_file,
    project_name,
    dataset_hyperparam_name,
    gpu_num,
    hpo_max_runs,
    hpo_max_duration,
    hpo_tuner_name,
    hpo_mode,
    hpo_port,
):
    with open(search_space_file) as f:
        hpo_search_space = json.loads(f.read())
    AnylearnConfig.init(
        cluster_address=cluster_address,
        username=username,
        password=password,
    )

    print(
        f"""---
        Algorithm folder: {algorithm_dir}
        Dataset folder: {dataset_dir}
        ---
        Starting HPO...
        """
    )
    # Note that only foreground mode works for now,
    # since NNI's REST server runs in subprocess
    # which would be killed if anylearnctl does not
    # hang in terminal.
    # TODO: make run_hpo work in process
    run_hpo(
        hpo_search_space=hpo_search_space,
        hpo_max_runs=hpo_max_runs,
        hpo_max_duration=hpo_max_duration,
        hpo_tuner_name=hpo_tuner_name,
        hpo_mode=hpo_mode,
        hpo_port=hpo_port,
        algorithm_dir=algorithm_dir,
        algorithm_entrypoint=algorithm_entrypoint,
        algorithm_output=algorithm_output,
        dataset_dir=dataset_dir,
        project_name=project_name,
        dataset_hyperparam_name=dataset_hyperparam_name,
        gpu_num=gpu_num,
        foreground=foreground,
    )


@cli.command()
@click.argument("cluster_address")
# TODO: implement API token auth and replace the basic auth below
@click.argument("username")
@click.argument("password")
@click.argument("project_id")
@click.argument("algorithm_id")
@click.argument("dataset_id")
@click.option(
    "--dataset-hyperparam-name",
    default="dataset",
    help="""Parameter name to pass dataset into algorithm.
    """
)
@click.option(
    "--hyperparam",
    multiple=True,
    help="""Hyperparameters for trial formated '<key>=<value>'. 
    This option could be used multiple times to pass multiple hyperparameters.
    \b\r\n
    Example:
    anylearnctl trial --hyperparam batch_size=64 --hyperparam lr=0.01 [OTHER_OPTIONS]
    """
)
@click.option(
    "--gpu-num",
    default=1,
    help="""Number of GPU claimed for trial.
    """
)
def trial(
    cluster_address,
    username,
    password,
    project_id,
    algorithm_id,
    dataset_id,
    dataset_hyperparam_name,
    hyperparam,
    gpu_num,
):
    AnylearnConfig.init(
        cluster_address=cluster_address,
        username=username,
        password=password,
    )
    print(
        f"""---
        Project ID: {project_id}
        Algorithm ID: {algorithm_id}
        Dataset ID: {dataset_id}
        ---
        Running trial...
        """
    )
    hyperparams = {k: v for k, v in [
        (i.split("=")[0], i.split("=")[1])
        for i in list(hyperparam)
    ]}
    train_task = run_hpo_trial(
        project_id=project_id,
        algorithm_id=algorithm_id,
        dataset_id=dataset_id,
        dataset_hyperparam_name=dataset_hyperparam_name,
        hyperparams=hyperparams,
        gpu_num=gpu_num,
    )
    print("---")
    metric = train_task.get_final_metric()
    print(f"Final metric: {metric}")


MSG_HELP_TRAIN_ALGO_OPTIONS = (
    "At least one of the options "
    "["
    "'--algorithm-id', "
    "'--algorithm-dir', "
    "'--algorithm-archive'"
    "] "
    "should be specified."
)
MSG_HELP_TRAIN_DSET_OPTIONS = (
    "At least one of the options "
    "["
    "'--dataset-id', "
    "'--dataset-dir', "
    "'--dataset-archive'"
    "] "
    "should be specified."
)


@cli.command()
@click.argument("cluster_address")
# TODO: implement API token auth and replace the basic auth below
@click.argument("username")
@click.argument("password")
@click.option(
    "-d", "--detach",
    is_flag=True,
    default=False,
    help="""Launch training and print remote training task ID 
    without waiting training result.
    """
)
@click.option(
    "--algorithm-id",
    default=None,
    help="""Remote algorithm ID.
    \b\r\n
    """ + MSG_HELP_TRAIN_ALGO_OPTIONS,
)
@click.option(
    "--algorithm-dir",
    default=None,
    help="""Local algorithm folder absolute path.
    \b\r\n
    """ + MSG_HELP_TRAIN_ALGO_OPTIONS,
)
@click.option(
    "--algorithm-archive",
    default=None,
    help="""Local algorithm archive absolute path.
    \b\r\n
    """ + MSG_HELP_TRAIN_ALGO_OPTIONS,
)
@click.option(
    "--dataset-id",
    default=None,
    help="""Remote dataset ID.
    \b\r\n
    """ + MSG_HELP_TRAIN_DSET_OPTIONS,
)
@click.option(
    "--dataset-dir",
    default=None,
    help="""Local dataset folder absolute path.
    \b\r\n
    """ + MSG_HELP_TRAIN_DSET_OPTIONS,
)
@click.option(
    "--dataset-archive",
    default=None,
    help="""Local dataset archive absolute path.
    \b\r\n
    """ + MSG_HELP_TRAIN_DSET_OPTIONS,
)
@click.option(
    "--project-id",
    default=None,
    help="""Remote training project ID.
    """
)
@click.option(
    "--algorithm-entrypoint",
    default=None,
    help="""Entrypoint command of algorithm. 
    Required when using local algorithm.
    """
)
@click.option(
    "--algorithm-output",
    default=None,
    help="""Model saving path of algorithm. 
    Required when using local algorithm.
    """
)
@click.option(
    "--dataset-hyperparam-name",
    default="dataset",
    help="""Parameter name to pass dataset into algorithm.
    """
)
@click.option(
    "--hyperparam",
    multiple=True,
    help="""Hyperparameters for training formated '<key>=<value>'. 
    This option could be used multiple times to pass multiple hyperparameters.
    \b\r\n
    Example:
    anylearnctl train --hyperparam batch_size=64 --hyperparam lr=0.01 [OTHER_OPTIONS]
    """
)
@click.option(
    "--gpu-num",
    default=1,
    help="""Number of GPU claimed for training.
    """
)
def train(
    cluster_address,
    username,
    password,
    detach,
    algorithm_id,
    algorithm_dir,
    algorithm_archive,
    dataset_id,
    dataset_dir,
    dataset_archive,
    project_id,
    algorithm_entrypoint,
    algorithm_output,
    dataset_hyperparam_name,
    hyperparam,
    gpu_num,
):
    if not any([algorithm_id, algorithm_dir, algorithm_archive]):
        raise AnyLearnMissingParamException(MSG_HELP_TRAIN_ALGO_OPTIONS)
    if not any([dataset_id, dataset_dir, dataset_archive]):
        raise AnyLearnMissingParamException(MSG_HELP_TRAIN_DSET_OPTIONS)
    AnylearnConfig.init(
        cluster_address=cluster_address,
        username=username,
        password=password,
    )
    hyperparams = {k: v for k, v in [
        (i.split("=")[0], i.split("=")[1])
        for i in list(hyperparam)
    ]}
    train_task, algo, dset, project = quick_train(
        algorithm_id=algorithm_id,
        algorithm_dir=algorithm_dir,
        algorithm_archive=algorithm_archive,
        dataset_id=dataset_id,
        dataset_dir=dataset_dir,
        dataset_archive=dataset_archive,
        project_id=project_id,
        entrypoint=algorithm_entrypoint,
        output=algorithm_output,
        dataset_hyperparam_name=dataset_hyperparam_name,
        hyperparams=hyperparams,
        gpu_num=gpu_num,
    )
    print(
        f"""---
        Project ID: {project.id}
        Training ID: {train_task.id}
        Algorithm ID: {algo.id}
        Dataset ID: {dset.id}
        """
    )
    if detach:
        return
    print(
        """---
        Waiting training result...
        """
    )
    while not train_task.finished():
        time.sleep(20) # TODO: make polling interval dynamic
        train_task.get_detail()
        try:
            metric = train_task.get_intermediate_metric()
            print(f"- Intermediate metric: {metric}")
        except:
            continue
    print("---")
    print(f"Final metric: {train_task.get_final_metric()}")
    print(f"Model export from CLI will soon be supported.")


@cli.command()
def evaluate():
    print("Coming soon.")


@cli.command()
def serve():
    print("Coming soon.")


@cli.command()
def resources():
    print("Coming soon.")


if __name__ == '__main__':
    cli()
