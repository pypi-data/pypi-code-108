import os 
import click
import pkg_resources

from cookiecutter.main import cookiecutter
from functools import reduce

import yaml
from phobos import __version__ as version

from phobos.cli.utils import datalab, get_all_tasks_eu, get_task_details_eu, export_annotations_eu, DataLab
from phobos.cli.middleware import Middleware

def checkValidRoot():
    root_path = os.curdir
    required_files = ['train.py', 'metadata.yaml', '.phobos_run']
    return reduce(
        lambda x, y: x and y,
        [os.path.exists(
            os.path.join(root_path, fl)
            ) for fl in required_files])

def getProject():
    with open('.phobos_run/run.yaml', 'r') as fp:
        run_config = yaml.safe_load(fp)
    project = {}
    project['name'] = run_config['project_name']
    project['description'] = run_config['description']
    if len(run_config['tags']) > 1 or run_config['tags'][0] != '':
        project['tags'] = run_config['tags']
    print(project)
    return project, run_config
    
@click.group()
@click.version_option(version, message='%(version)s')
def cli():
    pass


middleware = Middleware()

@click.command()
@click.option('--project_name', required=True, help='Project directory name, Project Id for Polyaxon/Datalab')
@click.option(
    '--description',
    required=False,
    default="",
    help='Short description about the project')
@click.option(
    '--tags',
    required=False,
    type=str,
    default="",
    help='tags related to the project')
@click.option(
    '--node_pool',
    required=False,
    default="v100-pool",
    help='Cluster Name')
@click.option(
    '--image',
    required=False,
    default="gcr.io/granular-ai/phobos:latest",
    help='docker image')
@click.option(
    '--num_gpus',
    required=False,
    default=1,
    type=int,
    help='per node GPU requirement')
@click.option(
    '--num_worker_replicas',
    required=False,
    default=1,
    type=int,
    help="No. of worker replicas for distributed training config")
def init(project_name,
        description,
        tags, 
        node_pool,
        image,
        num_gpus,
        num_worker_replicas):
    '''
    phobos init

    Initializes template repository with provided project attributes

    Params:
    --- project specific ---
    project_name:           Project directory name, Polyaxon project ID.
    description:            (Optional) Description string.
    tags:                   (Optional) Project tags eg, phobos-stabalize.
    --- polyaxon defaults for template ---
    node_pool:              (Optional) Target node-pool for exp.
    image:                  (Optional) Target docker image for exp.
    num_gpus:               (Optional) No. of GPUs required at pod-level.
    num_worker_replicas:    (Optional) No. of worker pods for distributed training mode.
    '''
    if not os.path.exists(project_name):
        click.echo("Creating template project directory!")
        cookiecutter(
            pkg_resources.resource_filename("phobos", "cli/cookiecutter-phobos-project"), 
            extra_context={
                'project_name': project_name,
                'node_pool': node_pool,
                'num_gpus': num_gpus,
                'image': image,
                'distributed': {
                    'num_worker_replicas': num_worker_replicas
                }
            },
            no_input=True)
        with open(os.path.join(os.path.curdir, project_name)+'/.phobos_run/run.yaml', 'r') as fp:
            run_config = yaml.safe_load(fp)
        run_config['project_name'] = project_name
        run_config['description'] = description
        run_config['tags'] = tags.split(',')
        with open(os.path.join(os.path.curdir, project_name)+'/.phobos_run/run.yaml', 'w') as fp:
            yaml.dump(run_config, fp)
        middleware.exec(f"cd {project_name}")
    else:
        click.echo(f"{project_name} already exist locally.")


@click.command()
@click.option('--context', required=False, default="", help="datalab/local")
@click.option(
    '--distributed',
    required=False,
    type=int,
    default=-1,
    help='For running distributed training. "0" for non-distributed, "1" for distributed')
