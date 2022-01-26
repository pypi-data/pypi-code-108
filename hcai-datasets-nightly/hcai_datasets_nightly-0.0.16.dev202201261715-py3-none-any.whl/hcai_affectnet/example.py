import tensorflow_datasets as tfds
import os
import hcai_datasets


ds, ds_info = tfds.load(
    "hcai_affectnet/emo_net",
    split="train",
    #decoders={
    #    "image": tfds.decode.SkipDecoding(),
    #},
    with_info=True,
    as_supervised=False,
    builder_kwargs={"dataset_dir": os.path.join("\\\\137.250.171.12", "Korpora", "AffectNet")},
)

tfds.show_examples(ds, ds_info, cols=3, rows=20)


# ds_iter = ds.as_numpy_iterator()
# class_names = ds_info.features._feature_dict['expression'].names
# for i in range(100):
#  sample = next(ds_iter)
#  plt.imshow(sample['image'] / 255.)
#  plt.title(class_names[sample['expression']])
#  plt.show()
