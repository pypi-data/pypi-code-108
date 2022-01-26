from os.path import join, exists
import PIL
from typing import Optional
import glob
import numpy as np
import pandas as pd
import torch as T
import math


class IntelMobileODTCervical(T.utils.data.Dataset):
    """Intel-MobileODT Cervix Type Dataset of cervix images for classifying
    the visualized cervix as one of three types.

    Summary:
        X: images
        y: categorical labels {0,1,2} (classifying cervix as one of 3 types)

    The dataset has multiple stages:
        - "train" 1481 images + labels
        - "test" 512 images + labels
        - "additional" 4633 images  + labels
        - "test_stg2" 3506 images   (NO labels)

    Note 1: The filesizes range widely, but the distribution of aspect ratios
    is similar across each stage.  We include a method to copy and resize
    the dataset to same size while preserving original aspect ratios.

    Note 2: We arbitrary use label -1 for all "test_stg2" samples, since the
    stage has no labels.

    **Note 3: These stages are not disjoint!  Training images may appear in the
    test set.  Images from one patient are in multiple subsets.  Some images
    are identical and but unfortunately some are different images of the same
    cervix.  Some identical images even have different labels.  These issues
    make the prospect of evaluating on a test set very questionable due to risk
    of overfitting.

        Some discussion of the problem:
          - https://www.kaggle.com/kylehounslow/a-method-for-finding-leaked-images-in-test-set
          - https://www.kaggle.com/aamaia/leeak
          - The dataset (in June 2017) has been modified and some duplicates
          removed.  This code assumes the dataset is downloaded after this date.

        # TODO:
        #  To address the quality problems,
        #    - Evaluate the extent of the issue after March/June 2017 corrections.
        #    - Compute a hash of all images, and use the hash to remove duplicates
        #      from "additional", "train", "test" in that order.
        #    - To create a more "out-of-distribution" test set, use the pairwise
        #      distances between K-nearest samples to remove training imgs.

    Usage:
        ```
        # download dataset to ./data/
        # (Note: This runs a bash script and works on linux)
        IntelMobileODTCervical.download()

        # Use the datasets
        dset_train = IntelMobileODTCervical('train')
        dset_train = IntelMobileODTCervical('train+additional')
        dset_train = IntelMobileODTCervical('test')
        img, label = dset_train[0]

        # Use resized version of dataset
        IntelMobileODTCervical.copy_and_resize_dataset()  # long run time
        dset_train = IntelMobileODTCervical(
            'train', './data/intel_mobileodt_cervical_resized')
        img, label = dset_train[0]
        img.shape == (200,150)
        ```
    """
    LABELS = (1,2,3)
    LABEL_NAMES = ('Type_1', 'Type_2', 'Type_3')

    def __init__(self, stage='train', base_dir='./data/intel_mobileodt_cervical'):
        self.stage = stage
        self.base_dir = base_dir
        if not exists(base_dir):
            raise Exception(
                'Cannot find dataset.  Did you'
                ' IntelMobileODTCervical.download() it?'
                f'  Looked in: \n{base_dir}')
        stages = stage.split('+')
        assert all(
            stage in {'train', 'additional', 'test', 'test_stg2'} for stage in stages)
        # image filepaths
        fps = []
        if 'additional' in stages:
            _fps = ((fp, label) for label in self.LABELS for fp in glob.glob(join(
                base_dir, f'additional_Type_{label}_v2/Type_{label}', '*')))
            _fps = [x for x in _fps if not any(x[0].endswith(fn) for fn in {
                "Type_1/3068.jpg",  # truncated file. usable. discard anyways
                "Type_2/7.jpg",  # truncated file. usable. discard anyways
                "Type_1/5893.jpg",  # empty file
                "Type_2/2845.jpg",  # empty file
                "Type_2/5892.jpg",  # empty file
            })]
            assert len(_fps) == 6734 - 5, 'corrupt dataset'
            fps.extend(_fps)
        if 'train' in stages:
            _fps = (
                (fp, label)
                for st, label in zip(self.LABEL_NAMES, self.LABELS)
                for fp in glob.glob(join(base_dir, 'train/train', st, '*')))
            _fps = [x for x in _fps if not all(x[0].endswith(fn) for fn in {
                "Type_1/1339.jpg",  # still usable
            })]
            assert len(_fps) == 1481-1, 'corrupt dataset'
            fps.extend(_fps)
        if 'test' in stages:
            _df = pd.read_csv(join(base_dir, 'solution_stg1_release.csv'))
            _df['kls'] = _df[list(self.LABEL_NAMES)].values.argmax(1) +1
            _df['fp'] = _df['image_name'].apply(
                lambda x: join(base_dir, 'test/test', x))
            _fps = list(_df[['fp', 'kls']].itertuples(index=False))
            del _df
            assert len(_fps) == 512, 'corrupt dataset'
            fps.extend(_fps)
        if 'test_stg2' in stages:
            _fps = list((x, -1) for x in glob.glob(join(base_dir, 'test_stg2/*')))
            assert len(_fps) == 3506, 'corrupt dataset'
            fps.extend(_fps)
        self.fps = fps

    def __getitem__(self, idx:int):
        return self.getitem(idx)

    def getitem(self, idx:int, load_img=True):
        img_fp, label = self.fps[idx]
        if load_img:
            img = PIL.Image.open(img_fp)
            img = T.from_numpy(np.array(img)).permute(2,0,1)
        else:
            img = None
        return img, T.tensor(label, dtype=T.int8)

    def __len__(self) -> int:
        return len(self.fps)

    def __repr__(self):
        return f'{self.__class__.__name__}:{self.stage}'

    def class_distribution(self):
        """
        Return the count of images for each cervix type.
        Assuming LABELS=(1,2,3)
        """
        y = T.stack([self.getitem(i, False)[1] for i in range(len(self))])
        return y.sort().values.bincount()[1:]

    @staticmethod
    def download():
        """Download the IntelMobileODTCervical dataset via a bash script.

        Bash script works on linux.  Requires kaggle python client api,
        unzip and 7z.

        Always check the source before you run a bash script!"""
        download_intel_mobileodt()

    @staticmethod
    def copy_and_resize_dataset(**kwargs):
        """
        Create copy of dataset with all images resized to (200,150),
        taking care to preserve aspect ratio during resize by padding zeros
        and transposing images.

        Usage:
            copy_and_resize_dataset()
            dset = IntelMobileODTCervical(
                'train', './data/intel_mobileodt_cervical_resized')
        """
        copy_and_resize_dataset(**kwargs)

    @staticmethod
    def fix_aspect_ratio(img):
        """
        Helper pre-processing function to avoid stretching resized images

        Usage:
            preprocess = tvt.Compose([
                IntelMobileODTCervical.fix_aspect_ratio,
                tvt.Resize((133+1/3, 100))
            ])

            for x,y in IntelMobileODTCervical(...):
                x = preprocess(x)
                ...

        IntelMobileODTCervical images almost entirely have aspect ratio of .75
        or 1/.75.  Get them all aligned to .75 aspect ratio, and padding
        zeros if necessary.

        This is useful for resizing, but introduces (hopefully harmless) biases
        that "wide" images are transposed, and that "too tall" images have
        black vertical borders (and in theory, "too wide" images have black
        horizontal borders).
        note: The transposed bias can be removed by randomly transposing
            minibatches.
        """
        aspect = img.shape[2] / img.shape[1]
        # make all images tall not wide (transposing them if necessary)
        if aspect > 1:
            img = img.permute(0,2,1)
            aspect = img.shape[2] / img.shape[1]
        # pad zeros to make aspect ratio .75
        a,b = img.shape[1:]
        if aspect < .75:  # make b bigger so its aspect ratio is .75
            # eqtn: .75 = (b+delta) / a ==> delta = .75a - b
            delta = (.75*a-b)/2
        elif aspect > .75:  # make a bigger so its aspect ratio is .75
            # eqtn: .75 = b/(a+d) ==> d = b/.75 - a
            delta = (b/.75-2)/2
        else:
            delta = 0
        img = T.nn.functional.pad(img, [int(delta), int(math.ceil(delta))])
        assert abs(img.shape[2] / img.shape[1] - .75) < .001, 'code bug'
        return img


