# -*- mode: python; coding: utf-8 -*-
# Copyright 2020 the AAS WorldWide Telescope project
# Licensed under the MIT License.

"""
Support for loading images from an AstroPix feed.

TODO: update metadata tomfoolery to match the new things that I've learned. Cf.
the ``wwtdatatool wtml report`` utility and the djangoplicity implementation.

NOTE: AstroPix seems to have its image parity backwards. Standard JPEGs are
reported with ``wcs_scale[0] < 0``, which is *positive* AKA bottoms-up AKA FITS
parity. If we pass their parameters more-or-less straight through to WWT, we get
the right appearance onscreen.

"""

__all__ = """
AstroPixImageSource
AstroPixCandidateInput
""".split()

import codecs
from datetime import datetime
import json
import numpy as np
import os.path
import requests
import shutil
from urllib.parse import quote as urlquote

from ..image import ImageLoader
from . import CandidateInput, ImageSource, NotActionableError


EXTENSION_REMAPPING = {
    "jpeg": "jpg",
}


class AstroPixImageSource(ImageSource):
    """
    An ImageSource that obtains its inputs from a query to the AstroPix service.
    """

    _json_query_url = None

    @classmethod
    def get_config_key(cls):
        return "astropix"

    @classmethod
    def deserialize(cls, data):
        inst = cls()
        inst._json_query_url = data["json_query_url"]
        return inst

    def query_candidates(self):
        with requests.get(self._json_query_url, stream=True) as resp:
            feed_data = json.load(resp.raw)

        for item in feed_data:
            yield AstroPixCandidateInput(item)

    def fetch_candidate(self, unique_id, cand_data_stream, cachedir):
        with codecs.getreader("utf8")(cand_data_stream) as text_stream:
            info = json.load(text_stream)

        lower_id = info["image_id"].lower()
        global_id = info["publisher_id"] + "_" + lower_id

        if info["resource_url"] and len(info["resource_url"]):
            source_url = info["resource_url"]
        else:
            # Original image not findable. Get the best version available from
            # AstroPix.
            #
            # GROSS: saving this code since I won't be testing this super
            # thoroughly ... but it looks like now the original is being made
            # available consistently?

            ##size = int(info['image_max_boundry'])
            ##if size >= 24000:
            ##    best_astropix_size = 24000
            ##elif size >= 12000:
            ##    best_astropix_size = 12000
            ##elif size >= 6000:
            ##    best_astropix_size = 6000
            ##elif size >= 3000:
            ##    best_astropix_size = 3000
            ##elif size >= 1600:
            ##    best_astropix_size = 1600
            ##elif size > 1024:  # transition point to sizes that are always generated
            ##    best_astropix_size = 1280
            ##elif size > 500:
            ##    best_astropix_size = 1024
            ##elif size > 320:
            ##    best_astropix_size = 500
            ##else:
            ##    best_astropix_size = 320

            source_url = (
                "http://astropix.ipac.caltech.edu/archive/%s/%s/%s_original.jpg"
                % (
                    urlquote(info["publisher_id"]),
                    urlquote(lower_id),
                    urlquote(global_id),
                )
            )

        # Now ready to download the image.

        ext = source_url.rsplit(".", 1)[-1].lower()
        ext = EXTENSION_REMAPPING.get(ext, ext)

        with requests.get(source_url, stream=True) as resp:
            if not resp.ok:
                raise Exception(f"error downloading {source_url}: {resp.status_code}")

            with open(os.path.join(cachedir, "image." + ext), "wb") as f:
                shutil.copyfileobj(resp.raw, f)

    def process(self, unique_id, cand_data_stream, cachedir, builder):
        # Set up the metadata.

        with codecs.getreader("utf8")(cand_data_stream) as text_stream:
            info = json.load(text_stream)

        if info["resource_url"] and len(info["resource_url"]):
            ext = info["resource_url"].rsplit(".", 1)[-1].lower()
            ext = EXTENSION_REMAPPING.get(ext, ext)
        else:
            ext = "jpg"

        img_path = os.path.join(cachedir, "image." + ext)
        md = AstroPixMetadata(info)

        # Load up the image.

        img = ImageLoader().load_path(img_path)

        # Do the processing.

        builder.tile_base_as_study(img)
        builder.make_thumbnail_from_other(img)

        builder.imgset.set_position_from_wcs(
            md.as_wcs_headers(img.width, img.height),
            img.width,
            img.height,
            place=builder.place,
        )

        builder.set_name(info["title"])
        builder.imgset.credits_url = md.get_credit_url()

        builder.cascade()


