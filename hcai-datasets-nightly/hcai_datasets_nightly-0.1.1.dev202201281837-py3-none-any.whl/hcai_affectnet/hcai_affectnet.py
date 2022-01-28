"""hcai_affectnet dataset."""

import tensorflow_datasets as tfds
import tensorflow as tf
import pandas as pd
import json
import numpy as np
from pathlib import Path
from tensorflow_datasets.core.splits import Split
from hcai_dataset_utils.statistics import Statistics


_DESCRIPTION = """
Affectnet is a dataset that has been crawled from the internet and annotated with respect to affective classes as well as valence and arousal.
The annotations also include automatically extracted facial landmarks.
Overall the dataset consists of roughly 1Million images. Half of the images are manually annotated where the other half has been annotated automatically.
Since there is currently no official test set available the validation set is used for testing and a split of the training set is used for validation.
The number of images in test is only 5499 since one corrupt image has been deleted
"""

_CITATION = """
@article{mollahosseini2017affectnet,
  title={Affectnet: A database for facial expression, valence, and arousal computing in the wild},
  author={Mollahosseini, Ali and Hasani, Behzad and Mahoor, Mohammad H},
  journal={IEEE Transactions on Affective Computing},
  volume={10},
  number={1},
  pages={18--31},
  year={2017},
  publisher={IEEE}
}
"""

VERSION = tfds.core.Version("1.0.0")
RELEASE_NOTES = {
    "1.0.0": "Initial release.",
}


class HcaiAffectnetConfig(tfds.core.BuilderConfig):
    """BuilderConfig for HcaiAffectnetConfig."""

    def __init__(
        self,
        *,
        include_auto=False,
        ignore_duplicate=True,
        ignore_unsupported_format=True,
        ignore_lists=None,
        **kwargs
    ):
        """BuilderConfig for HcaiAffectnetConfig.
        Args:
          ignore_duplicate: bool. Flag to determine whether the duplicated files in the dataset should be included. Only affects the training set.
          ignore_wrong_format:  bool. Flag to determine whether files that are not in tensorflow compatible encoding should be ignored. Affects all sets.
          ignore_lists: list. Custom ignore lists for additional configurations.
          include_auto: bool. Flag to determine whether the automatically annotated files should be included in the dataset.
          **kwargs: keyword arguments forwarded to super.
        """
        super(HcaiAffectnetConfig, self).__init__(version=VERSION, **kwargs)
        if ignore_lists is None:
            ignore_lists = []

        if ignore_duplicate:
            ignore_lists.append("affect_net_ignore_list_duplicates.json")

        if ignore_unsupported_format:
            ignore_lists.append("affect_net_ignore_list_wrong_format.json")

        self.include_auto = include_auto
        self.ignore_lists = ignore_lists


