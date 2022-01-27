import cv2
import numpy as np
from kornia import losses
from kornia.utils import image_to_tensor
from scipy import ndimage

D_TYPE = np.float32

THRESHOLD = 1
WINDOWS_AREA = 1000 * 1000


def found_alpha_axis(img):
    return (np.expand_dims(img, axis=2) if len(img.shape) == 2 else img[..., :1]).astype(D_TYPE)


def found_alpha_channel(img):
    return (img if len(img.shape) == 2 else img[..., 0]).astype(D_TYPE)


def bounding_rect_area(chn_mask):
    sum_area = 0
    contours, hierarchy = cv2.findContours(chn_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for _, cnt in enumerate(contours):
        x, y, w, h = cv2.boundingRect(cnt)

        sum_area += w * h

    return sum_area


def calc_flaws_area(chn_mask):
    sum_area = 0
    contours, hierarchy = cv2.findContours(chn_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for _, cnt in enumerate(contours):
        sum_area += cv2.contourArea(cnt)

    return sum_area


def norm_to_heatmap(chn_norm):
    out_hvs = np.zeros((*(chn_norm.shape if len(chn_norm.shape) == 2 else chn_norm.shape[:2]), 3), np.uint8)
    out_hvs[..., 0] = (chn_norm * 120)[..., 0].astype(np.uint8)
    out_hvs[..., 1] = 172
    out_hvs[..., 2] = 230

    out_bgr = cv2.cvtColor(out_hvs, cv2.COLOR_HSV2BGR)

    return out_bgr


def eval_flaws_norm(gt, mark):
    chn_gt = found_alpha_axis(gt)
    chn_mask = found_alpha_axis(mark)

    chn_min = np.full(chn_mask.shape, dtype=D_TYPE, fill_value=-255)
    chn_max = np.full(chn_gt.shape, dtype=D_TYPE, fill_value=510)

    # 0 ~ 1
    chn_hvs = ((chn_gt - chn_mask) - chn_min) / chn_max

    return chn_hvs


def eval_heatmap(pred, target):
    chn_gt = found_alpha_axis(pred)
    chn_mask = found_alpha_axis(target)

    # -1 ~ 1
    img_flaws = chn_gt - chn_mask
    img_flaws[img_flaws < 0] *= -1

    return img_flaws.astype(np.uint8)


def eval_heatmap_error(pred, mark, result_mask=False, all_result=False):
    result = []

    chn_gt = found_alpha_axis(pred)
    chn_mask = found_alpha_axis(mark)

    # -1 ~ 1
    img_flaws = chn_gt - chn_mask
    loss_mse = np.mean(np.power(img_flaws, 2)) / 1000
    result.append(loss_mse)

    if result_mask or all_result:
        img_flaws[img_flaws < 0] *= -1
        flaws_output = img_flaws.copy().astype(np.uint8)

        result.append(flaws_output)

    if all_result:
        norm_mask = chn_mask / 255
        sum_mask = np.sum(norm_mask[chn_mask > THRESHOLD])

        h, w = img_flaws.shape[:2]
        area_image = h * w

        norm_flows = img_flaws / 255
        sum_flaws = np.sum(norm_flows[img_flaws > THRESHOLD])
        area_mask = bounding_rect_area(chn_mask)

        result.extend([sum_flaws, sum_mask, area_mask, area_image])

    return result


def eval_mse_loss(pred, target):
    chn_gt = found_alpha_axis(pred)
    chn_mask = found_alpha_axis(target)

    # -1 ~ 1
    img_flaws = (chn_gt - chn_mask) / 255
    return np.mean(np.power(img_flaws, 2)).item()


def eval_gradient_error(pred, target):
    """
    Error measure with Gradient
    """

    # alpha matte的归一化梯度，标准差=1.4，1阶高斯导数的卷积
    predict_grad = ndimage.filters.gaussian_filter(pred.astype(float), 1.4, order=1)
    gt_grad = ndimage.filters.gaussian_filter(target.astype(float), 1.4, order=1)
    error_grad = np.sum(np.power(predict_grad - gt_grad, 2))

    return error_grad


def eval_js_div_loss(pred, target):
    return losses.js_div_loss_2d(image_to_tensor(pred.astype(float), keepdim=False), image_to_tensor(target.astype(float), keepdim=False)).item() / WINDOWS_AREA


def eval_kl_div_loss(pred, target):
    return losses.kl_div_loss_2d(image_to_tensor(pred.astype(float), keepdim=False), image_to_tensor(target.astype(float), keepdim=False)).item() / WINDOWS_AREA


def eval_ssim_error(pred, target, window_size=11):
    return losses.ssim_loss(image_to_tensor(pred.astype(float), keepdim=False), image_to_tensor(target.astype(float), keepdim=False), window_size).item()


def eval_connectivity_error(pred, target, step=0.1, trimap=None):
    """
    计算预测alpha和真实alpha的连通度
    :param pred: 预测alpha，单通道图像， 0-255，(h, w)
    :param target: 真实alpha，单通道图像 0-255，(h, w)
    :param step: 默认为0.1
    :param trimap(optional): 如果提供，只计算trimap128区域的连通度；单通道图像，只有三个值，0-128-255，(h,w)
    :return: loss
    """
    pred = np.array(pred, dtype=float) / 255
    target = np.array(target, dtype=float) / 255

    h, w = pred.shape

    thresh_steps = np.linspace(0, 1, int(1 / step + 1))
    l_map = np.ones(shape=pred.shape) * -1
    dist_maps = np.zeros((h, w, len(thresh_steps)))

    for ii in range(2, len(thresh_steps)):
        pred_alpha_thresh = pred >= thresh_steps[ii]
        target_alpha_thresh = target >= thresh_steps[ii]

        binary = np.array(pred_alpha_thresh & target_alpha_thresh, dtype='uint8')
        num, labels = cv2.connectedComponents(binary, connectivity=4)
        la, la_num = np.unique(labels[labels != 0], return_counts=True)
        max_la = la[np.argmax(la_num)]
        omega = np.zeros((h, w))
        omega[labels == max_la] = 1
        flag = (l_map == -1) & (omega == 0)
        l_map[flag == 1] = thresh_steps[ii - 1]
        dist_maps[:, :, ii] = ndimage.distance_transform_edt(omega)
        dist_maps[:, :, ii] = dist_maps[:, :, ii] / np.max(dist_maps[:, :, ii])

    l_map[l_map == -1] = 1
    pred_d = pred - l_map
    target_d = target - l_map
    pred_phi = 1 - pred_d * (pred_d > 0.15)
    target_phi = 1 - target_d * (target_d > 0.15)
    if trimap is None:
        loss = np.sum(np.abs(pred_phi - target_phi))
    else:
        loss = np.sum(np.abs(pred_phi - target_phi) * (trimap == 128))

    return loss
