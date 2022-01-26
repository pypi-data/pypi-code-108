import json
import textwrap
from argparse import RawTextHelpFormatter

from las import Client


def post_predictions(
    las_client: Client,
    document_id,
    model_id,
    auto_rotate,
    max_pages,
    image_quality,
    postprocess_config,
):
    return las_client.create_prediction(
        document_id,
        model_id,
        auto_rotate=auto_rotate,
        max_pages=max_pages,
        image_quality=image_quality,
        postprocess_config=postprocess_config,
    )


def list_predictions(las_client: Client, max_results=None, next_token=None):
    return las_client.list_predictions(max_results=max_results, next_token=next_token)


def create_predictions_parser(subparsers):
    parser = subparsers.add_parser('predictions')
    subparsers = parser.add_subparsers()

    create_predicton_parser = subparsers.add_parser('create', formatter_class=RawTextHelpFormatter)
    create_predicton_parser.add_argument('document_id')
    create_predicton_parser.add_argument('model_id')
    create_predicton_parser.add_argument('--auto-rotate', action='store_true', default=False)
    create_predicton_parser.add_argument('--max-pages', type=int, default=1)
    create_predicton_parser.add_argument('--image-quality', type=str, default='LOW', choices={'LOW', 'HIGH'})
    create_predicton_parser.add_argument('--postprocess-config', type=json.loads, help=textwrap.dedent('''
        Post processing configuration for predictions
        {
            "strategy": "BEST_FIRST" | "BEST_N_PAGES",  (required)
            "parameters": {                             (required if strategy=BEST_N_PAGES, omit otherwise)
                "n": int,                               (required if strategy=BEST_N_PAGES, omit otherwise)
                "collapse": true | false (default)      (optional if strategy=BEST_N_PAGES, omit otherwise)
            }
        }
        Examples:
        {"strategy": "BEST_FIRST"}
        {"strategy": "BEST_N_PAGES", "parameters": {"n": 3}}
        {"strategy": "BEST_N_PAGES", "parameters": {"n": 3, "collapse": true}}
    '''))
    create_predicton_parser.set_defaults(cmd=post_predictions)

    list_predictions_parser = subparsers.add_parser('list')
    list_predictions_parser.add_argument('--max-results', '-m', type=int, default=None)
    list_predictions_parser.add_argument('--next-token', '-n', default=None)
    list_predictions_parser.set_defaults(cmd=list_predictions)

    return parser
