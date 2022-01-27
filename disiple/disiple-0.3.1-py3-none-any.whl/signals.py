from abc import ABC, abstractmethod
from copy import deepcopy
from pathlib import Path
from math import sqrt
import warnings
import numpy as np
from scipy import fft, signal
from IPython.display import display
from miniaudio import get_file_info, decode_file, SampleFormat, convert_frames
from bokeh.plotting import figure, show
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource
from bokeh.models.mappers import LinearColorMapper
from bokeh.models.ranges import DataRange1d
from bokeh.models.tools import PanTool, BoxZoomTool, WheelZoomTool, ZoomInTool, ZoomOutTool, SaveTool, ResetTool, HoverTool, InspectTool
from bokeh.palettes import Viridis256
from bokeh.io import output_notebook
from .util import Audio


try:
    ipyname = get_ipython().__class__.__name__
    ipymodule = get_ipython().__class__.__module__
    if ipyname == 'ZMQInteractiveShell' or ipymodule == 'google.colab._shell':
        output_notebook()
except NameError:
    pass


def get_samples_and_rate(input_signal, samplerate):
    if isinstance(input_signal, TimeSignal):
        if samplerate is not None:
            print('Explicitly defined samplerate gets ignored when input is a TimeSignal', samplerate)
        samples = input_signal.samples
        samplerate = input_signal.samplerate
    elif np.ndim(input_signal) > 0:
        if samplerate is None:
            raise ValueError('The samplerate needs to be defined explicitly when input is an array or other iterable')
        samples = np.asarray(input_signal)
    else:
        raise TypeError('Only TimeSignals, Numpy arrays or other iterables are supported as input, not {}'.format(type(input_signal)))
    return samples, samplerate


def get_samples(input_signal):
    if isinstance(input_signal, TimeSignal):
        return input_signal.samples
    elif np.ndim(input_signal) > 0:
        return np.asarray(input_signal)
    else:
        raise TypeError('Only TimeSignals, Numpy arrays or other iterables are supported as input, not {}'.format(type(input_signal)))


def _get_compatible_samples(ref_signal, other):
    if isinstance(other, TimeSignal):
        if ref_signal.samplerate != other.samplerate:
            raise ValueError('Signals need to have the same sample rates')
        other_samples = other.samples
    else:
        other_samples = np.asarray(other)
    if np.issubdtype(other_samples.dtype, np.number):
        return other_samples
    raise TypeError('Only TimeSignals or numeric iterables are supported as operands, not {}'.format(type(other)))


def _get_compatible_size_samples(ref_signal, other):
    other_samples = _get_compatible_samples(ref_signal, other)
    if other_samples.size != ref_signal.samples.size:
        raise ValueError('Signals need to have the same size')
    return other_samples


def get_both_samples_and_rate(input_signal1, input_signal2, samplerate=None):
    samples1, samplerate1 = get_samples_and_rate(input_signal1, samplerate)
    samples2, samplerate2 = get_samples_and_rate(input_signal2, samplerate)
    if samplerate1 != samplerate2:
        raise ValueError('Both signals need to have the same samplerate')
    return samples1, samples2, samplerate1


def get_both_samples(input_signal1, input_signal2):
    samples1 = get_samples(input_signal1)
    samples2 = get_samples(input_signal2)
    if isinstance(input_signal1, TimeSignal) and isinstance(input_signal2, TimeSignal) and input_signal1.samplerate != input_signal2.samplerate:
        raise ValueError('Both signals need to have the same samplerate')
    return samples1, samples2


def same_type_as(output_samples, input_signal):
    if isinstance(input_signal, TimeSignal):
        return type(input_signal)(output_samples, input_signal.samplerate)
    else:
        return output_samples


class Signal(ABC):

    @abstractmethod
    def plot(self, **fig_args):
        pass

    def _repr_html_(self):
        return show(self.plot())

    def display(self, **fig_args):
        show(self.plot(**fig_args))

