import pandas as pd
import torch as T
import torchvision.transforms as tvt
import numpy as np
from os.path import join
import PIL


class CheXpert(T.utils.data.Dataset):
    """Load CheXpert Dataset, assuming you already have a copy on disk.
    This loads the images and labels under the "train" directory, and applies
    optional transforms.  We also clean up the labels.

    An example usage looks like this:

        >>> dset = CheXpert(
            img_transform=tvt.Compose([
                tvt.RandomCrop((512, 512)),
                tvt.ToTensor(),
            ]),
            getitem_transform=lambda dct: (
                dct['image'],
                CheXpert.format_labels(dct, labels=CheXpert.LABELS_DIAGNOSTIC),
                ),
            )
            # note: CheXpert.LABELS_DIAGNOSTIC_LEADERBOARD is a subset of 5 of
            # the 14 LABELS_DIAGNOSTIC classes.

        There are 18 classes exposed by the dataset that a model could predict.
        Of these, 14 diagnostic classes are of primary interest, with values:
            0:   negative
            1:   positive
            -1:  diagnosis uncertain
            Nan: no diagnostic marking available (typically this is same as negative)
        By default, for diagnostic classes, we re-assign Nan to 3, and -1 to 2.

        By default, we also convert all labels to numeric values:
            - all Nan for diagnostic classes are reassigned to 3.
            - Frontal/Lateral:  Frontal = 0, Lateral = 1.
            - AP/PA:  nan=-1, AP=0, PA=1, LL=2, RL=3
            - Sex: Unknown=0, Female=1, Male=2

        Note: A subset of 5 of the 14 classes are used in the CheXpert
        benchmark / leaderboard.  The subset is defined in
        `CheXpert.LABELS_DIAGNOSTIC_LEADERBOARD`.
    """
    LABELS_DIAGNOSTIC = [
        'No Finding',
        'Enlarged Cardiomediastinum', 'Cardiomegaly', 'Lung Opacity',
        'Lung Lesion', 'Edema', 'Consolidation', 'Pneumonia',
        'Atelectasis', 'Pneumothorax', 'Pleural Effusion',
        'Pleural Other', 'Fracture', 'Support Devices']
    LABELS_DIAGNOSTIC_LEADERBOARD = [
        # The chexpert leaderboard evaluates only this subset of the tasks,
        'Atelectasis', 'Cardiomegaly', 'Consolidation', 'Edema',
        'Pleural Effusion']
    LABELS_METADATA = ['Sex', 'Age', 'Frontal/Lateral', 'AP/PA',
                       # and some that are inferred from the filepaths:
                       'Patient', 'Study', 'View', 'Num Views',
                       # and the index that corresponds to __getitem__
                       'index',
                       ]
    LABELS_ALL = LABELS_METADATA + LABELS_DIAGNOSTIC

    LABEL_CLEANUP_DICT = {
        col: {0:0,  # negative
              1:1,  # positive
              -1:2, # uncertain (unclear whether positive or negative)
              np.nan: 3,  # no marking by physician was found with labeling tool (original chexpert paper assumes this means negative)
              } for col in LABELS_DIAGNOSTIC}
    LABEL_CLEANUP_DICT.update({
        'Frontal/Lateral': {'Frontal': 0, 'Lateral': 1},
        'AP/PA': {'AP': 0, 'PA': 1, 'LL': 2, 'RL': 3, np.nan: 4},
        'Sex': {'Female': 0, 'Male': 1, 'Unknown': 2},
        'Age': {i: i for i in range(91)}})

    @staticmethod
    def format_labels(getitem_dct: dict, labels=LABELS_ALL, explode=False):
        """Helper method for converting the labels into a tensor or numpy array.

        :dct: the dict received in getitem_transform.
        :labels: either "all" or "diagnostic" or an ordered list of label names.
            ['Sex', 'Age', 'Frontal/Lateral', 'AP/PA', 'No Finding',
            'Enlarged Cardiomediastinum', 'Cardiomegaly', 'Lung Opacity', 'Lung
            Lesion', 'Edema', 'Consolidation', 'Pneumonia', 'Atelectasis',
            'Pneumothorax', 'Pleural Effusion', 'Pleural Other', 'Fracture',
            'Support Devices'].
        :explode: If true, convert each class into a one-hot vector.
          For instance, 'Age' would get expanded into a one-hot vector of 90
          ages.  The diagnostic classes are expanded to four values
          corresponding to [0 (neg), 1 (pos), 2 (uncertain), 3 (blank)].

        :returns: If explode=False, return torch.tensor of numeric label values.
            If explode=True, return [torch.tensor(one_hot), ...] corresponding
            to the given `labels`.
        """
        if explode:
            y = []
            for lname in labels:
                tmp = T.zeros(
                    len(CheXpert.LABEL_CLEANUP_DICT[lname]), dtype=T.int8)
                tmp[getitem_dct['labels'][lname]] = 1
                y.append(tmp)
        else:
            y = T.tensor(getitem_dct['labels'][labels].values)
        return y

    def __init__(self, dataset_dir="./data/CheXpert-v1.0/",
                 use_train_set=True,
                 img_transform=tvt.ToTensor(),
                 getitem_transform=lambda x: (
                     x['image'], CheXpert.format_labels(x)),
                 label_cleanup_dct=LABEL_CLEANUP_DICT
                 ):

        train_or_valid = 'train' if use_train_set else 'valid'
        label_fp = f"{dataset_dir.rstrip('/')}/{train_or_valid}.csv"
        self.labels_csv = pd.read_csv(label_fp)

        # add extra columns to the csv by parsing the filepath
        self.labels_csv = self.labels_csv.join(
            self.labels_csv['Path'].str.extract('.*/patient(?P<Patient>\d+)/study(?P<Study>\d+)/view(?P<View>\d+).*')
        )
        self.labels_csv = self.labels_csv.sort_values(['Patient', 'Study', 'View'])
        self.labels_csv['Num Views'] = self.labels_csv\
                .groupby(['Patient', 'Study'], sort=False)['View'].transform('count')
        #  assert (  # sanity check
        #      self.labels_csv.groupby(['Patient', 'Study'])['View'].count()
        #      == self.labels_csv.groupby(['Patient', 'Study'])['Num Views'].first()).all()
        # --> add the 'index' column corresponding to that used by __getitem__
        self.labels_csv['index'] = np.arange(self.labels_csv.shape[0])

        # join the labels_csv Path column to the actual filepath
        self.labels_csv.set_index('Path', inplace=True)
        start_idx = self.labels_csv.index[0].index('/') + 1
        self.fps = [join(dataset_dir, x[start_idx:])
                    for x in self.labels_csv.index]
        self.__getitem_transform = getitem_transform
        self.__img_transform = img_transform

        # clean up the labels csv
        if label_cleanup_dct is not None:
            self.labels_csv.replace(label_cleanup_dct, inplace=True)
            self.labels_csv = self.labels_csv.astype('int')

    def __len__(self):
        return self.labels_csv.shape[0]

    def _getimage(self, index):
        fp = self.fps[index]
        with PIL.Image.open(fp) as im:
            im.load()
        if self.__img_transform:
            im = self.__img_transform(im)
        dct = {'image': im, 'fp': fp}
        return dct

    def __getitem__(self, index, _getitem_transform=True):
        sample = self._getimage(index)
        sample['labels'] = self.labels_csv.iloc[index]
        assert index == sample['labels']['index'], 'sanity check'
        if _getitem_transform and self.__getitem_transform is not None:
            return self.__getitem_transform(sample)
        else:
            return sample

    def get_other_views_in_study(self, index=None, path=None,
                                 patient=None, study=None, view=None):
        """
        Expected inputs are one of these combinations:
          - (patient, study, view)  # if a study has 3 views, returns the other 2 views.
          - (patient, study)  # gives all N<=3 views in the study
          - (index, )  # the index of the sample in the dataset (as used for __getitem__)
          - (path, )  # if a study has 3 views, returns the other 2 views.
        Returns pd.DataFrame with columns (Path, index, Patient, Study, View)
        """
        tmp = self.labels_csv[['index', 'Patient', 'Study', 'View']]
        if index is not None:
            _index, patient, study, view = tmp.iloc[index]
            assert _index == index, 'sanity check'
        elif path is not None:
            _index, patient, study, view = tmp.loc[path]
            assert _index == index, 'sanity check'
        cols = ['index', 'Patient', 'Study', 'View']
        outs = self.labels_csv[cols].query(
            f'Patient == {patient} and Study == {study}'
            f"{f' and View != {view}' if view is not None else ''}").reset_index()
        return outs



