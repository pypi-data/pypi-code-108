import math
import numpy as np
from matplotlib import animation
import matplotlib.pyplot as plt
from IPython.display import display, HTML
from .signals import get_samples, get_samples_and_rate, get_both_samples


def sine_approx(signal, samplerate=None, include_cosines=False, controls=True, min_freq=0, figsize=(12, 6), title='', fps=5):
    samples, samplerate = get_samples_and_rate(signal, samplerate)
    num_samples = len(samples)
    timepoints = np.arange(num_samples) / samplerate
    
    if min_freq == 0:
        min_freq = samplerate / num_samples
    
    num_freqs = math.ceil((samplerate / 2) / min_freq) + 1
    
    freqs = np.empty(num_freqs)
    sin_corr = np.empty(num_freqs)
    cos_corr = np.empty(num_freqs)
    cumul = np.zeros(num_samples)
    
    fig, axes = plt.subplots(2, figsize=figsize)
    fig.suptitle(title)
    fig.subplots_adjust(hspace=0.4)
    
    sine_components, = axes[0].plot([], [], lw=2, marker='s', linestyle='None', color='C0')
    cosine_components, = axes[0].plot([], [], lw=2, marker='o', linestyle='None', color='C1')
    progress = axes[0].axvline(0, color='k')
    axes[0].set_xlim((0, samplerate / 2))
    if include_cosines:
        axes[0].set_xlabel('frequencies of sine and cosine components [Hz]')
        axes[0].legend([sine_components, cosine_components], ['sines', 'cosines'], loc='upper right', frameon=False)
    else:
        axes[0].set_xlabel('frequencies of sine components [Hz]')
    axes[0].set_ylim((-1.1, 1.3))
    axes[0].set_ylabel('correlation coefficient')
    label = axes[0].text(0.2, 1.11, '')
    
    axes[1].plot(timepoints, samples, lw=2, color='C2')
    approx, = axes[1].plot([], [], lw=2, color='C3')
    axes[1].set_xlim((0, timepoints[-1]))
    axes[1].set_xlabel('time [s]')
    axes[1].set_ylim((-1.2, 1.2))
    axes[1].set_ylabel('amplitude')

    def animate(i):
        # compute contribution of current sinusoidal component to signal
        freqs[i] = min_freq * i
        cur_sin = np.sin(2*np.pi*freqs[i]*timepoints)
        sin_corr[i] = np.correlate(cur_sin, samples) / (num_samples / 2)
        nonlocal cumul
        cumul += sin_corr[i] * cur_sin
        if include_cosines:
            cur_cos = np.cos(2*np.pi*freqs[i]*timepoints)
            cos_corr[i] = np.correlate(cur_cos, samples) / (num_samples / 2)
            cumul += cos_corr[i] * cur_cos

        
        # plot
        if include_cosines:
            x_offset = samplerate / 2 / num_freqs / 10 # offset of 1/10th of inter-marker distance to avoid overlapping markers
            sine_components.set_data(freqs[:i+1]-x_offset, sin_corr[:i+1])
            cosine_components.set_data(freqs[:i+1]+x_offset, cos_corr[:i+1])
            label.set_text('{} Hz, sin corr {:.3f}, cos corr {:.3f}'.format(freqs[i], sin_corr[i], cos_corr[i]))
        else:
            sine_components.set_data(freqs[:i+1], sin_corr[:i+1])
            label.set_text('{} Hz, sin corr {:.3f}'.format(freqs[i], sin_corr[i]))
#         update_stemcontainer_lc(stems, output[:i])
        progress.set_data([freqs[i], freqs[i]], [0, 1])
        approx.set_data(timepoints, cumul)
        return (sine_components, cosine_components, progress, approx, label)
    
    anim = animation.FuncAnimation(fig, animate, frames=num_freqs, interval=1000/fps, blit=True, repeat=False)
    if controls:
        display(HTML(anim.to_jshtml()))
    else:
        display(HTML(anim.to_html5_video()))
    plt.close(fig)


