# -*- coding: utf-8 -*-
import tempfile
from contextlib import contextmanager

from requests import HTTPError

from arkindex_worker import logger
from arkindex_worker.image import download_tiles, open_image, polygon_bounding_box


class MagicDict(dict):
    """
    A dict whose items can be accessed like attributes.
    """

    def _magify(self, item):
        """
        Automagically convert lists and dicts to MagicDicts and lists of MagicDicts
        Allows for nested access: foo.bar.baz
        """
        if isinstance(item, list):
            return list(map(self._magify, item))
        if isinstance(item, dict):
            return MagicDict(item)
        return item

    def __getitem__(self, item):
        item = super().__getitem__(item)
        return self._magify(item)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(
                "{} object has no attribute '{}'".format(self.__class__.__name__, name)
            )

    def __setattr__(self, name, value):
        return super().__setitem__(name, value)

    def __delattr__(self, name):
        try:
            return super().__delattr__(name)
        except AttributeError:
            try:
                return super().__delitem__(name)
            except KeyError:
                pass
            raise

    def __dir__(self):
        return super().__dir__() + list(self.keys())


class Element(MagicDict):
    """
    Describes any kind of element.
    """

    def resize_zone_url(self, size="full"):
        if size == "full":
            return self.zone.url
        else:
            parts = self.zone.url.split("/")
            parts[-3] = size
            return "/".join(parts)

    def image_url(self, size="full"):
        """
        When possible, will return the S3 URL for images, so an ML worker can bypass IIIF servers
        :param size: Subresolution of the image.
        """
        if not self.get("zone"):
            return
        url = self.zone.image.get("s3_url")
        if url:
            return url
        url = self.zone.image.url
        if not url.endswith("/"):
            url += "/"
        return "{}full/{}/0/default.jpg".format(url, size)

    @property
    def requires_tiles(self):
        if not self.get("zone") or self.zone.image.get("s3_url"):
            return False
        max_width = self.zone.image.server.max_width or float("inf")
        max_height = self.zone.image.server.max_height or float("inf")
        bounding_box = polygon_bounding_box(self.zone.polygon)
        return bounding_box.width > max_width or bounding_box.height > max_height

    def open_image(self, *args, max_size=None, use_full_image=False, **kwargs):
        """
        Open this element's image as a Pillow image.

        If use_full_image is False:
            Use zone url, instead of the full image url to be able to get
            single page from double page image.
        Else:
            This does not crop the image to the element's polygon.

        :param max_size: Subresolution of the image.
        """
        if not self.get("zone"):
            raise ValueError("Element {} has no zone".format(self.id))

        if self.requires_tiles:
            if max_size is None:
                return download_tiles(self.zone.image.url)
            else:
                raise NotImplementedError

        if max_size is not None:
            bounding_box = polygon_bounding_box(self.zone.polygon)
            original_size = {"w": self.zone.image.width, "h": self.zone.image.height}
            # No resizing if the element is smaller than the image.
            if (
                bounding_box.width != original_size["w"]
                or bounding_box.height != original_size["h"]
            ):
                resize = "full"
                logger.warning(
                    "Only full image size elements covered, "
                    + "downloading full size image."
                )
            # No resizing if the image is smaller than the wanted size.
            elif original_size["w"] <= max_size and original_size["h"] <= max_size:
                resize = "full"
            # Resizing if the image is bigger than the wanted size.
            else:
                ratio = max_size / max(original_size.values())
                new_width, new_height = [int(x * ratio) for x in original_size.values()]
                resize = "{},{}".format(new_width, new_height)
        else:
            resize = "full"

        if use_full_image:
            url = self.image_url(resize)
        else:
            url = self.resize_zone_url(resize)

        try:
            return open_image(
                url,
                *args,
                rotation_angle=self.rotation_angle,
                mirrored=self.mirrored,
                **kwargs
            )
        except HTTPError as e:
            if (
                self.zone.image.get("s3_url") is not None
                and e.response.status_code == 403
            ):
                # This element uses an S3 URL: the URL may have expired.
                # Call the API to get a fresh URL and try again
                # TODO: this should be done by the worker
                raise NotImplementedError
                return open_image(self.image_url(resize), *args, **kwargs)
            raise

    @contextmanager
    def open_image_tempfile(self, format="jpeg", *args, **kwargs):
        """
        Get the element's image as a temporary file stored on the disk.
        To be used as a context manager: with element.open_image_tempfile() as f: ...
        """
        with tempfile.NamedTemporaryFile() as f:
            self.open_image(*args, **kwargs).save(f, format=format)
            yield f

    def __str__(self):
        if isinstance(self.type, dict):
            type_name = self.type["display_name"]
        else:
            type_name = str(self.type)
        return "{} {} ({})".format(type_name, self.name, self.id)
