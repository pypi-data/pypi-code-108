import os
import glob

import cv2
import numpy as np
import time
import re
import h5py
import matplotlib.pyplot as plt
from functools import partial
from tqdm import tqdm
from PIL import Image
from whacc.image_tools import h5_iterative_creator
from sklearn.preprocessing import normalize
from whacc import utils, image_tools, analysis
import matplotlib.pyplot as plt
import numpy as np
import copy
from scipy.signal import medfilt


def track_h5(template_image, h5_file, match_method='cv2.TM_CCOEFF', ind_list=None):
    with h5py.File(h5_file, 'r') as h5:
        if isinstance(template_image, int):  # if termplate is an ind to the images in the h5
            template_image = h5['images'][template_image, ...]
        elif len(template_image.shape) == 2:
            template_image = np.repeat(template_image[:, :, None], 3, axis=2)

        if ind_list is None:
            ind_list = range(len(h5['labels'][:]))
        # width and height of img_stacks will be that of template (61x61)
        max_match_val = []
        try:
            method_ = eval(match_method)
        except:
            method_ = match_method
        max_match_val = []
        for frame_i in tqdm(ind_list):
            img = h5['images'][frame_i, ...]
            # Apply template Matching
            if isinstance(method_, str):
                print('NOOOOOOOOOOOOOOO')
                if method_ == 'calc_diff':
                    max_val = np.sum(np.abs(img.flatten() - template_image.flatten()))
                elif method_ == 'mse':
                    max_val = np.mean((img.flatten() - template_image.flatten()) ** 2)
            else:
                res = cv2.matchTemplate(img, template_image, method_)
                min_val, max_val, min_loc, top_left = cv2.minMaxLoc(res)
            max_match_val.append(max_val)
            # top_left = np.flip(np.asarray(top_left))
    return max_match_val, template_image


x = '/Users/phil/Downloads/test_pole_tracker/AH0667x170317.h5'
utils.print_h5_keys(x)
max_val_stack = image_tools.get_h5_key_and_concatenate(x, 'max_val_stack')
locations_x_y = image_tools.get_h5_key_and_concatenate(x, 'locations_x_y')
trial_nums_and_frame_nums = image_tools.get_h5_key_and_concatenate(x, 'trial_nums_and_frame_nums')
template_img = image_tools.get_h5_key_and_concatenate(x, 'template_img')
frame_nums = trial_nums_and_frame_nums[1, :].astype(int)
trial_nums = trial_nums_and_frame_nums[0, :].astype(int)
asdfasdfasdf
method = 'TM_CCOEFF_NORMED'
ind_list = None
max_match_val_new, template_image_out = track_h5(template_img, x, match_method='cv2.' + method, ind_list=ind_list)

method = 'calc_diff'
ind_list = None
template_img = 2000
max_match_val_new, template_image_out = track_h5(template_img, x, match_method=method, ind_list=ind_list)

method = 'mse'
ind_list = None
template_img = 2000
max_match_val_new, template_image_out = track_h5(template_img, x, match_method=method, ind_list=ind_list)

for k1, k2 in utils.loop_segments(frame_nums):
    plt.plot(max_match_val_new[k1:k2], linewidth=.3)
plt.legend(trial_nums)

match_list = ['TM_SQDIFF_NORMED', 'TM_CCORR_NORMED', 'TM_CCOEFF_NORMED', 'TM_SQDIFF', 'TM_CCORR', 'TM_CCOEFF']

h5_file = '/Users/phil/Downloads/test_pole_tracker/AH0667x170317.h5'
meth_dict = dict()
meth_dict['h5_file'] = h5_file
ind_list = None
for template_image_ind in [0, 2000]:
    for method in match_list:
        max_match_val_new, template_image = track_h5(template_image_ind, h5_file, match_method='cv2.' + method,
                                                     ind_list=ind_list)
        meth_dict['ind_' + str(template_image_ind) + '_' + method] = max_match_val_new

for method in match_list:
    max_match_val_new, template_image = track_h5(template_img, h5_file, match_method='cv2.' + method, ind_list=ind_list)
    meth_dict['ind_template_img_' + method] = max_match_val_new

