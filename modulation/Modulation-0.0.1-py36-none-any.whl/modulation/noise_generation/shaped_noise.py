#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 09-12-2020
           """

from pathlib import Path
from typing import Iterable

import numpy

import torchaudio
from draugr.random_utilities.seeding import numpy_seed
from draugr.numpy_utilities import zero_pad_to_power_2
from draugr.torch_utilities import to_tensor
from draugr import next_pow_2
from matplotlib import pyplot
from numpy import fft
from scipy.signal import butter, filtfilt, welch

from modulation.audio_utilities.funcs import hilbert_envelope

__all__ = ["generate_speech_shaped_noise"]


def spectrum_like_noise(
    signal: numpy.ndarray,
    *,
    sampling_rate=40000,
    keep_signal_amp_envelope=False,
    low_pass_cutoff=50,  # Hz
    low_pass_order=6,
    seed: int = 42,
    window_length_sec: float = 20 / 1000,  # 20 ms
    p_overlap: float = 0.5,
    long_term_avg: bool = True
) -> numpy.ndarray:
    """Create a noise with same spectrum as the input signal.
    randomises phase

    Parameters
    ----------
    signal : array_like
        Input signal.
    sampling_rate : int
         Sampling frequency of the input signal. (Default value = 40000)
    keep_signal_amp_envelope : bool
         Apply the envelope of the original signal to the noise. (Default
         value = False)
    low_pass_cutoff : float
    low_pass_order : int
    seed : int
    long_term_avg : bool
    window_length_sec: int
    p_overlap: float


    Returns
    -------
    ndarray
        Noise signal.

    """
    assert window_length_sec > 0
    assert 0 <= p_overlap <= 1
    signal = zero_pad_to_power_2(signal)  # Ensure welch works with any window size
    signal_length = signal.shape[-1]
    window_sum_squares = signal_length  # scaling factor defined as sum of squared samples of window function
    sc = 2 / (
        sampling_rate * window_sum_squares
    )  # Scaling coefficient 2 takes into account removal of energy at negative frequencies (we drop this side of PSD)

    if not long_term_avg:
        n_fft = next_pow_2(signal_length)
        spec = numpy.abs(fft.rfft(signal, n_fft))
        psd = (spec ** 2) * sc
    else:
        n_per_seg = next_pow_2(
            int(sampling_rate * window_length_sec)
        )  # next_pow_2 per seg == n_fft
        n_overlap = int(n_per_seg * p_overlap)
        f, psd = welch(
            signal,
            sampling_rate,
            nperseg=n_per_seg,
            noverlap=n_overlap,
            scaling="density",
            return_onesided=True,
            detrend=False,
            # window='boxcar',
            window="hanning",
        )
        n_fft = n_per_seg
        psd /= signal_length / n_per_seg  # normalise?
    spec = numpy.sqrt((psd / sc))

    noise = []
    runs = signal_length // n_fft
    for i in range(runs + 1):
        numpy_seed(seed + i)
        noise.extend(
            numpy.real(
                fft.irfft(
                    spec
                    * numpy.exp(
                        2 * numpy.pi * 1j * numpy.random.random(spec.shape[-1])
                    ),  # Randomise phase. 0->360, 2 pi rads
                    n_fft,
                )
            )
        )  # Give each spectral component a random phase, PHI(f(k)) = random number,
        # uniformly distributed between 0 and 360 degrees (or equivalently, between 0 and 2Pi radians);

    noise = numpy.array(noise)[:signal_length]

    if keep_signal_amp_envelope:
        [bb, aa] = butter(
            low_pass_order, low_pass_cutoff / (sampling_rate / 2)
        )  # Cutoff Hz, LP filter
        noise *= filtfilt(
            bb,  # numerator
            aa,  # denominator
            hilbert_envelope(signal),  # envelope of speech signal in time domain
        )

    return numpy.expand_dims(noise, 0)


def generate_speech_shaped_noise(
    samples: Iterable[numpy.ndarray],
    sampling_rate,
    *,
    export_path: Path = None,
    long_term_avg=True,
    window_length_sec=20 / 1000,
    p_overlap=0.5
) -> Iterable:
    """
    White (flat-spectrum) noise has more energy at high frequencies, and therefore produces more masking of the higher formants and frication noises than speech-shaped noise, speech shaped noise mask evenly throughout the speech signal spectrum
    """

    samples = numpy.concatenate(samples, -1)[0]
    noise = spectrum_like_noise(
        samples,
        sampling_rate=sampling_rate,
        long_term_avg=long_term_avg,
        window_length_sec=window_length_sec,
        p_overlap=p_overlap,
    )
    if export_path:
        torchaudio.save(str(export_path), to_tensor(noise), sampling_rate)
    return noise


if __name__ == "__main__":

    def reald():
        from draugr.visualisation import ltass_plot
        from modulation.data.audio.speech.recognition.libri_speech import LibriSpeech

        libri_speech = LibriSpeech(
            path=Path.home() / "Data" / "Audio" / "Speech" / "LibriSpeech"
        )
        files, sr = zip(
            *[(v[0].numpy(), v[1]) for _, v in zip(range(20), libri_speech)]
        )
        assert all([sr[0] == s for s in sr[1:]])
        sr = sr[0]

        # from modulation.noise_generation import generate_babble_noise
        # files = generate_babble_noise(samples, sampling_rate)
        samples_len = len(numpy.concatenate(files, -1)[0])

        noise_welch = generate_speech_shaped_noise(
            files, sr, long_term_avg=True, export_path=Path("exclude") / "ssn_welch.wav"
        )[0]
        noise_fft = generate_speech_shaped_noise(
            files, sr, long_term_avg=False, export_path=Path("exclude") / "ssn_fft.wav"
        )[0]
        # noise_welch_full = generate_speech_shaped_noise(files, sr, long_term_avg=True, window_length_sec= samples_len/sr,p_overlap=0)[0]
        files = numpy.concatenate(files, -1)[0]
        torchaudio.save(str(Path("exclude") / "ssn_signal.wav"), to_tensor(files), sr)

        ltass_plot(files, sr, label="signal")
        ltass_plot(noise_welch, sr, label="noise_welch")
        # ltass_plot(noise_welch_full, sr, label='noise_welch_full')
        ltass_plot(noise_fft, sr, label="noise_fft")

        pyplot.legend()
        pyplot.show()

    def synth():
        from draugr.visualisation import ltass_plot
        from modulation.data.audio.speech.recognition.libri_speech import LibriSpeech

        signal_length_sec = 11
        t = numpy.linspace(
            0, signal_length_sec, int(1000 * signal_length_sec), endpoint=False
        )
        signal = (
            numpy.sin(50 * 2 * numpy.pi * t)
            + numpy.sin(200 * 2 * numpy.pi * t)
            + numpy.sin(400 * 2 * numpy.pi * t)
        )
        sr = len(t) / signal_length_sec

        noise_welch = spectrum_like_noise(signal, sampling_rate=sr, long_term_avg=True)[
            0
        ]
        noise_welch_full = spectrum_like_noise(
            signal,
            sampling_rate=sr,
            long_term_avg=True,
            window_length_sec=signal_length_sec,
            p_overlap=0,
        )[0]
        noise_fft = spectrum_like_noise(signal, sampling_rate=sr, long_term_avg=False)[
            0
        ]

        ltass_plot(signal, sr, label="signal")
        ltass_plot(noise_welch, sr, label="noise_welch")
        ltass_plot(noise_welch_full, sr, label="noise_welch_full")
        ltass_plot(noise_fft, sr, label="noise_fft")

        pyplot.legend()
        pyplot.show()

    def distinct_real():
        from draugr.visualisation import ltass_plot
        from modulation.data.audio.speech.recognition.libri_speech import LibriSpeech

        samples = 6
        d_male = iter(
            LibriSpeech(
                path=Path.home() / "Data" / "Audio" / "Speech" / "LibriSpeech",
                custom_subset=LibriSpeech.CustomSubsets.male,
            )
        )
        d_female = iter(
            LibriSpeech(
                path=Path.home() / "Data" / "Audio" / "Speech" / "LibriSpeech",
                custom_subset=LibriSpeech.CustomSubsets.female,
            )
        )
        male_unique = {}
        while len(male_unique) < samples // 2:
            s = next(d_male)
            speaker_id = s[-3]
            if speaker_id not in male_unique:
                male_unique[speaker_id] = s

        female_unique = {}
        while len(female_unique) < samples // 2:
            s = next(d_female)
            speaker_id = s[-3]
            if speaker_id not in female_unique:
                female_unique[speaker_id] = s

        unique = (*male_unique.values(), *female_unique.values())

        files, sr = zip(*[(v[0].numpy(), v[1]) for _, v in zip(range(samples), unique)])
        assert all([sr[0] == s for s in sr[1:]])
        sr = sr[0]

        noise_welch = generate_speech_shaped_noise(
            files, sr, long_term_avg=True, export_path=Path("exclude") / "ssn_welch.wav"
        )[0]
        noise_fft = generate_speech_shaped_noise(
            files, sr, long_term_avg=False, export_path=Path("exclude") / "ssn_fft.wav"
        )[0]
        files = numpy.concatenate(files, -1)[0]
        torchaudio.save(str(Path("exclude") / "ssn_signal.wav"), to_tensor(files), sr)

        ltass_plot(files, sr, label="signal")
        ltass_plot(noise_welch, sr, label="noise_welch")
        ltass_plot(noise_fft, sr, label="noise_fft")

        pyplot.legend()
        pyplot.show()

    # reald()
    # synth()
    distinct_real()
