"""hcai_librispeech dataset."""

import tensorflow_datasets as tfds
import tensorflow as tf
import pathlib
import os

_DESCRIPTION = """
LibriSpeech is a corpus of approximately 1000 hours of read English speech with sampling rate of 16 kHz,
prepared by Vassil Panayotov with the assistance of Daniel Povey. The data is derived from read
audiobooks from the LibriVox project, and has been carefully segmented and aligned.87
"""

_CITATION = """
  title={Librispeech: an ASR corpus based on public domain audio books},
  author={Panayotov, Vassil and Chen, Guoguo and Povey, Daniel and Khudanpur, Sanjeev},
  booktitle={Acoustics, Speech and Signal Processing (ICASSP), 2015 IEEE International Conference on},
  pages={5206--5210},
  year={2015},
  organization={IEEE}
}"""

class HcaiLibrispeech(tfds.core.GeneratorBasedBuilder):
    """DatasetBuilder for hcai_librispeech dataset."""

    VERSION = tfds.core.Version('1.0.0')
    RELEASE_NOTES = {
      '1.0.0': 'Initial release.',
    }

    def __init__(self, *, dataset_dir=None, **kwargs):
        super(HcaiLibrispeech, self).__init__(**kwargs)
        self.dataset_dir = os.path.join(dataset_dir)

    def _info(self) -> tfds.core.DatasetInfo:
        """Returns the dataset metadata."""
        return tfds.core.DatasetInfo(
            builder=self,
            description=_DESCRIPTION,
            features=tfds.features.FeaturesDict({
                "speech": tfds.features.Text(),
                "text": tfds.features.Text(),
                "speaker_id": tf.int64,
                "chapter_id": tf.int64,
                "id": tf.string,
            }),
            # If there's a common (input, target) tuple from the
            # features, specify them here. They'll be used if
            # `as_supervised=True` in `builder.as_dataset`.
            supervised_keys=('speech', 'text'),  # Set to `None` to disable
            homepage='https://dataset-homepage/',
            citation=_CITATION,
            metadata=tfds.core.MetadataDict(sample_rate=16000,),
        )

    def _populate_metadata(self, directory):
        # All dirs contain the same metadata.
        self.info.metadata["speakers"] = self._read_metadata_file(
          os.path.join(directory, "LibriSpeech/SPEAKERS.TXT"),
          ["speaker_id", "gender", "subset", "minutes", "name"])
        self.info.metadata["chapters"] = self._read_metadata_file(
          os.path.join(directory, "LibriSpeech/CHAPTERS.TXT"), [
              "chapter_id", "speaker_id", "minutes", "subset", "project_id",
              "book_id", "chapter_title", "project_title"
          ])

    def _read_metadata_file(self, path, field_names):
        metadata = {}
        with tf.io.gfile.GFile(path) as f:
            for line in f:
                if line.startswith(";"):
                    continue
                fields = line.split("|", len(field_names))
                metadata[int(fields[0])] = {
                    k: v.strip() for k, v in zip(field_names[1:], fields[1:])
                }
        return metadata

    def _split_generators(self, dl_manager: tfds.download.DownloadManager):
        """Returns SplitGenerators."""
        self._populate_metadata()

        splits = ['dev-clean', 'dev-other', 'test-clean', 'test-other', 'train-clean-100', 'train-clean-360', 'train-other-500']
        return { s: self._generate_examples(self.dataset_dir / 'Librispeech' / s) for s in splits }

    def _generate_examples(self, directory):
        transcripts_glob = os.path.join(directory, "*/*/*.txt")
        for transcript_file in tf.io.gfile.glob(transcripts_glob):
            path = os.path.dirname(transcript_file)
            with tf.io.gfile.GFile(os.path.join(path, transcript_file)) as f:
                for line in f:
                    line = line.strip()
                    key, transcript = line.split(" ", 1)
                    audio_file = "%s.flac" % key
                    speaker_id, chapter_id = [int(el) for el in key.split("-")[:2]]
                    example = {
                      "id": key,
                      "speaker_id": speaker_id,
                      "chapter_id": chapter_id,
                      "speech": os.path.join(path, audio_file),
                      "text": transcript
                    }
                    yield key, example