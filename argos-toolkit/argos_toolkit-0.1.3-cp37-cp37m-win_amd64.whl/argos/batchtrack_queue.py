# -*- coding: utf-8 -*-
# Author: Subhasis Ray <ray dot subhasis at gmail dot com>
# Created: 2020-07-15 5:00 PM
import os
from typing import Tuple
import sys
import logging
import threading
from functools import partial
import numpy as np
import cv2
import yaml
import time
import pandas as pd
import torch
import torch.multiprocessing as mp
import torch.backends.cudnn as cudnn
from yolact import Yolact
from yolact.data import config as yconfig
# This is actually yolact.utils
from yolact.utils.augmentations import FastBaseTransform
from yolact.layers import output_utils as oututils
import queue

logging.basicConfig(stream=sys.stdout,
                    format='%(asctime)s '
                           'p=%(processName)s[%(process)d] '
                           't=%(threadName)s[%(thread)d] '
                           '%(filename)s#%(lineno)d:%(funcName)s: '
                           '%(message)s',
                    level=logging.DEBUG)

try:
    mp.set_start_method('spawn')
except RuntimeError:
    pass


def load_config(filename):
    config = yconfig.cfg
    if filename == '':
        return
    with open(filename, 'r') as cfg_file:
        cfg = yaml.safe_load(cfg_file)
        for key, value in cfg.items():
            config.__setattr__(key, value)
        if 'mask_proto_debug' not in cfg:
            config.mask_proto_debug = False
    return config


def load_weights(filename, cuda):
    if filename == '':
        raise ValueError('Empty filename for network weights')
    tic = time.perf_counter_ns()
    with torch.no_grad():
        if cuda:
            cudnn.fastest = True
            torch.set_default_tensor_type('torch.cuda.FloatTensor')
        else:
            torch.set_default_tensor_type('torch.FloatTensor')
        # torch.set_default_tensor_type('torch.FloatTensor')
        ynet = Yolact()
        ynet.load_weights(filename, False)
        ynet.eval()
    toc = time.perf_counter_ns()
    logging.debug(f'Time to load weights: {1e-9 * (toc - tic)}')
    return ynet


def consume(in_queue: mp.Queue, out_queue: mp.Queue, weights_file: str,
            config_file: str,
            cuda: bool, score_threshold: float, top_k: int):
    """:returns (classes, scores, boxes)

    where `boxes` is an array of bounding boxes of detected objects in
    (xleft, ytop, width, height) format.

    `classes` is the class ids of the corresponding objects.

    `scores` are the computed class scores corresponding to the detected objects.
    Roughly high score indicates strong belief that the object belongs to
    the identified class.
    """
    config = load_config(config_file)
    ynet = load_weights(weights_file, cuda)
    while True:
        try:
            in_data = in_queue.get(timeout=1)
        except queue.Empty:
            logging.info('Input queue empty')
            continue
        if in_data is None:
            logging.info('Finishing')
            out_queue.put(None)
            return
        pos, image = in_data
        logging.debug(f'Received frame {pos}')
        if ynet is None:
            raise ValueError('Network not initialized')
        # Partly follows yolact eval.py
        tic = time.perf_counter_ns()
        with torch.no_grad():
            if cuda:
                image = torch.from_numpy(image).cuda().float()
            else:
                image = torch.from_numpy(image).float()
            batch = FastBaseTransform()(image.unsqueeze(0))
            preds = ynet(batch)
            image_gpu = image / 255.0
            h, w, _ = image.shape
            save = config.rescore_bbox
            config.rescore_bbox = True
            classes, scores, boxes, masks = oututils.postprocess(
                preds, w, h,
                visualize_lincomb=False,
                crop_masks=True,
                score_threshold=score_threshold)
            idx = scores.argsort(0, descending=True)[:top_k]
            # if self.config.eval_mask_branch:
            #     masks = masks[idx]
            classes, scores, boxes = [x[idx].cpu().numpy()
                                      for x in (classes, scores, boxes)]
            # Convert from top-left bottom-right format to
            # top-left, width, height format
            if len(boxes) > 0:
                boxes[:, 2:] = boxes[:, 2:] - boxes[:, :2]
            toc = time.perf_counter_ns()
            logging.debug('Time to process single _image: %f s',
                          1e-9 * (toc - tic))
            out_queue.put((pos, boxes))
            logging.debug(f'Sent bboxes for frame {pos}')


