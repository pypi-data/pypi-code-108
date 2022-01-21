import gdown
from os.path import join, isfile
import torch
import textwrap
import dingo_enets

ENET_URLS = {
    "O1-H1L1": "https://drive.google.com/uc?export=download&id=15QiCJx89SnzqMICYQtRYpWPN49tnMALy",
}


def build_enet(run, detectors, model_dir):
    """
    Builds an embedding network for the a specific observing run and detector
    configuration. It checks, whether a model file is located in model_dir. If not,
    the model file is downloaded.

    Parameters
    ----------
    run: str
        observing run, e.g. O1
    detectors: list
        list with detectors, e.g. ['H1', 'L1']
    model_dir: str
        directory where dingo_enet models are located

    Returns
    -------
    enet
        embedding network
    """
    ID = get_model_id(run, detectors)
    filename = download_model(ID, model_dir)
    enet = build_enet_from_file(filename)
    return enet


def download_model(ID, model_dir):
    """
    Check if the model for ID exists in model_dir. If not, download and save it.

    Parameters
    ----------
    ID: str
        model ID, generated with get_model_id
    model_dir: str
        model directory

    Returns
    -------
    filename: str
        filename of the model
    """
    filename = join(model_dir, f"enet_{ID}.pt")
    if not isfile(filename) or False:
        print(
            f"Model file {filename} does not exist. Start download. This may take a "
            f"while."
        )
        try:
            url = ENET_URLS[ID]
        except KeyError:
            raise KeyError(f"Unknown ID {ID}. Available IDs: {list(ENET_URLS.keys())}")
        gdown.download(url, filename, quiet=False)
        print("Done.")
    else:
        print(f"Model file {filename} already exists.")
    return filename


def get_model_id(run, detectors):
    """
    Generate the model id for a specific observing run and detector configuration.

    Parameters
    ----------
    run: str
        observing run, e.g. O1
    detectors: list
        list with detectors, e.g. ['H1', 'L1']

    Returns
    -------
    model_id: str
        the model id
    """
    return f"{run}-{''.join(sorted(detectors))}"


def build_enet_from_file(filename):
    """
    Builds an embedding network from a model file.

    Parameters
    ----------
    filename: str
        model filename

    Returns
    -------
    enet:
        embedding network
    """
    enet_dict = torch.load(filename)
    if (
        enet_dict["model_builder"]
        == "dingo_enets.create_enet_with_projection_layer_and_dense_resnet"
    ):
        model_builder = dingo_enets.create_enet_with_projection_layer_and_dense_resnet
    else:
        raise NotImplementedError(f"Unknown model builder {enet_dict['model_builder']}")
    print("Building model and loading saved weights.", end=" ")
    enet = model_builder(**enet_dict["model_kwargs"])
    enet.load_state_dict(enet_dict["model_state_dict"])
    print("Done. Model info:", end="\n\n")
    info_text = enet_dict["info"]
    print("\n".join(textwrap.wrap(info_text, 90, break_long_words=False)), end="\n\n")
    return enet
