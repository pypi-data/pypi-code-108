# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

""" Utility functions
    Note: This code is mainly adapted from https://github.com/ultralytics/yolov5/blob/master/utils/general.py
"""

import glob
import math
import os
import random
import time
from typing import Any, List, cast

import cv2
import numpy as np
import torch
import torch.nn as nn
import torchvision
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from torch.nn.modules.loss import _Loss
from torch.tensor import Tensor

from .torch_utils import torch_init_seeds

logger = get_logger(__name__)


# TODO RK: split this file in multiple smaller ones


def init_seeds(seed=0):
    """Set randomization seed

    :param seed: randomization seed
    :type seed: int
    """
    random.seed(seed)
    np.random.seed(seed)
    torch_init_seeds(seed=seed)


def check_img_size(img_size, s=32):
    """Verify img_size is a multiple of stride s

    :param img_size: randomization seed
    :type img_size: int
    :param s: stride
    :type s: int
    :return: new_size which is a multiple of stride s
    :rtype: int
    """
    new_size = make_divisible(img_size, int(s))  # ceil gs-multiple
    if new_size != img_size:
        logger.info("[WARNING: --img-size {} must be multiple of max stride {}, updating to {}]".format(
            img_size, s, new_size))
    return new_size


def check_anchor_order(m):
    """Check anchor order against stride order for YOLOv5 Detect() module m, and correct if necessary

    :param m: Detect() module
    :type m: <class 'azureml.automl.dnn.vision.object_detection_yolo.models.yolo.Detect'>
    """
    a = m.anchor_grid.prod(-1).view(-1)  # anchor area
    da = a[-1] - a[0]  # delta a
    ds = m.stride[-1] - m.stride[0]  # delta s
    if da.sign() != ds.sign():  # same order
        m.anchors[:] = m.anchors.flip(0)
        m.anchor_grid[:] = m.anchor_grid.flip(0)


def check_file(file):
    """Searches for file if not found locally

    :param file: File to find it's existence
    :type file: string
    :return: found file
    :rtype: string
    """
    if os.path.isfile(file):
        return file
    else:
        files = glob.glob('./**/' + file, recursive=True)  # find file
        assert len(files), 'File Not Found: %s' % file  # assert file was found
        return files[0]  # return first file if multiple found


def make_divisible(x, divisor):
    """Returns x evenly divisble by divisor

    :param x: value to check whether it is evenly divisble by divisor
    :type x: int
    :param divisor: divisor
    :type divisor: int
    :return: new value which is divisble by the divisor
    :rtype: int
    """
    return math.ceil(x / divisor) * divisor


def xyxy2xywh(x):
    """Convert nx4 boxes from [x1, y1, x2, y2] to [x, y, w, h] where xy1=top-left, xy2=bottom-right

    :param x: bbox coordinates in [x1, y1, x2, y2]
    :type x: <class 'numpy.ndarray'> or torch.Tensor
    :return: new bbox coordinates in [x center, y center, w, h]
    :rtype: <class 'numpy.ndarray'> or torch.Tensor
    """
    y = torch.zeros_like(x) if isinstance(x, torch.Tensor) else np.zeros_like(x)
    y[:, 0] = (x[:, 0] + x[:, 2]) / 2  # x center
    y[:, 1] = (x[:, 1] + x[:, 3]) / 2  # y center
    y[:, 2] = x[:, 2] - x[:, 0]  # width
    y[:, 3] = x[:, 3] - x[:, 1]  # height
    return y


def xywh2xyxy(x):
    """Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right

    :param x: bbox coordinates in [x center, y center, w, h]
    :type x: <class 'numpy.ndarray'> or torch.Tensor
    :return: new bbox coordinates in [x1, y1, x2, y2]
    :rtype: <class 'numpy.ndarray'> or torch.Tensor
    """
    y = torch.zeros_like(x) if isinstance(x, torch.Tensor) else np.zeros_like(x)
    y[:, 0] = x[:, 0] - x[:, 2] / 2  # top left x
    y[:, 1] = x[:, 1] - x[:, 3] / 2  # top left y
    y[:, 2] = x[:, 0] + x[:, 2] / 2  # bottom right x
    y[:, 3] = x[:, 1] + x[:, 3] / 2  # bottom right y
    return y


def clip_coords(boxes, img_shape):
    """Clip bounding xyxy bounding boxes to image shape (height, width)

    :param boxes: bbox
    :type boxes: <class 'torch.Tensor'>
    :return: img_shape: image shape
    :rtype: img_shape: <class 'tuple'>: (height, width)
    """
    boxes[:, 0].clamp_(0, img_shape[1])  # x1
    boxes[:, 1].clamp_(0, img_shape[0])  # y1
    boxes[:, 2].clamp_(0, img_shape[1])  # x2
    boxes[:, 3].clamp_(0, img_shape[0])  # y2