fig, ax = plt.subplots(nrows=3, ncols=3, sharex=True, sharey=False)
ax_list = fig.axes
cnt = -1
for k in meth_dict:
    if 'h5_file' not in k and 'NORM' in k:
        cnt += 1
        if len(ax_list) == cnt:
            cnt = 0
            fig, ax = plt.subplots(nrows=2, ncols=3, sharex=True, sharey=False)
            ax_list = fig.axes
        ax1 = ax_list[cnt]
        ax1.set_title(k)
        # plt.title(k)
        for k1, k2 in utils.loop_segments(frame_nums):
            try:
                x = np.asarray(meth_dict[k][k1:k2])
                # ax1.plot(x-x[0],linewidth=.3, alpha = 1)
                ax1.plot(x, linewidth=.3, alpha=1)
            except:
                break
plt.legend(trial_nums)

# plt.imshow(image_tools.get_h5_key_and_concatenate(h5_file, 'images'))

a = analysis.pole_plot('/Users/phil/Downloads/test_pole_tracker/AH0667x170317.h5')

a.current_frame = 0
a.plot_it()

a.current_frame = 1000
a.plot_it()
""""$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"""

h5_file = '/Users/phil/Downloads/test_pole_tracker/AH0667x170317.h5'
method = 'cv2.TM_CCOEFF'
method = 'cv2.TM_CCOEFF_NORMED'
method = 'cv2.TM_SQDIFF_NORMED'
ind_list = None
template_image_ind = 2000  # know this is a good starting point with no whiskers in it
ls = np.asarray(utils.loop_segments(frame_nums, returnaslist=True))
all_maxes = []
trial_inds = range(len(frame_nums))
self_references_frame_compares = np.zeros(np.sum(frame_nums))
max_match_all = []
max_match_all2 = []
trial_ind_all = []
template_img_all = []
template_image_ind_all = []
for k in range(len(frame_nums)):
    template_image_ind_all.append(template_image_ind)
    max_match, template_img = track_h5(int(template_image_ind), h5_file, match_method=method, ind_list=ind_list)
    template_img_all.append(template_img)
    max_match_all.append(np.asarray(max_match))
    max_match_all2.append(np.asarray(max_match))
    trial_ind = np.where(template_image_ind < np.cumsum(frame_nums))[0][0]
    trial_ind_all.append(trial_ind)
    self_references_frame_compares[ls[0, trial_ind]:ls[1, trial_ind]] = max_match[ls[0, trial_ind]:ls[1, trial_ind]]
    if k == len(frame_nums)-1:
        break
    for kt in trial_ind_all:
        for kk in max_match_all:
            kk[ls[0, kt]:ls[1, kt]] = np.nan
            kk[ls[0, kt]:ls[1, kt]] = np.nan
    _val = -99999999999
    _ind = -99999999999
    for kk in max_match_all:
        tmp1 = np.nanmax(kk)
        tmp2 = np.nanargmax(kk)
        if tmp1 > _val:
            _val = copy.deepcopy(tmp1)
            _ind = copy.deepcopy(tmp2)
    # template_image_ind = copy.deepcopy(_ind)
    template_image_ind = template_image_ind+4000

kernel_size = 1
for k1, k2 in utils.loop_segments(frame_nums):
    plt.plot(medfilt(self_references_frame_compares[k1:k2], kernel_size=kernel_size), linewidth = 0.3)
plt.legend(range(len(frame_nums)))
plt.title(method)


# pred_bool_smoothed = medfilt(copy.deepcopy(pred_bool_temp), kernel_size=kernel_size)

fig, ax = plt.subplots(nrows=1, ncols=5, sharex=True, sharey=False)
ax_list = fig.axes
for i, k in enumerate(ax_list):
    k.imshow(template_img_all[i])
    k.set_title(template_image_ind_all[i])



x = np.mean(np.asarray(max_match_all2), axis = 0)
kernel_size = 1
for k1, k2 in utils.loop_segments(frame_nums):
    plt.plot(medfilt(x[k1:k2], kernel_size=kernel_size), linewidth = 0.3)
plt.legend(range(len(frame_nums)))
plt.title(method)
"""$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"""

h5_file = '/Users/phil/Dropbox/HIRES_LAB/curation_for_auto_curator/Data/Jon/AH0667/170317/AH0667x170317.h5'
trial_nums_and_frame_nums = image_tools.get_h5_key_and_concatenate(h5_file, 'trial_nums_and_frame_nums')
frame_nums = trial_nums_and_frame_nums[1, :].astype(int)

method = 'cv2.TM_CCORR_NORMED'
frame_to_compare = 2000
testing_frames_start = 1250
testing_frames_len = 50

method = 'cv2.TM_CCOEFF'#console regular# best
frame_to_compare = 1
testing_frames_start = 1250
testing_frames_len = 50

