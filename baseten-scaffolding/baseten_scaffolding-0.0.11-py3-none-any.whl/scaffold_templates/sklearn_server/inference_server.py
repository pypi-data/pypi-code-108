import argparse

import kfserving

from common.b10server import B10Server
from server.inference_model import SKLearnModel

DEFAULT_MODEL_NAME = 'model'

parser = argparse.ArgumentParser(parents=[kfserving.kfserver.parser])
parser.add_argument('--model_dir', required=True,
                    help='A URI pointer to the model binary directory')
parser.add_argument('--model_name', default=DEFAULT_MODEL_NAME,
                    help='The name that the model is served under.')
args, _ = parser.parse_known_args()

if __name__ == '__main__':
    model = SKLearnModel(args.model_name, args.model_dir)
    model.load()
    B10Server(workers=1).start([model])


