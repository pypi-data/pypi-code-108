import os
from pathlib import Path
from natsort import natsorted
from typing import List
from .logger import logger

class DirLinker:
	def __init__(self, ngcDir, trainDir: Path, validationDir: Path, semisupervisedDirs: List[Path]):
		self.ngcDir = ngcDir
		self.trainDir = trainDir
		self.validationDir = validationDir
		self.semisupervisedDirs = semisupervisedDirs

	# @brief Creates a symlink between a training directory (given supervised list)
	#  and the data directory in the ngcdir
	def linkTrainDir(self, iteration: int):
		"""Creates a symlink between a training directory (given supervised data) and the data directory in the ngcdir
		"""
		nodeNames = self.ngcDir.getNodes()["names"]
		dataDir = self.ngcDir.path / f"iter{iteration}/data"
		logger.debug(f"Linking training dir {self.trainDir} -> {dataDir}")

		for nodeName in nodeNames:
			outDir = Path(dataDir / nodeName)
			if outDir.exists():
				logger.debug(f"Node out dir '{outDir}' exists. Skipping.")
				continue
			outDir.mkdir(exist_ok=False, parents=True)
			inDir = self.trainDir / nodeName
			inFiles = natsorted([str(x) for x in inDir.glob("*.npz")])
			outFiles = [outDir / f"train_{i}.npz" for i in range(len(inFiles))]
			for inFile, outFile in zip(inFiles, outFiles):
				os.symlink(inFile, outFile)
		logger.debug(f"Finished linking training dir.")

	def linkInputNodes(self, inputNodes: List[str], iteration: int):
		"""Links all inpiut nodes for this iteration based on the input nodes list."""
		dataDir = self.ngcDir.path / f"iter{iteration}/data"
		logger.debug(f"Linking semisupervised dirs ({len(self.semisupervisedDirs)}) -> {dataDir} for all "
			f"input nodes: {inputNodes}")
		dataDir = self.ngcDir.path / f"iter{iteration}/data"
		for j, ssDir in enumerate(self.semisupervisedDirs):
			for nodeName in inputNodes:
				assert (dataDir / nodeName).exists(), dataDir / nodeName
				assert (ssDir / nodeName).exists(), ssDir / nodeName
				inFiles = natsorted([str(x) for x in (ssDir / nodeName).glob("*.npz")])
				outFiles = [dataDir / nodeName / f"ss{j}_{i}.npz" for i in range(len(inFiles))]
				for inFile, outFile in zip(inFiles, outFiles):
					if not outFile.exists():
						os.symlink(inFile, outFile)
		logger.debug(f"Finished linking input nodes for semisupervised dirs.")
