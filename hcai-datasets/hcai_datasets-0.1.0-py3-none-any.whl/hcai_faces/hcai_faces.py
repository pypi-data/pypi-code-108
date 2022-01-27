"""hcai_faces dataset."""

import tensorflow as tf
import tensorflow_datasets as tfds
import pandas as pd
from tensorflow_datasets.core.splits import Split
from pathlib import Path
from hcai_dataset_utils.statistics import Statistics


_DESCRIPTION = """
FACES is a set of images of naturalistic faces of 171 young (n = 58), middle-aged (n = 56), and older (n = 57) women and 
men displaying each of six facial expressions: neutrality, sadness, disgust, fear, anger, and happiness. 
The FACES database was developed between 2005 and 2007 by Natalie C. Ebner, Michaela Riediger, 
and Ulman Lindenberger at the Center for Lifespan Psychology, Max Planck Institute for Human Development, Berlin, Germany.
"""

_CITATION = """
@article{ebner2010faces,
  title={FACES—A database of facial expressions in young, middle-aged, and older women and men: Development and validation},
  author={Ebner, Natalie C and Riediger, Michaela and Lindenberger, Ulman},
  journal={Behavior research methods},
  volume={42},
  number={1},
  pages={351--362},
  year={2010},
  publisher={Springer}
}
"""


class HcaiFaces(tfds.core.GeneratorBasedBuilder, Statistics):
    """DatasetBuilder for hcai_faces dataset."""

    VERSION = tfds.core.Version("1.0.0")
    RELEASE_NOTES = {
        "1.0.0": "Initial release.",
    }

    def __init__(self, *, dataset_dir=None, **kwargs):
        super(HcaiFaces, self).__init__(**kwargs)
        self.dataset_dir = Path(dataset_dir) / "bilder"

    def _info(self) -> tfds.core.DatasetInfo:
        """Returns the dataset metadata."""
        return tfds.core.DatasetInfo(
            builder=self,
            description=_DESCRIPTION,
            metadata=tfds.core.MetadataDict({}),
            features=tfds.features.FeaturesDict(
                {
                    # These are the features of your dataset like images, labels ...
                    "image": tfds.features.Image(shape=(3543, 2835, 3)),
                    "id": tf.int64,
                    "age": tfds.features.ClassLabel(names=["y", "o", "m"]),
                    "gender": tfds.features.ClassLabel(names=["m", "f"]),
                    "emotion": tfds.features.ClassLabel(
                        names=["a", "d", "f", "h", "n", "s"]
                    ),
                    "set": tfds.features.ClassLabel(names=["a", "b"]),
                    "rel_file_path": tf.string,
                }
            ),
            supervised_keys=("image", "emotion"),
            homepage="https://dataset-homepage/",
            citation=_CITATION,
        )

    def _populate_meta_data(self, data):
        df = pd.DataFrame(data, columns=["id", "age", "gender", "emotion", "set"])
        self._populate_stats(df)

    def _split_generators(self, dl_manager: tfds.download.DownloadManager):
        """Returns SplitGenerators."""
        f_names = list(self.dataset_dir.glob("*.jpg"))
        parsed = [n.stem.split("_") for n in f_names]
        self._populate_meta_data(parsed)

        return {
            Split.TRAIN: self._generate_examples(zip(f_names, parsed)),
        }

    def _generate_examples(self, files):
        """Yields examples.
        # Labels are parese using filenames:
        # "ID_ageGroup_gender_emotion_pictureSet.jpg"""
        for f, p in files:

            id, age, gender, emotion, set = p

            yield str(f), {
                "image": f,
                "id": int(id),
                "age": age,
                "gender": gender,
                "emotion": emotion,
                "set": set,
                "rel_file_path": str(f.relative_to(f.parents[1])),
            }