# method = 'cv2.TM_CCOEFF' #console (1)
# frame_to_compare = 2000
# testing_frames_start = 1250
# testing_frames_len = 50

ind_list = None
all_tests = []
for ktrial, _ in utils.loop_segments(frame_nums):
    template_image_ind = frame_to_compare+ktrial
    max_match_all = []
    for k1, k2 in utils.loop_segments(frame_nums):
        ind_list = np.arange(testing_frames_start, testing_frames_start+testing_frames_len) + k1
        max_match, template_img = track_h5(int(template_image_ind), h5_file, match_method=method, ind_list=ind_list)
        max_match = np.asarray(max_match).astype(float)
        max_match_all.append(max_match-max_match[0])
    all_tests.append(np.asarray(max_match_all).flatten())

all_var = []
for i, k in enumerate(all_tests):
    addto = (10**6)*i*2
    k = k[(k>np.quantile(k,0.1)) & (k<np.quantile(k,0.9))]
    plt.plot(k+addto, '.', markersize = 0.3)
    # plt.plot(k+addto, '-k', linewidth = 0.05)
    all_var.append(np.var(k))
plt.legend(np.argsort(all_var))

plt.figure()
for i, k in enumerate(all_tests):
    addto = (10**6)*i*2
    plt.plot(k+addto, '.', markersize = 0.3)





k1, k2 = utils.loop_segments(frame_nums, returnaslist=True)
template_image_ind = frame_to_compare+k1[np.argmin(all_var)]

ind_list = None
max_match, template_img = track_h5(int(template_image_ind), h5_file, match_method=method, ind_list=ind_list)

locations_x_y = image_tools.get_h5_key_and_concatenate(h5_file, 'locations_x_y')
tmp1 = np.argsort(locations_x_y[:, 0][2000::4000])

k1, k2 = utils.loop_segments(frame_nums, returnaslist = True)

for i, k in enumerate(tmp1):
    addto = i*10**6
    plt.plot(np.asarray(max_match[k1[k]:k2[k]])+addto, linewidth=0.3)


for i, k in enumerate(tmp1):
    addto = i*10**-3
    plt.plot(np.asarray(max_match[k1[k]:k2[k]])+addto, linewidth=0.3)



"""$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"""
k1, k2 = utils.loop_segments(frame_nums, returnaslist=True)
all_var_inds = np.argsort(all_var)
all_max = []
for ii in range(4):
    template_image_ind = frame_to_compare+k1[all_var_inds[ii]]
    ind_list = None
    max_match, template_img = track_h5(int(template_image_ind), h5_file, match_method=method, ind_list=ind_list)
    all_max.append(max_match)


max_match_mean = np.nanmean(np.asarray(all_max), axis = 0)
tmp1 = np.argsort(locations_x_y[:, 0][2000::4000])
for i, k in enumerate(tmp1):
    addto = i*10**6
    plt.plot(np.asarray(max_match_mean[k1[k]:k2[k]])+addto, linewidth=0.3)


x = np.asarray(all_max)
for i, k in enumerate(tmp1):
    addto = i*10**6
    x1  = x[0][k1[k]:k2[k]]+addto
    x2  = x[1][k1[k]:k2[k]]+addto
    plt.plot(x1-x2, linewidth=0.3)











"""$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"""
"""$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"""
"""$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"""
"""$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"""
"""$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"""


from IPython.utils import io

vit = dict()
vit['all_acc_before_no_pole_mask'] = []
vit['all_acc_after_no_pole_mask'] = []
vit['all_acc_before'] = []
vit['all_acc_after'] = []
vit['h5_img_file'] = []
vit['h5_img_file_full_dir'] = []

vit['m_name'] = m_names
vit['L_key']= label_key
vit['vm_name'] = vit_m_names
vit['h5_img_file_full_dir']= to_pred_h5s
for k in vit['h5_img_file_full_dir']:
  vit['h5_img_file'].append(os.path.basename(k))