class HcaiAffectnet(tfds.core.GeneratorBasedBuilder, Statistics):
    """DatasetBuilder for hcai_affectnet dataset."""

    BUILDER_CONFIGS = [
        HcaiAffectnetConfig(
            name="default",
            include_auto=False,
            ignore_duplicate=True,
            ignore_unsupported_format=True,
        ),
        HcaiAffectnetConfig(
            name="inc_auto",
            include_auto=True,
            ignore_duplicate=True,
            ignore_unsupported_format=True,
        ),
        HcaiAffectnetConfig(
            name="emo_net",
            include_auto=False,
            ignore_duplicate=True,
            ignore_unsupported_format=True,
            ignore_lists=['affect_net_emo_net_ignore_list.json']
        ),
    ]

    IMAGE_FOLDER_COL = "image_folder"

    def __init__(self, *, dataset_dir=None, **kwargs):
        self.dataset_dir = dataset_dir
        self.LABELS = [
            "neutral",
            "happy",
            "sad",
            "suprise",
            "fear",
            "disgust",
            "anger",
            "contempt",
            "none",
            "uncertain",
            "non-face",
        ]
        super(HcaiAffectnet, self).__init__(**kwargs)

    def _info(self) -> tfds.core.DatasetInfo:
        """Returns the dataset metadata."""
        return tfds.core.DatasetInfo(
            builder=self,
            description=_DESCRIPTION,
            metadata=tfds.core.MetadataDict({}),
            features=tfds.features.FeaturesDict(
                {
                    # These are the features of your dataset like images, labels ...
                    "image": tfds.features.Image(shape=(None, None, 3)),
                    "expression": tfds.features.ClassLabel(names=self.LABELS),
                    "arousal": tf.float32,
                    "valence": tf.float32,
                    "facial_landmarks": tfds.features.Tensor(
                        shape=(68, 2), dtype=tf.float32
                    ),
                    "rel_file_path": tf.string,
                    #"face_bbox": tf.tuple(),
                }
            ),
            supervised_keys=(
                "image",
                "expression",
            ),
            homepage="http://mohammadmahoor.com/affectnet/",
            citation=_CITATION,
        )

    def _populate_meta_data(self, data: pd.DataFrame):
        """
        Updating the metadata dictionary
        Args:
            data: the dataframe that will be used for calulating the metadata
        """
        for split_name, df in data:
            # Filter only necessary columns
            df_filtered = df.filter(["expression", "arousal", "valence"])

            # Replacing -2 values with nan for the statistics
            df_filtered = df_filtered.applymap(lambda x: np.nan if x == -2 else x)

            # Converting integer to type object to enable correct description
            convert_dict = {"expression": "object"}
            df_filtered = df_filtered.astype(convert_dict)
            self._populate_stats(df_filtered, split_name)

    def _split_generators(self, dl_manager: tfds.download.DownloadManager):
        """Returns SplitGenerators."""
        print("Loading Labels...")

        train_csv_path = (
            Path(self.dataset_dir) / "Manually_Annotated_file_lists" / "training.csv"
        )

        # The official test set has not been released in this version so we use the validation set as test set
        test_csv_path = (
            Path(self.dataset_dir) / "Manually_Annotated_file_lists" / "validation.csv"
        )

        train_csv_path_auto = (
            Path(self.dataset_dir)
            / "Automatically_Annotated_file_lists"
            / "automatically_annotated.csv"
        )

        train_df = pd.read_csv(train_csv_path, index_col=0)
        test_df = pd.read_csv(test_csv_path, index_col=0)
        train_df[self.IMAGE_FOLDER_COL] = ["Manually_Annotated_Images"] * len(train_df)
        test_df[self.IMAGE_FOLDER_COL] = ["Manually_Annotated_Images"] * len(test_df)

        # append automatic labels if not ignored:
        if self.builder_config.include_auto:
            train_df_auto = pd.read_csv(train_csv_path_auto, index_col=0)
            train_df_auto[self.IMAGE_FOLDER_COL] = ["Automatically_Annotated_Images"]
            train_df = pd.concat([train_df, train_df_auto])

        len_train = len(train_df)
        len_test = len(test_df)
        print(
            "...loaded {} images for train\n...loaded {} images for test".format(
                len_train, len_test
            )
        )

        # removing labels that are specified in the ignore-lists
        print("Applying ignore lists...")

        filter_list_path = Path(__file__).parent / "Ignore_Lists"
        for filter_list in self._builder_config.ignore_lists:
            print("... {}:".format(filter_list))
            with open(filter_list_path / filter_list) as json_file:
                filter = json.load(json_file)
                train_df.drop(filter, errors="ignore", inplace=True)
                test_df.drop(filter, errors="ignore", inplace=True)
            print(
                "\t...dropped {} images from train\n\t... dropped {} images from test".format(
                    len_train - len(train_df), len_test - len(test_df)
                )
            )
            len_train = len(train_df)
            len_test = len(test_df)

        print(
            "Final set sizes: \nTrain {}\nTest {}".format(len(train_df), len(test_df))
        )

        data = [(Split.TRAIN, train_df), (Split.TEST, test_df)]

        self._populate_meta_data(data)

        return {
            split_name: self._generate_examples(split_data)
            for split_name, split_data in data
        }

    def _generate_examples(self, label_df):
        for index, row in label_df.iterrows():
            landmarks = np.fromstring(
                    row["facial_landmarks"], sep=";", dtype=np.float32
                ).reshape((68, 2))

            #ymin = row["face_y"]
            #ymax = row["face_height"] + ymin
            #xmin = row["face_x"]
            #xmax = row["face_width"] + xmin

            yield index, {
                "image": Path(self.dataset_dir) / row[self.IMAGE_FOLDER_COL] / index,
                "expression": row["expression"],
                "arousal": row["arousal"],
                "valence": row["valence"],
                "facial_landmarks": landmarks,
                "rel_file_path": row[self.IMAGE_FOLDER_COL] + "/" + index,
                #"face_bbox": tfds.features.BBox(ymin=ymin, xmin=xmin, ymax=ymax, xmax=xmax)
            }
