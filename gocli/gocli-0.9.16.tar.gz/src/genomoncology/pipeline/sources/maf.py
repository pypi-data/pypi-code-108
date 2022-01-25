from cytoolz.curried import curry, assoc

from genomoncology.parse import ensures, DocType, __TYPE__, __CHILD__
from .base import LazyFileSource


@curry
class MAFSource(LazyFileSource):
    def __init__(self, filename, columns, **meta):
        self._mapper = None
        self.columns = ensures.ensure_collection(columns)
        self.meta = meta
        self.delimiter = "\t"

        if __TYPE__ not in meta:
            self.meta = assoc(self.meta, __TYPE__, DocType.MAF.value)

        super().__init__(filename)

    def __iter__(self):
        # noinspection PyUnresolvedReferences
        iterator = super(MAFSource.func, self).__iter__()

        while not self.columns:
            line = next(iterator)
            if line[0] == "#":
                continue
            self.columns = line.strip().split("\t")

        yield self.create_header()

        for record in iterator:
            record = record.replace("\n", "").split("\t")
            ref_index = self.columns.index("Reference_Allele")
            alt1_index = self.columns.index("Tumor_Seq_Allele1")
            alt2_index = self.columns.index("Tumor_Seq_Allele2")
            for alt_index in [alt1_index, alt2_index]:
                if record[ref_index] != record[alt_index]:
                    yield self.create_maf_call(
                        record, alt_index, self.meta["build"]
                    )

    def create_header(self):
        return {
            __TYPE__: DocType.HEADER.value,
            __CHILD__: self.meta.get(__TYPE__),
            "columns": self.columns,
            "meta": self.meta,
            "file_path": self.name,
        }

    def create_maf_call(self, record, alt_index, build):
        maf_d = dict(__type__=DocType.MAF.value, alt=record[alt_index])
        for column in self.columns:
            maf_d[column] = record[self.columns.index(column)]
        maf_d["Chromosome"] = maf_d["Chromosome"].replace("chr", "")
        maf_d["build"] = build
        return maf_d
