import os.path
import deeplabcut
from typing import List
from logging import info


def dlc_analyze(
    config: str,
    paths: List[str],
    gputouse: int = 0,
    filter: bool = True,
) -> (List[str], str):
    """
    DLC analyze videos or a batch of videos with the same file extension. will use the 0th paths extension for encoding
    :param config: the directory containing the config.yaml file
    :param paths: the paths to the videos to be analyzed
    :param gputouse: the CUDA capable Nvidia GPU to use for inference. If not set GPU inference will be disabled
    :param filter: if set true the data will be filtered
    :param min_confidence: value between 0 and 1 the minimum confidence for data when filtering. any data below
     min_confidence will be discarded
    :return: h5, model_slug: h5: a list of the h5 paths from the analysis, model_slug: the name of then DLC model in the
     h5 file
    """
    cfg = os.path.join(config, "config.yaml")
    _, vidtype = os.path.splitext(paths[0])
    dest, _ = os.path.split(paths[0])
    if gputouse >= 0:
        model_slug = deeplabcut.analyze_videos(
            cfg,
            paths,
            videotype=vidtype,
            destfolder=dest,
            gputouse=gputouse,
            save_as_csv=True,
            TFGPUinference=True,
        )
    else:
        model_slug = deeplabcut.analyze_videos(
            cfg,
            paths,
            videotype=vidtype,
            destfolder=dest,
            save_as_csv=True,
            TFGPUinference=False,
        )
    h5 = []
    if filter:
        deeplabcut.filterpredictions(cfg, paths, videotype=vidtype)
        for path in paths:
            h5.append(
                os.path.join(
                    dest,
                    os.path.splitext(os.path.split(path)[1])[0] + model_slug + "_filtered" + ".h5",
                )
            )
    info("analysis done")
    return h5, model_slug