def unpad_bbox(boxes, img_shape, pad):
    """Correct bbox coordinates by removing the padded area from letterbox image

    :param boxes: bbox absolute coordinates from prediction
    :type boxes: <class 'torch.Tensor'>
    :param img_shape: image shape
    :type img_shape: <class 'tuple'>: (height, width)
    :param pad: pad used in letterbox image for inference
    :type pad: <class 'tuple'>: (width, height)
    :return: (unpadded) image height and width
    :rtype: <class 'tuple'>: (height, width)
    """
    dw, dh = pad
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    img_width = img_shape[1] - (left + right)
    img_height = img_shape[0] - (top + bottom)

    if boxes is not None:
        boxes[:, 0] -= left
        boxes[:, 1] -= top
        boxes[:, 2] -= left
        boxes[:, 3] -= top
        clip_coords(boxes, (img_height, img_width))

    return img_height, img_width


def bbox_iou(box1, box2, x1y1x2y2=True, GIoU=False, DIoU=False, CIoU=False):
    """Returns the intersection of union of box1 to box2.

    :param box1: bbox in (Tensor[4, N]), 4 for the box coordinates and N for multiple bboxes
    :type box1: <class 'torch.Tensor'>
    :param box2: bbox in (Tensor[N, 4])
    :type box2: <class 'torch.Tensor'>
    :param x1y1x2y2: is the box coordinate in x1y1x2y2
    :type x1y1x2y2: bool
    :param GIoU: Generalized IoU https://arxiv.org/pdf/1902.09630.pdf
    :type GIoU: bool
    :param DIoU: Distance IoU https://arxiv.org/abs/1911.08287v1
    :type DIoU: bool
    :param CIoU: Complete IoU https://arxiv.org/abs/1911.08287v1
    :type CIoU: bool
    :return: IoU of box1 to box2 in (Tensor[N])
    :rtype: <class 'torch.Tensor'>
    """
    box2 = box2.t()

    # Get the coordinates of bounding boxes
    if x1y1x2y2:  # x1, y1, x2, y2 = box1
        b1_x1, b1_y1, b1_x2, b1_y2 = box1[0], box1[1], box1[2], box1[3]
        b2_x1, b2_y1, b2_x2, b2_y2 = box2[0], box2[1], box2[2], box2[3]
    else:  # transform from xywh to xyxy
        b1_x1, b1_x2 = box1[0] - box1[2] / 2, box1[0] + box1[2] / 2
        b1_y1, b1_y2 = box1[1] - box1[3] / 2, box1[1] + box1[3] / 2
        b2_x1, b2_x2 = box2[0] - box2[2] / 2, box2[0] + box2[2] / 2
        b2_y1, b2_y2 = box2[1] - box2[3] / 2, box2[1] + box2[3] / 2

    # Intersection area
    inter = (torch.min(b1_x2, b2_x2) - torch.max(b1_x1, b2_x1)).clamp(0) * \
            (torch.min(b1_y2, b2_y2) - torch.max(b1_y1, b2_y1)).clamp(0)

    # Union Area
    w1, h1 = b1_x2 - b1_x1, b1_y2 - b1_y1
    w2, h2 = b2_x2 - b2_x1, b2_y2 - b2_y1
    union = (w1 * h1 + 1e-16) + w2 * h2 - inter

    iou = inter / union  # iou
    if GIoU or DIoU or CIoU:
        cw = torch.max(b1_x2, b2_x2) - torch.min(b1_x1, b2_x1)  # convex (smallest enclosing box) width
        ch = torch.max(b1_y2, b2_y2) - torch.min(b1_y1, b2_y1)  # convex height
        if GIoU:
            c_area = cw * ch + 1e-16  # convex area
            return iou - (c_area - union) / c_area  # GIoU
        if DIoU or CIoU:
            # convex diagonal squared
            c2 = cw ** 2 + ch ** 2 + 1e-16
            # centerpoint distance squared
            rho2 = ((b2_x1 + b2_x2) - (b1_x1 + b1_x2)) ** 2 / 4 + ((b2_y1 + b2_y2) - (b1_y1 + b1_y2)) ** 2 / 4
            if DIoU:
                return iou - rho2 / c2  # DIoU
            elif CIoU:  # https://github.com/Zzh-tju/DIoU-SSD-pytorch/blob/master/utils/box/box_utils.py#L47
                v = (4 / math.pi ** 2) * torch.pow(torch.atan(w2 / h2) - torch.atan(w1 / h1), 2)
                with torch.no_grad():
                    alpha = v / (1 - iou + v)
                return iou - (rho2 / c2 + v * alpha)  # CIoU

    return iou


def box_iou(box1, box2):
    """Return intersection-over-union (Jaccard index) of boxes.
    Both sets of boxes are expected to be in (x1, y1, x2, y2) format.
    https://github.com/pytorch/vision/blob/master/torchvision/ops/boxes.py

    :param box1: bbox in (Tensor[N, 4]), N for multiple bboxes and 4 for the box coordinates
    :type box1: <class 'torch.Tensor'>
    :param box2: bbox in (Tensor[M, 4]), M is for multiple bboxes
    :type box2: <class 'torch.Tensor'>
    :return: iou of box1 to box2 in (Tensor[N, M]), the NxM matrix containing the pairwise
            IoU values for every element in boxes1 and boxes2
    :rtype: <class 'torch.Tensor'>
    """

    def box_area(box):
        # box = 4xn
        return (box[2] - box[0]) * (box[3] - box[1])

    area1 = box_area(box1.t())
    area2 = box_area(box2.t())

    # inter(N,M) = (rb(N,M,2) - lt(N,M,2)).clamp(0).prod(2)
    inter = (torch.min(box1[:, None, 2:], box2[:, 2:]) - torch.max(box1[:, None, :2], box2[:, :2])).clamp(0).prod(2)
    return inter / (area1[:, None] + area2 - inter)  # iou = inter / (area1 + area2 - inter)


