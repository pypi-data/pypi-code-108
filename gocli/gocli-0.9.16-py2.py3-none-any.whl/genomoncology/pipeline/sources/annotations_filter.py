from cytoolz.curried import curry

from genomoncology.pipeline.sources.base import LazyFileSource


@curry
class AnnotationsFilterFileSource(LazyFileSource):
    def __init__(self, ann_file):
        assert ann_file, "Annotations filter file not provided"
        self.file = open(ann_file, "r")
        self.entries = self.file.readlines()

    def __iter__(self):
        for annotation_field in self.entries:
            yield annotation_field.strip()
        self.file.close()
