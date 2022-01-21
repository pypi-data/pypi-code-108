import os
from pathlib import Path
from typing import Dict, List

import click
from ruamel.yaml import YAML

from anylearn.applications.quickstart import quick_train
from anylearn.cli.anylearn_cli_config import AnylearnCliConfig
from anylearn.cli.utils import (
    check_config,
    check_connection,
    cmd_confirm_or_abort,
    cmd_error,
    cmd_info,
    cmd_success,
    cmd_warning,
    get_cmd_command,
)
from anylearn.interfaces import TrainTask


@click.group("run")
def commands():
    """
    Run training, evaluation or serving on remote Anylearn.
    """
    pass


@commands.command()
@click.argument('algorithm_name')
@click.option(
    '-d', '--data',
    multiple=True,
    help="""
    Dataset(s) KV pair in `<key>=<dataset-name>` format.
    """
)
@click.option(
    '--data-yaml',
    help="""
    Absolute path of datasets KV definition file in YAML format.
    If specified, datasets through `-d|--data` option will be ignored.
    """
)
@click.option(
    '-p', '--param',
    multiple=True,
    help="""
    Hyperparam(s) KV pair in `<key>=<value>` format.
    """
)
@click.option(
    '--param-yaml',
    help="""
    Absolute path of hyperparams KV definition file in YAML format.
    If specified, hyperparams through `-p|--param` option will be ignored.
    """
)
@click.option(
    '-g', '--quota-group',
    default='default',
    help="""
    Specify a certain QuotaGroup to request computing resource within.
    """
)
@click.option(
    '-r', '--resource',
    multiple=True,
    help="""
    Computing resource(s) KV pair in `<key>=<value>` format.
    """
)
@click.option(
    '--resource-yaml',
    help="""
    Absolute path of resource request K-KV definition file in YAML format.
    If specified, resource request through `-g|--quota-group` and `-r|--resource`
    options will be ignored.
    """
)
@click.option(
    '--save',
    is_flag=True,
    default=False,
    help="""
    Whether save the training as reusable configuration file.
    """
)
@check_config()
@check_connection()
@get_cmd_command()
def training(
    algorithm_name: str,
    data: tuple,
    param: tuple,
    resource: tuple,
    data_yaml: str=None,
    param_yaml: str=None,
    resource_yaml: str=None,
    quota_group: str='default',
    save: bool=False,
):
    """
    Run training task.
    Note that algorithm to train is selected by name.
    Therefore, please maintain unique algorithm names in current project's scope.
    """
    config = AnylearnCliConfig.load()
    _check_project(config)
    _check_algorithm_name(config, algorithm_name)
    data_config = _get_data_config(list(data), data_yaml)
    param_config = _get_param_config(list(param), param_yaml)
    resource_config = _get_resource_config(quota_group,
                                           list(resource),
                                           resource_yaml)
    kwargs = {
        'algorithm_name': algorithm_name,
        'data_config': data_config,
        'param_config': param_config,
        'resource_config': resource_config,
    }
    if save:
        path = _dump_training_config(**kwargs)
        cmd_info(msg=f"Training config saved in {path}")
    task = _do_train(config=config, **kwargs)
    cmd_success(msg=f"CREATED {task.id}")


def _check_project(config: AnylearnCliConfig):
    if not config.project or not config.project.id:
        cmd_error(msg=(
            "Local project is broken or has not been published to Anylearn remote.\n"
            "Call `anyctl reset` then `anyctl init` if project configuration is corrupted, "
            f"or call `anyctl push project` to publish local project."
        ))
        raise click.Abort


def _check_algorithm_name(config: AnylearnCliConfig, algorithm_name: str):
    try:
        algo = config.algorithms[algorithm_name]
        _ = config.path['algorithm'][algorithm_name]
    except KeyError:
        cmd_error(msg=(
            f"Algorithm {algorithm_name} does not exist in current project."
        ))
        raise click.Abort
    if not algo.id:
        cmd_error(msg=(
            f"Algorithm {algorithm_name} has not been pushed to Anylearn remote.\n"
            f"Call `anyctl push algorithm {algorithm_name}` first."
        ))
        raise click.Abort


def _check_dataset_name(config: AnylearnCliConfig, dataset_name: str):
    try:
        dset = config.datasets[dataset_name]
        _ = config.path['dataset'][dataset_name]
    except KeyError:
        cmd_error(msg=(
            f"Dataset named {dataset_name} does not exist in current project."
        ))
        raise click.Abort
    if not dset.id:
        cmd_error(msg=(
            f"Dataset {dataset_name} has not been pushed to Anylearn remote.\n"
            f"Call `anyctl push dataset {dataset_name}` first."
        ))
        raise click.Abort


