import os
import pathlib

SKLEARN = 'sklearn'
TENSORFLOW = 'tensorflow'
KERAS = 'keras'
PYTORCH = 'pytorch'
CUSTOM = 'custom'
HUGGINGFACE_TRANSFORMER = 'huggingface_transformer'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE_DIR = pathlib.Path(BASE_DIR, 'baseten_scaffolding')
SERVING_DIR = pathlib.Path(CODE_DIR, 'scaffold_templates')
