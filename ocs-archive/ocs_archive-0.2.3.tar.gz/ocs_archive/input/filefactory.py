from importlib import import_module

from ocs_archive.input.file import DataFile, FileSpecificationException
from ocs_archive.settings import settings

EXTENSION_TO_FILE_CLASS = {
    '.fits.fz': 'ocs_archive.input.lcofitsfile.LcoFitsFile',
    '.fits': 'ocs_archive.input.fitsfile.FitsFile',
    '.tar.gz': 'ocs_archive.input.tarwithfitsfile.TarWithFitsFile',
    '.pdf': 'ocs_archive.input.file.DataFile'
}


class FileFactory:
    """
    This factory returns the proper datafile subclass based on the file extension.
    It has a default mapping defined above, but that can be extended and overridden
    via the FILETYPE_MAPPING_OVERRIDES environment variable.
    """
    @staticmethod
    def get_datafile_class_for_extension(extension: str):
        extensions_dict = EXTENSION_TO_FILE_CLASS.copy()
        if isinstance(settings.FILETYPE_MAPPING_OVERRIDES, dict):
            extensions_dict.update(settings.FILETYPE_MAPPING_OVERRIDES)
        if extension not in extensions_dict:
            raise FileSpecificationException(f'file extension {extension} is not a currently supported file type')

        module_path, _, class_name = extensions_dict[extension].rpartition('.')
        try:
            loaded_module = import_module(module_path)
        except ModuleNotFoundError:
            raise FileSpecificationException(f'module {module_path} was not found. Please ensure the class path is correct')

        try:
            file_class = getattr(loaded_module, class_name)
        except AttributeError:
            raise FileSpecificationException(f'class {class_name} does not exist within module {module_path}. Please ensure the class path is correct')

        if not issubclass(file_class, DataFile):
            raise FileSpecificationException(f'class {class_name} must be a subclass of the ocs_archive.input.file.DataFile class')

        return file_class
