from upyog.imports import *
from upyog.image.io import *

# We don't need to import anythin from this module because we're only patching stuff
__all__ = []


@fastcore.patch
def __or__(self: Image.Image, other: Image.Image):
    "Horizontally stack two PIL Images"
    assert isinstance(other, Image.Image)
    this_W, this_H = self.size
    that_W, that_H = other.size

    if not this_H == that_H:
        other = other.resize_pad((that_W, this_H))

    widths, heights = zip(*(i.size for i in [self, other]))
    new_img = Image.new("RGB", (sum(widths), max(heights)), 255)

    x_offset = 0
    for img in [self, other]:
        new_img.paste(img, (x_offset, 0))
        x_offset += img.size[0]
    return new_img


@fastcore.patch
def __floordiv__(self: Image.Image, other: Image.Image):
    "Vertically stack two PIL Images"
    assert isinstance(other, Image.Image)
    this_W, this_H = self.size
    that_W, that_H = other.size

    if not this_W == that_W:
        other = other.resize_pad((this_W, that_H))

    widths, heights = zip(*(i.size for i in [self, other]))
    new_img = Image.new("RGB", (max(widths), sum(heights)), 255)

    y_offset = 0
    for img in [self, other]:
        new_img.paste(img, (0, y_offset))
        y_offset += img.size[1]
    return new_img
