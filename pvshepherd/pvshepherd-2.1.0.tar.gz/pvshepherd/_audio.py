import argparse
import wave

import numpy as np


def pcm_to_wave(input_pcm, output):
    pcm_array_int16 = np.array(input_pcm).astype(np.int16)
    with wave.open(output, 'wb') as f:
        f.setparams((1, 2, 16000, 0, 'NONE', 'NONE'))
        f.writeframes(pcm_array_int16)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_pcm', required=True)
    parser.add_argument('--output_path', required=True)
    args = parser.parse_args()

    pcm_to_wave(args.input_pcm, args.output_path)


if __name__ == '__main__':
    main()
