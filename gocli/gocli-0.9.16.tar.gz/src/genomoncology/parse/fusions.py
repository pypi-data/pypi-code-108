from genomoncology.parse.ensures import flatten
from cytoolz.curried import curry
from glom import glom

from .doctypes import DocType


class TuxedoMapper(object):
    def __init__(self, bed_filter):
        self.bed_filter = bed_filter
        self.base = dict(__type__=DocType.ALTERATION.value)
        self.seen = set()

    def get_genes(self, chromosome, position):
        tree = self.bed_filter.get_tree(chromosome)
        genes = []
        if tree:
            genes = [interval.data for interval in tree.search(position)]
        return flatten(genes) or [None]

    def add_meta(self, fusion, name, value):
        fusion.setdefault("meta", {})[name] = value

    def construct_fusion(self, *genes):
        genes = list(filter(None, genes))

        if genes:
            fusion = self.base.copy()
            if len(genes) == 1 or genes[0] != genes[1]:
                fusion["mutation_hash"] = "{} Fusion".format("-".join(genes))
            else:
                genes = list(set(genes))
                assert len(genes) == 1, f"Expected inversion: {genes}"
                fusion["mutation_hash"] = "{} Inversion".format(
                    "-".join(genes)
                )

            self.add_meta(fusion, "genes", genes)
            return fusion

    def __call__(self, doc):  # pragma: no mccabe
        if DocType.HEADER.is_a(doc):
            self.base["file_path"] = doc.get("file_path", None)
            self.seen.clear()

        elif DocType.TUXEDO.is_a(doc):
            chr_1, chr_2 = doc.get("chr_1"), doc.get("chr_2")
            pos_1, pos_2 = doc.get("pos_1"), doc.get("pos_2")

            for gene_1 in self.get_genes(chr_1, pos_1):
                for gene_2 in self.get_genes(chr_2, pos_2):
                    fusion = self.construct_fusion(gene_1, gene_2)
                    if fusion and fusion["mutation_hash"] not in self.seen:
                        self.seen.add(fusion["mutation_hash"])

                        for (name, value) in doc.items():
                            if not name.startswith("__"):
                                self.add_meta(fusion, name, value)

                        yield fusion


DEFAULT_TUXEDO_FILE_COLUMNS = [
    "chromosomes",
    "pos_1",
    "pos_2",
    "orientation",
    "spanning",
    "mate_pairs",
    "mate_pairs_and_spanning_one",
    "contradictory_reads",
]

SPEC = {
    "__type__": "__type__",
    "chr_1": ("chromosomes", lambda x: x.split("-")[0].replace("chr", "")),
    "chr_2": ("chromosomes", lambda x: x.split("-")[1].replace("chr", "")),
    "pos_1": ("pos_1", int),
    "pos_2": ("pos_2", int),
    "orientation": "orientation",
    "spanning": ("spanning", int),
    "mate_pairs": ("mate_pairs", int),
    "mate_pairs_and_spanning_one": ("mate_pairs_and_spanning_one", int),
    "contradictory_reads": ("contradictory_reads", int),
}


@curry
def iterate_tuxedo_files(file_paths, columns=None):
    columns = columns or DEFAULT_TUXEDO_FILE_COLUMNS

    for file_path in file_paths:

        # todo: refactor: cannot depend on pipeline!
        from genomoncology.pipeline.sources import DelimitedFileSource

        source = DelimitedFileSource(
            file_path,
            delimiter="\t",
            columns=columns,
            __type__=DocType.TUXEDO.value,
        )

        for record in source:
            if DocType.HEADER.is_a(record):
                yield record
            else:
                transformed = glom(record, SPEC)
                yield transformed
