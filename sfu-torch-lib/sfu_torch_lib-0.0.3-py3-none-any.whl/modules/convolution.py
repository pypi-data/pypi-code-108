from torch.nn import Conv2d, ConvTranspose2d


def conv(in_channels: int, out_channels: int, kernel_size: int, stride: int):
    return Conv2d(
        in_channels,
        out_channels,
        kernel_size=(kernel_size, kernel_size),
        stride=(stride, stride),
        padding=(kernel_size // 2, kernel_size // 2),
    )


def deconv(in_channels: int, out_channels: int, kernel_size: int, stride: int):
    return ConvTranspose2d(
        in_channels,
        out_channels,
        kernel_size=(kernel_size, kernel_size),
        stride=(stride, stride),
        output_padding=(stride - 1, stride - 1),
        padding=(kernel_size // 2, kernel_size // 2),
    )