class TimeSignal(Signal):

    def __init__(self, in_data, samplerate=None):
        if isinstance(in_data, Spectrogram):
            if not signal.check_NOLA(in_data.window, in_data._frame_size, in_data._overlap_size):
                raise ValueError('A spectrogram created with this combination of parameters cannot be inverted')
            if not signal.check_COLA(in_data.window, in_data._frame_size, in_data._overlap_size):
                warnings.warn('A spectrogram created with this combination of parameters cannot be perfectly inverted')
            self.times, self.samples = signal.istft(in_data.spectrogram, in_data._samplerate, in_data.window, in_data._frame_size, in_data._overlap_size, in_data._num_bins)
            self.samples = np.clip(self.samples, -1, 1)
            self.samplerate = in_data._samplerate
        else:
            if isinstance(in_data, Spectrum):
                self.samples = fft.irfft(in_data.spectrum, in_data._num_bins, norm='forward')
                self.samplerate = in_data._samplerate
            else:
                if samplerate is None:
                    raise ValueError('Specify sample rate when creating TimeSignal from samples')
                self.samples = in_data
                self.samplerate = samplerate
            self.times = np.arange(len(self.samples)) / self.samplerate

    def plot(self, **fig_args):
        default_args = {
            'width': 900, 'height': 300,
            'x_axis_label': 'time [s]', 'y_axis_label': 'amplitude',
            'tools': 'pan,wheel_zoom,box_zoom,zoom_in,zoom_out,save,reset',
            'active_drag': 'pan',
            'output_backend': 'webgl',
        }
        fig = figure(**{**default_args, **fig_args})
        fig.line(self.times, self.samples, line_width=2)
        return fig


    def __len__(self):
        return len(self.times)


    def __add__(self, other):
        if np.isscalar(other):
            return same_type_as(self.samples + other, self)
        other_samples = _get_compatible_size_samples(self, other)
        return same_type_as(self.samples + other_samples, self)


    def __mul__(self, other):
        if np.isscalar(other):
            return same_type_as(self.samples * other, self)
        other_samples = _get_compatible_size_samples(self, other)
        return same_type_as(self.samples * other_samples, self)


    def __and__(self, other):
        if np.isscalar(other):
            return same_type_as(np.tile(self.samples, other), self)
        other_samples = _get_compatible_samples(self, other)
        return same_type_as(np.concatenate((self.samples, other_samples)), self)


    def rms(self):
        return sqrt(self.power(dB=False))


    def power(self, dB=True):
        power = np.mean(self.samples ** 2)
        return 10*np.log10(power) if dB else power


    def filter(self, coefficients):
        if isinstance(coefficients, tuple):
            if len(coefficients) == 1:
                numerator, = coefficients
                denominator = 1
            else:
                numerator, denominator = coefficients
                filtered_samples = signal.lfilter(numerator, denominator, self.samples)
        else:
            filtered_samples = signal.lfilter(coefficients, 1, self.samples)
        return same_type_as(filtered_samples, self)


    def resample(self, samplerate):
        resampled_signal = deepcopy(self)
        if samplerate != self.samplerate:
            resampled_signal.samplerate = samplerate
            resampled_signal.samples = np.frombuffer(convert_frames(
                SampleFormat.FLOAT32, 1, self.samplerate, self.samples.astype(np.float32).tobytes(),
                SampleFormat.FLOAT32, 1, samplerate
            ), dtype=np.float32)
            resampled_signal.times = np.arange(len(resampled_signal.samples)) / samplerate
            resampled_signal.samples = np.clip(resampled_signal.samples, -1, 1)
        return resampled_signal


class AudioSignal(TimeSignal):

    def __init__(self, in_data, samplerate=None):
        if isinstance(in_data, (str, Path)):
            if samplerate is None:
                file_info = get_file_info(in_data)
                samplerate = file_info.sample_rate
            decoded_file = decode_file(filename=in_data, output_format=SampleFormat.FLOAT32, nchannels=1, sample_rate=samplerate)
            samples = np.asarray(decoded_file.samples)
            super().__init__(samples, samplerate)
        else:
            super().__init__(in_data, samplerate)

    def play(self, normalize=False):
        return display(Audio(self.samples, rate=self.samplerate, normalize=normalize))

    def plot(self, **fig_args):
        default_args = {
            'width': 900, 'height': 300,
            'x_axis_label': 'time [s]', 'y_axis_label': 'amplitude',
            'y_range': (-1.09, 1.09),
            'tools': [
                PanTool(dimensions='width'),
                BoxZoomTool(),
                WheelZoomTool(dimensions='width'),
                ZoomInTool(dimensions='width'),
                ZoomOutTool(dimensions='width'),
                SaveTool(),
                ResetTool(),
            ],
            'active_drag': 'auto',
            'active_inspect': 'auto',
            'active_scroll': 'auto',
            'toolbar_location': 'above',
            'tooltips': [('time [s]', '@x{0.000}'), ('amplitude', '@y{0.000}')],
        }
        kwargs = {**default_args, **fig_args}
        if kwargs['tooltips'] is not None:
            kwargs['tools'].append(HoverTool(mode='vline'))
        fig = figure(**kwargs)
        fig.line(self.times, self.samples, line_width=2)
        return fig


