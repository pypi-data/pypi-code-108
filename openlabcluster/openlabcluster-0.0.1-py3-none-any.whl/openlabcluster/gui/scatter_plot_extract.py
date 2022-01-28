
import umap
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
DIMENSION_REDUCTION_DICT = {'PCA': PCA, 'tSNE': TSNE, 'UMAP':umap.UMAP}
import os
from pathlib import Path

def return_train_network_path(config, shuffle=1, trainingsetindex=0, modelprefix=""):
    """ Returns the training and test pose config file names as well as the folder where the snapshot is
    Parameters
    ----------
    config : string
        Full path of the config.yaml file as a string.

    shuffle: int
        Integer value specifying the shuffle index to select for training.

    trainingsetindex: int, optional
        Integer specifying which TrainingsetFraction to use. By default the first (note that TrainingFraction is a list in config.yaml).

    Returns the triple: trainposeconfigfile, testposeconfigfile, snapshotfolder
    """
    from openlabcluster.utils import auxiliaryfunctions

    cfg = auxiliaryfunctions.read_config(config)
    modelfoldername = auxiliaryfunctions.GetModelFolder(
        cfg["TrainingFraction"][trainingsetindex], shuffle, cfg, modelprefix=modelprefix
    )
    trainposeconfigfile = Path(
        os.path.join(
            cfg["project_path"], str(modelfoldername), "train", "pose_cfg.yaml"
        )
    )
    testposeconfigfile = Path(
        os.path.join(cfg["project_path"], str(modelfoldername), "test", "pose_cfg.yaml")
    )
    snapshotfolder = Path(
        os.path.join(cfg["project_path"], str(modelfoldername), "train")
    )

    return trainposeconfigfile, testposeconfigfile, snapshotfolder

from threading import Thread
from wx.lib.pubsub import pub
class transform_hidden(Thread):
    def __init__(self, config, shuffle=1,
    trainingsetindex=0,
    max_snapshots_to_keep=5,
    displayiters=None,
    saveiters=None,
    maxiters=None,
    reducer_name = 'PCA',
    dimension = 2,
    allow_growth=False,
    gputouse=None,
    autotune=False,
    keepdeconvweights=True,
    modelprefix="",
):
        Thread.__init__(self)

        from openlabcluster.utils import auxiliaryfunctions

        # TF.reset_default_graph()
        start_path = os.getcwd()
        self.config = config
        # Read file path for pose_config file. >> pass it on
        self.displayiters = displayiters
        self.saveiters = saveiters
        self.maxiters = maxiters
        self.reducer_name = reducer_name
        self.dimension = dimension
        self.run()

    def run(self):
        from openlabcluster.gui.plot_hidden import extract_hid
        # self.transform = hidden_pre(
        #     str(self.config),
        #     self.displayiters,
        #     self.saveiters,
        #     self.maxiters,
        #     reducer_name=self.reducer_name,
        #     dimension=self.dimension
        # )
        tmp = extract_hid(self.config,reducer_name=self.reducer_name,dimension=self.dimension)
        self.transform = tmp.transformed
    def transformed(self):
        return self.transform

