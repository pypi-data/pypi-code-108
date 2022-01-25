from intervaltree import IntervalTree


# method to map from one chromosome to another (i.e. "M" should map to "MT)
def map_chr(chromosome):
    if chromosome == "M":
        return "MT"
    return chromosome


def clean_chr(chromosome):
    return map_chr(str(chromosome).replace("chr", ""))


class BEDFilter(object):
    def __init__(self, file_path, padding=0):
        self._map = {}

        for line in open(file_path, "r"):
            values = line.strip().split("\t")
            (chromosome, start, end) = values[:3]
            chromosome = clean_chr(chromosome)
            tree = self.get_tree(chromosome)

            start = int(start) - padding
            end = int(end) + 1 + padding  # +1 to make search inclusive

            tree[start:end] = values[3:]

    def __contains__(self, item):
        chromosome, pos = to_chr_pos(item)
        return self.get_tree(chromosome).overlaps(pos)

    def __call__(self, item):
        return item in self

    def get_tree(self, chromosome):
        chromosome = str(chromosome)

        if chromosome not in self._map:
            self._map[chromosome] = IntervalTree()

        return self._map[chromosome]

    def search(self, item):
        chromosome, pos = to_chr_pos(item)
        return self.get_tree(chromosome).search(pos)


# support both plain and chr-prefix versions of 1-22, X, Y, and MT
KNOWN_CHROMOSOMES = list(map(str, range(1, 23))) + ["X", "Y", "MT", "M"]
KNOWN_CHROMOSOMES += list(map(lambda x: f"chr{x}", KNOWN_CHROMOSOMES))


class ValidChromosomeFilter(object):
    def __contains__(self, item):
        chromosome, _ = to_chr_pos(item)
        return chromosome in KNOWN_CHROMOSOMES

    def __call__(self, item):
        return item in self


def to_chr_pos(item):
    if isinstance(item, tuple):
        (chromosome, pos) = (clean_chr(item[0]), int(item[1]))
    else:
        (chromosome, pos) = (clean_chr(item.chrom), int(item.pos))

    return chromosome, pos