class CheXpert_Small(CheXpert):
    def __init__(self, dataset_dir="./data/CheXpert-v1.0-small/", **kwargs):
        super().__init__(dataset_dir=dataset_dir, **kwargs)


if __name__ == "__main__":
    """
    to test this code, run
    $ ipython -im simplepytorch.datasets.chexpert
    """

    #  Test Set
    dset = CheXpert_Small(use_train_set=False, getitem_transform=lambda x: (x['image'], CheXpert.format_labels(x, labels=CheXpert.LABELS_DIAGNOSTIC, explode=True)))
    print('z = dset[0] ; print(img, av_mask = z)')
    z = dset[0]
    print('image x-ray size:', z[0].shape)
    print('one-hot labels', list(zip(CheXpert.LABELS_DIAGNOSTIC, z[1])))

    print('')

    # Training Set
    dset = CheXpert_Small(use_train_set=True)
    print('z = dset[0] ; print(img, av_mask = z)')
    z = dset[0]
    print('image x-ray size:', z[0].shape)
    print('labels', CheXpert.LABELS_ALL, z[1])

    # other: useful functionality
    print(dset.get_other_views_in_study(patient=21e3, study=1))
    print(dset.get_other_views_in_study(patient=21e3, study=1, view=2))
    print(dset.get_other_views_in_study(index=87433))
