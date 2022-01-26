from hcai_audioset import HcaiAudioset
import tensorflow_datasets as tfds
import tensorflow as tf
import pydub
import soundfile as sf
import numpy as np
import librosa


def pp(x,y):
    file_path = bytes.decode(x.numpy())
    print(file_path)
    ext = file_path.split('.')[-1]
    codec = None
    a = None
    if ext == 'opus':
        for codec in ['libopus', 'vorbis']:
            try:
                a = pydub.AudioSegment.from_file(file_path, codec=codec)
            except:
                continue
    else:
        a = pydub.AudioSegment.from_file(file_path)

    if not a:
        print('Could not load{}'.format(file_path))
    a = a.set_frame_rate(16000)
    a = a.set_channels(1)
    a = np.array(a.get_array_of_samples())
    a = a.astype(np.int16)
    return a, y


ds, ds_info = tfds.load(
    'hcai_audioset',
    split='train',
    with_info=True,
    as_supervised=True,
    decoders={
       'audio': tfds.decode.SkipDecoding()
    }
)

ds = ds.map(lambda x,y : (tf.py_function(func=pp, inp=[x, y], Tout=[tf.int16, tf.int64])))
#Z:\AudioSet\raw\files\0.opus
#Z:\AudioSet\raw\files\1.opus
#Z:\AudioSet\raw\files\2.opus
#Z:\AudioSet\raw\files\3.opus
#Z:\AudioSet\raw\files\4.opus
#Z:\AudioSet\raw\files\5.m4a
#Z:\AudioSet\raw\files\7.m4a
#Z:\AudioSet\raw\files\8.m4a
#Z:\AudioSet\raw\files\9.m4a

print('')
a = ds.as_numpy_iterator()
for i in range(10):
    print(i)
    audio, label = next(a)
    sf.write('test_{}.wav'.format(i), audio, 16000, format='flac')
