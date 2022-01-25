from cytoolz.curried import curry
from collections import deque

from specd.sdk.create import make_iterable

from .base import FileSink
from govcf.variant_files import ensure_collection
from genomoncology.parse import DocType

import related


@related.immutable()
class DummyVariantRecord(object):
    chrom = related.StringField()
    pos = related.IntegerField()
    ref = related.StringField()
    alt = related.StringField()
    info = related.ChildField(dict, default=dict)

    CHR_FIELDS = ["chr", "c"]
    POS_FIELDS = ["pos", "s", "start", "hg19_pos", "hg37_pos", "hg38_pos"]
    REF_FIELDS = ["ref", "r"]
    ALT_FIELDS = ["alt", "a"]
    INFO_IGNORE = {"__type__", "build"}

    def __str__(self):
        return (
            "\t".join(
                [
                    self.chrom,
                    str(self.pos),
                    ".",
                    self.ref,
                    self.alt,
                    ".",
                    ".",
                    self.info_str,
                ]
            )
            + "\n"
        )

    @property
    def info_str(self):
        return ";".join(self.info_nvp())

    def info_nvp(self):
        for (name, value) in self.info.items():
            if name == "info":
                ivalues = value[0].items()
                for (iname, ivalue) in ivalues:
                    yield f"{iname}={ivalue}"

            elif name not in self.INFO_IGNORE:
                value_str = ",".join(map(str, value))
                yield f"{name}={value_str}"

    @classmethod
    def pop_first(cls, unit: dict, field_names: list):
        for field_name in field_names:
            value = unit.pop(field_name, None)
            if value is not None:
                return value

    @classmethod
    def create_from_unit(cls, unit: dict):
        unit = unit.copy()
        chrom = cls.pop_first(unit, cls.CHR_FIELDS)
        pos = cls.pop_first(unit, cls.POS_FIELDS)
        ref = cls.pop_first(unit, cls.REF_FIELDS)
        alt = cls.pop_first(unit, cls.ALT_FIELDS)

        info = {}
        for (name, value) in unit.items():
            info[name] = ensure_collection(value)

        return DummyVariantRecord(chrom, pos, ref, alt, info)


@curry
class HistoricalVcfFileSink(FileSink):
    def __init__(self, filename, header_file_path=None):
        super().__init__(filename, insert_newlines=False)
        self.recent_records_seen = deque(maxlen=100)
        self.count = 0
        self.header_file_path = header_file_path
        # map from original record to a dict containing:
        #   - the total number of alts for this record
        #   - the number of the alts already encountered
        #   - the updated record object (with annotations
        #     from its alts in the INFO column)
        self.multi_alt_lines = {}

    def handle_key(self, key, alt_index=None):
        return "%s__%d" % (key, alt_index) if alt_index else key

    def handle_value(self, value):
        return "|".join(
            [
                ascii(item).replace(" ", "_").replace("'", "")
                for item in make_iterable(value)
            ]
        )

    def handle_gene_annotations(
        self, info_dict, gene_annotations, alt_index=None
    ):
        # loop through all gene annotations and add them in the format
        # {ann_key_name}__{gene_name}=value. This way, we can successfully
        # handle variants that span across multiple genes.
        for gene_ann in gene_annotations:
            gene_name = gene_ann.pop("gene", "")
            if gene_ann:
                for k, v in gene_ann.items():
                    key = self.handle_key("%s__%s" % (k, gene_name), alt_index)
                    value = self.handle_value(v)
                    if value:
                        info_dict[key] = value

    def add_annotations_to_info(self, existing_info, unit, alt_index=None):
        # handle existing info
        if not existing_info or existing_info == ".":
            existing_info = ""

        annotations = unit.get("annotations", {})
        info_dict = {}

        # add annotation key-value pairs to info_dict
        for key, value in annotations.items():
            if key == "gene_annotations":
                self.handle_gene_annotations(info_dict, value, alt_index)
                continue
            value = self.handle_value(annotations.get(key))
            key = self.handle_key(key, alt_index)
            if value:
                info_dict[key] = value

        # merge all info values into a semicolon-separated string
        info_strings = [f"{key}={value}" for key, value in info_dict.items()]

        # add semicolon to end of existing info if there isn't one already
        if info_strings and existing_info and existing_info[-1] != ";":
            existing_info += ";"

        updated_info = existing_info + ";".join(info_strings)
        if not updated_info:
            updated_info = "."

        return updated_info

    def handle_historical(self, record, unit, alt_index=None):
        columns = record.split("\t")
        if len(columns) >= 10 and not columns[0].startswith("#"):
            # add annotations from unit to record_info
            record_info = columns[7]
            columns[7] = self.add_annotations_to_info(
                record_info, unit, alt_index
            )
        return "\t".join(columns)

    def get_record_alt(self, record):
        columns = record.split("\t")
        if len(columns) >= 10 and not columns[0].startswith("#"):
            return columns[4].split(",")
        return []

    def handle_multi_alt(self, record, unit, record_alt):
        # figure out what alt_index this is
        unit_alt = unit.get("alt", "")
        alt_index = record_alt.index(unit_alt)
        if alt_index < 0:
            return record

        # see if this record has already been encountered!
        multi_alt_record = self.multi_alt_lines.get(record, {})
        if not multi_alt_record:
            # set up default value
            multi_alt_record = {
                "total_num_alts": len(record_alt),
                "num_alts_encountered": 0,
                "updated_record": record,
            }
        multi_alt_record["num_alts_encountered"] = (
            multi_alt_record.get("num_alts_encountered") + 1
        )
        multi_alt_record["updated_record"] = self.handle_historical(
            multi_alt_record.get("updated_record"), unit, alt_index + 1
        )
        self.multi_alt_lines[record] = multi_alt_record

        num_encountered = multi_alt_record.get("num_alts_encountered")
        total_num_alts = multi_alt_record.get("total_num_alts")
        if num_encountered == total_num_alts:
            # we have encountered all of the alts for this record!
            # No need to keep it in the map.
            _ = self.multi_alt_lines.pop(record)
            return multi_alt_record.get("updated_record")
        else:
            return None

    def get_header(self):
        if self.header_file_path is not None:
            with open(self.header_file_path) as header_file:
                header_file_lines = header_file.readlines()
                return "".join(header_file_lines)
        return DEFAULT_VCF_HEADER

    def get_record_str(self, unit) -> str:
        record = unit.get("__record__")
        if record is None:
            if DocType.HEADER.is_a(unit):
                record = self.get_header()
            else:
                record = DummyVariantRecord.create_from_unit(unit)
        # even if there IS a record, if this is a header
        # and we have a header override, use the override
        if DocType.HEADER.is_a(unit) and self.header_file_path is not None:
            record = self.get_header()
        record = str(record)
        return record

    def convert(self, unit):
        self.count += 1
        record = self.get_record_str(unit)

        # handle this record if is is a multi-alt record
        record_alt = self.get_record_alt(record)
        is_multi_alt = len(record_alt) > 1
        if is_multi_alt:
            # if multi_alt_record is None, this multi-alt record is not yet
            # ready to be written to the VCF because we have not yet seen
            # all of its constituent alts. But if we HAVE seen them all,
            # multi_alt_record will be populated with the record string
            # (with the annotations from all the constituent alts in
            # the INFO column)
            multi_alt_record = self.handle_multi_alt(record, unit, record_alt)
            if multi_alt_record:
                return multi_alt_record

        if record not in self.recent_records_seen and not is_multi_alt:
            self.recent_records_seen.append(record)
            # add the annotations to the INFO column.
            record = self.handle_historical(record, unit)
            return record


