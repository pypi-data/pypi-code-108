import json
from pathlib import Path

from las import Client

from lascli.util import NotProvided, nullable


def create_model(
    las_client: Client,
    width,
    height,
    field_config_path,
    preprocess_config_path=None,
    **optional_args,
):
    field_config = json.loads(Path(field_config_path).read_text())
    preprocess_config = json.loads(Path(preprocess_config_path).read_text()) if preprocess_config_path else None
    return las_client.create_model(
        width=width,
        height=height,
        field_config=field_config,
        preprocess_config=preprocess_config,
        **optional_args
    )


def list_models(las_client: Client, max_results, next_token):
    return las_client.list_models(max_results=max_results, next_token=next_token)


def update_model(
    las_client: Client,
    model_id,
    width=None,
    height=None,
    field_config_path=None,
    preprocess_config_path=None,
    start_training=False,
    **optional_args,
):
    field_config = json.loads(Path(field_config_path).read_text()) if field_config_path else None
    preprocess_config = json.loads(Path(preprocess_config_path).read_text()) if preprocess_config_path else None
    status = 'training' if start_training else None

    return las_client.update_model(
        model_id=model_id,
        width=width,
        height=height,
        field_config=field_config,
        preprocess_config=preprocess_config,
        status=status,
        **optional_args,
    )


def create_data_bundle(
    las_client: Client,
    model_id,
    dataset_ids,
    **optional_args,
):
    return las_client.create_data_bundle(
        model_id=model_id,
        dataset_ids=dataset_ids,
        **optional_args,
    )


def list_data_bundles(las_client: Client, model_id, max_results, next_token):
    return las_client.list_data_bundles(model_id, max_results=max_results, next_token=next_token)


def delete_data_bundle(las_client: Client, model_id, data_bundle_id):
    return las_client.delete_data_bundle(model_id, data_bundle_id)


def update_data_bundle(las_client: Client, model_id, data_bundle_id, **optional_args):
    return las_client.update_data_bundle(model_id, data_bundle_id, **optional_args)


def create_training(las_client: Client, model_id, data_bundle_ids, instance_type, **optional_args):
    return las_client.create_training(
        model_id=model_id,
        data_bundle_ids=data_bundle_ids,
        instance_type=instance_type,
        **optional_args,
    )


def list_trainings(las_client: Client, model_id, max_results, next_token):
    return las_client.list_trainings(model_id, max_results=max_results, next_token=next_token)


def create_models_parser(subparsers):
    parser = subparsers.add_parser('models')
    subparsers = parser.add_subparsers()

    create_parser = subparsers.add_parser('create')
    create_parser.add_argument('width', type=int)
    create_parser.add_argument('height', type=int)
    create_parser.add_argument('field_config_path', help='configuration of the fields that the model will predict')
    create_parser.add_argument('--preprocess-config-path', '-p', help='configuration of the step before the prediction')
    create_parser.add_argument('--name')
    create_parser.add_argument('--description')
    create_parser.set_defaults(cmd=create_model)

    update_parser = subparsers.add_parser('update')
    update_parser.add_argument('model_id')
    update_parser.add_argument(
        '--field-config-path',
        '-f',
        help='configuration of the fields that the model will predict',
    )
    update_parser.add_argument('--width', type=int)
    update_parser.add_argument('--height', type=int)
    update_parser.add_argument('--start-training', action='store_true', default=False)
    update_parser.add_argument('--preprocess-config-path', '-p', help='configuration of the step before the prediction')
    update_parser.add_argument('--name', type=nullable, default=NotProvided)
    update_parser.add_argument('--description', type=nullable, default=NotProvided)
    update_parser.set_defaults(cmd=update_model)

    list_parser = subparsers.add_parser('list')
    list_parser.add_argument('--max-results', '-m', type=int, default=None)
    list_parser.add_argument('--next-token', '-n', type=str, default=None)
    list_parser.set_defaults(cmd=list_models)

    create_data_bundle_parser = subparsers.add_parser('create-data-bundle')
    create_data_bundle_parser.add_argument('model_id')
    create_data_bundle_parser.add_argument('dataset_ids', nargs='+')
    create_data_bundle_parser.add_argument('--name')
    create_data_bundle_parser.add_argument('--description')
    create_data_bundle_parser.set_defaults(cmd=create_data_bundle)

    list_data_bundles_parser = subparsers.add_parser('list-data-bundles')
    list_data_bundles_parser.add_argument('model_id')
    list_data_bundles_parser.add_argument('--max-results', '-m', type=int, default=None)
    list_data_bundles_parser.add_argument('--next-token', '-n', type=str, default=None)
    list_data_bundles_parser.set_defaults(cmd=list_data_bundles)

    update_data_bundles_parser = subparsers.add_parser('update-data-bundle')
    update_data_bundles_parser.add_argument('model_id')
    update_data_bundles_parser.add_argument('data_bundle_id')
    update_data_bundles_parser.add_argument('--name', type=nullable, default=NotProvided)
    update_data_bundles_parser.add_argument('--description', type=nullable, default=NotProvided)
    update_data_bundles_parser.set_defaults(cmd=update_data_bundle)

    delete_data_bundles_parser = subparsers.add_parser('delete-data-bundle')
    delete_data_bundles_parser.add_argument('model_id')
    delete_data_bundles_parser.add_argument('data_bundle_id')
    delete_data_bundles_parser.set_defaults(cmd=delete_data_bundle)

    create_training_parser = subparsers.add_parser('create-training')
    create_training_parser.add_argument('model_id')
    create_training_parser.add_argument('data_bundle_ids', nargs='+')
    create_training_parser.add_argument('--instance-type')
    create_training_parser.add_argument('--name')
    create_training_parser.add_argument('--description')
    create_training_parser.set_defaults(cmd=create_training)

    list_trainings_parser = subparsers.add_parser('list-trainings')
    list_trainings_parser.add_argument('model_id')
    list_trainings_parser.add_argument('--max-results', '-m', type=int, default=None)
    list_trainings_parser.add_argument('--next-token', '-n', type=str, default=None)
    list_trainings_parser.set_defaults(cmd=list_trainings)

    return parser
