import pickle
import os


def save_model(best_model, model_path="model/best_model.pkl"):
    """ Save model

    Args:
        best_model (object, optional): Best model object, default to None
            If None, best model will provide automaticly from previouse step

        model_path (str, optional): Path to file model name, default to `model/best_model.pkl`

    """
    parse = model_path.split("/")
    fname = parse[-1]
    dir = "/".join(parse[:-1])
    os.makedirs(dir, exist_ok=True)
    pickle.dump(best_model, open(f"{dir}/{fname}", "wb"))


def load_model(model_path="model/best_model.pkl"):
    """ Model loader

    Args:
        model_path (str, optional): Path to file model name, default to `model/best_model.pkl`

    """
    return pickle.load(open(model_path, "rb"))
