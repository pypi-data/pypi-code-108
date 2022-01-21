from typing import Dict, List, Tuple
import io
import base64
import numpy as np
import matplotlib.pyplot as plt
from media_processing_lib.image import image_read

def npArayToBase64(arr: np.ndarray) -> str:
    plt.figure()
    plt.imshow(arr)
    res = pltToBase64(dpi=300, axis=False)
    plt.close()
    return res

def pltToBase64(dpi=None, axis: bool=True) -> str:
    f = io.BytesIO()
    if axis is False:
        plt.gca().set_axis_off()
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        plt.margins(0, 0)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.savefig(f, format="jpg", bbox_inches="tight", pad_inches=0, dpi=dpi)
    f.seek(0)
    jpgBase64 = str(base64.b64encode(f.read()), "utf8")
    return jpgBase64

def metricToBase64(trainData: List, valData: List, metricName: str) -> str:
    plt.figure()
    plt.plot(range(1, len(trainData) + 1), trainData, label="Train")
    plt.plot(range(1, len(valData) + 1), valData, label="Validation")
    minX, minValue = np.argmin(valData), np.min(valData)
    plt.annotate(f"Epoch {minX + 1}\nMin {minValue:2.2f}", xy=(minX + 1, minValue))
    plt.plot([minX + 1], [minValue], "o")
    plt.title(metricName)
    plt.legend()
    res = pltToBase64()
    plt.close()
    return res

def getMetricData(edgeData: Dict, metricName: str) -> Tuple[List, List]:
    trainLosses = [edgeData["historyDict"][i]["Train"][metricName] for i in range(len(edgeData["historyDict"]))]
    valLosses = [edgeData["historyDict"][i]["Validation"][metricName] for i in range(len(edgeData["historyDict"]))]
    return trainLosses, valLosses

def getBestLoss(edgeData: Dict, metricName: str) -> float:
    valLosses = [edgeData["historyDict"][i]["Validation"][metricName] for i in range(len(edgeData["historyDict"]))]
    return np.min(valLosses)

def cacheFn(path) -> str:
    """Create the stack only if needed, otherwise cache it for later usage."""
    cacheImgPath = path / "img.base64"
    if cacheImgPath.exists():
        res = open(cacheImgPath, "r").read()
    else:
        res = np.concatenate([image_read(str(x)) for x in path.glob("*.png")], axis=0)
        res = npArayToBase64(res)
        open(cacheImgPath, "w").write(res)
    return res

def button(textStr: str, imgStr: str) -> str:
    return f"""
<button class="buttonWithDiv">{textStr}</button>
<div class="hiddenDiv">
    <img src="data:image/jpg;base64, {imgStr}" />
</div>"""


