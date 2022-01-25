import numpy as np
import torch as tr
from pathlib import Path
from typing import List
from ..readers import NGCNpzReader
from ..logger import logger, drange
from ..models.ngc import NGC
from ..nodes import Semantic

# @brief Assuming a pretrained model, we'll copy/link the labels of the training directory and then, for all
#  semisupervised directories, pass the data through the NGC model and save the results.
def exportPseudoLabels(model: NGC, semisupervisedDirs: List[Path], nextDataDir: Path, debug: bool):
	logger.debug(f"Exporting the trainDir and {len(semisupervisedDirs)} semisupervised dirs")
	logger.debug(f"Next data directory: '{nextDataDir}'")

	def exportOneDir(model: NGC, nextDataDir: Path, ssDir: Path, dirNumber: int, debug: bool):
		nodeNames = {node.name:node for node in model.nodes}
		inputNodes = [nodeNames[x] for x in model.cfg["inputNodes"]]
		reader = NGCNpzReader(path=ssDir, nodes=inputNodes, gtNodes=inputNodes)
		loader = reader.toDataLoader(randomize=False, debug=debug, numWorkers=0).__iter__()
		for j in drange(len(loader), desc="Pseudolabels"):
			x = next(loader)["data"]
			y = model.npForward(x)
			for nodeName, node in nodeNames.items():
				outDir = nextDataDir / nodeName
				assert outDir.exists()
				if nodeName in model.cfg["inputNodes"]:
					continue
				else:
					messages = y[node]
					assert len(messages) == 1, messages
					message = list(messages)[0]
					assert message.path[-1] == "Vote"
					nodeOutput = message.output[0]
					if isinstance(node, Semantic):
						nodeOutput = np.argmax(nodeOutput, axis=-1).astype(np.uint8)
				outFilePath = outDir / f"ss{dirNumber}_{j}.npz"
				if nodeOutput.dtype == np.float32:
					nodeOutput = nodeOutput.astype(np.float16)
				np.savez_compressed(outFilePath, nodeOutput)

	# Export pseudolabels for all semisupervised dirs (while copying the input nodes)
	logger.info("Exporting pseudolabels...")
	model.eval()
	for i in drange(len(semisupervisedDirs), desc="Pseudolabel dir"):
		ssDir = semisupervisedDirs[i]
		exportOneDir(model, nextDataDir, ssDir, dirNumber=i, debug=debug)

def export_new_dataset_every_iteration(ngcTrainer, iteration: int, debug: bool):
	"""The standard strategy, where for every new iteration, a new dataset is used to export pseudolabels.
	For all input nodes, there must be a reference gt label in semisupervised/iteration_x/node_name.
	"""
	from .edge_trainer import EdgeTrainer
	iterationModelsDir = ngcTrainer.ngcDir.getAllDataDirs(iteration)["models"][iteration]
	ngcTrainer.model.train()
	ngcTrainer.model.loadAllEdges(iterationModelsDir, EdgeTrainer.getEdgeDirName)
	ngcTrainer.model.eval()
	dataDir = ngcTrainer.ngcDir.getAllDataDirs(iteration + 1)["data"][iteration + 1]
	# Link all train labels
	ngcTrainer.dirLinker.linkTrainDir(iteration + 1)
	# Link all input nodes
	ngcTrainer.dirLinker.linkInputNodes(ngcTrainer.model.cfg["inputNodes"], iteration + 1)
	# Then export pseudolabels on top of train data
	exportPseudoLabels(ngcTrainer.model, ngcTrainer.dirLinker.semisupervisedDirs, dataDir, debug)

def export_train_set_only(ngcTrainer, iteration: int, debug: bool):
	# Just Link all train labels
	ngcTrainer.dirLinker.linkTrainDir(iteration + 1)

def export_pseudolabels_train_set_only(ngcTrainer, iteration: int, debug: bool):
	"""Method used by c-shift, where same dataset (train set) is iterated here. Input nodes are copied."""
	assert False, "TODO"
	ngcTrainer.dirLinker.linkTrainDir(iteration + 1)

def iterationPrologue(ngcTrainer, iteration: int, debug: bool):
	tr.use_deterministic_algorithms(False)
	method = ngcTrainer.method
	logger.info(f"Iteration {iteration - 1} prologue. Method: '{method}'")
	if method == "export_new_dataset_every_iteration":
		export_new_dataset_every_iteration(ngcTrainer, iteration, debug)
	elif method == "export_pseudolabels_train_set_only":
		export_pseudolabels_train_set_only(ngcTrainer, iteration, debug)
	elif method == "export_train_set_only":
		export_train_set_only(ngcTrainer, iteration, debug)
	else:
		assert False, f"Unknown method: '{method}'"
