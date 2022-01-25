from cytoolz.curried import curry

from genomoncology.pipeline.sources.base import LazyFileSource


@curry
class BedFileSource(LazyFileSource):
    def __init__(self, _, bed_file, **meta):
        assert bed_file, "BED not provided"
        self.file = open(bed_file, "r")
        self.entries = self.file.readlines()
        self.meta = meta

    def __iter__(self):
        for line in self.entries:
            data = line.split("\t")
            if len(data) > 2:
                chromosome = data[0]
                start = data[1]
                end = data[2]
                yield (chromosome, start, end)

        self.file.close()
