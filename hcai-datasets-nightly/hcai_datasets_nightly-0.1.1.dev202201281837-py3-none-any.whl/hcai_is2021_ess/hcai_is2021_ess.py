"""hcai_is2021_ess dataset."""

import tensorflow_datasets as tfds
import tensorflow as tf
import pathlib
import os

# TODO(hcai_is2021_ess): Markdown description  that will appear on the catalog page.
_DESCRIPTION = """
Description is **formatted** as markdown.

It should also contain any processing which has been applied (if any),
(e.g. corrupted example skipped, images cropped,...):
"""

# TODO(hcai_is2021_ess): BibTeX citation
_CITATION = """
"""


class HcaiIs2021Ess(tfds.core.GeneratorBasedBuilder):
  """DatasetBuilder for hcai_is2021_ess dataset."""

  VERSION = tfds.core.Version('1.0.0')
  RELEASE_NOTES = {
      '1.0.0': 'Initial release.',
  }

  def _info(self) -> tfds.core.DatasetInfo:
    """Returns the dataset metadata."""
    # TODO(hcai_is2021_ess): Specifies the tfds.util.DatasetInfo object
    return tfds.core.DatasetInfo(
        builder=self,
        description=_DESCRIPTION,
        features=tfds.features.FeaturesDict({
            "speech": tfds.features.Text(),
            "label": tf.string,
            "id": tf.string,
            "text":  tfds.features.Text(),
        }),
        # If there's a common (input, target) tuple from the
        # features, specify them here. They'll be used if
        # `as_supervised=True` in `builder.as_dataset`.
        supervised_keys=('speech', 'label'),  # Set to `None` to disable
        homepage='https://dataset-homepage/',
        citation=_CITATION,
        metadata=tfds.core.MetadataDict(sample_rate=16000,)
    )

  def _split_generators(self, dl_manager: tfds.download.DownloadManager):
      """Returns SplitGenerators."""
      label_dir = pathlib.Path(r'Z:\Interspeech\2021\ComParE2021_ESS\dist')
      splits = ['train', 'devel', 'test']
      return { s: self._generate_examples(os.path.join(label_dir), s) for s in splits }

  def _generate_examples(self, dist_dir, set):
      header = True
      with tf.io.gfile.GFile(os.path.join(dist_dir, 'lab', set + '.csv')) as f:
          for line in f:
              if header:
                  header = False
                  continue
              line = line.strip()
              fn, label = line.split(",", 1)
              fn = fn.split('.')[0]
              audio_file = "%s.wav" % fn
              transcript_file = "%s.txt" % fn
              transcript = ''
              transcript_clean = ''
              with tf.io.gfile.GFile(os.path.join(dist_dir, 'text', transcript_file)) as t:
                  for tl in t:
                        transcript = tl

              example = {
                  "id": fn,
                  "speech": os.path.join(dist_dir, 'wav', audio_file),
                  "text": transcript,
                  'label': label
              }
              yield fn, example