for h5_img_file in to_pred_h5s:
  in_range = image_tools.get_h5_key_and_concatenate([h5_img_file], 'in_range')
  tmp1 = []
  tmp2 = []
  tmp3 = []
  tmp4 = []
  for iii, (vm_name, m_name, L_key) in enumerate(tzip(vit_m_names, m_names, label_key)):
    pred_m_raw = image_tools.get_h5_key_and_concatenate([h5_img_file], key_name=m_name)
    pred_v = image_tools.get_h5_key_and_concatenate([h5_img_file], key_name=vm_name)
    real = image_tools.get_h5_key_and_concatenate([h5_img_file], key_name=L_key)
    if pred_m_raw.shape[1] ==1:
      pred_m = ((pred_m_raw>0.5)*1).flatten()
    else:
      pred_m = np.argmax(pred_m_raw, axis = 1)# turn into integers instead of percentages

    # get everything back to binary (if possible)
    with io.capture_output() as captured:#prevents crazy printing

      pred_m_bool = utils.convert_labels_back_to_binary(pred_m, L_key)
      real_bool = utils.convert_labels_back_to_binary(real, L_key)
      pred_v_bool = utils.convert_labels_back_to_binary(pred_v, L_key)
    if real_bool is None: # convert labels will return None if it cant convert
    #it back to the normal format. i.e. only onset or only offsets...
      tmp1.append(0)
      tmp2.append(0)
      tmp3.append(0)
      tmp4.append(0)
    else:
      tmp1.append(np.mean(real_bool == pred_m_bool))
      tmp2.append(np.mean(real_bool == pred_v_bool))
      tmp3.append(np.mean(real_bool*in_range == pred_m_bool*in_range))
      tmp4.append(np.mean(real_bool*in_range == pred_v_bool*in_range))

  vit['all_acc_before_no_pole_mask'].append(tmp1)
  vit['all_acc_after_no_pole_mask'].append(tmp2)
  vit['all_acc_before'].append(tmp3)
  vit['all_acc_after'].append(tmp4)
  # vit['m_name'] = list(dict.fromkeys(vit['m_name']))
  # vit['L_key'] = list(dict.fromkeys(vit['L_key']))
  # vit['h5_img_file_full_dir'].append(h5_img_file)


vit2 = copy.deepcopy(vit)
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################

# def grab_frames(x, lstm_len, end_frame_num):
#     # if

# h5 = '/Users/phil/Dropbox/HIRES_LAB/GitHub/Phillip_AC/model_testing/all_data/all_models/regular_80_border/data/regular/train_regular.h5'
h5 = '/Users/phil/Dropbox/HIRES_LAB/GitHub/Phillip_AC/model_testing/all_data/test_data/small_h5s/3lag/small_test_3lag.h5'
utils.print_h5_keys(h5)
# (None, 5, 96, 96, 3)
lstm_len = 5
assert lstm_len%2 == 1
with h5py.File(h5, 'r') as h:
    print(len(h['images']))
    batch_size = 20
    print(h['images'][0:batch_size].shape)
    x = h['images'][20:20 + batch_size]
    x2 = x[:, None, ...]
    print(x2.shape)
    print(x2[:-5, ...].shape)
    # print(x[4:-1, ...].shape)
    x3 = np.stack(( x[:-4, ...],  x[1:-3, ...], x[2:-2, ...], x[3:-1, ...], x[4:, ...]), axis = 1)
    print(x3.shape)
    print(x.shape)
    # print(x[4:-1, ...].shape)
    y = x3[0]
    y2 = y

    plt.figure()
    for i, k in enumerate(y):
        plt.subplot(3,2, i+1)
        plt.imshow(k)



# finished extractor........
lstm_len = 5
assert lstm_len%2 == 1, "number of images must be odd"
batch_size = 10
chunk_num = 24

lstm_len//2

with h5py.File(h5, 'r') as h:
    b = lstm_len//2
    tot_len = h['images'].shape[0]
    i1 = chunk_num * batch_size - b
    i2 = chunk_num * batch_size + batch_size + b
    edge_left_trigger = abs(min(i1, 0))
    edge_right_trigger = abs(min(tot_len-i2, 0))
    x = h['images'][max(i1, 0):min(i2, tot_len)]
    print(x.shape)
    if edge_left_trigger+edge_right_trigger>0: # in case of edge cases
        pad_shape = list(x.shape); pad_shape[0] = edge_left_trigger+edge_right_trigger
        pad = np.zeros(pad_shape).astype('uint8')
        if edge_left_trigger>edge_right_trigger:
            x = np.concatenate((pad, x), axis = 0)
        else:
            x = np.concatenate((x, pad), axis = 0)

    s = list(x.shape)
    s.insert(1, lstm_len)
    out = np.zeros(s).astype('uint8')


    for i in range(lstm_len):
        i1 = max(0, b-i)
        i2 = min(s[0], s[0]+b-i)
        i3 = max(0, i-b)
        i4 = min(s[0], s[0]+i-b)
        print('take ', i3,' to ',  i4, ' and place in ', i1,' to ', i2)
        out[i1:i2, i, ...] = x[i3:i4, ...]
    out = out[b:s[0]-b, ...]

    y = out[-1]
    print(out.shape)
    plt.figure()
    for i, k in enumerate(y):
        plt.subplot(3,2, i+1)
        # plt.figure()
        plt.imshow(k)



