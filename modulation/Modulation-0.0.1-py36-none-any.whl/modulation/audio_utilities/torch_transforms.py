import warnings
from typing import Union, Tuple

import librosa
import numpy
import torch
from torch import nn
import torchaudio

from warg import passes_kws_to


class PreEmphasis(torch.nn.Module):
    def __init__(self, coef: float = 0.97):
        super().__init__()
        self.coef = coef
        # make kernel
        # In pytorch, the convolution operation uses cross-correlation. So, filter is flipped.
        self.register_buffer(
            "flipped_filter",
            torch.FloatTensor([-self.coef, 1.0]).unsqueeze(0).unsqueeze(0),
        )

    def forward(self, input: torch.tensor) -> torch.tensor:
        assert (
            len(input.size()) == 3
        ), "The number of dimensions of input tensor must be 3!"
        # reflect padding to match lengths of in/out
        input = F.pad(input, (1, 0), "reflect")
        return F.conv1d(input, self.flipped_filter)


class InversePreEmphasis(torch.nn.Module):
    """
    Implement Inverse Pre-emphasis by using RNN to boost up inference speed.
    """

    def __init__(self, coef: float = 0.97):
        super().__init__()
        self.coef = coef
        self.rnn = torch.nn.RNN(1, 1, 1, bias=False, batch_first=True)
        # use originally on that time
        self.rnn.weight_ih_l0.data.fill_(1)
        # multiply coefficient on previous output
        self.rnn.weight_hh_l0.data.fill_(self.coef)

    def forward(self, input: torch.tensor) -> torch.tensor:
        x, _ = self.rnn(input.transpose(1, 2))
        return x.transpose(1, 2)


class MelSpectrogram(nn.Module):
    """
    torchaudio MelSpectrogram wrapper for audiomentations's Compose
    """

    @passes_kws_to(torchaudio.transforms.MelSpectrogram)
    def __init__(
        self, clip_min_value=1e-5, *, sample_rate, n_fft, n_mels, f_min, f_max, **kwargs
    ):
        super().__init__()
        self.transform = torchaudio.transforms.MelSpectrogram(
            sample_rate, n_fft, n_mels, f_min, f_max, **kwargs
        )
        self.clip_min_value = clip_min_value

        mel_basis = librosa.filters.mel(
            sr=sample_rate,
            n_fft=n_fft,
            n_mels=n_mels,
            fmin=f_min,
            fmax=f_max,
        ).T
        self.transform.mel_scale.fb.copy_(torch.tensor(mel_basis))

    def forward(
        self, samples: Union[numpy.ndarray, torch.Tensor], sample_rate: int
    ) -> torch.Tensor:
        if not isinstance(samples, torch.Tensor):
            samples = torch.tensor(samples)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            samples = self.transform.forward(samples)
        samples.clamp_(min=self.clip_min_value)
        return samples


class Spectrogram(nn.Module):
    """
    Apply stft and magphase transformations
    """

    def __init__(self, n_fft, win_length, hop_length):
        super().__init__()
        self.n_fft = n_fft
        self.win_length = win_length
        self.hop_length = hop_length

    def forward(
        self, samples: Union[numpy.ndarray, torch.Tensor], sample_rate: int = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Apply transfrom
        :return: two tensors
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            spec = torch.stft(
                samples,
                n_fft=self.n_fft,
                win_length=self.win_length,
                hop_length=self.hop_length,
            )
        mag, phase = torchaudio.functional.magphase(spec)
        return mag, phase


class InverseSpectrogram(nn.Module):
    """
    Convert from magphase to complex and perform istft
    """

    def __init__(self, n_fft, win_length, hop_length):
        super().__init__()
        self.n_fft = n_fft
        self.win_length = win_length
        self.hop_length = hop_length

    def forward(
        self, samples: Union[numpy.ndarray, torch.Tensor], sample_rate: int = None
    ) -> torch.Tensor:
        mag, phase = samples
        spec = torch.stack([torch.cos(phase) * mag, torch.sin(phase) * mag], dim=-1)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            signal = torch.istft(
                spec,
                n_fft=self.n_fft,
                win_length=self.win_length,
                hop_length=self.hop_length,
            )
        return signal


class ToMono(nn.Module):
    """
    Convert stereo signal to mono
    """

    def __call__(
        self, samples: Union[numpy.ndarray, torch.Tensor], sample_rate: int = None
    ) -> torch.Tensor:
        """

        :param samples:
        :param sample_rate: dummy parameter for compatibility
        :return:
        """
        return torch.mean(samples, dim=0)


class Squeeze(nn.Module):
    """
    Transform to squeeze mono channel waveform
    """

    def __call__(self, samples: Union[numpy.ndarray, torch.Tensor], sample_rate: int):
        return samples.squeeze(0)


class ToNumpy(nn.Module):
    """
    Transform to make numpy array
    """

    def __call__(self, samples: Union[numpy.ndarray, torch.Tensor], sample_rate: int):
        return numpy.array(samples)


class ToTorch(nn.Module):
    """
    Transform to make torch.tensor
    """

    def __call__(self, samples: Union[numpy.ndarray, torch.Tensor], sample_rate: int):
        return torch.tensor(samples)


class LogTransform(nn.Module):
    """
    Transform for taking logarithm of mel spectrograms (or anything else)
    :param fill_value: value to substitute non-positive numbers with before applying log
    """

    def __init__(self, fill_value: float = 1e-5) -> None:
        super().__init__()
        self.fill_value = fill_value

    def __call__(self, samples: torch.Tensor, sample_rate: int):
        samples = samples.masked_fill((samples <= 0), self.fill_value)
        return torch.log(samples)