class Spectrum(Signal):

    def __init__(self, in_data, dB=True, num_bins=None, exponent=1, norm_single_side_band=False, samplerate=None):
        samples, samplerate = get_samples_and_rate(in_data, samplerate)

        if num_bins is None:
            num_bins = len(samples)

        self._samplerate = samplerate
        self._num_bins = num_bins
        self.exponent = exponent
        self._norm_single_side_band = norm_single_side_band
        self.dB = dB

        spectrum = fft.rfft(samples, num_bins, norm='forward')
        self.magnitude = np.abs(spectrum)
        self.phase = np.angle(spectrum)
        self.frequencies = np.arange(len(spectrum)) * samplerate / num_bins

        if norm_single_side_band:
            if self._num_bins % 2 == 0:
                self.magnitude[1:-1] *= sqrt(2)
            else:
                self.magnitude[1:] *= sqrt(2)
        if dB:
            self.magnitude = 20 * np.log10(np.clip(self.magnitude, 1e-6, None))
        else:
            self.magnitude **= exponent


    def plot(self, **fig_args):
        default_args = {
            'width': 900, 'height': 300,
            'x_axis_label': 'frequency [Hz]', 'y_axis_label': 'magnitude',
            'tools': [
                PanTool(),
                BoxZoomTool(),
                WheelZoomTool(),
                ZoomInTool(),
                ZoomOutTool(),
                SaveTool(),
                ResetTool(),
            ],
            'active_drag': 'auto',
            'active_inspect': 'auto',
            'active_scroll': 'auto',
            'toolbar_location': 'above',
            'tooltips': [('frequency [Hz]', '@x{0.0}'), ['magnitude', '@y{0.000}']],
        }
        if self.exponent == 2 or self.dB:
            default_args['y_axis_label'] = 'power'
            default_args['tooltips'][-1][0] = 'power'
        if self.dB:
            default_args['y_axis_label'] += ' [dB]'
            default_args['tooltips'][-1][0] += ' [dB]'
        kwargs = {**default_args, **fig_args}
        if kwargs['tooltips'] is not None:
            kwargs['tools'].append(HoverTool(mode='vline'))
        fig = figure(**kwargs)
        if isinstance(fig.x_range, DataRange1d):
            fig.x_range.range_padding = 0
        if isinstance(fig.y_range, DataRange1d):
            fig.y_range.range_padding = 0
        fig.line(self.frequencies, self.magnitude, line_width=2)
        return fig


    def __len__(self):
        return len(self.frequencies)


    def rms(self):
        return sqrt(self.power(dB=False))


    def power(self, dB=True):
        if self.dB:
            power_per_freq = 10 ** (self.magnitude / 10)
        else:
            power_per_freq = self.magnitude ** (2/self.exponent)
        if self._norm_single_side_band:
            power = np.sum(power_per_freq)
        elif self._num_bins % 2 == 0:
            power = power_per_freq[0] + 2*np.sum(power_per_freq[1:-1]) + power_per_freq[-1]
        else:
            power = power_per_freq[0] + 2*np.sum(power_per_freq[1:])
        return 10*np.log10(power) if dB else power


    def set_magnitude(self, value, start=None, end=None):
        start_idx = np.argmin(np.abs(self.frequencies - start)) if start is not None else 0
        end_idx = np.argmin(np.abs(self.frequencies - end)) if end is not None else len(self.frequencies)-1
        modified_spectrum = deepcopy(self)
        modified_spectrum.magnitude[start_idx:end_idx+1] = value
        return modified_spectrum


    def modify_magnitude(self, amount, start=None, end=None):
        start_idx = np.argmin(np.abs(self.frequencies - start)) if start is not None else 0
        end_idx = np.argmin(np.abs(self.frequencies - end)) if end is not None else len(self.frequencies)-1
        modified_spectrum = deepcopy(self)
        if self.dB:
            modified_spectrum.magnitude[start_idx:end_idx+1] = np.clip(modified_spectrum.magnitude[start_idx:end_idx+1] + amount, -120, None)

        else:
            modified_spectrum.magnitude[start_idx:end_idx+1] *= amount
        return modified_spectrum


    @property
    def spectrum(self):
        if self.dB:
            magnitude = 10 ** (self.magnitude / 20)
        else:
            magnitude = self.magnitude ** (1/self.exponent)
        if self._norm_single_side_band:
            if self._num_bins % 2 == 0:
                self.magnitude[1:-1] /= sqrt(2)
            else:
                self.magnitude[1:] /= sqrt(2)
        return magnitude * np.exp(1j*self.phase)


class PowerSpectrum(Spectrum):
    def __init__(self, in_data, **kwargs):
        exponent = kwargs.pop('exponent', None)
        if exponent is not None and exponent != 2:
            warnings.warn('Magnitude exponent is automatically set to 2 for a PowerSpectrum')
        super().__init__(in_data, exponent=2, **kwargs)