@click.option('--logging', is_flag=True, help="Run with terminal logs")
@click.option('--stop_forward', is_flag=True, help="stop port forwarding")
@click.option('--dry_run', is_flag=True, help="Use dryrun i.e. non-polyaxon local run on non-distributed mode")
@click.option('--tags', required=False, type=str, default="", help='Run tags')
@click.option('--description', required=False, type=str, default="", help='Run tags')
def run(context, distributed, logging, stop_forward, dry_run, tags, description):
    '''
    phobos run

    Runs a polyaxon experiment, If any of the mentioned args is not provided then default ars are used.

    Params:
    ------
    context:         (Optional) Target context "datalab/local".
    distributed:     (Optional) Target distributed mode 0(single)/1(distributed).
    logging:         (Optional) To enable logging feature for experiment.
    stop_forward:    (Optional) Stop port forwarding.
    dry_run:         (Optional) Use dryrun i.e. non-polyaxon local run on non-distributed mode.
    '''
    if not checkValidRoot():
        click.echo("To run this command. Make sure you are inside project directory.")
        return
    if dry_run:
        middleware.exec("POLYAXON_NO_OP=true python3 train.py", pipe=False)
        return

    project, run_config = getProject()

    if len(context) == 0 or ((not context == "datalab") and (not context == "local")):
        context = run_config['context']
    if distributed == -1 or ((not distributed == 0) and (not distributed == 1)):
        distributed = int(run_config['distributed'])
    mode = "distributed" if distributed == 1 else "single"
    if stop_forward:
        if context == "local":
            middleware.close_port(context)
            return
        else:
            raise Exception("Invalid context provided!")

    click.echo("Run the project. Make sure you are inside project directory.")
    config_file = f".phobos_run/polyaxonfile_{context}_{mode}.yaml"
    print(f"Running: {config_file}")

    if context == "datalab":
        datalabClient = DataLab()

        datalabClient.createRun(
            project = project,
            polyaxon_file = config_file,
            tags = tags.split(','),
            description = description
        )
    else:
        middleware.polyaxon_forward(mode=context)
        middleware.exec(
            f"polyaxon run -u-to code -f {config_file} {'-l' if logging else ''}",
            in_='N',
            pipe=False)


@click.command()
@click.option(
    '--uuid',
    required=True,
    help='"uuid" for single uuid or "uuid-1,..,uuid-n" for multiple uuids')
def tensorboard(uuid):
    '''
    phobos tensorboard

    Runs tensorboard for a given uuid/project

    Params:
    ------
    uuid:           Experiment uuid/uuid1,..,uuidn
    '''
    if not checkValidRoot():
        click.echo("To run this command the project. Make sure you are inside project directory.")
        return
    
    project, run_config = getProject()

    uuids = uuid.split(',')
    
    datalabClient = DataLab()

    datalabClient.run_tensorboard(project, uuid=uuids)


def yaml_set_args(path, config_, context="datalab", distributed=False):
    '''
    Helper function for 'phobos config'

    Updates polyaxonfile specified by 'path' using provided 'config_'

    Params:
    ------
    path:               Path to polyaxon file
    config_:            Config dict
    context:            target experiment context "datalab/local"
    distributed:        distributed training mode 0(single pod)/1(distributed training)
    '''
    if not os.path.exists(path):
        print("First navigate to Project directory")
        return
    node_pool = config_['node_pool']
    image = config_['image']
    num_gpus = config_['num_gpus']
    num_worker_replicas = config_['num_worker_replicas']

    file_ = path.split('/')[-1]
    print(context)
    print(f"Updating file: {file_}")

    with open(path, 'r') as fp:
        data = yaml.safe_load(fp)
        if not distributed:
            if context == "datalab" and len(node_pool) > 0:
                data['run']['environment']['nodeSelector']['polyaxon'] = node_pool
            if len(image) > 0:
                data['run']['container']['image'] = image
            if num_gpus != -1 and num_gpus >= 1:
                data['run']['container']['resources']['requests']['nvidia.com/gpu'] = num_gpus
                data['run']['container']['resources']['limits']['nvidia.com/gpu'] = num_gpus
        else:
            if context == "datalab" and len(node_pool) > 0:
                data['run']['master']['environment']['nodeSelector']['polyaxon'] = node_pool
                data['run']['worker']['environment']['nodeSelector']['polyaxon'] = node_pool
            if len(image) > 0:
                data['run']['master']['container']['image'] = image
                data['run']['worker']['container']['image'] = image
            if num_gpus != -1 and num_gpus >= 1:
                data['run']['master']['container']['resources']['requests']['nvidia.com/gpu'] = num_gpus
                data['run']['master']['container']['resources']['limits']['nvidia.com/gpu'] = num_gpus
                data['run']['worker']['container']['resources']['requests']['nvidia.com/gpu'] = num_gpus
                data['run']['worker']['container']['resources']['limits']['nvidia.com/gpu'] = num_gpus
            if num_worker_replicas != -1 and num_worker_replicas >= 1:
                data['run']['worker']['replicas'] = num_worker_replicas
    with open(path, 'w') as fp:
        yaml.dump(data, fp)
        print("Updated !")


@click.command()
@click.option('--set', is_flag=True, help='To set args')
@click.option(
    '--run',
    is_flag=True,
    help="Set default run context, distributed with --set")
@click.option(
    '--project_name',
    required=False,
    default="",
    help="Modify project_name with --set and --run")
@click.option(
    '--context',
    required=False,
    default="",
    help='datalab/local. with --run & --set modifies defaut run.yaml, \
        with only --set modifies polyaxon*.yaml config')
@click.option(
    '--distributed',
    required=False,
    default=-1,
    type=int,
    help='For running distributed training. \
         "0" for non-distributed, "1" for distributed. \
              with --run & --set modifies defaut run.yaml, \
                  with only --set modifies polyaxon*.yaml config')