@curry
class VcfFileSink(FileSink):
    def __init__(self, filename, header_file_path=None):
        super().__init__(filename, insert_newlines=False)
        self.recent_records_seen = deque(maxlen=100)
        self.count = 0
        self.header_file_path = header_file_path

    def get_header(self):
        if self.header_file_path is not None:
            with open(self.header_file_path) as header_file:
                header_file_lines = header_file.readlines()
                return "".join(header_file_lines)
        return DEFAULT_VCF_HEADER

    def get_record_str(self, unit) -> str:
        record = unit.get("__record__")
        if record is None:
            if DocType.HEADER.is_a(unit):
                record = self.get_header()
            else:
                record = DummyVariantRecord.create_from_unit(unit)
        # even if there IS a record, if this is a header
        # and we have a header override, use the override
        if DocType.HEADER.is_a(unit) and self.header_file_path is not None:
            record = self.get_header()
        record = str(record)
        return record

    def convert(self, unit):
        self.count += 1
        record = self.get_record_str(unit)

        if record not in self.recent_records_seen:
            self.recent_records_seen.append(record)
            return record


DEFAULT_VCF_HEADER = """##fileformat=VCFv4.2
##contig=<ID=1,length=249250621>
##contig=<ID=2,length=243199373>
##contig=<ID=3,length=198022430>
##contig=<ID=4,length=191154276>
##contig=<ID=5,length=180915260>
##contig=<ID=6,length=171115067>
##contig=<ID=7,length=159138663>
##contig=<ID=8,length=146364022>
##contig=<ID=9,length=141213431>
##contig=<ID=10,length=135534747>
##contig=<ID=11,length=135006516>
##contig=<ID=12,length=133851895>
##contig=<ID=13,length=115169878>
##contig=<ID=14,length=107349540>
##contig=<ID=15,length=102531392>
##contig=<ID=16,length=90354753>
##contig=<ID=17,length=81195210>
##contig=<ID=18,length=78077248>
##contig=<ID=19,length=59128983>
##contig=<ID=20,length=63025520>
##contig=<ID=21,length=48129895>
##contig=<ID=22,length=51304566>
##contig=<ID=X,length=155270560>
##contig=<ID=Y,length=59373566>
##contig=<ID=MT,length=16569>
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
"""
