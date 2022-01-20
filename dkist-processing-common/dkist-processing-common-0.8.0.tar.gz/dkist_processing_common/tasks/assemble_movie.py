"""
Task(s) for assembling a browse movie
"""
from abc import ABC
from abc import abstractmethod
from typing import List
from typing import Literal

import moviepy.editor as mpy
import numpy as np
import pkg_resources
from matplotlib import cm
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from dkist_processing_common.models.fits_access import FitsAccessBase
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.parsers.l0_fits_access import L1FitsAccess
from dkist_processing_common.tasks import ParsedL0InputTaskBase
from dkist_processing_common.tasks.mixin.fits import FitsDataMixin


__all__ = ["AssembleMovie"]


class AssembleMovie(ParsedL0InputTaskBase, FitsDataMixin, ABC):
    """
    Assemble all movie frames (tagged with Tag.movie_frame()) into an mp4 movie file.
    It is intended to be subclassed so, e.g., instrument-specific overlays can be added.

    Subclassing guide
    =================

    Vocabulary
    ----------
    * frame - A single movie frame in the actual file. We don't really deal with these

    * image - One of the sequential movie images. I.e., each file tagged with Tag.movie_frame(). This is different than
      "frame" because it is very likely that each image will exist in the movie for multiple frames.

    Required
    --------

    * self.write_overlay(PIL.ImageDraw, FitsAccessBase) -> None

      Can be used to draw whatever you want on each "image". See the PIL.ImageDraw documentation for all of the options.
      A convenience function `self.write_line` is provided for text overlays. If you don't want to draw anything you
      still need to `pass` this function. The second argument is a single movie "image", i.e., a single array tagged
      with Tag.movie_frame.

    More Control
    ------------

    Class Default Properties
    ************************

    * MOVIE_FRAME_SHAPE - (x, y) tuple of the final pixel size of the movie

    * IMAGES_PER_SEC - Int that defines how many "images" to display per second. Think of this as the useful information "framerate".

    * FPS - Int that defines the final movie frames-per-sec. Change this to conform the video for whatever service you need.

    * FONT_FILE - Str pointing to a ttf file with whatever font you want to use

    * TEXT_MARGIN_PX - Int with padding used by `write_line()`

    * MPL_COLOR_MAP - Str of matplotlib named colormap. Only used in the default `apply_colormap`. An easy and simple way to change the colormap

    Class @properties
    *****************

    * fits_parsing_class - The subclass of L0FitsAccess to use for reading images

    * num_images - Int that defines the total number of "images" in the final movie. Probably num_dsps_repeats, but maybe not for weird data.

    * tags_for_image_n - List that contains the tags used to grab image "n". Probably just the dsps_repeat num, but maybe not for weird data.

    Other Functions
    ***************

    * apply_colormap(ndarray) -> ndarray

      You can override the default if you need some fancy way to convert single floats to (RGB) color info. The output needs
      to have shape (x, y, 3).

      Default is to use matplotlib to apply whatever colormap is defined as self.MPL_COLOR_MAP

    * write_line(draw: PIL.ImageDraw, text: str, line: int, column: Literal["left", "middle", "right"],
      **text_kwargs) -> None

      Useful for writing a line of text in `write_overlay`. ``line = 0`` is the bottom of the frame.

    """

    MOVIE_FRAME_SHAPE = (1024, 768)  # Is this a/THE standard size?
    IMAGES_PER_SEC = 3
    FPS = 15
    FONT_FILE = pkg_resources.resource_filename("dkist_processing_common", "fonts/Lato-Regular.ttf")
    TEXT_MARGIN_PX = 5
    MPL_COLOR_MAP = "viridis"

    @property
    def fits_parsing_class(self):
        return L1FitsAccess

    @property
    def num_images(self) -> int:
        """ The total number of images that will be used in the final movie """
        return self.constants.num_dsps_repeats

    def tags_for_image_n(self, n: int) -> List[str]:
        """ The tags to use to read the n'th image in the movie. It's OK to omit Tag.movie_frame. """
        return [Tag.dsps_repeat(n + 1)]

    def apply_colormap(self, array: np.ndarray) -> np.ndarray:
        """
        Convert floats to RGB colors.

        Default is to use matplotlib to apply a named colormap; whatever is named in self.MPL_COLOR_MAP
        """
        color_mapper = cm.get_cmap(self.MPL_COLOR_MAP)
        scaled_array = array / array.max()
        return color_mapper(scaled_array, bytes=True)[
            :, :, :-1
        ]  # Drop the last (alpha) color dimension

    def pre_run(self) -> None:
        """
        Set up some movie and font constants
        """
        super().pre_run()
        self.font_15 = ImageFont.truetype(self.FONT_FILE, size=15)
        self.font_18 = ImageFont.truetype(self.FONT_FILE, size=18)
        self.duration = self.num_images / self.IMAGES_PER_SEC

    def run(self) -> None:
        """
        Setup moviepy's VideoClip mechanism, write the movie, and tag it as a movie()

        Unlike other files, the movie file has a specific name (because .mp4 extension is needed by ffmpeg). It is
        "{dataset_id}.mp4"
        """
        clip = mpy.VideoClip(self.make_frame, duration=self.duration)

        relative_movie_path = f"{self.dataset_id}.mp4"
        absolute_movie_path = str(self.scratch.absolute_path(relative_movie_path))

        clip.write_videofile(absolute_movie_path, fps=self.FPS, codec="mpeg4")
        self.tag(path=absolute_movie_path, tags=[Tag.movie(), Tag.output()])

    def make_frame(self, t: float) -> np.ndarray:
        """
        Single-frame generator used by the moviepy machinery.

        This function takes in a numpy array, converts it to 8-bit int, and draws it into a movie frame canvas.
        It also calls the overlay function to write any metadata onto the frame.
        """
        image_num = int(t * self.IMAGES_PER_SEC)
        tags = self.tags_for_image_n(image_num)
        if Tag.movie_frame() not in tags:
            tags.append(Tag.movie_frame())

        frame_access_list = list(
            self.fits_data_read_fits_access(tags=tags, cls=self.fits_parsing_class)
        )
        if len(frame_access_list) == 0:
            raise ValueError(f"Did not find any frames for {image_num=} at time {t}")
        if len(frame_access_list) > 1:
            raise ValueError(
                f"Found {len(frame_access_list)} frames for {image_num=}. Expected only 1"
            )

        frame_access = frame_access_list[0]
        frame_data = frame_access.data
        colored_image = self.apply_colormap(frame_data)
        if colored_image.shape[-1] != 3:
            raise ValueError(
                f"Expected an RGB color image. Got shape {colored_image.shape} instead."
            )

        background = Image.new("RGB", self.MOVIE_FRAME_SHAPE, (0, 0, 0))
        frame_im = Image.fromarray(colored_image, mode="RGB")
        frame_im = frame_im.resize(self.MOVIE_FRAME_SHAPE)
        background.paste(frame_im)
        draw = ImageDraw.Draw(background)
        self.write_overlay(draw, frame_access)
        return np.array(background)

    @abstractmethod
    def write_overlay(self, draw: ImageDraw, fits_obj: FitsAccessBase) -> None:
        """
        Draw whatever you want on the data contained in a single FitsAccess object.

        See the documentation for PIL.ImageDraw for what you can do. If all that's needed is some text then use
        `write_line`.

        Example
        -------
        def write_overlay(self, draw, fits_obj):
            self.write_line(draw, f"INSTRUMENT: FOO", 1, column="left")
            self.write_line(draw, f"WAVELENGTH: {fits_obj.wavelength}", 2, column="middle")
            self.write_line(draw, f"DATE BEGIN: {fits_obj.date_begin}", 3, column="right")
        """
        pass

    def write_line(
        self,
        draw: ImageDraw,
        text: str,
        line: int,
        column: Literal["left", "middle", "right"],
        **text_kwargs,
    ) -> None:
        """Draws one line of text on the video frame

         Parameters

         draw
             The ImageDraw object of the current frame

         text
             The text to write

        line
             The row at which to write the text. 0 is the lowest row.

         column
             Must be either "left", "middle", or "right". The horizontal alignment of the text.

         text_kwargs
             Any additional kwargs to pass to `ImageDraw.ImageDraw.text`
        """
        text_width, text_height = draw.textsize(text, font=text_kwargs.get("font"))
        y = self.MOVIE_FRAME_SHAPE[1] - (self.TEXT_MARGIN_PX * line) - (text_height * line)

        if column == "right":
            anchor = "rd"
            x = self.MOVIE_FRAME_SHAPE[0] - self.TEXT_MARGIN_PX
        elif column == "middle":
            anchor = "md"
            x = self.MOVIE_FRAME_SHAPE[0] // 2
        elif column == "left":
            anchor = "ld"
            x = self.TEXT_MARGIN_PX
        else:
            raise ValueError(
                f"column argument must be in ['left', 'middle', 'right'], got {column=}"
            )

        draw.text((x, y), text, anchor=anchor, **text_kwargs)
