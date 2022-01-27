# -*- mode: python; coding: utf-8 -*-
# Copyright 2020 the AAS WorldWide Telescope project
# Licensed under the MIT License.

"""
Building up WWT imagery data sets.

This gets a little complex since the generation of a tiled image involves
several tasks that may or may not be implemented in several, swappable ways:
generating the tiled pixel data; positioning the image on the sky; filling in
metadata; and so on. We try to provide a framework that allows the
implementations of different tasks to be swapped out without getting too airy
and abstract.

"""
from __future__ import absolute_import, division, print_function

__all__ = """
Builder
""".split()

from wwt_data_formats.enums import DataSetType, ProjectionType
from wwt_data_formats.imageset import ImageSet
from wwt_data_formats.layers import ImageSetLayer, LayerContainerReader
from wwt_data_formats.place import Place

from .image import ImageLoader


class Builder(object):
    """
    State for some kind of imagery data set that's being assembled.
    """

    pio = None
    "A PyramidIO object representing the backing storage of the tiles and other image data."

    imgset = None
    """
    The WWT ImageSet data describing the image data and their positioning on the sky.

    Data URLs in this ImageSet should be populated as relative URLs.

    """
    place = None
    "The WWT Place data describing a default view of the image data."

    def __init__(self, pio):
        self.pio = pio

        self.imgset = ImageSet()
        self.imgset.name = "Toasty"
        self.imgset.file_type = "." + pio.get_default_format()
        self.imgset.url = pio.get_path_scheme() + self.imgset.file_type

        self.place = Place()
        self.place.foreground_image_set = self.imgset
        self.place.name = "Toasty"

    def _check_no_wcs_yet(self):
        """
        The astrometric fields of ImageSet change their meaning depending on
        whether the image in question is tiled or not. Therefore, you'll get
        bogus results if change the tiling status *after* setting the
        astrometric information. This method should be called by other methods
        that control tiling in order to catch the issue if the user does things
        backwards.
        """
        if self.imgset.center_x != 0 or self.imgset.center_y != 0:
            raise Exception(
                "order-of-operations error: you must apply WCS after applying tiling settings"
            )

    def prepare_study_tiling(self, image):
        """
        Set up to tile the specified image as a WWT "study".

        Parameters
        ----------
        image : `toasty.image.Image`
            The image that will be tiled

        Returns
        -------
        tiling : `toasty.study.StudyTiling`
            The prepared tiling information

        Notes
        -----
        After calling this method, you should set up the WCS for the tiled
        imagery, using :meth:`default_tiled_study_astrometry` as a backstop if
        no real information is available. Then use :meth:`execute_study_tiling`
        to actually perform the tiling process.
        """

        from .study import StudyTiling

        tiling = StudyTiling(image.width, image.height)
        tiling.apply_to_imageset(self.imgset)
        return tiling

    def execute_study_tiling(self, image, tiling, **kwargs):
        """
        Tile the specified image as a WWT "study".

        Parameters
        ----------
        image : `toasty.image.Image`
            The image that will be tiled
        tiling : `toasty.study.StudyTiling`
            The prepared tiling information
        **kwargs
            Arguments relayed to :meth:`toasty.study.StudyTiling.tile_image`,
            such as ``cli_progress``.

        Returns
        -------
        *self*
        """

        tiling.tile_image(image, self.pio, **kwargs)
        return self

    def tile_base_as_study(self, image, **kwargs):
        """
        Tile an image assuming that it is in the appropriate format for WWT's
        "study" framework, namely that it uses a tangential (gnomonic)
        projection on the sky.

        Use of this method is somewhat discouraged since it both analyzes and
        performs the tiling all at once, which means that you can only correctly
        set (and validate) the WCS information *after* doing all the work of
        tiling. (Which in turn is because the proper way to apply WCS
        information to an imageset depends on the tiling parameters.) It is
        generally better to use :meth:`prepare_study_tiling` and
        :meth:`execute_study_tiling`, applying the WCS metadata in between, so
        that WCS errors can be caught and reported before doing the I/O.
        """

        from .study import tile_study_image

        self._check_no_wcs_yet()
        tiling = tile_study_image(image, self.pio, **kwargs)
        tiling.apply_to_imageset(self.imgset)

        return self

    def default_tiled_study_astrometry(self):
        self._check_no_wcs_yet()
        self.imgset.data_set_type = DataSetType.SKY
        self.imgset.base_degrees_per_tile = 1.0
        self.imgset.projection = ProjectionType.TAN
        self.place.zoom_level = 1.0
        return self

    def load_from_wwtl(self, cli_settings, wwtl_path, cli_progress=False):
        from contextlib import closing
        from io import BytesIO

        # Load WWTL and see if it matches expectations
        with closing(LayerContainerReader.from_file(wwtl_path)) as lc:
            if len(lc.layers) != 1:
                raise Exception("WWTL file must contain exactly one layer")

            layer = lc.layers[0]
            if not isinstance(layer, ImageSetLayer):
                raise Exception("WWTL file must contain an imageset layer")

            imgset = layer.image_set
            if imgset.projection != ProjectionType.SKY_IMAGE:
                raise Exception(
                    'WWTL imageset layer must have "SkyImage" projection type'
                )

            # Looks OK. Read and parse the image.
            loader = ImageLoader.create_from_args(cli_settings)
            img_data = lc.read_layer_file(layer, layer.extension)
            img = loader.load_stream(BytesIO(img_data))

        # (Re-)initialize with the imageset info extracted from the WWTL.

        self.imgset = imgset
        self.place.foreground_image_set = self.imgset

        self.imgset.file_type = "." + self.pio.get_default_format()
        self.imgset.url = self.pio.get_path_scheme() + self.imgset.file_type
        self.place.name = self.imgset.name

        # Transmogrify untiled image info to tiled image info. We reuse the
        # existing imageset as much as possible, but update the parameters that
        # change in the tiling process.

        wcs_keywords = self.imgset.wcs_headers_from_position(height=img.height)
        self.imgset.center_x = (
            self.imgset.center_y
        ) = 0  # hack to satisfy _check_no_wcs_yet()
        self.tile_base_as_study(img, cli_progress=cli_progress)
        self.imgset.set_position_from_wcs(
            wcs_keywords, img.width, img.height, place=self.place
        )

        return img

    def toast_base(self, sampler, depth, is_planet=False, is_pano=False, **kwargs):
        from .toast import sample_layer, ToastCoordinateSystem

        self._check_no_wcs_yet()

        coordsys = (
            ToastCoordinateSystem.PLANETARY
            if is_planet
            else ToastCoordinateSystem.ASTRONOMICAL
        )
        coordsys = kwargs.pop("coordsys", coordsys)
        sample_layer(self.pio, sampler, depth, coordsys=coordsys, **kwargs)

        if is_planet:
            self.imgset.data_set_type = DataSetType.PLANET
        elif is_pano:
            self.imgset.data_set_type = DataSetType.PANORAMA
        else:
            self.imgset.data_set_type = DataSetType.SKY

        self.imgset.base_degrees_per_tile = 180
        self.imgset.projection = ProjectionType.TOAST
        self.imgset.tile_levels = depth
        self.place.zoom_level = 360

        return self

    def cascade(self, **kwargs):
        from .merge import averaging_merger, cascade_images

        cascade_images(self.pio, self.imgset.tile_levels, averaging_merger, **kwargs)
        if "fits" in self.imgset.file_type:
            from .pyramid import Pos
            from astropy.io import fits
            import numpy as np

            with fits.open(
                self.pio.tile_path(
                    pos=Pos(n=0, x=0, y=0), format="fits", makedirs=False
                )
            ) as top_tile:
                self.imgset.data_min = top_tile[0].header["DATAMIN"]
                self.imgset.data_max = top_tile[0].header["DATAMAX"]
                (
                    self.imgset.pixel_cut_low,
                    self.imgset.pixel_cut_high,
                ) = np.nanpercentile(top_tile[0].data, [0.5, 99.5])

        return self

    def make_thumbnail_from_other(self, thumbnail_image):
        thumb = thumbnail_image.make_thumbnail_bitmap()
        with self.pio.open_metadata_for_write("thumb.jpg") as f:
            thumb.save(f, format="JPEG")
        self.imgset.thumbnail_url = "thumb.jpg"

        return self

    def make_placeholder_thumbnail(self):
        import numpy as np
        from .image import Image

        arr = np.zeros((45, 96, 3), dtype=np.uint8)
        img = Image.from_array(arr)

        with self.pio.open_metadata_for_write("thumb.jpg") as f:
            img.aspil().save(f, format="JPEG")

        self.imgset.thumbnail_url = "thumb.jpg"
        return self

    def apply_wcs_info(self, wcs, width, height):
        self.imgset.set_position_from_wcs(
            wcs.to_header(),
            width,
            height,
            place=self.place,
        )

        return self

    def apply_avm_info(self, avm, width, height):
        # So. The AVM standard discusses how parity should be expressed and how
        # it should be translated into WCS data, but in practice things are a
        # bit wonky: the AVM data that we've seen in the wild basically express
        # FITS-like (positive parity) WCS, while the actual associated image
        # data have a JPEG-like (negative parity) data layout. WCS can express
        # either parity so it would arguably be more correct for the generated
        # WCS to have negative parity. Based on the current state of knowledge,
        # I think the best option for now is to always flip the parity of the
        # WCS that pyavm hands us. We might need to change the heuristic or
        # allow the user to change the behavior.

        wcs = avm.to_wcs(target_shape=(width, height))
        from .image import _flip_wcs_parity

        wcs = _flip_wcs_parity(wcs, height)

        self.apply_wcs_info(wcs, width, height)

        if avm.Title:
            self.imgset.name = avm.Title

        if avm.Description:
            self.imgset.description = avm.Description

        if avm.Credit:
            self.imgset.credits = avm.Credit

        if avm.ReferenceURL:
            self.imgset.credits_url = avm.ReferenceURL

        return self

    def set_name(self, name):
        self.imgset.name = name
        self.place.name = name
        return self

    def create_wtml_folder(self):
        """
        Create a one-item :class:`wwt_data_formats.folder.Folder` object
        capturing this image.
        """
        from wwt_data_formats.folder import Folder

        self.place.name = self.imgset.name
        self.place.data_set_type = self.imgset.data_set_type
        self.place.thumbnail = self.imgset.thumbnail_url

        folder = Folder()
        folder.name = self.imgset.name

        # For all-sky/all-planet datasets, don't associate the imageset with a
        # particular Place. Otherwise, loading up the imageset causes the view
        # to zoom to a particular RA/Dec or lat/lon, likely 0,0. We might want
        # to make this manually configurable but this heuristic should Do The
        # Right Thing most times.
        if self.imgset.projection == ProjectionType.TOAST:
            folder.children = [self.imgset]
        else:
            folder.children = [self.place]

        return folder

    def write_index_rel_wtml(self):
        from wwt_data_formats import write_xml_doc

        folder = self.create_wtml_folder()

        with self.pio.open_metadata_for_write("index_rel.wtml") as f:
            write_xml_doc(folder.to_xml(), dest_stream=f, dest_wants_bytes=True)

        return self