def wh_iou(wh1, wh2):
    """Returns the nxm IoU matrix. wh1 is nx2, wh2 is mx2

    :param wh1: width and height of bbox in (Tensor[N, 2])
    :type wh1: <class 'torch.Tensor'>
    :param wh2: width and height of bbox in (Tensor[M, 2])
    :type wh2: <class 'torch.Tensor'>
    :return: iou of wh1 to wh2 in (Tensor[N, M]), the NxM matrix containing the pairwise
            IoU values for every element in wh1 and wh2
    :rtype: <class 'torch.Tensor'>
    """
    wh1 = wh1[:, None]  # [N,1,2]
    wh2 = wh2[None]  # [1,M,2]
    inter = torch.min(wh1, wh2).prod(2)  # [N,M]
    return inter / (wh1.prod(2) + wh2.prod(2) - inter)  # iou = inter / (area1 + area2 - inter)


class FocalLoss(nn.Module):
    """
    Wraps focal loss around existing loss_fcn(), i.e. criteria = FocalLoss(nn.BCEWithLogitsLoss(), gamma=1.5)
    """

    def __init__(self, loss_fcn: _Loss, gamma: float = 1.5, alpha: float = 0.25) -> None:
        """
        :param loss_fcn:
        :type loss_fcn:
        :param gamma:
        :type gamma: float
        :param alpha:
        :type alpha: float
        """
        super(FocalLoss, self).__init__()
        self.loss_fcn = loss_fcn  # must be nn.BCEWithLogitsLoss()
        self.gamma = gamma
        self.alpha = alpha
        self.reduction = loss_fcn.reduction
        self.loss_fcn.reduction = 'none'  # required to apply FL to each element

    def forward(self, pred, true):
        """ forward function """
        loss = self.loss_fcn(pred, true)
        # p_t = torch.exp(-loss)
        # loss *= self.alpha * (1.000001 - p_t) ** self.gamma  # non-zero power for gradient stability

        # TF implementation https://github.com/tensorflow/addons/blob/v0.7.1/tensorflow_addons/losses/focal_loss.py
        pred_prob = torch.sigmoid(pred)  # prob from logits
        p_t = true * pred_prob + (1 - true) * (1 - pred_prob)
        alpha_factor = true * self.alpha + (1 - true) * (1 - self.alpha)
        modulating_factor = (1.0 - p_t) ** self.gamma
        loss *= alpha_factor * modulating_factor

        if self.reduction == 'mean':
            return loss.mean()
        elif self.reduction == 'sum':
            return loss.sum()
        else:  # 'none'
            return loss


def smooth_BCE(eps=0.1):
    """ Class label smoothing https://arxiv.org/pdf/1902.04103.pdf eqn 3
    https://github.com/ultralytics/yolov3/issues/238#issuecomment-598028441

    :param eps: small constant epsilon
    :type eps: float
    :return: positive and negative label smoothing smoothing BCE targets
    :rtype: float
    """
    return 1.0 - 0.5 * eps, 0.5 * eps


