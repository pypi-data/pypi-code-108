import numpy as np
from typing import Any

from galleries.annotations_parsers.gallery_annots_parsers import GalleryAnnotationsParser
from galleries.igallery import IGallery
from galleries.images_providers.gallery_images_provider import GalleryImagesProvider


class Gallery(IGallery):

	def __init__(
			self,
			name: str,
			images_provider: GalleryImagesProvider,
			annots_parser: GalleryAnnotationsParser
	):
		self._name = name
		self._images_provider = images_provider
		self._annots_parser = annots_parser

	@property
	def name(self):
		return self._name

	@name.setter
	def name(self, value):
		self._name = value

	@property
	def images_provider(self):
		return self._images_provider

	@images_provider.setter
	def images_provider(self, value):
		self._images_provider = value

	@property
	def annotations_parser(self):
		return self._annots_parser

	@annotations_parser.setter
	def annotations_parser(self, value):
		self._annots_parser = value

	def get_indices(self):
		return self._images_provider.get_indices()

	def get_annotations_by_index(self, img_index):
		return self._annots_parser.get_annotations_by_image_index(img_index)

	def get_image_by_index(self, index: Any) -> np.ndarray:
		return self._images_provider.get_image_by_index(index)
