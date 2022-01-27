
#https://www.tensorflow.org/tutorials/audio/transfer_learning_audio
# Util functions for loading audio files and ensure the correct sample rate

@tf.function
def load_wav_16k_mono(filename):
  """ read in a waveform file and convert to 16 kHz mono """
  file_contents = tf.io.read_file(filename)
  wav, sample_rate = tf.AUDIO.decode_wav(
    file_contents,
    desired_channels=1)
  wav = tf.squeeze(wav, axis=-1)
  sample_rate = tf.cast(sample_rate, dtype=tf.int64)
  wav = tfio.AUDIO.resample(wav, rate_in=sample_rate, rate_out=16000)
  return wav

testing_wav_data = load_wav_16k_mono(testing_wav_file_name)

_ = plt.plot(testing_wav_data)

# Play the audio file.
display.Audio(testing_wav_data,rate=16000)