@click.option('--node_pool', default="", help='Cluster Name. requires --set')
@click.option(
    '--image',
    required=False,
    default="",
    help='docker image. requires --set')
@click.option(
    '--num_gpus',
    required=False,
    default=-1,
    type=int,
    help='Per node GPU requirement. requires --set')
@click.option(
    '--num_worker_replicas',
    required=False,
    default=-1,
    type=int,
    help="No. of worker replicas for distributed training config. \
        requires --set")
def config(set, run, project_name, context, distributed, node_pool, image,
        num_gpus, num_worker_replicas):
    '''
    phobos config

    Updated experiment config polyaxon's yaml/ phobos run defaults

    Params:
    ------
    set:                    To set args 
    run:                    Set default run context, distributed with --set
    project_name:           Modify Polyaxon project_name with --set and --run 
    context:                (Optional) Project tags eg, phobos-stabalize
    distributed:            datalab/local. with --run & --set modifies defaut run.yaml, \
        with only --set modifies polyaxon*.yaml config
    node_pool:              Cluster Name. requires --set.
    image:                  docker image. requires --set.
    num_gpus:               Per node GPU requirement. requires --set
    num_worker_replicas:    No. of worker replicas for distributed training config. \
        requires --set
    '''
    if not checkValidRoot():
        click.echo("Run the project. Make sure you are inside project directory.")
        return
    if not set and not run:
        print("To view the configs kindly check \
            .phobos_run/polyaxon_(context)_(training_mode).yaml")
    elif set and not run:
        config_ =  {
            'context': context,
            'distributed': distributed,
            'node_pool': node_pool,
            'image': image,
            'num_gpus': num_gpus,
            'num_worker_replicas': num_worker_replicas
        }
        context_filter, distributed_filter = False, False
        if len(context) == 0:
            context_filter = True
        if distributed == -1:
            distributed_filter = True
        
        if len(context) > 0 and not ( context == "datalab" or context =="local"):
            print("Please enter a valid value for context use --help to know more")
            return
        if distributed != -1 and not (distributed == 0 or distributed == 1):
            print("Please enter a valid value for distributed.")
            return
        contexts, modes = [], []
        if context_filter:
            contexts += ["local", "datalab"]
        else:
            contexts += [context]
        if distributed_filter:
            modes += ["single", "distributed"]
        else:
            modes += ["distributed" if distributed==1 else "single"]
        for con_ in contexts:
            for mo_ in modes:
                yaml_set_args(
                    f".phobos_run/polyaxonfile_{con_}_{mo_}.yaml",
                    config_,
                    con_,
                    distributed=mo_=="distributed")
    elif set and run:
        with open('.phobos_run/run.yaml', 'r') as fp:
            run_config = yaml.safe_load(fp)
        if len(project_name) == 0:
            project_name = run_config['project_name']
        if len(context) == 0 or ((not context == "datalab") and (not context == "local")):
            context = run_config['context']
        if distributed == -1 or ((not distributed == 0) and (not distributed == 1)):
            distributed = int(run_config['distributed'])
        run_config['project_name'] = project_name
        run_config['context'] = context
        run_config['distributed'] = True if distributed==1 else False
        with open('.phobos_run/run.yaml', 'w') as fp:
            yaml.dump(run_config, fp)
    elif (not set) and run:
        with open('.phobos_run/run.yaml', 'r') as fp:
            run_config = yaml.safe_load(fp)
        print(run_config)

            
@click.command()
@click.option('--all', is_flag=True, help='To retrieve all tasks')
@click.option('--details', is_flag=True, help='To retrieve details of a particular task')
@click.option('--email', required=True, default="", help="email id for Europa access")
@click.option('--passwd', required=True, default="", help="password for Europa access")
@click.option('--task', required=False, default="", help="task id")
def get(all, details, email, passwd, task):
    '''
    phobos get

    Accesses Europa APIs to list tasks, task details and retrieve annotations

    Params:
    -------
    all     :   to retrieve all tasks (optional)
    details :   to retrieve details of a particular task (optional)   
    email   :   email id for Europa access
    passwd  :   password for Europa access
    task    :   task id (optional)
    '''
    if email == "" or passwd == "":
        print('please provide credentials through options \'email\' and \'passwd\'')
        return
    if all:
        get_all_tasks_eu(email=email, passwd=passwd)
        return
    if task == "":
        print('please provide task id')
        return
    else:
        if details:
            get_task_details_eu(id=task, email=email, passwd=passwd)
            return
        else:
            export_annotations_eu(id=task, email=email, passwd=passwd)
            

cli.add_command(init)
cli.add_command(run)
cli.add_command(get)
cli.add_command(config)
cli.add_command(tensorboard)


if __name__ == "__main__":
    cli()
