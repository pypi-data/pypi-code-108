"""hcai_audioset dataset."""

import tensorflow_datasets as tfds
import tensorflow as tf
import pathlib
import json
import os
import pickle

# TODO(hcai_audioset): Markdown description  that will appear on the catalog page.
_DESCRIPTION = """
Description is **formatted** as markdown.

It should also contain any processing which has been applied (if any),
(e.g. corrupted example skipped, images cropped,...):
"""

# TODO(hcai_audioset): BibTeX citation
_CITATION = """
"""


class HcaiAudioset(tfds.core.GeneratorBasedBuilder):
  """DatasetBuilder for hcai_audioset dataset."""

  VERSION = tfds.core.Version('1.0.0')
  RELEASE_NOTES = {
      '1.0.0': 'Initial release.',
  }

  def _info(self) -> tfds.core.DatasetInfo:
    """Returns the dataset metadata."""
    with open(os.path.join( os.path.dirname(__file__),'ontology.json')) as o:
        ontology = json.load(o)

    return tfds.core.DatasetInfo(
        builder=self,
        description=_DESCRIPTION,
        features=tfds.features.FeaturesDict({
            # These are the features of your dataset like images, labels ...
            'audio': tfds.features.Text(),
            'label': tfds.features.ClassLabel(names=[x['id'] for x in ontology])
        }),
        # If there's a common (input, target) tuple from the
        # features, specify them here. They'll be used if
        # `as_supervised=True` in `builder.as_dataset`.
        supervised_keys=('audio', 'label'),  # Set to `None` to disable
        homepage='https://dataset-homepage/',
        citation=_CITATION,
        metadata=tfds.core.MetadataDict(ontology=ontology)
    )

  def _populate_metadata(self, directory):
    m_path = directory / 'raw' / 'mapping.pickle'
    with open(m_path, 'rb') as m:
        self._mapping = {k : list(v) for k,v in pickle.load(m).items()}
    print('')

  def _split_generators(self, dl_manager: tfds.download.DownloadManager):
    """Returns SplitGenerators."""
    extracted_dir = pathlib.Path(r'Z:\AudioSet')
    self._populate_metadata(extracted_dir)
    splits = ['train']
    return { s: self._generate_examples(extracted_dir) for s in splits }

  def _generate_examples(self, path):
    """Yields examples."""
    for label, samples in self._mapping.items():
        for s in list(samples):
            yield s + '_' + label, {
              'audio': os.path.join(path, 'raw', 'files', s),
              'label': label,
            }