def download_intel_mobileodt():
    """Download the IntelMobileODTCervical dataset from a bash script.
    Bash script works on linux.  Requires kaggle python client api,
    unzip and 7z. """
    script = """
# code to download and extract datasets
function intel_mobileodt_cervical() {
  # cervical cancer dataset
  # this dataset has major quality problems and needs to be carefully handled.
  # the training, test and extra set have duplicate images with different ground truth labels!
  if [ ! -e ./intel_mobileodt_cervical_cancer_screening.zip ] ; then
    kaggle competitions download -c intel-mobileodt-cervical-cancer-screening
    mv intel-mobileodt-cervical-cancer-screening.zip intel_mobileodt_cervical_cancer_screening.zip
  fi
  if [ $? != 0 ] ; then
    cat <<EOF
    #
    # Please install kaggle python client api.  https://www.kaggle.com/docs/api
    # The instructions say to go to kaggle website, find your account settings
    # page, and download an api token to ~/.kaggle/kaggle.json.
    #
EOF
    return 1
  fi
  # md5sum - Alex got this md5sum from the dataset version he downloaded.
  # if ! md5sum --status -c <(echo ace43a7f15a0290941ea1104ce0a7f7b ./intel_mobileodt_cervical_cancer_screening.zip) ; then
    # echo "ERROR: intel_mobileodt_cervical: invalid md5sum"
    # return 1
  # fi

  mkdir -p intel_mobileodt_cervical
  pushd intel_mobileodt_cervical
  unzip ../intel_mobileodt_cervical_cancer_screening.zip
  # extract the real test set
  mkdir -p test_stg2
  7z x -pbyecervicalcancer test_stg2.7z
  # fix some data quality issues officially mentioned on Kaggle
  # (?) 80.jpg
  mv train/train/Type_{3,1}/968.jpg
  mv train/train/Type_{3,1}/1120.jpg
  # Note: Data Quality issues:
  # - also there are some 0 byte and incomplete files.
  # - there are duplicates, even dups with different labels
  # - the stages (train / test / additional / test_stg2) are not disjoint.  one
  #   patient may appear in any set.
  # * To avoid modifying dataset beyond these official corrections, the fixes
  #   happen in code.
  popd
  chmod -R -w ./intel_mobileodt_cervical  # protect the dataset
}
set -e
set -u
mkdir -p ./data
pushd ./data
intel_mobileodt_cervical
    """
    from subprocess import check_call
    return check_call(script, shell=True)