def autocorrelate(signal, controls=True, figsize=(12, 6), title='', fps=5):
    samples = get_samples(signal)
    acorrs = np.correlate(samples, samples, mode='full')
    _shift_animation(samples, samples, False, acorrs, 'acorr', controls, figsize, ['original signal', 'time-shifted copy'], title, fps)


def crosscorrelate(signal1, signal2, controls=True, figsize=(12, 6), legend=['signal1', 'signal2'], title='', fps=5):
    samples1, samples2 = get_both_samples(signal1, signal2)
    xcorrs = np.correlate(samples1, samples2, mode='full')
    _shift_animation(samples1, samples2, False, xcorrs, 'xcorr', controls, figsize, (legend[0], 'time-shifted ' + legend[1]), title, fps)    


def convolve(signal1, signal2, controls=True, figsize=(12, 6), legend=['signal1', 'signal2'], title='', fps=5):
    longest_samples, shortest_samples, swapped = _get_both_samples_ordered(signal1, signal2)
    convs = np.convolve(longest_samples, shortest_samples, mode='full')
    if swapped:
        legend = ('flipped & time-shifted ' + legend[0], legend[1])
    else:
        legend = (legend[0], 'flipped & time-shifted ' + legend[1])
    _shift_animation(longest_samples, np.flipud(shortest_samples), swapped, convs, 'conv', controls, figsize, legend, title, fps)


def _get_both_samples_ordered(signal1, signal2):
    samples1, samples2 = get_both_samples(signal1, signal2)
    if len(samples2) > len(samples1):
        return samples2, samples1, True
    else:
        return samples1, samples2, False


def _shift_animation(samples1, samples2, swapped, values, label, controls, figsize, legend, title, fps, init_func=None):
    length1 = len(samples1)
    length2 = len(samples2)

    fig, axes = plt.subplots(2, figsize=figsize)
    fig.suptitle(title)
    fig.subplots_adjust(hspace=0.4)
    
    axes[0].set_xlim((-length2, length1))
    axes[0].set_xlabel('lags')
    axes[0].set_ylim((-1.1, 1.3))
    axes[0].set_ylabel('amplitude')
    if swapped:
        color1, color2 = 'C1', 'C0'
    else:
        color1, color2 = 'C0', 'C1'
    waveform1, = axes[0].plot(np.arange(length1), samples1, lw=2, color=color1)
    waveform2, = axes[0].plot([], [], lw=2, color=color2)
    if swapped:
        legend_order = [waveform2, waveform1]
    else:
        legend_order = [waveform1, waveform2]
    axes[0].legend(legend_order, legend, loc='upper right', frameon=False, ncol=2)
    progress = axes[0].axvline(0, color='k')
    text = axes[0].text(-length2+2, 1, '')
    
    value_plot, = axes[1].plot([], [], lw=2, color='C2')
    axes[1].set_xlim((-length2, length1))
    axes[1].set_xlabel('lags')
    axes[1].set_ylim((np.amin(values), np.amax(values)))
    axes[1].set_ylabel('amplitude')

    lags = np.arange(-length2+1, length1)

    def animate(i):
        waveform2.set_data(np.arange(lags[i], lags[i]+length2), samples2)
        text.set_text('lag: {}, {}: {:.3f}'.format(lags[i], label, values[i]))
        progress.set_data([lags[i], lags[i]], [0, 1])
        value_plot.set_data(lags[:i+1], values[:i+1])
        return waveform2, value_plot, progress, text
    
    anim = animation.FuncAnimation(fig, animate, frames=np.arange(len(lags)), interval=1000/fps, blit=True, repeat=False)
    if controls:
        display(HTML(anim.to_jshtml()))
    else:
        display(HTML(anim.to_html5_video()))
    plt.close(fig)
