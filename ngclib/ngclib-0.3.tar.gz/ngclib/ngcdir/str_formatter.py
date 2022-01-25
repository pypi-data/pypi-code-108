from typing import Dict

def getDataStr(dataStatus: Dict) -> str:
    """Parses the data status of an iteration."""
    Str = "[Data]"
    if dataStatus == "n/a":
        Str += "\n  - n/a"
        return Str
    for node in dataStatus.keys():
        strTypes = ", ".join(dataStatus[node]["typesSemisupervised"])
        Str += f"\n  - Node: {node}"
        Str += f"\n    - Total={dataStatus[node]['numAll']}. Train={dataStatus[node]['numTrain']} "
        Str += f"Semisupervised={dataStatus[node]['numSemisupervised']} ({strTypes})"
    return Str

def getModelStr(modelStatus: Dict) -> str:
    """Parses the model status of an iteration"""
    Str = "[Model]"
    Str += f"\n  - Total edges: {modelStatus['totalEdges']}"
    Str += f"\n  - Total trained: {modelStatus['totalTrained']}"
    Str += f"\n  - Edges:"
    for edge, values in modelStatus["edges"].items():
        Str += f"\n    - {edge} -- "
        Str += f"Total epochs: {values['trainedEpochs']}. "
        Str += f"Best epoch: {values['bestEpoch']}. "
        Str += f"Duration: {values['duration']['total']}."
    Str += f"\n  - Total duration: {modelStatus['totalDuration']}"
    return Str

def strFormatter(status: Dict) -> str:
    """Given a status obtained via NgcDir(Path).getStatus(), returns a formatted string for pretty printing."""
    Str = "[NGCDir]"
    Str += f"\nPath: {status['Path']}"

    # graph cfg information (nodes, edges, hyperparameters, etc.)
    Str += "\nCfg: "
    for k in status["Cfg"].keys():
        Str += f"\n  - {k}: {status['Cfg'][k]}"

    # Iteration results (data and edges)
    Str += f"\nAvailable iterations: {status['numIterations']}"
    for iteration in range(1, status["numIterations"] + 1):
        iterDataStr = getDataStr(status["iterationInfo"][iteration]["data"])
        iterModelStr = getModelStr(status["iterationInfo"][iteration]["model"])
        Str += f"\n\n-- Iteration {iteration} --"
        Str += f"\n{iterDataStr}"
        Str += f"\n\n{iterModelStr}"
        Str += "\n________________________________________________________"
    return Str
