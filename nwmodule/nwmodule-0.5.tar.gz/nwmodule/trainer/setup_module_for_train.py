from typing import Dict
from functools import partial
import torch as tr
import numpy as np
from torch import optim

from ..nwmodule import NWModule
from ..logger import logger
from ..schedulers import ReduceLRAndBacktrackOnPlateau, ReduceLROnPlateau
from ..callbacks import EarlyStopping, SaveHistory, SaveModels, PlotMetrics

def setup_module_for_train(module: NWModule, train_cfg: Dict):
    """Sets up a NWModule for training using some standard details that are common, like optimizers, scheduler
    and standard callbacks.
    """
    assert "optimizer" in train_cfg and "args" in train_cfg["optimizer"]

    logger.debug(f"Setting up train cfg: {train_cfg}")
    if "seed" in train_cfg:
        logger.debug2(f"Setting up seed to {train_cfg['seed']}.")
        np.random.seed(train_cfg["seed"])
        tr.manual_seed(train_cfg["seed"])
    else:
        logger.debug2(f"No seed used.")

    module.train()
    module.reset_parameters()
    module.setTrainableWeights(True)

    # Optimizer
    optimizer_type = {
        "adam" : optim.Adam,
        "sgd" : optim.SGD,
        "rmsprop" : optim.RMSprop,
        "adamw" : optim.AdamW
    }[train_cfg["optimizer"]["type"]]
    optimizer_type = partial(optimizer_type, **train_cfg["optimizer"]["args"])
    module.setOptimizer(optimizer_type)

    # Scheduler
    if "scheduler" in train_cfg:
        assert "type" in train_cfg["scheduler"]
        assert "args" in train_cfg["scheduler"]
        schedulerType = {
            "ReduceLRAndBacktrackOnPlateau": partial(ReduceLRAndBacktrackOnPlateau, model=module),
            "ReduceLROnPlateau": partial(ReduceLROnPlateau, model=module)
        }[train_cfg["scheduler"]["type"]]
        scheduler = schedulerType(**train_cfg["scheduler"]["args"])
        logger.debug2(f"Scheduler provided: {scheduler}.")
        module.setOptimizerScheduler(scheduler)
    else:
        logger.debug2("No scheduler provided.")

    # Early Stopping
    if "EarlyStopping" in train_cfg:
        logger.debug2(f"Early Stopping provided. Args: {train_cfg['EarlyStopping']}")
        module.addCallback(EarlyStopping(**train_cfg["EarlyStopping"]))
    else:
        logger.debug2("Early stopping not provided.")

    # Callbacks
    logger.debug2("Adding default callbacks (SaveHistory, SaveModels(Loss, best & last) and PlotMetrics(Loss).")
    module.addCallbacks([
        SaveHistory("history.txt"), \
        SaveModels("best", "Loss"), \
        SaveModels("last", "Loss"), \
        PlotMetrics(["Loss"]), \
    ])