def compute_loss(p, targets, model):
    """ Compute loss

    :param p: predictions
    :type p: <class 'list'>
    :param targets: ground-truth bbox in (Tensor[N, 6]), 6 for (image index, target class, x center, y center, w, h)
    :type targets: <class 'torch.Tensor'>
    :param model: yolo model
    :type model: <class 'azureml.automl.dnn.vision.object_detection_yolo.models.yolo.Model'>
    :return: loss * batch size and (box loss, objectness loss, classification loss, sum of all three losses)
    :rtype: <class 'torch.Tensor'> and <class 'torch.Tensor'>
    """
    ft = torch.cuda.FloatTensor if p[0].is_cuda else torch.Tensor
    lcls, lbox, lobj = ft([0]), ft([0]), ft([0])
    tcls, tbox, indices, anchors = build_targets(p, targets, model)  # targets
    h = model.hyp  # hyperparameters
    gr = h['gr']
    red = 'mean'  # Loss reduction (sum or mean)

    # Define criteria
    BCEcls = nn.BCEWithLogitsLoss(pos_weight=ft([h['cls_pw']]), reduction=red)
    BCEobj = nn.BCEWithLogitsLoss(pos_weight=ft([h['obj_pw']]), reduction=red)

    cp, cn = smooth_BCE(eps=0.0)

    # focal loss
    g = h['fl_gamma']  # focal loss gamma
    if g > 0:
        BCEcls, BCEobj = FocalLoss(BCEcls, g), FocalLoss(BCEobj, g)

    # per output
    nt = 0  # number of targets
    np = len(p)  # number of outputs
    balance = [1.0, 1.0, 1.0]
    for i, pi in enumerate(p):  # layer index, layer predictions
        b, a, gj, gi = indices[i]  # image, anchor, gridy, gridx
        tobj = torch.zeros_like(pi[..., 0])  # target obj

        nb = b.shape[0]  # number of targets
        if nb:
            nt += nb  # cumulative targets
            ps = pi[b, a, gj, gi]  # prediction subset corresponding to targets

            # GIoU
            pxy = ps[:, :2].sigmoid() * 2. - 0.5
            pwh = (ps[:, 2:4].sigmoid() * 2) ** 2 * anchors[i]
            pbox = torch.cat((pxy, pwh), 1)  # predicted box
            giou = bbox_iou(pbox.t(), tbox[i], x1y1x2y2=False, GIoU=True)  # giou(prediction, target)
            lbox += (1.0 - giou).sum() if red == 'sum' else (1.0 - giou).mean()  # giou loss

            # Obj
            tobj[b, a, gj, gi] = (1.0 - gr) + gr * giou.detach().clamp(0).type(tobj.dtype)  # giou ratio

            # Class
            if model.nc > 1:  # cls loss (only if multiple classes)
                t = torch.full_like(ps[:, 5:], cn)  # targets
                t[range(nb), tcls[i]] = cp
                lcls += BCEcls(ps[:, 5:], t)  # BCE

        lobj += BCEobj(pi[..., 4], tobj) * balance[i]  # obj loss

    s = 3 / np  # output count scaling
    lbox *= h['giou'] * s
    lobj *= h['obj'] * s
    lcls *= h['cls'] * s
    bs = tobj.shape[0]  # batch size
    if red == 'sum':
        g = 3.0  # loss gain
        lobj *= g / bs
        if nt:
            lcls *= g / nt / model.nc
            lbox *= g / nt

    loss = lbox + lobj + lcls
    return loss * bs, torch.cat((lbox, lobj, lcls, loss)).detach()


def build_targets(p, targets, model):
    """ Build targets for compute_loss(), input targets(image,class,x,y,w,h)

    :param p: predictions
    :type p: <class 'list'>
    :param targets: ground-truth bbox in (Tensor[N, 6]), 6 for (image index, target class, x center, y center, w, h)
    :type targets: <class 'torch.Tensor'>
    :param model: yolo model
    :type model: <class 'azureml.automl.dnn.vision.object_detection_yolo.models.yolo.Model'>
    :return: target classes, target boxes, indices, anchors
    :rtype: <class 'list'>, <class 'list'>, <class 'list'>, <class 'list'>
    """
    det = model.module.model[-1] if type(model) in (nn.parallel.DataParallel, nn.parallel.DistributedDataParallel) \
        else model.model[-1]  # Detect() module
    na, nt = det.na, targets.shape[0]  # number of anchors, targets
    tcls, tbox, indices, anch = [], [], [], []
    gain = torch.ones(6, device=targets.device)  # normalized to gridspace gain
    off = torch.tensor([[1, 0], [0, 1], [-1, 0], [0, -1]], device=targets.device).float()  # overlap offsets
    at = torch.arange(na).view(na, 1).repeat(1, nt)  # anchor tensor, same as .repeat_interleave(nt)

    style = 'rect4'
    for i in range(det.nl):
        anchors = det.anchors[i]
        gain[2:] = torch.tensor(p[i].shape)[[3, 2, 3, 2]]  # xyxy gain

        # Match targets to anchors
        a: Any = []
        t, offsets = targets * gain, 0
        if nt:
            r = t[None, :, 4:6] / anchors[:, None]  # wh ratio
            j = torch.max(r, 1. / r).max(2)[0] < model.hyp['anchor_t']  # compare
            a, t = at[j], t.repeat(na, 1, 1)[j]  # filter

            # overlaps
            g = 0.5  # offset
            gxy = t[:, 2:4]  # grid xy
            z = torch.zeros_like(gxy)
            if style == 'rect2':
                j, k = ((gxy % 1. < g) & (gxy > 1.)).T
                a, t = torch.cat((a, a[j], a[k]), 0), torch.cat((t, t[j], t[k]), 0)
                offsets = cast(int, torch.cat((z, z[j] + off[0], z[k] + off[1]), 0) * g)
            elif style == 'rect4':
                j, k = ((gxy % 1. < g) & (gxy > 1.)).T
                l, m = ((gxy % 1. > (1 - g)) & (gxy < (gain[[2, 3]] - 1.))).T
                a, t = torch.cat((a, a[j], a[k], a[l], a[m]), 0), \
                    torch.cat((t, t[j], t[k], t[l], t[m]), 0)
                offsets = cast(int, torch.cat((z, z[j] + off[0], z[k] + off[1], z[l] + off[2], z[m] + off[3]), 0) * g)

        # Define
        b, c = t[:, :2].long().T  # image, class
        gxy = t[:, 2:4]  # grid xy
        gwh = t[:, 4:6]  # grid wh
        gij = (gxy - offsets).long()
        gi, gj = gij.T  # grid xy indices

        # Append
        indices.append((b, a, gj, gi))  # image, anchor, grid indices
        tbox.append(torch.cat((gxy - gij, gwh), 1))  # box
        anch.append(anchors[a])  # anchors
        tcls.append(c)  # class

    return tcls, tbox, indices, anch


