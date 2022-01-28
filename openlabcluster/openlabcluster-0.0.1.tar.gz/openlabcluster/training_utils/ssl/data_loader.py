## prepare data
# load file
import os
import random
import shutil
from torch.utils.data import Dataset, DataLoader, SubsetRandomSampler
from torch.nn.utils.rnn import pad_packed_sequence, pad_sequence, pack_padded_sequence
import random
import torch
import h5py
import numpy as np
import pandas as pd


class FeatureNameKeyError(KeyError):
    pass
class DataFileLoadingError(FileNotFoundError):
    pass

def get_data_paths(root_path, data_path, train_files):
    if type(train_files) == str:
        return [os.path.join(root_path, data_path, train_files)]
    
    return [os.path.join(root_path, data_path, file) for file in train_files]

def get_data_list(data_paths:list, indices = None, keypoint_names:list=None, return_video=False, videos_exist=False, max_data_len=None):
    '''
    data_paths - list of file paths to get data from (h5, h5py files)
    indices - list of indices of data to get
    keypoint_names - names of keypoints 
    return_video - whether to return the video names
    videos_exits - whether the video names are already in the file
    
    goes through each file path, with either format that project originally had or deeplabcut format.
    NOTE: this method does not downsample. downsampling is done separately 
    '''

    data_list = []
    label_list = []
    video_list = []

    for data_path in data_paths:
        try:
            f = h5py.File(data_path, 'r')
        except:
            raise DataFileLoadingError(data_path)
        
        if 'df_with_missing' in list(f.keys()):
            # DATA FROM DEEPLABCUT
            video_list.append(data_path)

            data = np.array([])

            # TODO: check for 3d videos 

            df = pd.read_hdf(data_path)
            scorers = set([key[0] for key in df.keys()])

            for scorer in scorers:
                # slice out the data in the dataframe
                idx = pd.IndexSlice

                if keypoint_names is None:
                    datapoint = df[scorer].loc[idx[:], idx[:, ('x','y')]].to_numpy()
                else:
                    try:
                        datapoint = df[scorer][keypoint_names].loc[idx[:], idx[:, ('x','y')]].to_numpy()
                    except KeyError as e:
                        raise FeatureNameKeyError(str(e))

                if len(data) == 0:
                    data = datapoint
                else:
                    np.concatenate((data, datapoint), axis=0)

            num_keypoints = data.shape[1]

            # preprocess data to normalize it 
            y_cor = np.arange(0, num_keypoints, 2)
            x_cor = np.arange(1, num_keypoints, 2)
            # normalize by image size
            max_26 = np.amax(data, axis=0)
            min_26 = np.amin(data, axis=0)
            max_x = np.max([max_26[i] for i in range(1, num_keypoints, 2)])
            max_y = np.max([max_26[i] for i in range(0, num_keypoints, 2)])
            min_x = np.min([min_26[i] for i in range(1, num_keypoints, 2)])
            min_y = np.min([min_26[i] for i in range(0, num_keypoints, 2)])

            data[:, y_cor] = (data[:, y_cor] - min_y) / (max_y-min_y)
            data[:, x_cor] = (data[:, x_cor] - min_x) / (max_x - min_x)

            x = torch.tensor(data, dtype=torch.float)
            y = 0 # TODO: Moishe: what is this supposed to be

            data_list.append(x)
            label_list.append(y)

        else:
            output = load_preprocessed_h5_datafile(data_path, indices=indices, videos_exist=videos_exist)

            data_list += output[0] # data list
            label_list += output[1] # label list

            if videos_exist:
                video_list += output[2]
            else:
                video_list += [data_path + '-clip' + str(i) for i in range(len(output[0]))]
                
    if max_data_len is not None:
        data_list = data_list[:max_data_len]
        label_list = label_list[:max_data_len]
        video_list = video_list[:max_data_len]

    if return_video:
        return data_list, label_list, video_list
        
    return data_list, label_list

