import argparse
import distutils.util
import os

import kfserving

from common.b10server import B10Server
from server.inference_model import TransformerModel


HF_TASK = os.environ.get('hf_task')
HAS_HYBRID_ARGS = bool(distutils.util.strtobool(os.environ.get('has_hybrid_args')))
HAS_NAMED_ARGS = bool(distutils.util.strtobool(os.environ.get('has_named_args')))

DEFAULT_MODEL_NAME = 'model'

parser = argparse.ArgumentParser(parents=[kfserving.kfserver.parser])
parser.add_argument('--model_name', default=DEFAULT_MODEL_NAME,
                    help='The name that the model is served under.')
parser.add_argument('--task', default=HF_TASK, type=str)
parser.add_argument('--has_hybrid_args', type=bool, default=HAS_HYBRID_ARGS)
parser.add_argument('--has_named_args', type=bool, default=HAS_NAMED_ARGS)


args, _ = parser.parse_known_args()

if __name__ == '__main__':

    model = TransformerModel(args.model_name, args.task, args.has_named_args, args.has_hybrid_args)
    model.load()
    B10Server(workers=1).start([model])

