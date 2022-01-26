import abc
import collections
from collections import Generator
from typing import Any, Tuple

import cv2 as cv
import logging
import os
from pathlib import Path
import pickle

# from algorithms import IDescriptor, IDetector
from galleries.igallery import IGallery
from galleries import files_utils


class GalleryDataHandler:
	relative_data_dir = '_gallery_data'
	SEP = ' '
	EXT = '.pkl'

	def __init__(self, gallery: IGallery, write_data_dir):
		self.gallery = gallery
		self.write_data_dir = write_data_dir

	@abc.abstractmethod
	def _get_supported_generator_type(self) -> type:
		"""
		Tipo de algoritmo que este writer soporta para guardar/leer datos.
		:return:
		"""
		pass

	@abc.abstractmethod
	def _get_writer_folder_name(self) -> str:
		"""
		Nombre de la carpeta donde se guardarán los datos de este writer.
		:return:
		"""
		pass

	@abc.abstractmethod
	def _get_generator_folder_name(self, data_generator: Any) -> str:
		pass

	@abc.abstractmethod
	def _get_unique_id(self, data_generator: Any) -> str:
		pass

	@abc.abstractmethod
	def _get_data(self, data_generator: Any, gallery: IGallery):
		pass

	def _is_generator_valid(self, data_generator: Any):
		return isinstance(data_generator, self._get_supported_generator_type())

	def _get_generator_folder(self, data_generator: Any):
		"""
		Devuelve el directorio donde se guardan los datos de un algoritmo.
		:param data_generator: algoritmo del que se desean guardar los datos.
		:return:
		"""
		writer_folder = self._get_writer_folder_name()
		generator_folder = self._get_generator_folder_name(data_generator)
		folder_dir = os.path.join(self.get_root(), writer_folder, generator_folder)
		return folder_dir

	def _get_index_file_dir(self, data_generator: Any):
		"""
		Devuelve la dirección del archivo donde se guardan, para cada posible configuración del algoritmo,
		la dirección del fichero donde se guardaron sus datos.
		:param data_generator: algoritmo del que se desean guardar los datos.
		:return:
		"""
		folder = self._get_generator_folder(data_generator)
		file_path = os.path.join(folder, 'index.txt')
		return file_path

	def _read_index_list(self, data_generator: Any):
		"""
		Devuelve lista con los índices de datos guardados de un algoritmo.
		:param data_generator: algoritmo del que se desean guardar los datos.
		:return:
		"""
		indices = []
		index_file = self._get_index_file_dir(data_generator)
		if os.path.exists(index_file):
			with open(index_file) as file:
				for line in file:
					line = line.strip()
					index, unique_id = line.split(sep=self.SEP, maxsplit=1)
					index = int(index)
					indices.append((index, unique_id))
		return indices

	def _write_indices(self, data_generator: Any, indices):
		"""
		Escribe el fichero de índices con los índices dados. Si el fichero no existe, se crea.
		Sobreescribe los índices que ya estuvieran guardados.
		:param data_generator:
		:param indices:
		:return:
		"""
		index_file = self._get_index_file_dir(data_generator)
		directory = Path(index_file).parent
		if not os.path.exists(directory):  # crear el directorio si no existe
			os.makedirs(directory)

		with open(index_file, 'w') as file:
			for index, conf in indices:
				file.write(f'{index}{self.SEP}{conf}\n')

	def _get_data_file_path(self, data_generator: Any, indices) -> str:
		"""
		Devuelve la dirección del archivo donde se guardarán los datos de un algoritmo a partir de un índice.
		:param data_generator: algoritmo del que se desean guardar los datos.
		:return:
		"""
		data_file = None
		if len(indices) > 0:
			data_generator_folder = self._get_generator_folder(data_generator)
			unique_id = self._get_unique_id(data_generator)
			for index, uid in indices:
				if uid == unique_id:
					data_file = os.path.join(data_generator_folder, f'{index}{self.EXT}')
					break
		return data_file

	def _add_generator_to_indices_if_not_exists(self, data_generator: Any, indices: list) -> bool:
		unique_id = self._get_unique_id(data_generator)
		exists = False
		max_index = -1
		for index, configuration in indices:
			if index > max_index:
				max_index = index
			if configuration == unique_id:
				exists = True
				break
		if not exists:
			indices.append((max_index + 1, unique_id))
		return not exists

	def _add_generator_to_index_file(self, data_generator: Any):
		"""
		Añade un algoritmo al índice. Si el algoritmo existe ya, entonces no sucede nada.
		Si el fichero índice no está creado entonces se crea. Además devuelve la dirección del fichero donde se
		guardarán los datos del algoritmo.
		:param data_generator: algoritmo del que se desean guardar los datos.
		:return:
		"""
		indices = self._read_index_list(data_generator)
		added = self._add_generator_to_indices_if_not_exists(data_generator, indices)
		if added:
			self._write_indices(data_generator, indices)
		data_file = self._get_data_file_path(data_generator, indices)
		return data_file

	def _write_data(self, data: Generator, file_path: str):
		"""
		Guardar datos a partir de un generador.
		:param data:
		:param file_path:
		:return: devuelve True si se guardó, False si el archivo ya existía.
		"""
		if not os.path.exists(file_path):
			files_utils.create_dir_of_file(file_path)
			file = open(file_path, 'wb')
			try:
				for d in data:
					pickle.dump(d, file)
					file.flush()
				file.close()
				return True
			except:
				file.close()
				raise RuntimeError('Un error ha ocurrido mientras se guardaban los datos.')

	def get_root(self):
		return os.path.join(self.write_data_dir, self.relative_data_dir)

	def write_data(self, data_generator: Any):
		if self._is_generator_valid(data_generator):
			indices = self._read_index_list(data_generator)
			self._add_generator_to_indices_if_not_exists(data_generator, indices)
			file_path = self._get_data_file_path(data_generator, indices)

			logging.info(f'Writing data with {data_generator} data_generator in {file_path}')

			data = self._get_data(data_generator, self.gallery)

			try:
				success = self._write_data(data, file_path)
				if success:
					self._write_indices(data_generator, indices)
			except:
				raise RuntimeError('Un error ha ocurrido mientras se guardaban los datos.')
		else:
			supported_type = self._get_supported_generator_type()
			msg = f'Tipo de dato incorrecto. El algoritmo debe ser de tipo {supported_type}.'
			logging.error(msg)
			raise TypeError(msg)

	def read_data(self, data_generator: Any):
		"""
		Cargar datos guardados de un algoritmo.
		:param data_generator:
		:return:
		"""
		indices = self._read_index_list(data_generator)
		file_path = self._get_data_file_path(data_generator, indices)
		if file_path is not None and os.path.exists(file_path):
			file = open(file_path, "rb")
			end_reached = False
			while not end_reached:
				try:
					row_data = pickle.load(file)
					yield row_data
				except EOFError:
					end_reached = True
			file.close()
		else:
			raise IOError(f'No existen datos guardados para este generador: {str(data_generator)}')

	def remove_corrupted_data(self):
		"""
		Eliminar datos guardados que estn corrompidos.
		:return:
		"""
		# TODO implementar esto
		pass

	def exists_data(self, data_generator: Any):
		indices = self._read_index_list(data_generator)
		file_path = self._get_data_file_path(data_generator, indices)
		return file_path is not None and os.path.exists(file_path)

	def remove_data(self, data_generator: Any):
		"""
		Eliminar algoritmo del índice así como sus datos.
		:param data_generator: algoritmo que se desea eliminar.
		:return:
		"""
		indices = self._read_index_list(data_generator)
		data_generator_conf = self._get_unique_id(data_generator)
		exists = False
		for i, (index, uid) in enumerate(indices):
			if uid == data_generator_conf:
				exists = True
				break
		if exists:
			# eliminar los datos guardados
			data_file = self._get_data_file_path(data_generator, indices)
			if os.path.exists(data_file):
				os.remove(data_file)
			# quitar el algoritmo del índice
			indices.pop(i)
			self._write_indices(data_generator, indices)