"""$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"""


# finished extractor........



lstm_len = 5

batch_size = 10
chunk_num = 24
with h5py.File(h5, 'r') as h:
    b = lstm_len//2
    tot_len = h['images'].shape[0]
    i1 = chunk_num * batch_size - b
    i2 = chunk_num * batch_size + batch_size + b
    edge_left_trigger = abs(min(i1, 0))
    edge_right_trigger = abs(min(tot_len-i2, 0))
    x = h['images'][max(i1, 0):min(i2, tot_len)]
    print(x.shape)
    if edge_left_trigger+edge_right_trigger>0: # in case of edge cases
        pad_shape = list(x.shape); pad_shape[0] = edge_left_trigger+edge_right_trigger
        pad = np.zeros(pad_shape).astype('uint8')
        if edge_left_trigger>edge_right_trigger:
            x = np.concatenate((pad, x), axis = 0)
        else:
            x = np.concatenate((x, pad), axis = 0)

    s = list(x.shape)
    s.insert(1, lstm_len)
    out = np.zeros(s).astype('uint8')


    for i in range(lstm_len):
        i1 = max(0, b-i)
        i2 = min(s[0], s[0]+b-i)
        i3 = max(0, i-b)
        i4 = min(s[0], s[0]+i-b)
        print('take ', i3,' to ',  i4, ' and place in ', i1,' to ', i2)
        out[i1:i2, i, ...] = x[i3:i4, ...]
    out = out[b:s[0]-b, ...]

    y = out[-1]
    print(out.shape)
    plt.figure()
    for i, k in enumerate(y):
        plt.subplot(3,2, i+1)
        # plt.figure()
        plt.imshow(k)




import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
import numpy as np
import h5py
import copy
import time
import os
from whacc import utils
import pdb

def reset_to_first_frame_for_each_file_ind(file_inds_for_H5_extraction):
    """reset_to_first_frame_for_each_file_ind - uses the output of batch_size_file_ind_selector
    to determine when to reset the index for each individual H5 file. using the above example
    the out put would be [0, 0, 2, 2, 2, 5, 5], each would be subtracted from the indexing to
    set the position of the index to 0 for each new H5 file.

    Parameters
    ----------
    file_inds_for_H5_extraction :


    Returns
    -------


    """
    subtract_for_index = []
    for k, elem in enumerate(file_inds_for_H5_extraction):
        tmp1 = np.diff(file_inds_for_H5_extraction)
        tmp1 = np.where(tmp1 != 0)
        tmp1 = np.append(-1, tmp1[0]) + 1
        subtract_for_index.append(tmp1[np.int(file_inds_for_H5_extraction[k])])
    return subtract_for_index


def batch_size_file_ind_selector(num_in_each, batch_size):
    """batch_size_file_ind_selector - needed for ImageBatchGenerator to know which H5 file index
    to use depending on the iteration number used in __getitem__ in the generator.
    this all depends on the variable batch size.

    Example: the output of the following...
    batch_size_file_ind_selector([4000, 4001, 3999], [2000])
    would be [0, 0, 1, 1, 1, 2, 2] which means that there are 2 chunks in the first
    H5 file, 3 in the second and 2 in the third based on chunk size of 2000

    Parameters
    ----------
    num_in_each :
        param batch_size:
    batch_size :


    Returns
    -------


    """
    break_into = np.ceil(np.array(num_in_each) / batch_size)
    extract_inds = np.array([])
    for k, elem in enumerate(break_into):
        tmp1 = np.array(np.ones(np.int(elem)) * k)
        extract_inds = np.concatenate((extract_inds, tmp1), axis=0)
    return extract_inds

def get_total_frame_count(h5_file_list):
    """

    Parameters
    ----------
    h5_file_list :


    Returns
    -------


    """
    total_frame_count = []
    for H5_file in h5_file_list:
        H5 = h5py.File(H5_file, 'r')
        images = H5['images']
        total_frame_count.append(images.shape[0])

    return total_frame_count