class AstroPixCandidateInput(CandidateInput):
    """
    A CandidateInput obtained from an AstroPix query.
    """

    def __init__(self, json_dict):
        self._json = json_dict
        self._lower_id = self._json["image_id"].lower()
        self._global_id = self._json["publisher_id"] + "_" + self._lower_id

    def get_unique_id(self):
        return self._global_id.replace("/", "_")

    def save(self, stream):
        # First check that this input is usable. The NRAO feed contains an
        # item like this, and based on my investigations they are just not
        # usable right now because the server APIs don't work. So: skip any
        # like this.
        if "/" in self._json["image_id"]:
            raise NotActionableError(
                'AstroPix images with "/" in their IDs aren\'t retrievable'
            )

        # TODO? A few NRAO images have SIN projection. Try to recover them?
        if self._json["wcs_projection"] != "TAN":
            raise NotActionableError("cannot ingest images in non-TAN projections")

        with codecs.getwriter("utf8")(stream) as text_stream:
            json.dump(self._json, text_stream, ensure_ascii=False, indent=2)


ASTROPIX_FLOAT_ARRAY_KEYS = [
    "wcs_reference_dimension",  # NB: should be ints, but sometimes expressed with decimal points
    "wcs_reference_pixel",
    "wcs_reference_value",
    "wcs_scale",
]

ASTROPIX_FLOAT_SCALAR_KEYS = [
    "wcs_rotation",
]


class AstroPixMetadata(object):
    """
    Metadata derived from AstroPix query results.
    """

    image_id = None
    publisher_id = None
    resource_url = None
    wcs_coordinate_frame = None  # ex: 'ICRS'
    wcs_equinox = None  # ex: 'J2000'
    wcs_projection = None  # ex: 'TAN'
    wcs_reference_dimension = None  # ex: [7416.0, 4320.0]
    wcs_reference_value = None  # ex: [187, 12.3]
    wcs_reference_pixel = (
        None  # ex: [1000.4, 1000.7]; from examples, this seems to be 1-based
    )
    wcs_rotation = None  # ex: -0.07 (deg, presumably)
    wcs_scale = None  # ex: [-6e-7, 6e-7]

    def __init__(self, json_dict):
        # Some massaging for consistency:

        for k in ASTROPIX_FLOAT_ARRAY_KEYS:
            if k in json_dict:
                json_dict[k] = list(map(float, json_dict[k]))

        for k in ASTROPIX_FLOAT_SCALAR_KEYS:
            if k in json_dict:
                json_dict[k] = float(json_dict[k])

        for k, v in json_dict.items():
            setattr(self, k, v)

    def as_wcs_headers(self, width, height):
        """
        The metadata here are essentially AVM headers. As described in
        `Builder.apply_avm_info()`, the data that we've seen in the wild are a
        bit wonky with regards to parity: the metadata essentially correspond to
        FITS-like parity, and we need to flip them to JPEG-like parity. See also
        very similar code in `djangoplicity.py`.
        """
        headers = {}

        # headers['RADECSYS'] = self.wcs_coordinate_frame  # causes Astropy warnings
        headers["CTYPE1"] = "RA---" + self.wcs_projection
        headers["CTYPE2"] = "DEC--" + self.wcs_projection
        headers["CRVAL1"] = self.wcs_reference_value[0]
        headers["CRVAL2"] = self.wcs_reference_value[1]

        # See Calabretta & Greisen (2002; DOI:10.1051/0004-6361:20021327), eqn 186
        crot = np.cos(self.wcs_rotation * np.pi / 180)
        srot = np.sin(self.wcs_rotation * np.pi / 180)
        lam = self.wcs_scale[1] / self.wcs_scale[0]

        pc1_1 = crot
        pc1_2 = -lam * srot
        pc2_1 = srot / lam
        pc2_2 = crot

        # If we couldn't get the original image, the pixel density used for
        # the WCS parameters may not match the image resolution that we have
        # available. In such cases, we need to remap the pixel-related
        # headers. From the available examples, `wcs_reference_pixel` seems to
        # be 1-based in the same way that `CRPIXn` are. Since in FITS, integer
        # pixel values correspond to the center of each pixel box, a CRPIXn of
        # [0.5, 0.5] (the lower-left corner) should not vary with the image
        # resolution. A CRPIXn of [W + 0.5, H + 0.5] (the upper-right corner)
        # should map to [W' + 0.5, H' + 0.5] (where the primed quantities are
        # the new width and height).

        factor0 = width / self.wcs_reference_dimension[0]
        factor1 = height / self.wcs_reference_dimension[1]

        headers["CRPIX1"] = (self.wcs_reference_pixel[0] - 0.5) * factor0 + 0.5
        headers["CRPIX2"] = (self.wcs_reference_pixel[1] - 0.5) * factor1 + 0.5

        # Now finalize and apply the parity flip

        cdelt1 = self.wcs_scale[0] / factor0
        cdelt2 = self.wcs_scale[1] / factor1
        headers["CD1_1"] = cdelt1 * pc1_1
        headers["CD1_2"] = -cdelt1 * pc1_2
        headers["CD2_1"] = cdelt2 * pc2_1
        headers["CD2_2"] = -cdelt2 * pc2_2
        headers["CRPIX2"] = height + 1 - headers["CRPIX2"]

        return headers

    def get_credit_url(self):
        if self.reference_url:
            return self.reference_url

        return "http://astropix.ipac.caltech.edu/image/%s/%s" % (
            urlquote(self.publisher_id),
            urlquote(self.image_id),
        )
