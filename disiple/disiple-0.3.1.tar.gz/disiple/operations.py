import numpy as np
from scipy import fft
from .signals import TimeSignal, get_samples, get_samples_and_rate, get_both_samples, same_type_as


def circ_convolve(signal1, signal2, num_points=None):
    samples1, samples2 = get_both_samples(signal1, signal2)
    if num_points == None:
        num_points = len(signal1)
    conv_samples = fft.irfft(fft.rfft(samples1, num_points) * fft.rfft(samples2, num_points))
    # conv_samples = signal.convolve(signal1, np.concatenate([signal2, signal2]), mode='same')
    return same_type_as(conv_samples, signal1)


def quantise(input_signal, depth, max_amp=1):
    """signal_quant = quantise(input, depth)

    quantises the input signal uniformly to "depth" bits
    input is assumed to fall within the range [-max_amp, max_amp]
    """
    samples = get_samples(input_signal)

    # clip out of range values
    samples_quant = np.clip(samples, -max_amp, max_amp)
    # scale data into positive range
    samples_quant = (samples_quant + max_amp) / (2 * max_amp)
    # expand data into number of integer values
    samples_quant = samples_quant * ((2**depth) - 1)
    # quantise by rounding
    samples_quant = np.around(samples_quant) / ((2**depth)-1)
    # rescale data
    samples_quant = samples_quant * 2 - max_amp

    return same_type_as(samples_quant, input_signal)


def apply_adsr(input_signal, sustain_amp, attack, decay, release, shape=1, samplerate=None):
    samples, samplerate = get_samples_and_rate(input_signal, samplerate)

    attack_size = round(attack * samplerate)
    decay_size = round(decay * samplerate)
    release_size = round(release * samplerate)
    sustain_size = len(samples) - attack_size - decay_size - release_size
    if sustain_size < 0:
        raise ValueError('The sum of attack, decay and release duration needs to be less than the signal duration')

    a = np.linspace(0, 1, attack_size, endpoint=False)
    d = np.linspace(1, sustain_amp, decay_size, endpoint=False)
    s = np.full(sustain_size, sustain_amp)
    r = np.linspace(sustain_amp, 0, release_size)
    if shape:
        a = a ** (1/shape)
        d = ((d - sustain_amp) / (1 - sustain_amp)) ** shape * (1 - sustain_amp) + sustain_amp
        r = (r / sustain_amp) ** shape * sustain_amp

    adsr_curve = np.concatenate((a, d, s, r))
    return same_type_as(samples * adsr_curve, input_signal)


def apply_gain(input_signal, amount=0, dB=True, saturate=True, samplerate=None):
    samples, samplerate = get_samples_and_rate(input_signal, samplerate)

    gain = 10**(amount/20) if dB else amount
    gain_samples = gain * samples
    if saturate:
        gain_samples = np.clip(gain_samples, -1, 1)

    return same_type_as(gain_samples, input_signal)


def apply_function(input_signal, function, samplerate=None):
    samples, samplerate = get_samples_and_rate(input_signal, samplerate)
    return same_type_as([function(s) for s in samples], input_signal)