def non_max_suppression(prediction, conf_thres=0.1, iou_thres=0.6, multi_label=False, merge=False,
                        classes=None, agnostic=False):
    """ Performs per-class Non-Maximum Suppression (NMS) on inference results

    :param prediction: predictions
    :type prediction: <class 'torch.Tensor'>
    :param conf_thres: confidence threshold
    :type conf_thres: float
    :param iou_thres: IoU threshold
    :type iou_thres: float
    :param multi_label: enable to have multiple labels in each box?
    :type multi_label: bool
    :param merge: Merge NMS (boxes merged using weighted mean)
    :type merge: bool
    :param classes: specific target class
    :type classes:
    :param agnostic: enable class agnostic NMS?
    :type agnostic: bool
    :return: detections with shape: nx6 (x1, y1, x2, y2, conf, cls)
    :rtype: <class 'list'>
    """
    if prediction.dtype is torch.float16:
        prediction = prediction.float()  # to FP32

    nc = prediction[0].shape[1] - 5  # number of classes
    xc = prediction[..., 4] > conf_thres  # candidates

    # min_wh = 2
    max_wh = 4096  # (pixels) maximum box width and height
    max_det = 300  # maximum number of detections per image
    time_limit = 10.0  # seconds to quit after
    redundant = True  # require redundant detections
    if multi_label and nc < 2:
        multi_label = False  # multiple labels per box (adds 0.5ms/img)

    t = time.time()
    output = [None] * prediction.shape[0]
    for xi, x in enumerate(prediction):  # image index, image inference
        # Apply constraints
        # x[((x[..., 2:4] < min_wh) | (x[..., 2:4] > max_wh)).any(1), 4] = 0  # width-height
        x = x[xc[xi]]  # confidence

        # If none remain process next image
        if not x.shape[0]:
            continue

        # Compute conf
        x[:, 5:] *= x[:, 4:5]  # conf = obj_conf * cls_conf

        # Box (center x, center y, width, height) to (x1, y1, x2, y2)
        box = xywh2xyxy(x[:, :4])

        # Detections matrix nx6 (xyxy, conf, cls)
        if multi_label:
            i, j = (x[:, 5:] > conf_thres).nonzero().t()
            x = torch.cat((box[i], x[i, j + 5, None], j[:, None].float()), 1)
        else:  # best class only
            conf, j = x[:, 5:].max(1, keepdim=True)
            x = torch.cat((box, conf, j.float()), 1)[conf.view(-1) > conf_thres]

        # Filter by class
        if classes:
            x = x[(x[:, 5:6] == torch.tensor(classes, device=x.device)).any(1)]

        # Apply finite constraint
        # if not torch.isfinite(x).all():
        #     x = x[torch.isfinite(x).all(1)]

        # If none remain process next image
        n = x.shape[0]  # number of boxes
        if not n:
            continue

        # Sort by confidence
        # x = x[x[:, 4].argsort(descending=True)]

        # Batched NMS
        c = x[:, 5:6] * (0 if agnostic else max_wh)  # classes
        boxes, scores = x[:, :4] + c, x[:, 4]  # boxes (offset by class), scores
        i = torchvision.ops.boxes.nms(boxes, scores, iou_thres)
        if i.shape[0] > max_det:  # limit detections
            i = i[:max_det]
        if merge and (1 < n < 3E3):
            try:  # update boxes as boxes(i,4) = weights(i,n) * boxes(n,4)
                iou = box_iou(boxes[i], boxes) > iou_thres  # iou matrix
                weights = iou * scores[None]  # box weights
                x[i, :4] = torch.mm(weights, x[:, :4]).float() / weights.sum(1, keepdim=True)  # merged boxes
                if redundant:
                    i = i[iou.sum(1) > 1]  # require redundancy
            except Exception:  # possible CUDA error https://github.com/ultralytics/yolov3/issues/1139
                logger.info("[WARNING: possible CUDA error ({} {} {} {})]".format(x, i, x.shape, i.shape))
                pass

        output[xi] = x[i]
        if (time.time() - t) > time_limit:
            break  # time limit exceeded

    return output


def load_image(path, img_size, augment, ignore_data_errors):
    """ loads 1 image from given path, returns img, original hw, resized hw

    :param path: image path
    :type path: str
    :param img_size: image size
    :type img_size: int
    :param augment: if we apply augmentation
    :type augment: bool
    :param ignore_data_errors: flag to specify if an error occurring when loading an image is silently ignored
    :type ignore_data_errors: bool
    :return: image, (original image height, width), (resized image height, width)
    :rtype: <class 'numpy.ndarray'>, <class 'tuple'>, <class 'tuple'>
    """

    from azureml.automl.dnn.vision.common.utils import _read_image
    img = _read_image(ignore_data_errors=ignore_data_errors,
                      image_url=path,
                      use_cv2=True)
    if img is None:
        return None, (None, None), (None, None)

    h0, w0 = img.shape[:2]  # orig hw
    r = img_size / max(h0, w0)  # resize image to img_size
    if r != 1:  # always resize down, only resize up if training with augmentation
        interp = cv2.INTER_AREA if r < 1 and not augment else cv2.INTER_LINEAR
        img = cv2.resize(img, (int(w0 * r), int(h0 * r)), interpolation=interp)
    return img, (h0, w0), img.shape[:2]  # img, hw_original, hw_resized