def _copy_and_resize_dataset(dset:IntelMobileODTCervical, new_base_dir:str):
    """Copy the given dataset, making smaller size images"""
    import torchvision.transforms as tvt
    from os.path import dirname
    from os import makedirs
    preprocess = tvt.Compose([
        IntelMobileODTCervical.fix_aspect_ratio,
        tvt.Resize((200, 150)),
        tvt.ToPILImage()
        ]) #  lambda x: x/255.,])
    fix_fp = lambda x: x.replace(dset.base_dir, new_base_dir)
    for i, (x,y) in enumerate(dset):
        x = preprocess(x)
        fp = fix_fp(dset.fps[i][0])
        makedirs(dirname(fp), exist_ok=True)
        x.save(fp)


def copy_and_resize_dataset(
        base_dir:Optional[str]=None,
        new_base_dir='./data/intel_mobileodt_cervical_resized'):
    """
    Create copy of dataset with all images resized to (200,150).

    Usage:
        copy_and_resize_dataset()
        dset = IntelMobileODTCervical(
            'train', './data/intel_mobileodt_cervical_resized')
    """
    from subprocess import check_call
    from shutil import copy2
    from os.path import join
    stage = '+'.join(['train', 'test', 'additional', 'test_stg2'])
    if base_dir:
        dset = IntelMobileODTCervical(stage, base_dir=base_dir)
    else:
        dset = IntelMobileODTCervical(stage)
    # copy the images
    _copy_and_resize_dataset(dset, new_base_dir)
    # copy the csv files
    for fp in ['solution_stg1_release.csv']:
        copy2(join(dset.base_dir, fp), join(new_base_dir, fp))
    # make not modifiable
    check_call(f'chmod -R -w {new_base_dir}', shell=True)


