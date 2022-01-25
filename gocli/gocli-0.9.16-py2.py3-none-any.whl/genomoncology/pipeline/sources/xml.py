import xml.etree.ElementTree as et

from cytoolz.curried import curry

from .one_off_sources import ClinvarXMLSource


@curry
class XMLSource:
    def __init__(self, file_paths, data_set_name=None):
        self.file_paths = file_paths
        self.data_set_name = data_set_name

    def __iter__(self):
        yield from self.iterate_xml(self.file_paths, self.data_set_name)

    def iterate_xml(self, file_paths, data_set_name):
        assert not isinstance(
            file_paths, str
        ), "Requires list or iterator of str."
        for file_path in file_paths:
            source = self.determine_xml_source(data_set_name, file_path)
            return source

    def get_root(self, file_path):
        try:
            root = et.parse(file_path)
            return root
        except et.ParseError:
            exit()

    def determine_xml_source(self, data_set_name, file_path):
        if data_set_name == "clinvar_xml":
            return ClinvarXMLSource(file_path)
        elif data_set_name == "clinvar_grch38_xml":
            return ClinvarXMLSource(file_path, is_grch38=True)
        return None
