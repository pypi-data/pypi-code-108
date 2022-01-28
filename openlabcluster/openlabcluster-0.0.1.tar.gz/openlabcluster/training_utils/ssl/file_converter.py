import h5py
from pathlib import Path
import yaml
import os
import numpy as np

dlcluster_config = '/Users/Moishe/Downloads/IC_GUI_real/deeplabcut_removetest_moishe/gui/2D-2021-05-01/config.yaml'

dlcluster_config = yaml.safe_load(open(dlcluster_config, 'r'))

root_path = dlcluster_config["project_path"]

if type(dlcluster_config['train']) == str:
    data_paths = os.path.join(root_path, dlcluster_config['data_path'], dlcluster_config['train'])
else:
    data_paths = [os.path.join(root_path, dlcluster_config['data_path'], file) for file in dlcluster_config['train']]

# h5_file = h5py.File()

for datapath in data_paths:
    # processing
    # leave normalization up to user
    # our default one in Data_preprocess.py
    # add normalization method to config 
    print(datapath)


    f = h5py.File(datapath,'r')

    data = []

    for idx, frame in list(f['df_with_missing']['table']):
        # TODO: check for 3d videos 

        keypoints_idx = sorted(list(range(0, len(frame), 3)) + list(range(1, len(frame), 3)))

        data.append(frame[keypoints_idx])
        
        # print(keypoints_idx)
        # print(data)

    data = np.array(data)

    print(data)
    print(data.shape)

    num_keypoints = data.shape[1]

    y_cor = np.arange(0, num_keypoints, 2)
    x_cor = np.arange(1, num_keypoints, 2)
    # normalize by image size
    max_26 = np.amax(data, axis=0)
    min_26 = np.amin(data, axis=0)
    max_x = np.max([max_26[i] for i in range(1, num_keypoints, 2)])
    max_y = np.max([max_26[i] for i in range(0, num_keypoints, 2)])
    min_x = np.min([min_26[i] for i in range(1, num_keypoints, 2)])
    min_y = np.min([min_26[i] for i in range(0, num_keypoints, 2)])

    print(min_x, min_y, max_x, max_y)

    data[:, y_cor] = (data[:, y_cor] - min_y) / (max_y-min_y)
    data[:, x_cor] = (data[:, x_cor] - min_x) / (max_x - min_x)

    print(data)


    break