def test_iterate_all_samples():
    """
    A basic sanity chec to check we ignored the truncated and empty images

    Iterate through all samples in dataset and load them into memory
    """
    for stage in ['train', 'additional', 'test', 'test_stg2']:
        dset = IntelMobileODTCervical(stage)
        print(stage, 'num samples', len(dset))
        for n,(x,y) in enumerate(dset):
            if x.shape[-1] == 0 or x.shape[-2] == 0:
                print(x.shape)


def test_can_we_resize_images():
    """the short answer: yes"""
    from matplotlib import pyplot as plt
    from subprocess import check_call
    from os.path import exists
    if not exists('./filesizes'):
        check_call(
            # note: need imagemagik (for identify) and gnu parallel.
            r"""
            find data/intel_mobileodt_cervical/ -type f -name "*.jpg"\
            | parallel 'identify -format "%w %h" {} ; echo  \ {} ' > filesizes
            """,
            shell=True)

    # find duplicates
    # find and visualize 1-nearest neighbors
    df = pd.read_csv('filesizes', names=['h', 'w', 'fp'], sep=' ')
    df = df.loc[~df.isnull().any(1)]  # drop 3 empty files
    df['w'] = df['w'].astype(int)
    df['h'] = df['h'].astype(int)
    df['stage'] = df['fp'].str.extract('(train|additional|test_stg2|test)')
    z = df.groupby(['stage', 'h', 'w'])['fp'].count().unstack(['h', 'w']).T.fillna(0)
    z2 = z / z.sum(0)
    z2.plot.bar(title='Distribution of Filesizes Across Stages.  \nNote: test_stg2 is out of distribution')

    df['aspect ratio (h/w)'] = df['h'] / df['w']
    z3 = df.groupby(['stage', 'aspect ratio (h/w)'])['fp'].count()
    z3.name = 'count'
    z3 = z3.reset_index()
    # --> normalize to probabilities
    z3['probability'] = z3.groupby('stage')['count'].transform(lambda x: x/x.sum())
    z3.pivot('aspect ratio (h/w)', 'stage', 'probability').fillna(0).plot(
        title="Distribution of Aspect Ratio Across Stages\nConc: can safely rescale imgs.")
    #  sns.scatterplot(x='aspect ratio (h/w)', y='probability', hue='stage', data=z3.reset_index(), x_jitter=True, y_jitter=True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    from matplotlib import pyplot as plt

    # get the dataset of high res images.
    # IntelMobileODTCervical.download()

    # make a copy of it with downsized (200,150) images.
    # IntelMobileODTCervical.copy_and_resize_dataset()

    # basic tests of dataset class
    #  base_dir = './data/intel_mobileodt_cervical'
    base_dir = './data/intel_mobileodt_cervical_resized'
    dset_train = IntelMobileODTCervical('train', base_dir)
    img1, label1 = dset_train[0]
    dset_add = IntelMobileODTCervical('additional', base_dir)
    img2, label2 = dset_add[0]
    dset_test = IntelMobileODTCervical('test', base_dir)
    img3, label3 = dset_test[0]
    dset_test2 = IntelMobileODTCervical('test_stg2', base_dir)
    img4, label4 = dset_test2[0]
    assert label4 == -1

    dset_combined1 = IntelMobileODTCervical('train+additional')
    assert len(dset_combined1) == len(dset_train) + len(dset_add)
    dset_combined2 = IntelMobileODTCervical('test+test_stg2')
    assert len(dset_combined2) == len(dset_test) + len(dset_test2)

    # visualize
    fig, axs = plt.subplots(2,2)
    for ax, stage, im, label in zip(
            axs.flat,
            ['train', 'additional', 'test', 'test_stg2'],
            [img1, img2, img3, img4],
            [label1, label2, label3, label4]):
        ax.imshow(im.permute(1,2,0))
        ax.set_title(f'dset: {stage}, label: {label.item()}')
    fig.tight_layout()
    plt.show(block=False)

    print('loaded imgs')

    #
    # basic analyses
    #

    # test_iterate_all_samples()
    # test_can_we_resize_images()  # answer: yes.
    # test_duplicates  # TODO in prog
