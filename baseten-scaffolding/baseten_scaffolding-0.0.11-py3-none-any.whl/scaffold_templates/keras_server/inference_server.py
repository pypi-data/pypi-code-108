import argparse

import kfserving
from server.inference_model import KerasModel

from common.b10server import B10Server


DEFAULT_MODEL_NAME = 'model'
DEFAULT_MODEL_DIR = 'model'

parser = argparse.ArgumentParser(parents=[kfserving.kfserver.parser])
parser.add_argument('--model_dir',  default=DEFAULT_MODEL_DIR,
                    help='A URI pointer to the model binary directory')
parser.add_argument('--model_name', default=DEFAULT_MODEL_NAME,
                    help='The name that the model is served under.')
args, _ = parser.parse_known_args()

if __name__ == '__main__':
    model = KerasModel(args.model_name, args.model_dir)
    model.load()
    B10Server(workers=1).start([model])
