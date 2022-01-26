import base64
import json
import logging
import pathlib

import filetype

from las import Client


def _create_ground_truth_dict(ground_truth_fields, ground_truth_path):
    ground_truth = None

    if ground_truth_fields:
        ground_truth = [f.split('=', 1) for f in ground_truth_fields]
        ground_truth = [{'label': k, 'value': v} for k, v in ground_truth]

    if ground_truth_path:
        ground_truth = json.loads(pathlib.Path(ground_truth_path).read_text())

        if isinstance(ground_truth, dict):
            ground_truth = [{'label': k, 'value': v} for k, v in ground_truth.items()]

    return ground_truth


def get_document(las_client: Client, document_id, download_content, output_content):
    document_resp = las_client.get_document(document_id)
    content = document_resp['content']

    if download_content:
        logging.info(f'Downloading content to {download_content}')
        binary = base64.b64decode(content)
        pathlib.Path(download_content).write_bytes(binary)

    if output_content:
        return document_resp
    else:
        return {**document_resp, 'content': document_resp['content'][:10] + '... [TRUNCATED]'}


def list_documents(las_client: Client, consent_id, dataset_id, max_results, next_token):
    return las_client.list_documents(
        consent_id=consent_id,
        dataset_id=dataset_id,
        max_results=max_results,
        next_token=next_token,
    )


def delete_documents(las_client: Client, consent_id, dataset_id, next_token, max_results):
    return las_client.delete_documents(
        consent_id=consent_id,
        dataset_id=dataset_id,
        next_token=next_token,
        max_results=max_results,
        delete_all=False if max_results else True,
    )


def delete_document(las_client: Client, document_id):
    return las_client.delete_document(document_id)


def create_document(
    las_client: Client,
    document_path,
    content_type,
    consent_id,
    dataset_id,
    ground_truth_fields,
    ground_truth_path,
):
    content = pathlib.Path(document_path).read_bytes()

    if not content_type:
        guessed_type = filetype.guess(content)
        assert guessed_type, 'Could not determine content type of document. ' \
                             'Please provide it manually with --content-type'
        content_type = guessed_type.mime

    ground_truth = _create_ground_truth_dict(ground_truth_fields, ground_truth_path)
    return las_client.create_document(
        content,
        content_type,
        consent_id=consent_id,
        dataset_id=dataset_id,
        ground_truth=ground_truth,
    )


def update_document(las_client: Client, document_id, dataset_id, ground_truth_fields, ground_truth_path):
    ground_truth = _create_ground_truth_dict(ground_truth_fields, ground_truth_path)
    return las_client.update_document(document_id, dataset_id=dataset_id, ground_truth=ground_truth)


def create_documents_parser(subparsers):
    parser = subparsers.add_parser('documents')
    subparsers = parser.add_subparsers()

    get_document_parser = subparsers.add_parser('get')
    get_document_parser.add_argument('document_id')
    get_document_parser.add_argument('--output-content', action='store_true')
    get_document_parser.add_argument('-d', '--download-content')
    get_document_parser.set_defaults(cmd=get_document)

    list_documents_parser = subparsers.add_parser('list')
    list_documents_parser.add_argument('--consent-id', nargs='+')
    list_documents_parser.add_argument('--dataset-id', nargs='+')
    list_documents_parser.add_argument('--max-results', '-m', type=int)
    list_documents_parser.add_argument('--next-token', '-n', type=str)
    list_documents_parser.set_defaults(cmd=list_documents)

    create_document_parser = subparsers.add_parser('create')
    create_document_parser.add_argument('document_path')
    create_document_parser.add_argument('--content-type')
    create_document_parser.add_argument('--consent-id')
    create_document_parser.add_argument('--dataset-id')
    create_document_ground_truth_group = create_document_parser.add_mutually_exclusive_group(required=False)
    create_document_ground_truth_group.add_argument('--ground-truth-fields', metavar='KEY=VALUE', nargs='+')
    create_document_ground_truth_group.add_argument('--ground-truth-path', type=str, help='Path to JSON file')
    create_document_parser.set_defaults(cmd=create_document)

    update_document_parser = subparsers.add_parser('update')
    update_document_parser.add_argument('document_id')
    update_document_parser.add_argument('--dataset-id')
    update_document_ground_truth_group = update_document_parser.add_mutually_exclusive_group(required=False)
    update_document_ground_truth_group.add_argument('--ground-truth-fields', metavar='KEY=VALUE', nargs='+')
    update_document_ground_truth_group.add_argument('--ground-truth-path', type=str, help='Path to JSON file')
    update_document_parser.set_defaults(cmd=update_document)

    delete_document_parser = subparsers.add_parser('delete')
    delete_document_parser.add_argument('document_id')
    delete_document_parser.set_defaults(cmd=delete_document)

    delete_documents_parser = subparsers.add_parser('delete-all')
    delete_documents_parser.add_argument('--consent-id', nargs='+')
    delete_documents_parser.add_argument('--dataset-id', nargs='+')
    delete_documents_parser.add_argument('--max-results', '-m', type=int)
    delete_documents_parser.add_argument('--next-token', '-n', type=str)
    delete_documents_parser.set_defaults(cmd=delete_documents)

    return parser
