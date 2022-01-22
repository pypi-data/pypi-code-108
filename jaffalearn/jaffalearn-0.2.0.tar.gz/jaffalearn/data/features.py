import torch.nn as nn

from torchaudio.transforms import (
    AmplitudeToDB,
    MelScale,
    Resample,
    Spectrogram,
)


class SpectrogramExtractor(nn.Module):
    def __init__(self,
                 n_fft=1024,
                 hop_length=512,
                 to_db=True,
                 top_db=None,
                 drop_last=False,
                 ):
        super().__init__()

        transforms = [Spectrogram(n_fft, hop_length=hop_length)]
        if to_db:
            transforms.append(AmplitudeToDB(top_db=top_db))
        self.transform = nn.Sequential(*transforms)
        self.drop_last = drop_last

    def forward(self, x, *_):
        if self.drop_last:
            return self.transform(x[..., :-1])
        return self.transform(x)


class MelSpectrogramExtractor(SpectrogramExtractor):
    def __init__(self, sample_rate, n_fft=1024, n_mels=128, **kwargs):
        super().__init__(n_fft, **kwargs)

        # Add a MelScale transform after the Spectrogram transform
        mel_transform = MelScale(n_mels, sample_rate, n_stft=n_fft // 2 + 1)
        transforms = list(self.transform)
        transforms.insert(1, mel_transform)
        self.transform = nn.Sequential(*transforms)


class Resampler(nn.Module):
    def __init__(self, orig_freq, new_freq):
        super().__init__()

        self.transform = Resample(orig_freq, new_freq)

    def __call__(self, x, *_):
        return self.transform(x)