# TODO RK: replace settings with exact params
def load_mosaic(index, image_urls, img_size, mosaic_border, labels, annotations, augment,
                affine_settings, ignore_data_errors):
    """ Loads images in a mosaic.

    :param index: image index
    :type index: int
    :param image_urls: dictionary with index and corresponding path
    :type image_urls: dict
    :param img_size: image size
    :type img_size: int
    :param mosaic_border: TODO
    :type mosaic_border: TODO
    :param labels: list of labels
    :type labels: list
    :param annotations: Dictionary of image_url to annotations (List[ObjectAnnotation]) for the image
    :type annotations: dict
    :param augment: if we apply augmentation
    :type augment: bool
    :param affine_settings: dictionary with parameters for the affine transformation
    :type affine_settings: dict
    :param ignore_data_errors: flag to specify if an error occurring when loading an image is silently ignored
    :type ignore_data_errors: bool
    :return: a mosaiced image (based on 4 images), adjusted labels for the mosaiced image,
             list of iscrowd corresponding to adjusted labels for the mosaiced image
    :rtype: <class 'numpy.ndarray'>, <class 'numpy.ndarray'>, <class 'list'>
    """
    labels4: List[Any] = []
    iscrowd4 = []
    s = img_size
    yc, xc = [int(random.uniform(-x, 2 * s + x)) for x in mosaic_border]  # mosaic center x, y
    indices = [index] + [random.randint(0, len(labels) - 1) for _ in range(3)]  # 3 additional image indices
    for i, index in enumerate(indices):
        # Load image
        img, _, (h, w) = load_image(image_urls[index], img_size, augment, ignore_data_errors)
        if img is None:
            return None, None, None

        # place img in img4
        if i == 0:  # top left
            img4 = np.full((s * 2, s * 2, img.shape[2]), 114, dtype=np.uint8)  # base image with 4 tiles
            x1a, y1a, x2a, y2a = max(xc - w, 0), max(yc - h, 0), xc, yc  # xmin, ymin, xmax, ymax (large image)
            x1b, y1b, x2b, y2b = w - (x2a - x1a), h - (y2a - y1a), w, h  # xmin, ymin, xmax, ymax (small image)
        elif i == 1:  # top right
            x1a, y1a, x2a, y2a = xc, max(yc - h, 0), min(xc + w, s * 2), yc
            x1b, y1b, x2b, y2b = 0, h - (y2a - y1a), min(w, x2a - x1a), h
        elif i == 2:  # bottom left
            x1a, y1a, x2a, y2a = max(xc - w, 0), yc, xc, min(s * 2, yc + h)
            x1b, y1b, x2b, y2b = w - (x2a - x1a), 0, w, min(y2a - y1a, h)
        elif i == 3:  # bottom right
            x1a, y1a, x2a, y2a = xc, yc, min(xc + w, s * 2), min(s * 2, yc + h)
            x1b, y1b, x2b, y2b = 0, 0, min(w, x2a - x1a), min(y2a - y1a, h)

        img4[y1a:y2a, x1a:x2a] = img[y1b:y2b, x1b:x2b]  # img4[ymin:ymax, xmin:xmax]
        padw = x1a - x1b
        padh = y1a - y1b

        # Labels
        x = labels[index]
        current_labels = x.copy()
        if x.size > 0:  # Normalized xywh to pixel xyxy format
            current_labels[:, 1] = w * (x[:, 1] - x[:, 3] / 2) + padw
            current_labels[:, 2] = h * (x[:, 2] - x[:, 4] / 2) + padh
            current_labels[:, 3] = w * (x[:, 1] + x[:, 3] / 2) + padw
            current_labels[:, 4] = h * (x[:, 2] + x[:, 4] / 2) + padh
        labels4.append(current_labels)  # type List[Any]
        current_annotations = annotations[image_urls[index]]
        iscrowd4.extend([annotation.iscrowd for annotation in current_annotations])

    # Concat/clip labels
    if len(labels4):
        labels4 = np.concatenate(labels4, 0)
        labels4_tensor = cast(Any, labels4)
        # np.clip(labels4[:, 1:] - s / 2, 0, s, out=labels4[:, 1:])  # use with center crop
        np.clip(labels4_tensor[:, 1:], 0, 2 * s, out=labels4_tensor[:, 1:])  # use with random_affine

    # Augment
    img4, labels4, iscrowd4 = random_affine(img4, labels4, iscrowd4,
                                            degrees=affine_settings['degrees'],
                                            translate=affine_settings['translate'],
                                            scale=affine_settings['scale'],
                                            shear=affine_settings['shear'],
                                            border=mosaic_border)  # border to remove
    return img4, labels4, iscrowd4


