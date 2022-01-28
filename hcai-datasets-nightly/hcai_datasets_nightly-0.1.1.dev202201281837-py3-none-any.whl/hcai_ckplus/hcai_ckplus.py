"""hcai_ckplus dataset."""
import tensorflow as tf
import tensorflow_datasets as tfds
import pandas as pd
from tensorflow_datasets.core.splits import Split
from pathlib import Path
from hcai_dataset_utils.statistics import Statistics


_DESCRIPTION = """
The Extended Cohn-Kanade (CK+) dataset contains 593 video sequences from a total of 123 different subjects, ranging from 18 to 50 years of age with a variety of genders and heritage.
"""

_CITATION = """
@inproceedings{lucey2010extended,
  title={The extended cohn-kanade dataset (ck+): A complete dataset for action unit and emotion-specified expression},
  author={Lucey, Patrick and Cohn, Jeffrey F and Kanade, Takeo and Saragih, Jason and Ambadar, Zara and Matthews, Iain},
  booktitle={2010 ieee computer society conference on computer vision and pattern recognition-workshops},
  pages={94--101},
  year={2010},
  organization={IEEE}
}
"""


class HcaiCkplus(tfds.core.GeneratorBasedBuilder, Statistics):
    """DatasetBuilder for hcai_ckplus dataset."""

    VERSION = tfds.core.Version("1.0.0")
    RELEASE_NOTES = {
        "1.0.0": "Initial release.",
    }

    LABELS = [
        "neutral",
        "anger",
        "contempt",
        "disgust",
        "fear",
        "happy",
        "sadness",
        "suprise",
    ]

    def __init__(self, *, dataset_dir=None, **kwargs):
        self.dataset_dir = Path(dataset_dir)
        super(HcaiCkplus, self).__init__(**kwargs)

    def _info(self) -> tfds.core.DatasetInfo:
        """Returns the dataset metadata."""
        return tfds.core.DatasetInfo(
            builder=self,
            description=_DESCRIPTION,
            metadata=tfds.core.MetadataDict({}),
            features=tfds.features.FeaturesDict(
                {
                    "image": tfds.features.Image(shape=(None, None, 3)),
                    # 0=neutral, 1=anger, 2=contempt, 3=disgust, 4=fear, 5=happy, 6=sadness, 7=surprise)
                    "label": tfds.features.ClassLabel(names=self.LABELS),
                    "rel_file_path": tf.string,
                }
            ),
            # If there's a common (input, target) tuple from the
            # features, specify them here. They'll be used if
            # `as_supervised=True` in `builder.as_dataset`.
            supervised_keys=("image", "label"),  # Set to `None` to disable
            homepage="https://dataset-homepage/",
            citation=_CITATION,
        )

    def _populate_meta_data(self, data):
        df = pd.DataFrame(data, columns=["file_name", "emotion"])
        df = df.drop(columns="file_name")
        self._populate_stats(df)

    def _split_generators(self, dl_manager: tfds.download.DownloadManager):
        """Returns SplitGenerators."""

        emo_anno_files = list(self.dataset_dir.glob("Emotion/**/**/*.txt"))
        samples = []

        for ef in emo_anno_files:
            with open(ef, "r") as f:
                emotion = self.LABELS[int(float(f.readline().strip()))]
                fn_img = ef.stem.replace("_emotion", ".png")
                samples.append((fn_img, emotion))

                # add neutral images
                fn_img_neut = ef.stem.rsplit("_", 2)[0] + "_00000001.png"
                samples.append((fn_img_neut, "neutral"))

        self._populate_meta_data(samples)
        return {Split.TRAIN: self._generate_examples(samples)}

    def _generate_examples(self, files):
        """Yields examples."""

        for f, e in files:
            rel_path = (Path(*f.split("_")[:-1]) / f).resolve()
            yield str(f), {
                "image": self.dataset_dir / "cohn-kanade-images" / rel_path,
                "label": e,
                "rel_file_path": str(rel_path),
            }
