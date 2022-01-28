import tensorflow_datasets as tfds
import os
import hcai_ckplus


ds, ds_info = tfds.load(
    "hcai_ckplus",
    split="train",
    with_info=True,
    # as_supervised=True,
    builder_kwargs={"dataset_dir": os.path.join("\\\\137.250.171.12", "Korpora", "CK+")},
)

tfds.show_examples(ds, ds_info)
