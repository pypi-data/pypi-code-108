import os
import inspect
import spacy


def load_model(model_name):
    current_directory = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    model = spacy.load(f"{current_directory}/{model_name}")
    return model