def load_preprocessed_h5_datafile(data_path, indices = None, videos_exist=False):
    '''
    data_path - filepath to data file
    indices - indices of data to select. None means select all data
    videos_exist - whether or not video names (for data points) are in the data file
    '''
    data_list = []
    label_list = []
    video_list = []

    f = h5py.File(data_path, 'r')

    if indices is not None:
        for i in indices:
            if np.shape(f[str(i)][:])[0] > 2:
                x = f[str(i)][:]
                # original matrix with probability
                y = f['label'][i]

                video = f['videos'][i]

                x = torch.tensor(x, dtype=torch.float)

                data_list.append(x)
                label_list.append(y)
                video_list.append(video)

    else:
        # pre-precessed data with multiple videos 
        for i in range(len(f['label'])):
            
            if np.shape(f[str(i)][:])[0] >= 2:
                x = f[str(i)][:]
                # original matrix with probability
                y = f['label'][i]
                x = torch.tensor(x, dtype=torch.float)

                data_list.append(x)
                label_list.append(y)
                if videos_exist:
                    video = f['videos'][i]
                    video_list.append(video)

    if videos_exist:
        return data_list, label_list, video_list

    return data_list, label_list

def downsample_frames(data_list, label_list, datafile_list, video_list, video_dir, video_list_filepath, is_multi_action=True, single_action_crop=50, multi_action_crop=10):
    '''
    data_list - list of tensors
    label_list - list of ints

    cuts data files into multiple segments if multi action is true
    selects frames from segments to meet single action crop 
    '''


    import cv2 

    print(list(video_list))
    print(list(data_list))

    if is_multi_action:
        data_list_new_1 = []
        label_list_new = []
        video_list_new = []

        # split video into multiple actions
        for datapoint, label, video in zip(data_list, label_list, list(video_list)):
            print(video)
            cap = cv2.VideoCapture(video)
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            new_datapoints = list(torch.split(datapoint, multi_action_crop))
            data_list_new_1 += new_datapoints
            label_list_new += [label] * len(new_datapoints)

            video_clips = [
                os.path.join(video_dir, "{0}-segment{2}-{3}-{4}.{1}".format(*os.path.basename(video).rsplit('.', 1) + [i] + [multi_action_crop, single_action_crop]))
                for i in range(len(new_datapoints))
            ]

            for i, (new_dp, vid_path) in enumerate(zip(new_datapoints, video_clips)):
                print(vid_path)

                if not os.path.exists(vid_path):
                    # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                    out = cv2.VideoWriter(vid_path, fourcc, fps, (width, height))

                    cap.set(cv2.CAP_PROP_POS_FRAMES, i*multi_action_crop)

                    for i in range(len(new_dp)):
                        ret, frame = cap.read()
                        out.write(frame)
                    
                    out.release()
                    out = None

            video_list_new += video_clips
    
    else:
        data_list_new_1 = data_list
        label_list_new = label_list
        video_list_new = [os.path.join(video_dir, os.path.basename(video)) for video in video_list]

        for og_path, new_path in zip(video_list, video_list_new):
            shutil.copyfile(og_path, new_path)

    data_list_new_2 = []

    for datapoint, vid_path in zip(data_list_new_1, video_list_new):
        # downsample the data because actions can be very long
        if len(datapoint) > single_action_crop:
            indx = np.sort(np.random.randint(0, len(datapoint), single_action_crop))
            datapoint = datapoint[indx]

            cap = cv2.VideoCapture(vid_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            new_frames = []

            for i in range(num_frames):
                ret, frame = cap.read()
                
                if i in indx:
                    new_frames.append(frame)

            if os.path.exists(vid_path):
                os.remove(vid_path)

            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            out = cv2.VideoWriter(vid_path, fourcc, fps, (width, height))
            
            for frame in new_frames:
                out.write(frame)
            
            out.release()

        data_list_new_2.append(datapoint)
    
    print('DATA LIST LENGTHS', len(data_list), len(data_list_new_2))
    print('DATA POINTS LENGTHS', len(data_list[0]), len(data_list_new_2[0]))

    with open(video_list_filepath, 'w') as video_list_file:
        print(video_list_new)
        video_list_file.writelines('\n'.join(video_list_new))

    return data_list_new_2, label_list_new, video_list_new

def save_compiled_h5_datafile(filepath, data_list:list, label_list, video_list):
    # data_list: list of torch tensors

    f = h5py.File(filepath, 'w')

    for idx, data in enumerate(data_list):
        # print(data.numpy())
        dset = f.create_dataset(str(idx), data=np.array(data.numpy()))

    # print(label_list)
    grp = f.create_dataset('label', data=np.array(label_list))

    asciiList = [n.encode("ascii", "ignore") for n in video_list]
    f.create_dataset('videos', (len(asciiList),),'S200', data=asciiList)

    f.close()

def add_videonames_to_h5(filepath, video_list):
    f = h5py.File(filepath, 'a')

    if 'videos' not in list(f.keys()):
        asciiList = [n.replace('\n', '').encode("ascii", "ignore") for n in video_list]
        f.create_dataset('videos', (len(asciiList),),'S200', data=asciiList)

    f.close()

# def FourierTrasnform(data_list):
#     n = len(data_list)
#     for i in range(n):
#         data_list[i] =  rfft(data_list[i],dim=0).abs()
#     return data_list

def TimeDifference(data_list):
    n = len(data_list)
    for i in range(n):
        data_list[i] = data_list[i][1:,:] - data_list[i][:-1, :]
    return data_list

def concate_data(data_path, seq_len=10):
    data_list, label_list = get_data_list(data_path)

    feature_len = data_list[0].size()[-1]
    data = torch.tensor(())
    for i in range(len(label_list)):
        if data_list[i].size()[0] == seq_len:
            tmp = torch.flatten(data_list[i])
            data = torch.cat((data, tmp)).unsqueeze(0)

        if data_list[i].size()[0] < seq_len:
            dif = seq_len - data_list.size()[0]
            tmp = torch.cat((data_list[i], torch.zeros((dif, feature_len))))
            tmp = torch.flatten(tmp)
            data = torch.cat((data, tmp)).unsqueeze(0)

        if data_list[i].size()[0] > seq_len:
            tmp = data_list[i][:seq_len, :]
            tmp = torch.flatten(tmp).unsqueeze(0)
            data = torch.cat((data, tmp))
    label_list = np.asarray(label_list)
    return data.numpy(), label_list


def pad_collate_semi(batch):
    lens = [len(x[0]) for x in batch]

    data = [x[0] for x in batch]
    label = [x[1] for x in batch]
    semi_label = [x[2] for x in batch]
    semi_label = np.asarray(semi_label)
    xx_pad = pad_sequence(data, batch_first=True, padding_value=0)
    return xx_pad, lens, label, semi_label


class SupDataset(Dataset):
    def __init__(self, root_path, data_path, data_files, label_path=None, test=False, keypoint_names:list=None):
        data_paths = get_data_paths(root_path, data_path, data_files)
        self.data, self.label = get_data_list(data_paths, keypoint_names=keypoint_names)
        # self.xy = zip(self.data, self.label)
        # self semi-label for semisupervised
        label = np.asarray(self.label)

        train_index = np.zeros(len(self.label))
        if test:
            self.semi_label = np.ones(len(self.label))
        else:
            if label_path==None:
                self.semi_label = np.zeros(len(self.label))
            else:
                self.semi_label = np.load(label_path)

    def __getitem__(self, index):
        sequence = self.data[index]

        step = sequence.shape[0]
        if step > 40:
            idx = np.random.choice(step, 40)
            idx = np.sort(idx)
            sequence = sequence[idx, :]
        label = self.label[index]
        semi_label = self.semi_label[index]

        return sequence, label, semi_label, index

    def __len__(self):
        return len(self.label)

class UnsupData(Dataset):
    def __init__(self, data_path, percentage=1, keypoint_names:list=None):

        self.data, self.label = get_data_list(data_path, keypoint_names=keypoint_names)
        self.semi_label = np.zeros(len(self.label))

    def __getitem__(self, index):
        sequence = self.data[index]
        steps = sequence.shape[0]
        if steps > 40:
            idx = np.random.choice(steps, 40)
            idx = np.sort(idx)
            sequence = sequence[idx, :]
        label = self.label[index]
        semi_label = self.semi_label[index]

        return sequence, label, semi_label, index

    def __len__(self):
        return len(self.label)

def pad_collate_iter(batch):
    lens = [len(x[0]) for x in batch]
    data = [x[0] for x in batch]
    label = [x[1] for x in batch]
    semi_label = [x[2] for x in batch]
    semi_label = np.asarray(semi_label)
    idex = [x[3] for x in batch]
    idex = np.asarray(idex)
    xx_pad = pad_sequence(data, batch_first=True, padding_value=0)

    return xx_pad, lens, label, semi_label, idex










