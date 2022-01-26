import abc
import cv2 as cv
import numpy as np
import pickle
from typing import Any

from galleries import files_utils


class IGallery(abc.ABC):
	"""
	Interfaz para implementar el acceso a una galería de imágenes y sus anotaciones
	"""

	@abc.abstractmethod
	def get_indices(self):
		"""
		Obtener los índices de las imágenes. Estos índices son utilizados después para obtener información de la imagen.
		Un índice puede ser, por ejemplo, la dirección de la imagen en el sistema de ficheros local.
		:return:
		"""
		pass

	@abc.abstractmethod
	def get_annotations_by_index(self, img_index):
		"""
		Obtener las anotaciones de una imagen dado su índice.
		:param img_index:
		:return:
		"""
		pass

	@abc.abstractmethod
	def get_image_by_index(self, index: Any) -> np.ndarray:
		pass

	def get_paths_annots(self):
		for img_index in self.get_indices():
			yield img_index, self.get_annotations_by_index(img_index)

	def get_images(self):
		for img_index in self.get_indices():
			yield cv.imread(img_index)

	def get_images_annots(self):
		for img_index, annots in self.get_paths_annots():
			img = cv.imread(img_index)
			yield img, annots

	@staticmethod
	def write_gallery(gallery: 'IGallery', file_path: str):
		files_utils.create_dir_of_file(file_path)
		file = open(file_path, 'wb')
		pickle.dump(gallery, file)
		file.close()

	@staticmethod
	def read_gallery(file_path: str) -> 'IGallery':
		file = open(file_path, 'rb')
		gallery = pickle.load(file)
		file.close()
		return gallery
