# -*- coding: utf-8 -*-
import math
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image, ImageChops, ImageOps

from arkindex_worker.image import download_tiles, open_image

FIXTURES = Path(__file__).absolute().parent / "data"
TILE = FIXTURES / "test_image.jpg"
FULL_IMAGE = FIXTURES / "tiled_image.jpg"
ROTATED_IMAGE = FIXTURES / "rotated_image.jpg"
MIRRORED_IMAGE = FIXTURES / "mirrored_image.jpg"
ROTATED_MIRRORED_IMAGE = FIXTURES / "rotated_mirrored_image.jpg"


def _root_mean_square(img_a, img_b):
    """
    Get the root-mean-square difference between two images for fuzzy matching
    See https://effbot.org/zone/pil-comparing-images.htm
    """
    h = ImageChops.difference(img_a, img_b).histogram()
    return math.sqrt(
        sum((value * ((idx % 256) ** 2) for idx, value in enumerate(h)))
        / float(img_a.size[0] * img_a.size[1])
    )


def test_download_tiles(responses):
    expected = Image.open(FULL_IMAGE).convert("RGB")
    with TILE.open("rb") as tile:
        tile_bytes = tile.read()

    responses.add(
        responses.GET,
        "http://nowhere/info.json",
        json={"width": 543, "height": 720, "tiles": [{"width": 181, "height": 240}]},
    )

    for x in (0, 181, 362):
        for y in (0, 240, 480):
            responses.add(
                responses.GET,
                f"http://nowhere/{x},{y},181,240/full/0/default.jpg",
                body=tile_bytes,
            )

    actual = download_tiles("http://nowhere")

    assert _root_mean_square(expected, actual) <= 5.0


def test_download_tiles_crop(responses):
    """
    Ensure download_tiles does not care about tiles that are slightly bigger than expected
    (occasional issue with the Harvard IDS image server where 1024×1024 tiles sometimes are returned as 1024x1025)
    """
    expected = Image.open(FULL_IMAGE).convert("RGB")
    tile_bytes = BytesIO()
    with TILE.open("rb") as tile:
        # Add one extra pixel to each tile to return slightly bigger tiles
        ImageOps.pad(Image.open(tile), (181, 241)).save(tile_bytes, format="jpeg")

    tile_bytes = tile_bytes.getvalue()

    responses.add(
        responses.GET,
        "http://nowhere/info.json",
        json={"width": 543, "height": 720, "tiles": [{"width": 181, "height": 240}]},
    )

    for x in (0, 181, 362):
        for y in (0, 240, 480):
            responses.add(
                responses.GET,
                f"http://nowhere/{x},{y},181,240/full/0/default.jpg",
                body=tile_bytes,
            )

    actual = download_tiles("http://nowhere")

    assert _root_mean_square(expected, actual) <= 5.0


def test_download_tiles_small(responses):
    small_tile = BytesIO()
    Image.new("RGB", (1, 1)).save(small_tile, format="jpeg")
    small_tile.seek(0)

    responses.add(
        responses.GET,
        "http://nowhere/info.json",
        json={"width": 543, "height": 720, "tiles": [{"width": 181, "height": 240}]},
    )

    responses.add(
        responses.GET,
        "http://nowhere/0,0,181,240/full/0/default.jpg",
        body=small_tile.read(),
    )

    with pytest.raises(ValueError) as e:
        download_tiles("http://nowhere")
    assert str(e.value) == "Expected size 181×240 for tile 0,0, but got 1×1"


@pytest.mark.parametrize(
    "path, is_local",
    (
        ("http://somewhere/test.jpg", False),
        ("https://somewhere/test.jpg", False),
        ("path/to/something", True),
        ("/absolute/path/to/something", True),
    ),
)
def test_open_image(path, is_local, monkeypatch):
    """Check if the path triggers a local load or a remote one"""

    monkeypatch.setattr("os.path.exists", lambda x: True)
    monkeypatch.setattr(Image, "open", lambda x: Image.new("RGB", (1, 10)))
    monkeypatch.setattr(
        "arkindex_worker.image.download_image", lambda x: Image.new("RGB", (10, 1))
    )

    image = open_image(path)

    if is_local:
        assert image.size == (1, 10)
    else:
        assert image.size == (10, 1)


@pytest.mark.parametrize(
    "rotation_angle,mirrored,expected_path",
    (
        (0, False, TILE),
        (45, False, ROTATED_IMAGE),
        (0, True, MIRRORED_IMAGE),
        (45, True, ROTATED_MIRRORED_IMAGE),
    ),
)
def test_open_image_rotate_mirror(rotation_angle, mirrored, expected_path):
    expected = Image.open(expected_path).convert("RGB")
    actual = open_image(str(TILE), rotation_angle=rotation_angle, mirrored=mirrored)
    actual.save(f"/tmp/{rotation_angle}_{mirrored}.jpg")
    assert _root_mean_square(expected, actual) <= 15.0