def letterbox(img, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True):
    """ Resize image to a 32-pixel-multiple rectangle
    https://github.com/ultralytics/yolov3/issues/232

    :param img: an image
    :type img: <class 'numpy.ndarray'>
    :param new_shape: target shape in [height, width]
    :type new_shape: <class 'int'>
    :param color: color for pad area
    :type color: <class 'tuple'>
    :param auto: minimum rectangle
    :type auto: bool
    :param scaleFill: stretch the image without pad
    :type scaleFill: bool
    :param scaleup: scale up
    :type scaleup: bool
    :return: letterbox image, scale ratio, padded area in (width, height) in each side
    :rtype: <class 'numpy.ndarray'>, <class 'tuple'>, <class 'tuple'>
    """
    shape = img.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better test mAP)
        r = min(r, 1.0)

    # Compute padding
    ratio = r, r  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, 64), np.mod(dh, 64)  # wh padding
    elif scaleFill:  # stretch
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return img, ratio, (dw, dh)


def random_affine(img, targets=(), iscrowd=[], degrees=10, translate=.1, scale=.1, shear=10, border=(0, 0)):
    """ torchvision.transforms.RandomAffine(degrees=(-10, 10), translate=(.1, .1), scale=(.9, 1.1), shear=(-10, 10))
    https://medium.com/uruvideo/dataset-augmentation-with-random-homographies-a8f4b44830d4
    targets = [cls, xyxy]

    :param img: an image
    :type img: <class 'numpy.ndarray'>
    :param targets: target labels in nx5, 5 for (cls, x1, y1, x2, y2)
    :type targets: <class 'numpy.ndarray'>
    :param iscrowd: list of iscrowd corresponding to the targets
    :type iscrowd: <class 'list'>
    :param degrees: degrees
    :type degrees: float
    :param translate: translate
    :type translate: float
    :param scale: scale
    :type scale: float
    :param shear: shear
    :type shear: float
    :param border: border
    :type border: <class 'list'>
    :return: affined image, adjusted labels, adjusted iscrowd
    :rtype: <class 'numpy.ndarray'>, <class 'numpy.ndarray'>, <class 'list'>
    """
    height = img.shape[0] + border[0] * 2  # shape(h,w,c)
    width = img.shape[1] + border[1] * 2

    # Rotation and Scale
    R = np.eye(3)
    a = random.uniform(-degrees, degrees)
    # a += random.choice([-180, -90, 0, 90])  # add 90deg rotations to small rotations
    s = random.uniform(1 - scale, 1 + scale)
    # s = 2 ** random.uniform(-scale, scale)
    R[:2] = cv2.getRotationMatrix2D(angle=a, center=(img.shape[1] / 2, img.shape[0] / 2), scale=s)

    # Translation
    T = np.eye(3)
    T[0, 2] = random.uniform(-translate, translate) * img.shape[1] + border[1]  # x translation (pixels)
    T[1, 2] = random.uniform(-translate, translate) * img.shape[0] + border[0]  # y translation (pixels)

    # Shear
    S = np.eye(3)
    S[0, 1] = math.tan(random.uniform(-shear, shear) * math.pi / 180)  # x shear (deg)
    S[1, 0] = math.tan(random.uniform(-shear, shear) * math.pi / 180)  # y shear (deg)

    # Combined rotation matrix
    M = S @ T @ R  # ORDER IS IMPORTANT HERE!!
    if (border[0] != 0) or (border[1] != 0) or (M != np.eye(3)).any():  # image changed
        img = cv2.warpAffine(img, M[:2], dsize=(width, height), flags=cv2.INTER_LINEAR, borderValue=(114, 114, 114))

    # Transform label coordinates
    n = len(targets)
    if n:
        # warp points
        xy = np.ones((n * 4, 3))
        xy[:, :2] = targets[:, [1, 2, 3, 4, 1, 4, 3, 2]].reshape(n * 4, 2)  # x1y1, x2y2, x1y2, x2y1
        xy = (xy @ M.T)[:, :2].reshape(n, 8)

        # create new boxes
        x = xy[:, [0, 2, 4, 6]]
        y = xy[:, [1, 3, 5, 7]]
        xy = np.concatenate((x.min(1), y.min(1), x.max(1), y.max(1))).reshape(4, n).T

        # reject warped points outside of image
        xy[:, [0, 2]] = xy[:, [0, 2]].clip(0, width)
        xy[:, [1, 3]] = xy[:, [1, 3]].clip(0, height)
        w = xy[:, 2] - xy[:, 0]
        h = xy[:, 3] - xy[:, 1]
        area = w * h
        area0 = (targets[:, 3] - targets[:, 1]) * (targets[:, 4] - targets[:, 2])
        ar = np.maximum(w / (h + 1e-16), h / (w + 1e-16))  # aspect ratio
        i = (w > 2) & (h > 2) & (area / (area0 * s + 1e-16) > 0.2) & (ar < 20)

        targets = targets[i]
        targets[:, 1:5] = xy[i]
        iscrowd = np.array(iscrowd)
        iscrowd = iscrowd[i]
        iscrowd = iscrowd.tolist()

    return img, targets, iscrowd


