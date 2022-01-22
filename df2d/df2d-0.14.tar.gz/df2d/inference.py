import os
import re
import subprocess
from itertools import product
from typing import *

import matplotlib.pyplot as plt
import numpy as np
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from df2d.dataset import Drosophila2Dataset
from df2d.model import Drosophila2DPose
from df2d.parser import create_parser
from df2d.util import heatmap2points, pwd

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def download_weights(path):
    command = f"curl -L -o {path} https://www.dropbox.com/s/csgon8uojr3gdd9/sh8_front_j8.tar?dl=0"
    print("Downloading network weights.")
    os.makedirs(os.path.dirname(path))
    subprocess.run(command, shell=True)


def inference_folder(
    folder: str,
    load_f: Callable = lambda x: plt.imread(x),
    args: Optional[Dict] = {},
    return_heatmap: bool = False,
    return_confidence: bool = False,
    max_img_id: Optional[int] = None,
):
    """processes all the images under a folder.
        returns normalized coordinates in [0, 1].
    >>> from df2d.inference import inference_folder
    >>> points2d = inference_folder('/home/user/Desktop/DeepFly3D/data/test/')
    >>> points2d.shape
    >>>     (7, 16, 19, 2) # n_cameras, n_images, n_joints, 2
    """
    checkpoint_path = os.path.join(pwd(), "../weights/sh8_deepfly.tar")
    if not os.path.exists(checkpoint_path):
        download_weights(checkpoint_path)
    args_default = create_parser().parse_args("").__dict__
    args_default.update(args)

    model = Drosophila2DPose(checkpoint_path=checkpoint_path, **args_default).to(device)

    inp = path2inp(
        folder, max_img_id=max_img_id
    )  # extract list of images under the folder
    dat = DataLoader(Drosophila2Dataset(inp, load_f=load_f), batch_size=8)

    return inference(
        model, dat, return_heatmap=return_heatmap, return_confidence=return_confidence
    )


import pickle


def pr2inp(path: str) -> List[str]:
    """converts pose result file into inp format
    >>> pr2inp("/data/test/df3d/df3d_result.pkl")
    >>>     [("/data/test/0.jpg", [[0,0], [.5,.5]]), ("/data/test/1.jpg", [[0,0], [.5,.5]])]
    """
    img_list = list()
    points2d = pickle.load(open(path, "rb"))["points2d"]
    n_cameras, n_images = points2d.shape[0] - 1, points2d.shape[1] - 1

    for cid, imgid in product(range(n_cameras), range(n_images)):
        img_path = os.path.join(
            os.path.dirname(path),
            "../camera_{cid}_img_{imgid}.jpg".format(cid=cid, imgid=imgid),
        )

        # skip if pose is missing
        if np.all(points2d[cid, imgid] == 0):
            continue

        if points2d[cid, imgid, 0, 0] == 0:
            pts = points2d[cid, imgid][19:]
            pts[..., 1] = 1 - pts[..., 1]
        else:
            pts = points2d[cid, imgid][:19]

        img_list.append((img_path, pts))

    return img_list


def path2inp(path: str, max_img_id: Optional[int] = None) -> List[str]:
    """
    >>> path2inp("/data/test/")
    >>>     ["/data/test/0.jpg", "/data/test/1.jpg"]
    """
    pattern = re.compile(r'camera_\d*_img_\d*.(jpg|png)')
    img_list = [
        (os.path.join(path, p), np.zeros((19)))
        for p in os.listdir(path)
        if pattern.match(p)
    ]

    if max_img_id is not None:
        img_list = [img for img in img_list if parse_img_path(img[0])[1] <= max_img_id]

    return img_list


def inference(
    model: Drosophila2DPose,
    dataset: Drosophila2Dataset,
    return_heatmap: bool = False,
    return_confidence: bool = False,
) -> np.ndarray:
    res = list()
    res_conf = list()
    heatmap = list()
    for batch in tqdm(dataset):
        x, _, d = batch
        hm = model(x)
        points, conf = heatmap2points(hm)
        points = points.cpu().data.numpy()
        conf = conf.cpu().data.numpy()
        if return_heatmap:
            heatmap.append(hm.cpu().data.numpy())
        for idx in range(x.size(0)):
            path = d[0][idx]
            res.append([path, points[idx]])
            res_conf.append([path, conf[idx]])

    points2d = inp2np(res)
    conf = inp2np(res_conf)

    if not return_heatmap and not return_confidence:
        return points2d

    ret = [points2d]
    if return_heatmap:
        ret.append(np.concatenate(heatmap, axis=0))
    if return_confidence:
        ret.append(conf)

    return ret


def parse_img_path(name: str) -> Tuple[int, int]:
    """returns cid and img_id"""
    name = os.path.basename(name)
    match = re.match(r"camera_(\d+)_img_(\d+)", name.replace(".jpg", ""))
    if match is None:
        print(f'Cannot parse image {name}')
    return int(match[1]), int(match[2])
        


def inp2np(inp: List) -> np.ndarray:
    """converts a list representation into numpy array in format C x J x 2
    each list element is a tuple, where the first element is a path in the camera_{camid}_img_{img_id} format.
    second element is a numpy array
    """
    n_cameras = max([parse_img_path(p)[0] for (p, _) in inp]) + 1
    n_images = max([parse_img_path(p)[1] for (p, _) in inp]) + 1

    n_joints = inp[0][1].shape[0]
    n_dim = inp[0][1].shape[1]

    points2d = np.zeros((n_cameras, n_images + 1, n_joints, n_dim))

    for (path, pts) in inp:
        cid, imgid = parse_img_path(path)
        points2d[cid, imgid] = pts

    return points2d
