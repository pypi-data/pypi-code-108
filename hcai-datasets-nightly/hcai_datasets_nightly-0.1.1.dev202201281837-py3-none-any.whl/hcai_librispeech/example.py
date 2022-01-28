import hcai_datasets
import tensorflow_datasets as tfds
import tensorflow as tf
import pydub
import numpy as np
import soundfile as sf
import os
import tensorflow_io as tfio

def pp_supervised(x,y):
    file_path = bytes.decode(x.numpy())
    audio, sr = sf.read(file_path)
    return audio, sr, y

def pp(speech, text, speaker_id, chapter_id, id):
    file_path = bytes.decode(speech.numpy())
    audio, sr = sf.read(file_path)
    return audio, sr, text, speaker_id, chapter_id, id

@tf.function
def load_wav_16k_mono(filename):
    """ read in a waveform file and convert to 16 kHz mono """

    file_contents = tf.io.read_file(filename)
    wav, sample_rate = tf.audio.decode_wav(
        file_contents,
        desired_channels=1)
    wav = tf.squeeze(wav, axis=-1)
    sample_rate = tf.cast(sample_rate, dtype=tf.int64)
    wav = tfio.AUDIO.resample(wav, rate_in=sample_rate, rate_out=16000)
    return wav

def pp_tf(speech):
    audio = load_wav_16k_mono(speech)
    return audio

ds, ds_info = tfds.load(
    'hcai_librispeech',
    split='dev-clean',
    with_info=True,
    as_supervised=False,
    decoders={
       'speech': tfds.decode.SkipDecoding()
    },
    builder_kwargs={'dataset_dir': os.path.join('\\\\137.250.171.12', 'Librispeech')}
)


ds = ds.map(lambda x : (tf.py_function(func=pp, inp=[x['speech'], x['text'], x['speaker_id'], x['chapter_id'], x['id']], Tout=[tf.float32, tf.int16, tf.string, tf.int64, tf.int64,  tf.string])))
#ds = ds.map(lambda x, y: (pp_tf(x), y))

print('')
audio, sr, text, speaker_id, chapter_id, id = next(ds.as_numpy_iterator())

sf.write('test.flac', audio, sr, format='wav')
