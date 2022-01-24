import argparse
import os

import kfserving

from common.b10server import B10Server
from server.inference_model import CustomBasetenModel


DEFAULT_MODEL_NAME = 'model'
DEFAULT_LOCAL_MODEL_DIR = 'model'
MODEL_CLASS_NAME = os.environ.get('MODEL_CLASS_NAME')
MODEL_CLASS_FILE = os.environ.get('MODEL_CLASS_FILE')

parser = argparse.ArgumentParser(parents=[kfserving.kfserver.parser])
parser.add_argument('--model_dir', default=DEFAULT_LOCAL_MODEL_DIR,
                    help='A URI pointer to the model directory')
parser.add_argument('--model_name', default=DEFAULT_MODEL_NAME,
                    help='The name that the model is served under.')
parser.add_argument('--model_class_name', default=MODEL_CLASS_NAME,
                    help='The class name for the model.')
parser.add_argument('--model_class_file', default=MODEL_CLASS_FILE,
                    help='The file defining the class for the model.')
args, _ = parser.parse_known_args()

if __name__ == '__main__':
    model = CustomBasetenModel(args.model_name, args.model_class_name, args.model_class_file, args.model_dir)
    model.load()
    B10Server(workers=1).start([model])
