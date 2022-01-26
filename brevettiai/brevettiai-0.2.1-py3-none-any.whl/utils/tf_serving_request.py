# Utility tool for getting a prediction

import argparse
import json
import logging
import time
from base64 import b64encode
from tkinter import filedialog
import matplotlib.pyplot as plt
import cv2
import numpy as np

import requests

log = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', help='Tensorflow serving ip', default="localhost")
    parser.add_argument('--port', help='Tensorflow serving port', default=18501)
    parser.add_argument('--model', help='model name', required=True)
    parser.add_argument('--version', help='model version', required=False)
    parser.add_argument('--image', help='path to image', required=False)
    parser.add_argument('--show', help='show image', action='store_true')
    parser.add_argument('--repeat', help='repeat prediction n times', type=int, default=1)
    parser.add_argument('--token', help='Bearer token', default='')
    parser.add_argument('--resize', help='Resize image to the following size', default='')

    args, unparsed = parser.parse_known_args()
    return args, unparsed


def tf_serving_request(ip, port, version, model, images, repeat=1, show=False, token=None, resize='', **kwargs):

    apiinfo = dict(ip=ip, port=port, model=model, version=version)
    if version is not None:
        url = "http://{ip}:{port}/v1/models/{model}/versions/{version}:predict".format(**apiinfo)
    else:
        url = "http://{ip}:{port}/v1/models/{model}".format(**apiinfo)

    headers = {
        "Content-Type": "application/json",
        "Holder-Nr": "10"
    }
    if token is not None:
        headers["Authorization"] = "Bearer {}".format(token)

    ts = []
    for image in images:
        log.info("{} -> {}".format(image, url))

        img = cv2.imread(image, -1)
        if resize:
            img = cv2.resize(img, tuple(map(int, resize.split(","))), cv2.INTER_LINEAR)
        success, imgbuffer = cv2.imencode('.bmp', img)

        payload = json.dumps({
            "instances": [{
                "image_bytes": {
                    "b64": b64encode(imgbuffer).decode("utf-8")
                }
            }]
        }).encode()
        n_left = repeat

        while n_left != 0:

            try:
                tstart = time.time()
                response = requests.post(url, data=payload, headers=headers, timeout=10)
                tend = time.time()
                dt = 1000 * (tend - tstart)
                ts.append(dt)
            except Exception as e:
                print("Exception in request")
                continue

            log.info(json.dumps(response.json(), indent=2))
            log.info("Prediction time: %1.1fms" % dt)

            if show:
                predictions = response.json()['predictions']

                try:
                    x_ = img
                    for roi in predictions[0].get('attention_locations', []):
                        roi = np.array(roi)*np.array(x_.shape)[[1,0,1,0]]
                        roi = roi.astype(np.int)
                        cv2.rectangle(x_, tuple(roi[:2]), tuple(roi[2:]), 255, 2)
                    plt.figure(str(image))
                    plt.imshow(x_)
                    key = next(x for x in predictions[0].keys() if "---" in x)
                    plt.title(predictions[0][key])
                    plt.show(block=False)
                    plt.pause(0.2)
                except:
                    pass

            n_left -= 1

    log.info("Average prediction time %1.3fms" % np.array(ts).mean())

    if show:
        plt.show()

if __name__ == "__main__":
    args, _ = parse_args()
    logging.basicConfig(level=logging.INFO)

    image = args.image
    if image is None:
        images = filedialog.askopenfilenames(title='Please select an image')
        pass
    else:
        images = [image]

    tf_serving_request(images=images, **args.__dict__)
    a = 1+1