def read_frame(filename, queue, max_frames=None, num_consumers=1):
    video = cv2.VideoCapture(filename)
    if (video is None) or not video.isOpened():
        for ii in range(num_consumers):
            queue.put(None)
        return
    while True:
        ret, frame = video.read()
        frame_no = int(video.get(cv2.CAP_PROP_POS_FRAMES))
        if frame is None or (max_frames is not None and frame_no >= max_frames):
            video.release()
            del video
            for ii in range(num_consumers):
                queue.put(None)
            logging.info('Finished reading')
            return
        logging.debug('Read frame no %d', frame_no)
        queue.put((frame_no, frame))


def batch_track(video_file, output_file, config_file, weights_file, cuda,
                processes,
                score_threshold, top_k, max_frames=None):
    procs = []
    tic = time.perf_counter_ns()
    frame_queue = mp.Queue()
    bbox_queue = mp.Queue()
    procs.append(mp.Process(target=read_frame,
                            args=(
                            video_file, frame_queue, max_frames, processes)))
    for ii in range(processes):
        procs.append(mp.Process(target=consume, args=(frame_queue, bbox_queue,
                                                      weights_file, config_file,
                                                      cuda,
                                                      score_threshold, top_k)))
    toc = time.perf_counter_ns()
    logging.info(f'Time to initialize queues and procs: {1e-9 * (toc - tic)}')
    tic = time.perf_counter_ns()
    for proc in procs:
        proc.start()
    results = []
    proc_count = processes
    while proc_count > 0:
        try:
            ret = bbox_queue.get()
            if ret is None:
                proc_count -= 1
                continue
            results += [{'frame': ret[0], 'x': ret[1][ii, 0],
                         'y': ret[1][ii, 1],
                         'w': ret[1][ii, 2],
                         'h': ret[1][ii, 3]} for ii in
                        range(ret[1].shape[0])]
            logging.debug(f'Processed result for frame {ret[0]}')
        except queue.Empty:
            logging.debug('Queue empty. Wait for subprocs')
            continue
    for proc in procs:
        proc.join(1.0)
        if proc.is_alive():
            print(f'Process {proc.pid} still alive')
            proc.terminate()
    bbox_queue.close()
    bbox_queue.join_thread()
    frame_queue.close()
    frame_queue.join_thread()
    toc = time.perf_counter_ns()

    results = pd.DataFrame(results)
    results = results.sort_values(by='frame')

    logging.info(f'Processed {results.frame.max()} frames in '
                 f'{1e-9 * (toc - tic)} seconds.')
    if output_file.endswith('.csv'):
        results.to_csv(output_file, index=False)
    elif output_file.endswith(
            '.h5') or output_file.endswith('.hdf'):
        results.to_hdf(output_file, 'track')
    logging.info(f'Saved segmentation in {output_file}')


if __name__ == '__main__':
    config_file = 'C:/Users/raysu/Documents/src/argos_data/yolact_annotations/yolact_config.yaml'
    weights_file = 'C:/Users/raysu/Documents/src/argos_data/yolact_annotations/babylocust_resnet101_119999_240000.pth'
    cuda = False
    batch_track(
        video_file='C:/Users/raysu/Documents/src/argos_data/dump/2020_02_20_00270.avi',
        output_file='C:/Users/raysu/Documents/src/argos_data/dump/2020_02_20_00270.avi.parallel.track.csv',
        config_file=config_file,
        weights_file=weights_file,
        score_threshold=0.15, top_k=10, cuda=cuda, processes=10, max_frames=25)
