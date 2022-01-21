# TODOs
# - automatic graph detection based on performance

import os
from typing import List, Dict, Union
from pathlib import Path

from .edge_trainer import EdgeTrainer
from .edge_trainer_sequential import EdgeTrainerSequential
from .edge_trainer_parallel import EdgeTrainerParallel
from .ngc_iteration_prologue import iterationPrologue
from ..models import NGC
from ..logger import logger
from ..readers import NGCNpzReader
from ..ngcdir import NGCDir
from ..dir_linker import DirLinker

def changeDirectory(Dir:Union[str, Path]):
	Dir = Path(Dir)
	Dir.mkdir(exist_ok=True, parents=True)
	logger.debug(f"Changing to working directory: {Dir}")
	os.chdir(Dir)

class NGCTrainer:
	def __init__(self, model: NGC, ngcDirPath: Path, method: str, trainCfg: Dict,
		trainDir: Path, validationDir: Path, semisupervisedDirs: List[Path]):
		self.model = model
		ngcDirPath.mkdir(exist_ok=True, parents=True)
		self.ngcDir = NGCDir(ngcDirPath, model.cfg)
		self.dirLinker = DirLinker(self.ngcDir, trainDir, validationDir, semisupervisedDirs)
		self.method = method
		self.trainCfg = trainCfg
		self.nameToNode = {node.name: node for node in self.model.getNodes()}

	# @brief Training for 1 iteration only
	def doOneIteration(self, edgeTrainer: EdgeTrainer, iteration:int, debug:bool):
		logger.info(f"Starting iteration {iteration}")
		modelDir = self.ngcDir.getAllDataDirs(iteration)["models"][iteration]
		dataDir = self.ngcDir.getAllDataDirs(iteration)["data"][iteration]
		cwd = Path.cwd()
		changeDirectory(modelDir)

		inputNodes = [self.nameToNode[x] for x in self.model.cfg["inputNodes"]]
		trainReader = NGCNpzReader(path=dataDir, nodes=self.model.getNodes(), gtNodes=inputNodes)
		validationReader = NGCNpzReader(path=self.dirLinker.validationDir, \
			nodes=self.model.getNodes(), gtNodes=inputNodes)

		self.model.train()
		edgeTrainer.run(self.trainCfg, trainReader, validationReader, debug)
		changeDirectory(cwd)

	# @brief The main public function to be called on an NGC model
	def run(self, startIteration: int, endIteration: int, parallelization: bool = False, debug: bool = False):
		logger.info(f"Training the NGC graph from iteration {startIteration} to {endIteration} " + \
				f"(parallelization: {parallelization}, debug: {debug}).")
		self.dirLinker.linkTrainDir(iteration=1)

		if parallelization:
			edgeTrainer = EdgeTrainerParallel(self.model)
		else:
			edgeTrainer = EdgeTrainerSequential(self.model)

		for iteration in range(startIteration, endIteration + 1):
			self.model.train()
			self.doOneIteration(edgeTrainer, iteration, debug)

			self.model.eval()
			iterationPrologue(self, iteration, debug)