class ImageBatchGenerator_LSTM(keras.utils.Sequence):
    """ """

    def __init__(self, lstm_len, batch_size, h5_file_list, label_key = 'labels', IMG_SIZE = 96):
        assert lstm_len%2 == 1, "number of images must be odd"
        h5_file_list = utils.make_list(h5_file_list, suppress_warning=True)
        num_frames_in_all_H5_files = get_total_frame_count(h5_file_list)
        file_inds_for_H5_extraction = batch_size_file_ind_selector(
            num_frames_in_all_H5_files, batch_size)
        subtract_for_index = reset_to_first_frame_for_each_file_ind(
            file_inds_for_H5_extraction)
        # self.to_fit = to_fit #set to True to return XY and False to return X
        self.label_key = label_key
        self.batch_size = batch_size
        self.H5_file_list = h5_file_list
        self.num_frames_in_all_H5_files = num_frames_in_all_H5_files
        self.file_inds_for_H5_extraction = file_inds_for_H5_extraction
        self.subtract_for_index = subtract_for_index
        self.IMG_SIZE = IMG_SIZE
        self.lstm_len = lstm_len

    def __getitem__(self, num_2_extract):
        h = self.H5_file_list
        i = self.file_inds_for_H5_extraction
        H5_file = h[np.int(i[num_2_extract])]
        num_2_extract_mod = num_2_extract - self.subtract_for_index[num_2_extract]
        with h5py.File(H5_file, 'r') as h:


            b = self.lstm_len//2
            tot_len = h['images'].shape[0]
            assert tot_len-b>self.batch_size, "reduce batch size to be less than total length of images minus floor(lstm_len) - 1, MAX->" + str(tot_len-b-1)
            i1 = num_2_extract_mod * self.batch_size - b
            i2 = num_2_extract_mod * self.batch_size + self.batch_size + b
            edge_left_trigger = abs(min(i1, 0))
            edge_right_trigger = abs(min(tot_len-i2, 0))
            x = h['images'][max(i1, 0):min(i2, tot_len)]
            if edge_left_trigger+edge_right_trigger>0: # in case of edge cases
                pad_shape = list(x.shape)
                pad_shape[0] = edge_left_trigger+edge_right_trigger
                pad = np.zeros(pad_shape).astype('float32')
                if edge_left_trigger>edge_right_trigger:
                    x = np.concatenate((pad, x), axis = 0)
                else:
                    x = np.concatenate((x, pad), axis = 0)
            x = self.image_transform(x)

            s = list(x.shape)
            s.insert(1, self.lstm_len)
            out = np.zeros(s).astype('float32')

            for i in range(self.lstm_len):
                i1 = max(0, b-i)
                i2 = min(s[0], s[0]+b-i)
                i3 = max(0, i-b)
                i4 = min(s[0], s[0]+i-b)
                # print('take ', i3,' to ',  i4, ' and place in ', i1,' to ', i2)
                out[i1:i2, i, ...] = x[i3:i4, ...]
            out = out[b:s[0]-b, ...]
            i1 = num_2_extract_mod * self.batch_size
            i2 = num_2_extract_mod * self.batch_size + self.batch_size

            raw_Y = h[self.label_key][i1:i2]
            return out, raw_Y

    def __len__(self):
        return len(self.file_inds_for_H5_extraction)

    def getXandY(self, num_2_extract):
        """

        Parameters
        ----------
        num_2_extract :


        Returns
        -------

        """
        rgb_tensor, raw_Y = self.__getitem__(num_2_extract)
        return rgb_tensor, raw_Y
    def getXandY_NOT_LSTM_FORMAT(self, num_2_extract):

        h = self.H5_file_list
        i = self.file_inds_for_H5_extraction
        H5_file = h[np.int(i[num_2_extract])]
        num_2_extract_mod = num_2_extract - self.subtract_for_index[num_2_extract]
        with h5py.File(H5_file, 'r') as h:


            b = self.lstm_len//2
            tot_len = h['images'].shape[0]
            assert tot_len-b>self.batch_size, "reduce batch size to be less than total length of images minus floor(lstm_len) - 1, MAX->" + str(tot_len-b-1)
            i1 = num_2_extract_mod * self.batch_size - b
            i2 = num_2_extract_mod * self.batch_size + self.batch_size + b
            edge_left_trigger = abs(min(i1, 0))
            edge_right_trigger = abs(min(tot_len-i2, 0))
            x = h['images'][max(i1, 0):min(i2, tot_len)]
            if edge_left_trigger+edge_right_trigger>0: # in case of edge cases
                pad_shape = list(x.shape)
                pad_shape[0] = edge_left_trigger+edge_right_trigger
                pad = np.zeros(pad_shape).astype('float32')
                if edge_left_trigger>edge_right_trigger:
                    x = np.concatenate((pad, x), axis = 0)
                else:
                    x = np.concatenate((x, pad), axis = 0)
            x = self.image_transform(x)
            out = x
            raw_Y = h[self.label_key][i1:i2]
            return out, raw_Y
    def image_transform(self, raw_X):
        """input num_of_images x H x W, image input must be grayscale
        MobileNetV2 requires certain image dimensions
        We use N x 61 x 61 formated images
        self.IMG_SIZE is a single number to change the images into, images must be square

        Parameters
        ----------
        raw_X :


        Returns
        -------


        """
        if len(raw_X.shape) == 4 and raw_X.shape[3] == 3:
            rgb_batch = copy.deepcopy(raw_X)
        else:
            rgb_batch = np.repeat(raw_X[..., np.newaxis], 3, -1)
        rgb_tensor = tf.cast(rgb_batch, tf.float32)  # convert to tf tensor with float32 dtypes
        rgb_tensor = (rgb_tensor / 127.5) - 1  # /127.5 = 0:2, -1 = -1:1 requirement for mobilenetV2
        rgb_tensor = tf.image.resize(rgb_tensor, (self.IMG_SIZE, self.IMG_SIZE))  # resizing
        self.IMG_SHAPE = (self.IMG_SIZE, self.IMG_SIZE, 3)
        return rgb_tensor