# def trandform_hidden(
#     config,
#     shuffle=1,
#     trainingsetindex=0,
#     max_snapshots_to_keep=5,
#     displayiters=None,
#     saveiters=None,
#     maxiters=None,
#     allow_growth=False,
#     gputouse=None,
#     autotune=False,
#     keepdeconvweights=True,
#     modelprefix="",
# ):
#     """Trains the network with the labels in the training dataset.
#
#     Parameter
#     ----------
#     config : string
#         Full path of the config.yaml file as a string.
#
#     shuffle: int, optional
#         Integer value specifying the shuffle index to select for training. Default is set to 1
#
#     trainingsetindex: int, optional
#         Integer specifying which TrainingsetFraction to use. By default the first (note that TrainingFraction is a list in config.yaml).
#
#     Additional parameters:
#
#     max_snapshots_to_keep: int, or None. Sets how many snapshots are kept, i.e. states of the trained network. Every savinginteration many times
#         a snapshot is stored, however only the last max_snapshots_to_keep many are kept! If you change this to None, then all are kept.
#         See: https://github.com/AlexEMG/DeepLabCut/issues/8#issuecomment-387404835
#
#     displayiters: this variable is actually set in pose_config.yaml. However, you can overwrite it with this hack. Don't use this regularly, just if you are too lazy to dig out
#         the pose_config.yaml file for the corresponding project. If None, the value from there is used, otherwise it is overwritten! Default: None
#
#     saveiters: this variable is actually set in pose_config.yaml. However, you can overwrite it with this hack. Don't use this regularly, just if you are too lazy to dig out
#         the pose_config.yaml file for the corresponding project. If None, the value from there is used, otherwise it is overwritten! Default: None
#
#     maxiters: this variable is actually set in pose_config.yaml. However, you can overwrite it with this hack. Don't use this regularly, just if you are too lazy to dig out
#         the pose_config.yaml file for the corresponding project. If None, the value from there is used, otherwise it is overwritten! Default: None
#
#     allow_groth: bool, default false.
#         For some smaller GPUs the memory issues happen. If true, the memory allocator does not pre-allocate the entire specified
#         GPU memory region, instead starting small and growing as needed. See issue: https://forum.image.sc/t/how-to-stop-running-out-of-vram/30551/2
#
#     gputouse: int, optional. Natural number indicating the number of your GPU (see number in nvidia-smi). If you do not have a GPU put None.
#         See: https://nvidia.custhelp.com/app/answers/detail/a_id/3751/~/useful-nvidia-smi-queries
#
#     autotune: property of TensorFlow, somehow faster if 'false' (as Eldar found out, see https://github.com/tensorflow/tensorflow/issues/13317). Default: False
#
#     keepdeconvweights: bool, default: true
#         Also restores the weights of the deconvolution layers (and the backbone) when training from a snapshot. Note that if you change the number of bodyparts, you need to
#         set this to false for re-training.
#
#     Example
#     --------
#     for training the network for first shuffle of the training dataset.
#     >>> deeplabcut.train_network('/analysis/project/reaching-task/config.yaml')
#     --------
#
#     for training the network for second shuffle of the training dataset.
#     >>> deeplabcut.train_network('/analysis/project/reaching-task/config.yaml',shuffle=2,keepdeconvweights=True)
#     --------
#
#     """
#     # import tensorflow as tf
#     #
#     # vers = (tf.__version__).split(".")
#     # if int(vers[0]) == 1 and int(vers[1]) > 12:
#     #     TF = tf.compat.v1
#     # else:
#     #     TF = tf
#
#     # reload logger.
#     import importlib
#     import logging
#
#     importlib.reload(logging)
#     logging.shutdown()
#
#     from openlabcluster.utils import auxiliaryfunctions
#
#     # TF.reset_default_graph()
#     start_path = os.getcwd()
#
#     # Read file path for pose_config file. >> pass it on
#     cfg = auxiliaryfunctions.read_config(config)
#     # modelfoldername = auxiliaryfunctions.GetModelFolder(
#     #     cfg["TrainingFraction"][trainingsetindex], shuffle, cfg, modelprefix=modelprefix
#     # )
#     # poseconfigfile = Path(
#     #     os.path.join(
#     #         cfg["project_path"], str(modelfoldername), "train", "pose_cfg.yaml"
#     #     )
#     # )
#     # if not poseconfigfile.is_file():
#     #     print("The training datafile ", poseconfigfile, " is not present.")
#     #     print(
#     #         "Probably, the training dataset for this specific shuffle index was not created."
#     #     )
#     #     print(
#     #         "Try with a different shuffle/trainingsetfraction or use function 'create_training_dataset' to create a new trainingdataset with this shuffle index."
#     #     )
#     # else:
#     #     # Set environment variables
#     #     if (
#     #         autotune is not False
#     #     ):  # see: https://github.com/tensorflow/tensorflow/issues/13317
#     #         os.environ["TF_CUDNN_USE_AUTOTUNE"] = "0"
#     #     if gputouse is not None:
#     #         os.environ["CUDA_VISIBLE_DEVICES"] = str(gputouse)
#     try:
#         # cfg_dlc = auxiliaryfunctions.read_plainconfig(poseconfigfile)
#         # if "multi-animal" in cfg_dlc["dataset_type"]:
#         #     from openlabcluster.training_utils.train_multianimal import train
#         #
#         #     print("Selecting multi-animal trainer")
#         #     train(
#         #         str(poseconfigfile),
#         #         displayiters,
#         #         saveiters,
#         #         maxiters,
#         #         max_to_keep=max_snapshots_to_keep,
#         #         keepdeconvweights=keepdeconvweights,
#         #         allow_growth=allow_growth,
#         #     )  # pass on path and file name for pose_cfg.yaml!
#         # else:
#         #from openlabcluster.training_utils.train import train
#
#         print("Selecting single-animal trainer")
#         transform = hidden_pre(
#             str(config),
#             displayiters,
#             saveiters,
#             maxiters,
#             max_to_keep=max_snapshots_to_keep,
#             keepdeconvweights=keepdeconvweights,
#             allow_growth=allow_growth,
#         )  # pass on path and file name for pose_cfg.yaml!
#
#     except BaseException as e:
#         raise e
#     finally:
#         os.chdir(str(start_path))
#     print(
#         "The network is now trained and ready to evaluate. Use the function 'evaluate_network' to evaluate the network."
#     )
#     return transform
#
#
