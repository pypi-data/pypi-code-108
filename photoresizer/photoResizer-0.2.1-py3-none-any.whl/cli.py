"""
cli for :mod:`photoResizer` application.
 
:creationdate:  06/01/2022 08:23
:moduleauthor: François GUÉRIN <fguerin@ville-tourcoing.fr>
:modulename: photoResizer.cli
"""
import enum
import logging


from logging import config as logger_config
from pathlib import Path
from typing import Optional, Union, List

import click

from photoResizer import __version__, __author__, __author_email__, __license__, __url__, __copyright__, config, resizer

__author__ = "fguerin"
logger = logging.getLogger(__name__)


class OutputType(enum.Enum):
    JPEG = "jpeg"
    PNG = "png"
    TIFF = "tiff"
    WEBP = "webp"


def print_version(ctx, self, value):
    """Print the version of the module."""
    if not value or ctx.resilient_parsing:
        return
    click.echo(
        f"{__name__} version {__version__}\n"
        f"{__author__} <{__author_email__}>\n"
        f"License: {__license__}\n"
        f"URL: {__url__}\n"
        f"{__copyright__}"
    )
    ctx.exit()


@click.command()
@click.option("--version", is_flag=True, callback=print_version, expose_value=False, is_eager=True)
@click.option("--width", "-W", type=int, default=None, help="Width of the output image.")
@click.option("--height", "-H", type=int, default=None, help="Height of the output image.")
@click.option("--quality", "-Q", type=int, default=None, help="Quality of the output image.")
@click.option(
    "--format",
    "-f",
    "image_format",
    type=click.Choice([item.value for item in list(OutputType)], case_sensitive=False),
    default=OutputType.JPEG.value,
    help="Type of the output image.",
)
@click.option(
    "--multiprocessing",
    "-p",
    "with_multiprocessing",
    is_flag=True,
    default=False,
    help="Use multiprocessing for image resizing.",
)
@click.option(
    "--face-detection",
    "-F",
    "with_face_detection",
    is_flag=True,
    default=False,
    help="Use face detection for image resizing (openCV required).",
)
@click.argument(
    "images",
    type=click.Path(exists=True),
    nargs=-1,
    required=True,
)
@click.argument("output_dir", type=click.Path(exists=True), nargs=1, required=True)
def resize_images(
    width: Optional[int],
    height: Optional[int],
    quality: Optional[int],
    image_format: str = "jpeg",
    with_multiprocessing: bool = False,
    with_face_detection: bool = False,
    images: Union[List, Path] = ...,
    output_dir: Path = "",
) -> int:
    """
    Resize images to a given width and height.
    """
    _config = config.load_config(Path(__file__).parent / "settings.yaml")
    logger_config.dictConfig(_config["logging"])
    config.load_logger_config(Path(__file__).parent / "settings.yaml")
    logger.info("Resizing images to %sx%s", width, height)
    logger.info("Images: %s", images)
    logger.info("Output directory: %s", output_dir)

    if isinstance(images, tuple):
        images = list(map(lambda x: Path(x), images))

    real_images = []
    for path in images:
        _path = Path(path)
        if _path.is_dir():
            real_images.extend(list(path.glob("*.JPG")))
        else:
            real_images.append(path)

    _resizer = resizer.PhotoResizer(
        input_files=real_images,
        output_dir=Path(output_dir),
        width=width,
        height=height,
        quality=quality,
        image_format=image_format,
        with_face_detection=with_face_detection,
    )
    _resizer.resize_images(
        with_multiprocessing=with_multiprocessing,
    )
    return 0