def getHtmlForModels(status: Dict, iteration: int, getLoss: bool, getBestSamples: bool, getLastSamples: bool) -> str:
    edges = status["iterationInfo"][iteration]["model"]["edges"]
    if len(edges) == 0:
        return ""

    Str = """
<h3> Edges </h3>
<table>
    <thead>
        <tr>
            <th rowspan="2"> Edge </th>
            <th rowspan="1" colspan="2"> Loss </th>
            <th rowspan="1" colspan="2"> Epochs </th>
            <th rowspan="2" colspan="1"> Duration </th>
            <th rowspan="1" colspan="4"> Samples </th>
        </tr>
        <tr>
            <th> Value </th>
            <th> Toggle </th>
            <th> Total </th>
            <th> Best </th>
            <th> Best train </th>
            <th> Best validation </th>
            <th> Last train </th>
            <th> Last validation </th>
        </tr>
    </thead>
"""

    for edgeName, edgeData in edges.items():
        trainLosses, valLosses = getMetricData(edgeData, metricName=("Loss", ))

        base64Loss = button("Toggle", metricToBase64(trainLosses, valLosses, metricName="Loss")) if getLoss else "n/a"
        bestValLoss = getBestLoss(edgeData, metricName=("Loss", ))

        samplesDir = status["Path"] / f"iter{iteration}/models/{edgeName}/samples"
        bestEpochDir = samplesDir / f"{np.argmin(valLosses) + 1}"
        lastEpochDir = samplesDir / f"{len(valLosses)}"
        bestTrainSamples = button("Toggle", cacheFn(bestEpochDir / "train")) if getBestSamples else "n/a"
        bestValidationSamples = button("Toggle", cacheFn(bestEpochDir / "validation")) if getBestSamples else "n/a"
        lastTrainSamples = button("Toggle", cacheFn(lastEpochDir / "train")) if getLastSamples else "n/a"
        lastValidationSamples = button("Toggle", cacheFn(lastEpochDir / "validation")) if getLastSamples else "n/a"

        Str += f"""
<tr>
<td>{edgeName}</td>
<td>{bestValLoss:.3f}</td>
<td>
    <div> {base64Loss} </div>
</td>
<td> {edgeData['trainedEpochs']} </td>
<td> {edgeData['bestEpoch']} </td>
<td> {edgeData['duration']['total']} </td>

<td> <div> {bestTrainSamples} </div> </td>
<td> <div> {bestValidationSamples} </div> </td>
<td> <div> {lastTrainSamples} </div> </td>
<td> <div> {lastValidationSamples} </div> </td>

</tr>"""

    Str += "</table>"
    return Str

def getHtmlForData(status: Dict, iteration: int) -> str:
    dataStatus = status["iterationInfo"][iteration]["data"]
    if dataStatus == "n/a":
        return "<h3> Data </h3> <br/> n/a"

    Str = """
<h3> Data </h3>
<table>
<tr>
    <th> Node </th>
    <th> Total </th>
    <th> Train </th>
    <th> Semisupervised </th>
    <th> Identifiers </th>
</tr>
"""
    for node in dataStatus.keys():
        strTypes = ", ".join(dataStatus[node]["typesSemisupervised"])
        Str += f"""
<tr>
    <td> {node} </td>
    <td> {dataStatus[node]["numAll"]} </td>
    <td> {dataStatus[node]["numTrain"]} </td>
    <td> {dataStatus[node]["numSemisupervised"]} </td>
    <td> {strTypes} </td>
</tr>
"""
    Str += "</table>"
    return Str

def js() -> str:
    Str = "<script src=\"https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js\"></script>"
    Str += """
<script>

function toggleHideShow(item) {
    if (item.is(":hidden")) {
        item.show();
    }
    else {
        item.hide();
    }
}

$(".buttonWithDiv").click(function() {
    // alert($(this).parent().next());
    nextDiv = $(this).next("div");
    toggleHideShow(nextDiv);
});

$(".hiddenDiv").click(function() {
    toggleHideShow($(this));
});

</script>
    """
    return Str

def css() -> str:
    Str = """
<style>

table, tr, td, th {
    border: 1px solid black;
    border-collapse: collapse;
}

.hiddenDiv {
    display: none;
}

</style>
"""
    return Str

def htmlFormatter(status: Dict, getLoss: bool=True, getBestSamples: bool=True, getLastSamples: bool=True) -> str:
    Str = f"""
<html>
    <head> {css()} </head>
    <h1> NGCDir status </h1>
    <div> Path: {status["Path"]} </div>
    <div> NGC Model type: {status["Cfg"]["graphConfig"]} </div>
"""

    for iteration in range(1, len(status["iterationInfo"]) + 1):
        Str += f"<h2> Iteration {iteration} </h2>"
        Str += getHtmlForData(status, iteration=iteration)
        Str += getHtmlForModels(status, iteration=iteration, getLoss=getLoss, \
            getBestSamples=getBestSamples, getLastSamples=getLastSamples)

    Str += f"""
    <footer> {js()} </footer>
</html>
"""
    return Str
