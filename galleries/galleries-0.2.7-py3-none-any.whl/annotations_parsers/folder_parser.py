import os
from typing import Optional, Dict

from galleries.annotations_parsers.gallery_annots_parsers import GalleryAnnotationsParser


class FolderParser(GalleryAnnotationsParser):
	"""
	Parser para obtener anotaciones a partir del directorio de las imágenes.
	Las anotaciones se obtienen El nombre del fichero es dividido con un separador y cada elemento obtenido es una anotación.
	Ejemplo 1:
		fp = FolderParser((('label', 'age', 'sex'), sep='_'))
		annots = fp('C:/Fulano_32_M/img1.jpg')

	annots va a ser igual a:
	{ 'label': 'Fulano', 'age': '32', 'sex': 'M' }

	Ejemplo 2:
		fp = FolderParser([(('label', 'age', 'sex'), sep='_'), (('video')])
		annots = fp('C:/Video1/Fulano_32_M/img1.jpg')

	annots va a ser igual a:
	{ 'label': 'Fulano', 'age': '32', 'sex': 'M', 'video': 'Video1' }
	"""

	def __init__(self, annot_names=None, sep='-'):
		self.annot_names = annot_names or []
		self.sep = sep

	def __call__(self, img_path: str) -> dict:
		return self.get_annotations_by_image_index(img_path)

	def get_annotations_by_image_index(self, img_index: str) -> dict:
		raise NotImplementedError

	def get_annotations_types(self) -> Optional[Dict[str, type]]:
		return {annot_name: str for annot_name in self.annot_names}

	def get_discrete_annotations_values(self) -> Dict[str, list]:
		return {}