import datetime

h5 = '/Users/phil/Dropbox/HIRES_LAB/GitHub/Phillip_AC/model_testing/all_data/test_data/small_h5s/3lag/small_test_3lag.h5'
h5 = '/Users/phil/Dropbox/HIRES_LAB/GitHub/Phillip_AC/model_testing/all_data/all_models/regular_80_border/data/regular/train_regular.h5'
lstm_len = 5;batch_size = 1000; h5_file_list = [h5];

G = ImageBatchGenerator_LSTM(lstm_len, batch_size, h5_file_list, label_key = 'labels', IMG_SIZE = 96)
start = datetime.now()
for k in range(G.__len__()):
    x, y = G.__getitem__(k)
print(datetime.now() - start)

x, y = G.getXandY(1)
x = (x+1)/2
y = x[488]
plt.figure()
for i, k in enumerate(y):

    print(all(k.flatten()==0))
    plt.subplot(3,2, i+1)

    # plt.figure()
    plt.imshow(k)

"""$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"""
real_bool = image_tools.get_h5_key_and_concatenate(h5_file, '[0, 1]- (no touch, touch)')
trial_nums_and_frame_nums = image_tools.get_h5_key_and_concatenate(h5_file, 'trial_nums_and_frame_nums')
frame_nums = trial_nums_and_frame_nums[1, :].astype(int)
in_range = image_tools.get_h5_key_and_concatenate(h5_file, 'in_range')

real_bool[np.invert(in_range.astype(bool))] = -1

kernel_size = 7
pred_bool_temp = image_tools.get_h5_key_and_concatenate(h5_file, key_name)
pred_bool_smoothed = foo_arg_max_and_smooth(pred_bool_temp, kernel_size, threshold, key_name, L_type_split_ind = 5)
# pred_bool_smoothed = foo_arg_max_and_smooth(pred_bool_temp, kernel_size, threshold, L_type_split_ind = 5)
pred_bool_smoothed[np.invert(in_range.astype(bool))] = -1

r = real_bool
p = pred_bool_smoothed



a = analysis.error_analysis(r, p, frame_num_array=frame_nums)




np.unique(a.coded_array)

from whacc import analysis
import numpy as np
r = np.asarray([0,1,1,0,0,0,1,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,1,0])
p = np.asarray([0,1,1,0,1,1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,0,0,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,0,1,0])

# r = np.asarray([0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1,1,1])
# p = np.asarray([0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,0])

a = analysis.error_analysis(r, p)
# ['miss', 'append', 'deduct', 'split', 'ghost']
# [[1, 2], [4, 5], [11], [19], [25, 26]]
from whacc import utils
utils.get_class_info(a,end_prev_len = 4000)
"""
onset graph 
find appends/deducts

all_errors_sorted --> are the inds to each error in -->all_error_type_sorted
"""

