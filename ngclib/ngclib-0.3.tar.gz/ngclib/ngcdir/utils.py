from typing import List, Dict

def edgeYamlStrToDirName(edgeYamlStr: List[str], graphCfg: Dict) -> str:
    """Given a yaml format string ([rgb, depth, semantic]) and a modelType (NGC_V1, NGC_Next etc.), returns the
    name of the dir inside ngcdir.
    """
    modelType = graphCfg["graphConfig"]
    if modelType == "NGC-V1":
        if len(edgeYamlStr) == 2:
            return f"SL_{edgeYamlStr[0]}_{edgeYamlStr[1]}"
        elif len(edgeYamlStr) == 3:
            return f"TH_NOGT_{edgeYamlStr[0]}_{edgeYamlStr[1]}_{edgeYamlStr[2]}"
    elif modelType == "NGC_AAAI2020":
        edge = edgeYamlStr.split("_")
        assert len(edge) == 2
        if edge[0] == graphCfg["inputNode"]:
            return f"SL_{edge[0]}_{edge[1]}"
        else:
            return f"TH_NOGT_{edge[0]}_{edge[1]}"
    elif modelType == "NGC-V2-Residual":
        if len(edgeYamlStr) == 2:
            if edgeYamlStr[0] == graphCfg["residualNode"]:
                return f"SL_{edgeYamlStr[0]}_{edgeYamlStr[1]}"
            else:
                return f"SLR_{graphCfg['residualNode']}+{edgeYamlStr[0]}_{edgeYamlStr[1]}"
        elif len(edgeYamlStr) == 3:
            return f"THR_NOGT_{graphCfg['residualNode']}+{edgeYamlStr[0]}_{edgeYamlStr[1]}_{edgeYamlStr[2]}"
    else:
        assert False, f"Unknown type {modelType}."
