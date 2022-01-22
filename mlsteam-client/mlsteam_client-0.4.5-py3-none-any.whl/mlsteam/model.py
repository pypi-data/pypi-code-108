import os
import uuid
import logging
import click
from .api import MyelindlApi, MyelindlApiError
from .utils import sizeof_fmt

@click.command('list')
@click.option('--offset', required=False, default=0, help='*optional start offset in model list')
@click.option('--limit', required=False, default=None, help='*optional start offset in model list')
def do_list(offset, limit):
    results = []
    try:
        api = MyelindlApi()
        results = api.model_list(
            offset=offset,
            limit=limit
        )
    except MyelindlApiError as e:
        click.echo('Fail due to {}'.format(str(e)))
        raise

    template = '| {:>30}|'
    header = template.format('model')

    click.echo('=' * len(header))
    click.echo(header)
    click.echo('=' * len(header))

    for ds in results:
        line = template.format(
            ds,
        )
        click.echo(line)
    click.echo('='* len(header))

@click.command()
@click.option('tag','--tag', required=True, help='model name (ex. user/model_name)')
@click.option('--offset', required=False, default=0, help='*optional start offset in model list')
@click.option('--limit', required=False, default=None, help='*optional start offset in model list')
def versions(tag, offset, limit):
    results = []
    try:
        api = MyelindlApi()
        results = api.model_versions(
            tag,
            offset=offset,
            limit=limit,
        )
    except MyelindlApiError as e:
        click.echo('Fail due to {}'.format(str(e)))
        raise

    longest = max(len(d['tag']) for d in results)
    if longest < 10:
        longest = 10
    template = '| {:>%d} | {:>20} | {:>10} | {:>10} | {:>10} | {:>10} |'% longest
    header = template.format('tag', 'name', 'version', 'size', 'type', 'user')


    click.echo('=' * len(header))
    click.echo(header)
    click.echo('=' * len(header))

    for ds in results:
        line = template.format(
            ds['tag'],
            ds['name'],
            ds['version'],
            sizeof_fmt(ds['size']),
            ds['type'],
            ds['username'],
        )
        click.echo(line)
    click.echo('='* len(header))



@click.command()
@click.option('tag','--tag', required=True, help='model tag (ex. user/model_name:tag)')
@click.option('--output_dir', required=False, default='', help='Speicify output directory  to pulled file')
def pull(tag, output_dir):
    try:
        api = MyelindlApi()
        api.model_pull(
            tag,
            output_dir
        )
        click.echo('Finish model pull {}' .format(tag))
    except MyelindlApiError as e:
        click.echo('Fail due to {}'.format(str(e)))
        raise



@click.command()
@click.option('tag','--tag', required=True, help='model tag (ex. user/model_name:tag)')
@click.option('--model-dir', required=True, help='target model directory')
@click.option('--description', required=False, default='', help='model description')
@click.option('--type', required=False, default='file', help='model type')
def push(tag, model_dir, description, _type):
    if not os.path.exists(model_dir):
        click.echo('model-dir: {} not exists!'.format(model_dir))

    temp_dir = 'mlt_tmp-{}'.format(str(uuid.uuid1())[:8])
    try:
        api = MyelindlApi()
        # api.data_upload(model_dir, temp_dir)
        result = api.model_push(
            tag,
            temp_dir,
            description,
            _type,
        )
        click.echo( 'Model {} pushed, {}'.format(tag, result))
    except MyelindlApiError as e:
        logging.warning("{}".format(e))
        click.echo( 'Dataset publish fail, due to {}'.format(str(e)))
        raise


@click.command()
@click.option('tag','--tag', required=True, help='model tag (ex. user/model_name:tag)')
def delete(tag):
    try:
        api = MyelindlApi()
        api.model_delete(tag)
        click.echo('Model deleted {}'.format(tag))
    except MyelindlApiError as e:
        click.echo('Fail due to {}'.format(str(e)))
        raise



@click.command()
@click.option('tag','--tag', required=True, help='model tag (ex. user/model_name:tag)')
def info(tag):
    result = {}
    try:
        api = MyelindlApi()
        result = api.model_info(tag)
    except MyelindlApiError as e:
        click.echo('Fail due to {}'.format(str(e)))
        raise

    longest = max(len(str(v)) for v in list(result.values()))
    longest = longest if longest >= 10 else 10
    template = '| {:>16} | {:>%d} |'% longest
    header = template.format('key', 'value')

    click.echo('=' * len(header))
    click.echo(header)
    click.echo('=' * len(header))

    for k,v in result.items():
        line = template.format(k, v)
        click.echo(line)
    click.echo('='* len(header))


@click.group()
def model():
    pass


model.add_command(do_list)
model.add_command(versions)
model.add_command(info)
model.add_command(push)
model.add_command(pull)
model.add_command(delete)