class Spectrogram(Signal):

    def __init__(self, input_signal, frame_duration, step_duration, dB=True, num_bins=None, window='hann', exponent=1, samplerate=None):
        samples, samplerate = get_samples_and_rate(input_signal, samplerate)

        self.window = window
        self.exponent = exponent
        self.dB = dB

        self._samplerate = samplerate
        self._frame_size = round(frame_duration * samplerate)
        self._overlap_size = round((frame_duration-step_duration) * samplerate)
        self._num_bins = num_bins if num_bins is not None else self._frame_size

        self.frequencies, self.times, spectrogram = signal.stft(samples, fs=samplerate, window=window, nperseg=self._frame_size, noverlap=self._overlap_size, nfft=num_bins)
        self.magnitude = np.abs(spectrogram)
        self.phase = np.angle(spectrogram)

        if dB:
            self.magnitude = 20 * np.log10(np.clip(self.magnitude, 1e-6, None))
        else:
            self.magnitude **= exponent


    def plot(self, lowest_value=None, highest_value=None, palette=None, **fig_args):
        if not palette:
            palette = Viridis256
        if not lowest_value:
            lowest_value = np.min(self.magnitude)
        if not highest_value:
            highest_value = np.max(self.magnitude)

        default_args = {
            'width': 900, 'height': 400,
            'x_axis_label': 'time [s]', 'y_axis_label': 'frequency [Hz]',
            'tools': 'pan,wheel_zoom,box_zoom,zoom_in,zoom_out,save,reset',
            'active_drag': 'pan',
            'active_inspect': 'auto',
            'active_scroll': 'auto',
            'toolbar_location': 'above',
            'tooltips': [('time [s]', '@time{0.000}'), ('frequency [Hz]', '@frequency{0.0}'), ['magnitude', '@magnitude{0.000}']],
        }

        if self.exponent == 2 or self.dB:
            default_args['tooltips'][-1][0] = 'power'
        if self.dB:
            default_args['tooltips'][-1][0] += ' [dB]'
        if fig_args.get('tooltips') is not None and self.magnitude.size > 2000000:
            fig_args['tooltips'] = None
            warnings.warn('Tooltips are automatically disabled when plotting large spectrograms for performance reasons. '
                          'Pass "tooltips=None" to silence this warning.')

        fig = figure(**{**default_args, **fig_args})
        if isinstance(fig.x_range, DataRange1d):
            fig.x_range.range_padding = 0
        if isinstance(fig.y_range, DataRange1d):
            fig.y_range.range_padding = 0
        if [t for t in fig.tools if isinstance(t, InspectTool)]:
            all_times = np.broadcast_to(self.times, self.magnitude.shape)
            all_freqs = np.broadcast_to(self.frequencies.reshape(-1, 1), self.magnitude.shape)
            step_time = (self._frame_size - self._overlap_size) / self._samplerate
            delta_freq = self._samplerate / self._num_bins
            img_source = ColumnDataSource({'magnitude': self.magnitude.reshape(-1, 1, 1).tolist(), 'time': all_times.ravel() , 'frequency': all_freqs.ravel()})
            color_indices = np.rint(np.interp(self.magnitude, (lowest_value, highest_value), (0, len(palette)-1))).astype(int)
            img_source.data['color'] = [palette[i] for i in color_indices.ravel()]
            fig.rect(x='time', y='frequency', width=step_time, height=delta_freq, color='color', source=img_source)
        else:
            mapper = LinearColorMapper(palette=palette, low=lowest_value, high=highest_value)
            fig.image([self.magnitude], x=self.times[0], y=self.frequencies[0], dw=self.times[-1], dh=self.frequencies[-1], color_mapper=mapper)
        return fig


    @property
    def spectrogram(self):
        if self.dB:
            magnitude = 10 ** (self.magnitude / 20)
        else:
            magnitude = self.magnitude ** (1/self.exponent)
        return magnitude * np.exp(1j*self.phase)


    def spectrum_at(self, *, time=None, index=None):
        if (time is None and index is None) or (time is not None and index is not None):
            raise ValueError('Specify either the time or the index of the requested spectrum')
        if time is not None:
            index = np.argmin(np.abs(self.times - time))
        spectrum = Spectrum([0], samplerate=self._samplerate, num_bins=self._num_bins, exponent=self.exponent, dB=self.dB)
        spectrum.magnitude = self.magnitude[:, index]
        spectrum.phase = self.phase[:, index]
        spectrum.frequencies = self.frequencies
        return spectrum