class GalleryGenericDataHandler(GalleryDataHandler):

	def _get_supported_generator_type(self) -> type:
		return type((str, str, collections.Callable))  # this returns tuple which is not entirely correct

	def _get_writer_folder_name(self) -> str:
		return 'generic'

	def _get_generator_folder_name(self, data_generator: Tuple[str, str, collections.Callable]) -> str:
		folder_name, _, _ = data_generator
		return folder_name

	def _get_unique_id(self, data_generator: Tuple[str, str, collections.Callable]) -> str:
		_, unique_id, _ = data_generator
		return unique_id

	def _get_data(self, data_generator: Tuple[str, str, collections.Callable], gallery: IGallery):
		_, _, data_generator_function = data_generator
		for img_path in self.gallery.get_indices():
			img = cv.imread(img_path)
			feats = data_generator_function(img)
			yield img_path, feats

#
# class GalleryFeaturesDataHandler(GalleryDataHandler):
#
# 	def _get_supported_generator_type(self) -> type:
# 		return IDescriptor
#
# 	def _get_writer_folder_name(self) -> str:
# 		return 'features'
#
# 	def _get_generator_folder_name(self, data_generator: IDescriptor) -> str:
# 		return data_generator.get_name()
#
# 	def _get_unique_id(self, data_generator: IDescriptor) -> str:
# 		return data_generator.configuration_string()
#
# 	def _get_data(self, descriptor: IDescriptor, gallery: IGallery):
# 		for img_path in self.gallery.get_paths():
# 			img = cv.imread(img_path)
# 			feats = descriptor.features(img)
# 			yield img_path, feats
#
#
# class GalleryDetectionsDataHandler(GalleryDataHandler):
#
# 	def _get_supported_generator_type(self) -> type:
# 		return IDetector
#
# 	def _get_writer_folder_name(self) -> str:
# 		return 'detections'
#
# 	def _get_generator_folder_name(self, data_generator: IDetector) -> str:
# 		return data_generator.get_name()
#
# 	def _get_unique_id(self, detector: IDetector) -> str:
# 		return detector.configuration_string()
#
# 	def _get_data(self, detector: IDetector, gallery: IGallery):
# 		for img_path in self.gallery.get_paths():
# 			img = cv.imread(img_path)
# 			dets = detector.detect(img)
# 			yield img_path, dets
