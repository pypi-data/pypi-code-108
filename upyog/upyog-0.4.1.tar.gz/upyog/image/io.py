from upyog.imports import *

__all__ = ["load_image", "resize_with_padding"]


def load_image(fn, mode="RGB") -> Image.Image:
    img = Image.open(fn)
    img.load()
    img = img._new(img.im)
    return img.convert(mode) if mode else img


@fastcore.patch
def resize_pad(
    self: Image.Image,
    size_WH: tuple,
    pad_location: Literal["center", "top"] = "center",
    fill: int = 0,
):
    return resize_with_padding(self, size_WH, fill, pad_location)


def get_ratio(from_WH, to_WH) -> np.ndarray:
    W, H = from_WH
    to_W, to_H = to_WH

    return min([to_H / H, to_W / W])


def resize_with_padding(
    img: Image.Image,
    target_WH,
    pad_fill=0,
    pad_location: Literal["center", "top"] = "center",
):
    to_W, to_H = target_WH
    W, H = img.size

    ratio = get_ratio(img.size, target_WH)
    W, H = int(ratio * W), int(ratio * H)

    if pad_location == "top":
        box = (0, 0)
    else:
        box = ((to_W - W) // 2, (to_H - H) // 2)

    # Create a new image and paste the resized on it
    padded_img = Image.new("RGB", (to_W, to_H), color=(pad_fill, pad_fill, pad_fill))
    padded_img.paste(img.resize((W, H), Image.ANTIALIAS), box)

    return padded_img