aet = np.asarray(a.all_error_type_sorted)
cirt_error_inds = np.where(np.logical_and(aet != 'deduct',  aet != 'append'))[0]
aet[cirt_error_inds]
print(len(cirt_error_inds))
plt.hist(aet[cirt_error_inds])


append_var = np.where(np.asarray(a.all_error_type_sorted) == 'append')[0]
deduct_var = np.where(np.asarray(a.all_error_type_sorted) == 'deduct')[0]
sided_append_or_deduct = np.diff(np.asarray(a.which_side_test_sorted)).flatten()

# onset_append_inds = append_var[sided_append_or_deduct[append_var]>0]
# offset_append_inds = append_var[sided_append_or_deduct[append_var]<0]
#
# onset_deduct_inds = deduct_var[sided_append_or_deduct[deduct_var]>0]
# offset_deduct_inds = deduct_var[sided_append_or_deduct[deduct_var]<0]
#
# onset_inds_real = utils.search_sequence_numpy(r, np.asarray([0,1]))+1
# offset_inds_pred = utils.search_sequence_numpy(r, np.asarray([1,0]))


# error_lengths = [len(k) for k in a.all_errors_sorted]


# correct_onset_inds_sorted = np.intersect1d(a.onset_inds_real, a.onset_inds_pred)
# correct_offset_inds_sorted = np.intersect1d(a.offset_inds_real, a.offset_inds_pred)
#
# onset_distance = np.concatenate((np.asarray(a.error_lengths_sorted)[a.onset_append_inds], np.asarray(a.error_lengths_sorted)[a.onset_deduct_inds]*-1))
# offset_distance = np.concatenate((np.asarray(a.error_lengths_sorted)[a.offset_append_inds], np.asarray(a.error_lengths_sorted)[a.offset_deduct_inds]*-1))
#
# onset_distance = np.concatenate((onset_distance, np.zeros_like(correct_onset_inds_sorted)))
# offset_distance = np.concatenate((offset_distance, np.zeros_like(correct_offset_inds_sorted)))
#


import matplotlib.pyplot as plt
# plt.hist(a.onset_distance, bins = np.linspace(-10, 10))

plt.figure()
bins = np.arange(-7, 7)+.5
plt.hist(np.clip(a.onset_distance, bins[0], bins[-1]), bins=bins)
plt.xlabel('distance from human defined onset'); plt.ylabel('count')

plt.figure()
bins = np.arange(-1, 7)+.5
tmp1 = plt.hist(np.clip(np.abs(a.onset_distance), bins[0], bins[-1]), bins=bins)
# plt.figure()
cum_dist = np.cumsum(tmp1[0]/np.sum(tmp1[0]))
plt.xlabel('absolute distance from human defined onset')
ax1 = plt.gca()
ax2 = ax1.twinx()
ax2.plot(bins[:-1]+.5, cum_dist, '-k')
plt.ylim([0.5, 1])
ax1.set_ylabel('count', color='b')
ax2.set_ylabel('cumulative distribution of total number of onsets', color='k')















from whacc import image_tools, utils
import numpy as np
import datetime


h5 = '/Users/phil/Dropbox/HIRES_LAB/GitHub/Phillip_AC/model_testing/all_data/test_data/small_h5s/3lag/small_test_3lag.h5'
imgs = image_tools.get_h5_key_and_concatenate(h5, 'images')
# h5 = '/Users/phil/Dropbox/HIRES_LAB/GitHub/Phillip_AC/model_testing/all_data/all_models/regular_80_border/data/regular/train_regular.h5'
lstm_len = 5;batch_size = 100; h5_file_list = [h5];

G = image_tools.ImageBatchGenerator_LSTM(lstm_len, batch_size, h5_file_list, label_key = 'labels', IMG_SIZE = 96)
x, y = G.__getitem__(0)
type(x[0][0][0][0][0])


start = datetime.now()
for k in range(G.__len__()):
    x, y = G.__getitem__(k)
print(datetime.now() - start)

x, y = G.getXandY(1)
x = (x+1)/2
y = x[488]
plt.figure()
for i, k in enumerate(y):

    print(all(k.flatten()==0))
    plt.subplot(3,2, i+1)

    # plt.figure()
    plt.imshow(k)



al_gen = image_tools.ImageBatchGenerator_simple(100, '/Users/phil/Desktop/content/ALL_RETRAIN_H5_data/3lag/small_train_3lag.h5', label_key='labels')

x, y = al_gen.__getitem__(0)