def convert_to_yolo_labels(images, annotations, class2index):
    """ Convert original (AML) labels to yolo labels

    :param images: images
    :type images: <class 'list'>
    :param annotations: original labels in (class name, x1, y1, x2, y2)
    :type annotations: default dictionary (list)
    :param class2index: class name to index
    :type class2index: dictionary
    :return: yolo labels in (class index, x center, y center, w, h)
    :rtype: <class 'list'>
    """
    labels = [np.zeros((0, 5), dtype=np.float32)] * len(images)
    for i, img_fname in enumerate(images):
        label = []
        for box in annotations[img_fname]:
            bbox = box.bounding_box
            new_bbox = bbox.copy()
            new_bbox[0] = class2index[bbox[0]]
            new_bbox[1] = (bbox[1] + bbox[3]) / 2
            new_bbox[2] = (bbox[2] + bbox[4]) / 2
            new_bbox[3] = (bbox[3] - bbox[1])
            new_bbox[4] = (bbox[4] - bbox[2])
            label.append(new_bbox)  # xywh
        labels[i] = np.array(label, dtype=np.float32)
    return labels


def get_image(index, image_urls, img_size, all_labels, annotations, settings, is_train, ignore_data_errors):
    """Returns the image that corresponds to the given index. For training,
    it loads 4 images at a time in a mosaic.

    :param index: index of the images in the list
    :type index: int
    :param image_urls: list of image paths
    :type image_urls: list
    :param img_size: size of the image
    :type img_size: int
    :param all_labels: the list of all labels
    :type all_labels: list
    :param annotations: Dictionary of image_url to annotations (List[ObjectAnnotation]) for the image
    :type annotations: dict
    :param settings: additional settings to use
    :type settings: dict
    :param is_train: flag that indicates if it is training
    :type is_train: bool
    :param ignore_data_errors: flag to specify if an error occurring when loading an image is silently ignored
    :type ignore_data_errors: bool
    :return: tuple (Image, labels, image path)
    :rtype: tuple
    """

    mosaic = is_train
    augment = is_train
    mosaic_border = [-img_size // 2, -img_size // 2]

    if mosaic:
        # Load mosaic
        img, labels, iscrowd = load_mosaic(index, image_urls, img_size, mosaic_border, all_labels, annotations,
                                           augment, settings, ignore_data_errors)
        if img is None:
            return None, None, None

    else:
        # Load image
        img, (h0, w0), (h, w) = load_image(image_urls[index], img_size, augment, ignore_data_errors)
        if img is None:
            return None, None, None

        # Letterbox
        shape = img_size  # final letterboxed shape
        img, ratio, pad = letterbox(img, shape, auto=False, scaleup=augment)

        # Load labels
        labels = []
        x = all_labels[index]
        iscrowd = [annotation.iscrowd for annotation in annotations[image_urls[index]]]
        if x.size > 0:
            # Normalized xywh to pixel xyxy format
            labels = x.copy()
            labels[:, 1] = ratio[0] * w * (x[:, 1] - x[:, 3] / 2) + pad[0]  # pad width
            labels[:, 2] = ratio[1] * h * (x[:, 2] - x[:, 4] / 2) + pad[1]  # pad height
            labels[:, 3] = ratio[0] * w * (x[:, 1] + x[:, 3] / 2) + pad[0]
            labels[:, 4] = ratio[1] * h * (x[:, 2] + x[:, 4] / 2) + pad[1]

    if augment:
        # Augment imagespace
        if not mosaic:
            img, labels, iscrowd = random_affine(img, labels, iscrowd,
                                                 degrees=settings['degrees'],
                                                 translate=settings['translate'],
                                                 scale=settings['scale'],
                                                 shear=settings['shear'])

    object_areas = []
    nL = len(labels)  # number of labels
    if nL:
        object_areas = ((labels[:, 3] - labels[:, 1]) * (labels[:, 4] - labels[:, 2])).tolist()
        # convert xyxy to xywh
        labels[:, 1:5] = xyxy2xywh(labels[:, 1:5])

        # Normalize coordinates 0 - 1
        labels[:, [2, 4]] /= img.shape[0]  # height
        labels[:, [1, 3]] /= img.shape[1]  # width

    if augment:
        # random left-right flip
        lr_flip = True
        if lr_flip and random.random() < 0.5:
            img = np.fliplr(img)
            if nL:
                labels[:, 1] = 1 - labels[:, 1]

        # random up-down flip
        ud_flip = False
        if ud_flip and random.random() < 0.5:
            img = np.flipud(img)
            if nL:
                labels[:, 2] = 1 - labels[:, 2]

    labels_out = torch.zeros((nL, 6))
    if nL:
        labels_out[:, 1:] = torch.from_numpy(labels)

    # Convert
    img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
    (_, image_height, image_width) = img.shape
    img = np.ascontiguousarray(img)
    image_info = {
        "areas": object_areas, "iscrowd": iscrowd, "filename": image_urls[index],
        "height": image_height, "width": image_width
    }
    return torch.from_numpy(img), labels_out, image_info
