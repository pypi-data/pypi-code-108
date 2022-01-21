import torch as tr
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
from functools import lru_cache
from datetime import datetime, timedelta
from .utils import edgeYamlStrToDirName
from .str_formatter import strFormatter
from .html_formatter import htmlFormatter

# Generic ngc dir analysis class. It should be able to tell us what edges are trained, for how many iterations and
#  other analysis stuff like this.
class NGCDir:
    def __init__(self, path: Path, graphCfg: Dict):
        self.path = Path(path)
        self.graphCfg = graphCfg
        assert self.path.exists(), self.path
        assert self.graphCfg is not None

    def getNodes(self) -> Dict[str, List[str]]:
        return {"types": self.graphCfg["nodeTypes"], "names": self.graphCfg["nodeNames"]}

    def getAvailableIterations(self) -> int:
        allDirs = list(filter(lambda x: x.is_dir() and x.name.startswith("iter"), self.path.iterdir()))
        return len(allDirs)

    # @brief Returns the number of data files for each node given an iteration (train & semisupervised)
    def getDataStatus(self, iteration: int) -> Dict[str, Dict[str, int]]:
        dataDir = self.path / f"iter{iteration}/data"
        iterDataDirs = filter(lambda x: x.is_dir(), dataDir.iterdir())
        res = {}
        for iterDataDir in iterDataDirs:
            npzFiles = [x.name for x in  iterDataDir.glob("*.npz")]
            trainNpzFiles = list(filter(lambda x: x.startswith("train_"), npzFiles))
            # ss1_XX.npz, ss2_XX.npz etc.
            ssFiles = list(filter(lambda x: x.startswith("ss"), npzFiles))
            resDataDir = {
                "all": len(npzFiles),
                "train": len(trainNpzFiles),
                "semisupervised": len(ssFiles)
            }
            uniqueSSPrefixes = set([x.split("_")[0] for x in ssFiles])
            uniqueSSFiles = {}
            for uniquePrefix in uniqueSSPrefixes:
                uniqueSSFiles[uniquePrefix] = list(filter(lambda x : x.startswith(f"{uniquePrefix}_"), ssFiles))
                resDataDir[uniquePrefix] = len(uniqueSSFiles[uniquePrefix])
            res[iterDataDir.name] = resDataDir
        return res

    def checkIfTrained(self, iteration: int, edgeName: str) -> bool:
        iterDir = self.path / f"iter{iteration}/models"
        edgeDir = iterDir / edgeName
        if not edgeDir.exists():
            return False
        modelPath = edgeDir / "model_best_Loss.pkl"
        if not modelPath.exists():
            return False
        return True

    # @brief Returns a dictionary of all edges with keys as the names of the edges and values with paths to the
    #  best and last epoch (if trained) or nones.
    def getEdgesStatus(self, iteration: int) -> Dict[str, Dict[str, Path]]:
        allEdges = self.graphCfg["edges"]
        if self.graphCfg["graphConfig"] in ("NGC-V1", "NGC_AAAI2020") and allEdges == "complete":
            from ..models.ngc_v1.ngc_v1 import NGCV1
            allEdges = NGCV1._getNGCEdgesComplete(self.graphCfg["nodeNames"], self.graphCfg["inputNodes"])

        res = {}
        for edge in allEdges:
            edgeName = edgeYamlStrToDirName(edge, self.graphCfg)
            trained = self.checkIfTrained(iteration, edgeName)
            res[edgeName] = trained
        return res

    @lru_cache
    def getTrainedEdgeMetadata(self, iteration: int, edgeName: str) -> Dict[str, Any]:
        assert self.checkIfTrained(iteration, edgeName)
        iterDir = f"{self.path}/iter{iteration}/models"
        modelPath = f"{iterDir}/{edgeName}/model_last.pkl"
        historyDict = tr.load(modelPath, map_location="cpu")["history_dict"]
        res = {
            "modelPath": modelPath,
            "historyDict": historyDict
        }
        return res

    def getAllDataDirs(self, numIterations: int) -> Dict[str, Dict[int, Path]]:
        dataDirs = {i: Path(f"{self.path}/iter{i}/data") for i in range(1, numIterations + 1)}
        modelsDirs = {i: Path(f"{self.path}/iter{i}/models") for i in range(1, numIterations + 1)}
        res = {"data": dataDirs, "models": modelsDirs}
        return res

    # @brief Generic status creating method, that can be used by other services to print the status of a ngcdir.
    # @return The dicitonary that contains all the information regarding the ngcdir.
    def getStatus(self) -> Dict:
        def getDuration(historyDict):
            epoch = datetime(1900, 1, 1)
            N = len(historyDict)
            res = {}
            total = timedelta(0)
            for i in range(N):
                res[i] = {}
                item = historyDict[i]
                if not "Train" in item or not "duration" in item["Train"]:
                    res[i]["train"] = timedelta(0)
                else:
                    res[i]["train"] = datetime.strptime(item["Train"]["duration"], "%H:%M:%S.%f") - epoch

                if not "Validation" in item or not "duration" in item["Validation"]:
                    res[i]["validation"] = timedelta(0)
                else:
                    res[i]["validation"] = datetime.strptime(item["Validation"]["duration"], "%H:%M:%S.%f") - epoch
                total += res[i]["train"] + res[i]["validation"]
            res["total"] = total
            return res

        res = {
            "Path": self.path,
            "Cfg": self.graphCfg,
            "numIterations": self.getAvailableIterations(),
            "iterationInfo": {}
        }
        numIterations = self.getAvailableIterations()
        for iteration in range(1, numIterations + 1):
            iterRes = {}

            # Data stuff
            dataStatus = self.getDataStatus(iteration=iteration)
            iterRes["data"] = {}
            if len(dataStatus) == 0:
                iterRes["data"] = "n/a"
            for node, values in dataStatus.items():
                typesSemisupervised = sorted(list(filter(lambda x: x.startswith("ss"), values.keys())))
                iterRes["data"][node] = {
                    "numAll": values["all"],
                    "numTrain": values["train"],
                    "numSemisupervised": values["semisupervised"],
                    "typesSemisupervised": typesSemisupervised
                }

            # Model stuff
            iterRes["model"] = {}
            modelStatus = self.getEdgesStatus(iteration = iteration)
            iterRes["model"]["totalEdges"] = len(modelStatus)
            iterRes["model"]["totalTrained"] = sum(list(modelStatus.values()))
            iterRes["model"]["edges"] = {}
            iterRes["model"]["totalDuration"] = timedelta(0)
            for edge in modelStatus.keys():
                if modelStatus[edge] == 0:
                    iterRes["model"][edge] = {"trainedEpochs": 0, "bestEpoch": 0, "historyDict": {}, "duration": 0}
                    continue

                edgeStatus = {}
                meta = self.getTrainedEdgeMetadata(iteration, edge)
                edgeStatus["trainedEpochs"] = len(meta["historyDict"])
                losses = [meta["historyDict"][i]["Validation"][('Loss', )] for i in range(len(meta["historyDict"]))]
                edgeStatus["bestEpoch"] = np.argmin(losses) + 1
                edgeStatus["duration"] = getDuration(meta["historyDict"])

                edgeStatus["historyDict"] = meta["historyDict"]
                iterRes["model"]["edges"][edge] = edgeStatus
                iterRes["model"]["totalDuration"] += edgeStatus["duration"]["total"]
            res["iterationInfo"][iteration] = iterRes
        return res

    def __str__(self) -> str:
        return strFormatter(self.getStatus())

    def toHtml(self, *args, **kwargs) -> str:
        return htmlFormatter(self.getStatus(), *args, **kwargs)

    def __repr__(self) -> str:
        return str(self)
