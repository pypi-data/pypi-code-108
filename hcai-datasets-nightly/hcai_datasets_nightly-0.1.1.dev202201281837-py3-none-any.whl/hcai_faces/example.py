import tensorflow_datasets as tfds
import os
import hcai_datasets


ds, ds_info = tfds.load(
    "hcai_faces",
    split="train",
    as_supervised=True,
    with_info=True,
    builder_kwargs={"dataset_dir": os.path.join("\\\\137.250.171.12", "Korpora", "FACES")},
)

tfds.show_examples(ds, ds_info)
