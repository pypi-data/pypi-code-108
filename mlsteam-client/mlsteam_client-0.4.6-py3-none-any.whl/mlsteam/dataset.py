import os
import uuid
import click
from .api import MyelindlApi, MyelindlApiError
from .utils import sizeof_fmt


# @click.command()
# @click.option('dataset_type', '--type', type=click.Choice(READERS.keys()), required=True)  # noqa
# @click.option('--data-dir', required=True, help='Where to locate the original data.')  # noqa
# @click.option('--output-dir', required=True, help='Where to save the transformed data.')  # noqa
# @click.option('splits', '--split', required=True,
#               multiple=True, help='The splits to transform (ie. train, test, val).')  # noqa
# @click.option('--debug', is_flag=True, help='Set level logging to DEBUG.')
# def conversion(dataset_type, data_dir,  output_dir, splits, debug):
#     from readers import get_reader, READERS
#     from writers import get_writer
#     import tensorflow as tf
#     tf.logging.set_verbosity(tf.logging.INFO)
#     if debug:
#         tf.logging.set_verbosity(tf.logging.DEBUG)

#     try:
#         reader = get_reader(dataset_type)
#     except ValueError as e:
#         tf.logging.error('Error getting reader: {}'.format(e))
#         return

#     try:
#         writer = get_writer(dataset_type)
#         for split in splits:
#             split_reader = reader(data_dir, split)
#             writer = writer(split_reader, output_dir, split)
#             writer.save()

#             tf.logging.info('Composition per class ({})'.format(split))
#     except ValueError as e:
#         tf.logging.error('Error reading dataset: {}'.format(e))


@click.command()
@click.option('name', '--name', required=True, help='Dataset name')
@click.option('--data-dir', required=True, help="Where to locate the directory contains coverted data.")
@click.option('--id', required=False, help="Specify id to update published dataset.")
@click.option('--type', required=False, help="Specify type of published dataset.(ex: object, file)")
@click.option('--description', required=False, help='Dataset description')
def publish(data_dir, name, _id, _type, description):

    if not os.path.exists(data_dir):
        click.echo('data-dir: {} not exists!'.format(data_dir))

    temp_dir = 'mlt_tmp-{}'.format(str(uuid.uuid1())[:8])
    try:
        api = MyelindlApi()
        # api.data_upload(data_dir, temp_dir)

        dataset_id = _id if _id else ''
        dataset_type = _type if _type else 'file'

        result = api.dataset_publish(
            _id=dataset_id,
            _type=dataset_type,
            name=name,
            description=description,
            data_dir=temp_dir,
        )

        click.echo('Dataset {} published with id {}'.format(name, result['id']))
    except MyelindlApiError as e:
        click.echo('Dataset publish fail, due to {}'.format(str(e)))
        raise


@click.command()
@click.option('id', '--id', required=True, help="Which dataset you want to unpublish")
def unpublish(_id):
    api = MyelindlApi()
    try:
        api.dataset_unpublish(_id)
        click.echo('Dataset {} unpublished'.format(_id))
    except MyelindlApiError as e :
        click.echo('Fail due to {}'.format(str(e)))
        raise


@click.command('list')
def do_list():
    api = MyelindlApi()
    try:
        result = api.dataset_list()
    except MyelindlApiError as e :
        click.echo('Fail due to {}'.format(str(e)))
        raise
    longest = 10
    if result['datasets']:
        longest = max(len(d['name']) for d in result['datasets'])
    if longest < 10:
        longest = 10
    template = '| {:>10} | {:>%d} | {:>30} | {:>10} | {:>10} | {:>10} |'% longest
    header = template.format('id', 'name', 'description','size', 'type', 'user')

    click.echo('=' * len(header))
    click.echo(header)
    click.echo('=' * len(header))

    for ds in result['datasets']:
        line = template.format(
            ds['id'],
            ds['name'],
            ds['description'],
            sizeof_fmt(ds['size']),
            ds['type'],
            ds['username'],
        )
        click.echo(line)
    click.echo('='* len(header))


@click.command()
@click.option('id', '--id', required=True, help="Which dataset you want to read information")
def info(_id):
    api = MyelindlApi()
    try:
        result = api.dataset_info(_id)
    except MyelindlApiError as e :
        click.echo('Fail due to {}'.format(str(e)))
        raise

    template = '| {:>20} | {:>30}|'
    header = template.format('Field', 'Value')

    click.echo('=' * len(header))
    click.echo(header)
    click.echo('=' * len(header))

    for k, v in result.items():
        line = template.format(k, v)
        click.echo(line)
    click.echo('='* len(header))


@click.command()
@click.option('--id',required=True)
@click.option('dir','--dir',required=False)
def browse(_id, _dir):

    api = MyelindlApi()
    try:
        result = api.dataset_items(_id, _dir)
        for file in result:
            if file['type'] == 'dir':
                click.echo('{}/'.format(file['basename']))
            else:
                click.echo(file['basename'])
    except Exception as e:
        click.echo("Fail due to {}".format(str(e)))
        raise
@click.group(help='Groups of commands to manage datasets')
def dataset():
    pass


#dataset.add_command(conversion)
#dataset.add_command(publish)
#dataset.add_command(unpublish)
dataset.add_command(do_list)
#dataset.add_command(browse)
#dataset.add_command(info)
