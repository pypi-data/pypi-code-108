import os
import json
import subprocess
from datetime import datetime
import click
from mlsteam.api import MyelindlApi, MyelindlApiError


@click.command()
@click.option('--job-name', required=True, help='job name')
@click.option('--package-path', help='package path (for package jobs)')
@click.option('--image-tag', help='docker images name (for container jobs)')
@click.option('--parameters', help='job hyperparameters for parallel run or hpo')
@click.option('--num-gpu', type=click.INT, default=1, help='number of GPU (default: 1)')
@click.argument('user-args', nargs=-1, type=click.Path())
def training(job_name, package_path, image_tag, parameters, num_gpu, user_args):
    job_id = None
    project = os.getenv('PROJECT', None)
    if project is None:
        click.echo("environment variable PROJECT not defined!, use export PROJECT=<project name> before training.")
        return
    if package_path:
        package_path = os.path.expanduser(package_path)
        if not os.path.exists(package_path):
            if not (package_path.startswith("ssh") or package_path.startswith("http")):
                click.echo('--package-path: {} not exists!'.format(package_path))
                return
    if parameters:
        if not os.path.exists(parameters):
            click.echo('parameter file: {} not exists'.format(parameters))
        with open(parameters, encoding='utf-8') as pfile:
            parameters = pfile.read()
    try:
        api = MyelindlApi()
        args = [a for a in user_args]
        result = api.job_create(
            project=project,
            image_tag=image_tag,
            job_name=job_name,
            pkg_path=package_path,
            parameters=parameters,
            num_gpu=num_gpu,
            user_args=' '.join(args),
        )
        job_id = result['id']
        if package_path:
            if (package_path.startswith("ssh://") or
                package_path.startswith("http")):
                pass
            else:
                bk_path = os.path.join("bk", job_id)
                subprocess.call("mc cp --recursive {} {}".format(package_path, bk_path), shell=True)
        click.echo('Job id: {}'.format(job_id))
        result = api.job_train(job_id)
        click.echo('Job {}: {}'.format(job_name, result))
    except MyelindlApiError as e:
        if job_id:
            api.job_delete(job_id)
        click.echo("submit failed, %s"% str(e))
        raise


@click.command('list')
@click.option('--json', 'is_json', default=False, help="return json format output")
def do_list(is_json):
    try:
        api = MyelindlApi()
        result = api.job_list()
        longest = 10
        if result['jobs']:
            longest = max(len(j['name']) for j in result['jobs'])
        if longest < 10:
            longest = 10
        if is_json:
            click.echo(json.dumps(result, indent=2, sort_keys=True)+'\n')
            return
        template = '| {:>16} | {:>%d} | {:>10} | {:>8} | {:>21} | {:>10} |'% longest
        header = template.format('id', 'name', 'project', 'status', 'create time', 'user')
        click.echo('=' * len(header))
        click.echo(header)
        click.echo('=' * len(header))
        for inst in result['jobs']:
            line = template.format(inst['id'],
                                   inst['name'],
                                   inst['project'],
                                   inst['status_history'][-1][0],
                                   datetime.fromtimestamp(inst['status_history'][0][1]).strftime("%Y %b %d, %H:%M:%S"),
                                   inst['username'])
            click.echo(line)
        click.echo('=' * len(header))
    except Exception as e:
        click.echo("submit failed, {}".format(e))
        raise


@click.command()
@click.option('--job-id', required=True, help='job id')
def log(job_id):
    try:
        api = MyelindlApi()
        click.echo(api.job_log(job_id))
    except MyelindlApiError as e:
        click.echo("failed, {}".format(e))
        raise


@click.command()
@click.option('--job-id', required=True, help='job id')
def delete(job_id):
    try:
        api = MyelindlApi()
        result = api.job_delete(job_id)
        click.echo('Job {} deleted, {}'.format(job_id, result))
    except Exception as e:
        click.echo("failed, {}".format(e))
        raise


@click.command()
@click.option('--job-id', required=True, help='job id')
def abort(job_id):
    try:
        api = MyelindlApi()
        api.job_abort(job_id)
        click.echo('Job {} aborted '.format(job_id))
    except Exception as e:
        click.echo("failed, {}".format(e))
        raise


@click.command()
@click.option('--job-id', required=True, help='job id')
def download(job_id):
    try:
        api = MyelindlApi()
        api.job_download(job_id)
    except Exception as e:
        click.echo("failed, {}".format(e))
        raise


@click.group(help='Groups of commands to manage submit')
def submit():
    pass


submit.add_command(training)


@click.group(help='Groups of commands to manage job')
def job():
    pass


job.add_command(submit)
job.add_command(do_list)
job.add_command(log)
job.add_command(delete)
job.add_command(abort)
job.add_command(download)