def _get_data_config(data_kv: List[str], data_yaml: str) -> Dict[str, str]:
    if data_yaml:
        yaml = YAML()
        yaml_path = Path(data_yaml)
        if not yaml_path.exists():
            cmd_error(msg=f"No such file: {data_yaml}.")
            raise click.Abort
        return yaml.load(yaml_path)
    elif data_kv and isinstance(data_kv, list):
        return dict(kv.split('=') for kv in data_kv)
    else:
        return {}


def _get_param_config(param_kv: List[str], param_yaml: str) -> Dict[str, str]:
    if param_yaml:
        yaml = YAML()
        yaml_path = Path(param_yaml)
        if not yaml_path.exists():
            cmd_error(msg=f"No such file: {param_yaml}.")
            raise click.Abort
        return yaml.load(yaml_path)
    elif param_kv and isinstance(param_kv, list):
        return dict(kv.split('=') for kv in param_kv)
    else:
        return {}


def _get_resource_config(quota_group: str,
                         resource_kv: List[str],
                         resource_yaml: str) -> Dict[str, str]:
    if resource_yaml:
        yaml = YAML()
        yaml_path = Path(resource_yaml)
        if not yaml_path.exists():
            cmd_error(msg=f"No such file: {resource_yaml}.")
            raise click.Abort
        return yaml.load(yaml_path)
    elif quota_group:
        req = {}
        for kv in resource_kv:
            rk, rv = kv.split('=')
            try:
                req[rk] = int(rv)
            except ValueError:
                cmd_error(msg=(f"Resource quantity is not integer: {kv}."))
                raise click.Abort
        return [{quota_group: req}]
    else:
        return {}


def _do_train(config: AnylearnCliConfig,
              algorithm_name: str,
              data_config: Dict[str, str],
              param_config: Dict[str, str],
              resource_config: Dict[str, str]) -> TrainTask:
    algo = config.algorithms[algorithm_name]
    algo_dir = config.path['algorithm'][algorithm_name]
    datasets = {}
    for k, v in data_config.items():
        _check_dataset_name(config, v)
        dset = config.datasets[v]
        dset_dir = config.path['dataset'][v]
        datasets[k] = {
            'val': f"${dset.id}",
            'dir': dset_dir,
        }
    # Sum up and call `quick_train`
    kwargs = {
        'project_id': config.project.id,
        'algorithm_id': algo.id,
        'algorithm_dir': algo_dir,
        'hyperparams': param_config,
        'resource_request': resource_config,
    }
    if datasets:
        # TODO: support multiple datasets in quick_train
        kwargs['dataset_hyperparam_name'] = list(datasets.keys())[0]
        kwargs['dataset_id'] = list(datasets.values())[0]['val'].replace('$', '')
    task, _, _, _ = quick_train(**kwargs)
    return task


def _dump_training_config(algorithm_name: str,
                          data_config: Dict[str, str],
                          param_config: Dict[str, str],
                          resource_config: Dict[str, str]) -> Path:
    cwd = Path(os.getcwd())
    i = 0
    while (cwd / f"AnylearnTraining.{i}.yaml").exists():
        i += 1
    training_config_path = cwd / f"AnylearnTraining.{i}.yaml"
    training_config_path.touch()
    yaml = YAML()
    yaml.dump(
        {
            'algorithm_name': algorithm_name,
            'data_config': data_config,
            'param_config': param_config,
            'resource_config': resource_config,
        },
        training_config_path,
    )
    return training_config_path


def _load_training_config(training_config_path: str) -> dict:
    training_config_path = Path(training_config_path)
    if not training_config_path.exists():
        cmd_error(msg=f"No such file {training_config_path}.")
        raise click.Abort
    yaml = YAML()
    training_config = dict({
        'algorithm_name': None,
        'data_config': {},
        'param_config': {},
        'resource_config': {},
    }, **yaml.load(training_config_path))
    if not training_config['algorithm_name']:
        cmd_error(msg="Field 'algorithm_name' is required.")
        raise click.Abort
    return training_config


@commands.command()
@get_cmd_command()
def evaluation():
    """
    Coming soon.
    """
    pass


@commands.command()
@get_cmd_command()
def serving():
    """
    Coming soon.
    """
    pass
