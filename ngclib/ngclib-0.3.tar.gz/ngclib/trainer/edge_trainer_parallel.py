import time
import threading
import torch as tr
from torch.utils.data import DataLoader
from queue import Queue
from overrides import overrides
from typing import Dict, List
from pathlib import Path
from nwgraph import Edge
from nwmodule.trainer import NWTrainer

from .edge_trainer import EdgeTrainer, get_loader
from .setup_edge import setup_edge
from ..logger import logger
from ..readers import NGCNpzReader
from ..models import NGC
from ..models.edges import TwoHopsNoGT, TwoHopsResidualNoGT

def trainOneEdge(device: tr.device, q: Queue, edge: Edge, \
        trainCfg: Dict, weightsDir: Path, edgeTrainLoader: DataLoader, edgeValidationLoader: DataLoader):
    logger.info(f"[device:{device.index}] Training edge '{edge}'.")
    try:
        edge.to(device)
        setup_edge(edge, trainCfg, weightsDir)
        Dir = Path.cwd() / EdgeTrainer.getEdgeDirName(edge)
        trainer = NWTrainer(edge, Dir)
        trainer.train(edgeTrainLoader, trainCfg["numEpochs"], edgeValidationLoader)
    except Exception as e:
        logger.debug(f"[device:{device.index}] Error while training edge '{edge}'. Exception: {str(e)}")
        breakpoint()
    logger.debug(f"[device:{device.index}] Finished training edge '{edge}'")
    q.put(device)
    del edgeTrainLoader
    del edgeValidationLoader

def getTorchAvailableGPUs() -> List[tr.device]:
    # Torch takes into account CUDA_VISIBLE_DEVICES and also reorders ids starting from 0, ignoring global cuda id
    torchAvailableDevices = []
    i = 0
    while True:
        try:
            device = tr.device(f"cuda:{i}")
            _ = tr.FloatTensor([0]).to(device)
            torchAvailableDevices.append(device)
        except Exception:
            break
        i += 1
    logger.debug(f"Torch available devices: {len(torchAvailableDevices)}")
    assert len(torchAvailableDevices) > 0
    return torchAvailableDevices

class EdgeTrainerParallel(EdgeTrainer):
    def __init__(self, model: NGC):
        self.model = model
        # This holds the torch-level available gpu ids
        self.torchAvailableDevices = getTorchAvailableGPUs()
        logger.debug(f"Num GPUs available: {len(self.torchAvailableDevices)}")

    @overrides
    def run(self, trainCfg: Dict, trainReader: NGCNpzReader, validationReader: NGCNpzReader, debug: bool):
        # Create a queue variable which will be shared amongst threads to announce when an edge was trained.
        q = Queue()

        if debug:
            trainCfg["numEpochs"] = 3
        weightsDir = Path.cwd()

        trained = self.model.getTrainedEdges(weightsDir, EdgeTrainer.getEdgeDirName)
        untrained, untrainedNames, inProgress, finished = [], [], [], []
        deviceToEdge = {}
        threads = {}
        for i, edge in enumerate(self.model.edges):
            if edge in trained:
                finished.append(edge)
                continue
            untrained.append(edge)
            untrainedNames.append(EdgeTrainer.getEdgeDirName(edge))
        logger.info(f"Num untrained edges: {len(untrained)} / {len(self.model.cfg['edges'])}")
        # Load all available gpus in this main thread
        for i in range(len(self.torchAvailableDevices)):
            q.put(self.torchAvailableDevices[i])

        self.model.to("cpu")
        while True:
            # Busy waiting, since the main thread is not really that relevant
            time.sleep(1)
            if q.empty():
                logger.debug2("Q is empty. Waiting...")
                continue

            device = q.get()
            logger.debug2(f"Got device {device} (id: {device.index})")

            # If this device was previously used by an edge, mark that edge as trained and remove it from untrained. Also
            #  join the thread so resources are unallocated properly
            if device.index in threads:
                assert device.index in deviceToEdge
                edge = deviceToEdge[device.index]
                assert edge in inProgress
                thread = threads.pop(device.index)
                thread.join()
                edge = inProgress.pop(inProgress.index(edge))
                finished.append(edge)
            
            if len(finished) == len(self.model.cfg["edges"]):
                assert len(inProgress) == 0
                assert len(untrained) == 0
                assert len(untrainedNames) == 0
                assert len(threads) == 0
                break
            
            # Still some in progress
            if len(untrained) == 0:
                q.put(device)
                continue

            edge = untrained.pop()
            edgeName = untrainedNames.pop()
            # We must wait for the single link to finish first
            # TODO: Make this generic using topo-sort.
            if isinstance(edge, (TwoHopsNoGT, TwoHopsResidualNoGT)):
                if not str(edge.singleLinkEdge) in str(finished):
                    q.put(device)
                    untrained.insert(0, edge)
                    untrainedNames.insert(0, edgeName)
                    continue

            # Otherwise, pop a new edge and start a new thread.
            inProgress.append(edge)
            trainLoader = get_loader(trainReader, edge, trainCfg, randomize=True, debug=debug, augmentation=True)
            valLoader = get_loader(validationReader, edge, trainCfg, randomize=False, debug=debug, augmentation=False)
            threadArgs = (device, q, edge, trainCfg, weightsDir, trainLoader, valLoader)
            threads[device.index] = threading.Thread(target=trainOneEdge, args=threadArgs)
            deviceToEdge[device.index] = edge
            threads[device.index].start()
        self.model.to(self.torchAvailableDevices[0])
        logger.debug("Finished all threads!")
