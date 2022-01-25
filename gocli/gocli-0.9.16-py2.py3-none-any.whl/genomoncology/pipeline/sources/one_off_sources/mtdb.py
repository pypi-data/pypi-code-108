from cytoolz.curried import curry, assoc

from genomoncology.parse import DocType, __TYPE__, __CHILD__
from ..base import LazyFileSource
import csv


@curry
class MTDBFileSource(LazyFileSource):
    def __init__(self, filename, **meta):
        self.filename = filename
        self.meta = meta

        if __TYPE__ not in meta:
            self.meta = assoc(self.meta, __TYPE__, DocType.MTDB_RECORD.value)

    def is_variant(self, base, aa, count):
        return count > 0 and aa != base

    def get_highest_aa_count(self, base, count_to_aa):
        highest_count = 0
        highest_aa = None
        for count, aa in count_to_aa.items():
            if aa != base and count > highest_count:
                highest_count = count
                highest_aa = aa
        return highest_aa

    def get_count(self, count):
        count = count.strip()
        if count:
            return int(count)
        return 0

    def __iter__(self):  # pragma: no mccabe
        yield self.create_header()

        with open(self.filename, mode="r") as tsv_file:
            csv_reader = csv.reader(tsv_file, delimiter="\t")
            for row in csv_reader:
                (
                    pos,
                    base,
                    a,
                    g,
                    c,
                    t,
                    gap,
                    location,
                    codon,
                    position,
                    amino_change,
                    syn,
                ) = row

                if pos == "Pos":
                    # skip header row
                    continue

                # clean up counts
                a = self.get_count(a)
                g = self.get_count(g)
                c = self.get_count(c)
                t = self.get_count(t)
                gap = self.get_count(gap)
                total = a + g + c + t + gap

                count_to_aa = {a: "A", g: "G", c: "C", t: "T", gap: "-"}

                highest_aa = self.get_highest_aa_count(base, count_to_aa)

                for count, aa in count_to_aa.items():
                    if self.is_variant(base, aa, count):
                        data = {
                            "chr": "M",
                            "start": pos,
                            "ref": base,
                            "alt": aa,
                            "functional_region": location,
                            "aa_change": None,
                            "count": count,
                            "total": total,
                            "frequency": float(count) / total
                            if total != 0
                            else None,
                            "csra": f"chrM|{pos}|{base}|{aa}|GRCh37",
                            "__type__": DocType.MTDB_RECORD,
                        }
                        if aa == highest_aa and amino_change and codon:
                            amino_change_vals = amino_change.split(" -> ")
                            if len(amino_change_vals) == 2:
                                data["aa_change"] = (
                                    amino_change_vals[0]
                                    + codon
                                    + amino_change_vals[1]
                                )
                        yield data

    def create_header(self):
        return {
            __TYPE__: DocType.HEADER.value,
            __CHILD__: self.meta.get(__TYPE__),
            "meta": self.meta,
            "fields": [
                "chr",
                "start",
                "ref",
                "alt",
                "functional_region",
                "aa_change",
                "count",
                "total",
                "frequency",
                "csra",
            ],
        }
