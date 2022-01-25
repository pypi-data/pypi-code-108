from enum import Enum
from cytoolz.curried import curry

__TYPE__ = "__type__"
__CHILD__ = "__child__"


class DocType(Enum):
    ANNOTATED_CALL = "ANNOTATED_CALL"
    ANNOTATED_MATCH_CALL = "ANNOTATED_MATCH_CALL"
    ANNOTATED_VARIANT = "ANNOTATED_VARIANT"
    ANNOTATED_TSV = "ANNOTATED_TSV"
    CALL = "CALL"
    REF_CALL = "REF_CALL"
    UNKNOWN_CALL = "UNKNOWN_CALL"
    SKIPPED_CALL = "SKIPPED_CALL"
    FEATURE = "FEATURE"
    GENE = "GENE"
    HEADER = "HEADER"
    VARIANT = "VARIANT"
    TRIAL = "TRIAL"
    CONTENT = "CONTENT"
    THERAPY = "THERAPY"
    TUXEDO = "TUXEDO"
    ALTERATION = "ALTERATION"
    MARKER = "MARKER"

    TSV = "TSV"
    AGGREGATE = "AGGREGATE"
    MAF = "MAF"

    UNIPROT_RECORD = "UNIPROT_RECORD"
    MITOMAP_RECORD = "MITOMAP_RECORD"
    MTDB_RECORD = "MTDB_RECORD"

    # Annotation Data Sets
    GNOMAD = "GNOMAD"
    HGMD = "HGMD"
    HGMD_GENE_LIST = "HGMD_GENE_LIST"
    BAYLOR_WGL = "BAYLOR_WGL"
    DBNSFP = "DBNSFP"
    CLINVAR = "CLINVAR"
    CLINVAR_XML = "CLINVAR_XML"
    THOUSANDGENOMES = "THOUSANDGENOMES"
    DBSNP = "DBSNP"
    EXAC = "EXAC"
    SPLICING = "SPLICING"
    EVS = "EVS"
    COSMIC = "COSMIC"
    BAYLOR_DECIPHER = "BAYLOR_DECIPHER"
    HPO = "HPO"
    OMIM = "OMIM"
    UNIPROT_PROTEIN_NAME = "UNIPROT_PROTEIN_NAME"
    UNIPROT_DOMAIN = "UNIPROT_DOMAIN"
    UNIPROT = "UNIPROT"
    MITOMAP = "MITOMAP"
    GNOMAD_GENE = "GNOMAD_GENE"
    GENE_TYPE = "GENE_TYPE"
    SECONDARY_FINDINGS_GENES = "SECONDARY_FINDINGS_GENES"
    MITO_TRNA = "MITO_TRNA"
    MTDB = "MTDB"
    CLINGEN_DOSAGE = "CLINGEN_DOSAGE"

    def is_a(self, a_dict):
        try:
            if isinstance(a_dict, dict):
                return a_dict[__TYPE__] == self.value
            return False
        except KeyError:
            return False

    def is_not(self, a_dict):
        return not self.is_a(a_dict)

    @classmethod
    def is_one(cls, doctypes, a_dict):
        """
        :param doctypes: iterable (preferably a set) of DocType values
        :param a_dict: object to check the type of
        :return:
        """

        try:
            return a_dict[__TYPE__] in doctypes
        except KeyError:
            return False

    @classmethod
    def get_doc_type(cls, a_dict):
        return a_dict.get(__CHILD__, a_dict.get(__TYPE__))

    @classmethod
    def get_default_columns(cls, a_dict):
        doc_type = cls.get_doc_type(a_dict)
        columns = DEFAULT_COLUMNS.get(doc_type)
        columns = columns or sorted(a_dict.keys())
        return [c for c in columns if not c.startswith("__")]

    @classmethod
    def get_header_names(cls, columns):
        return [to_header(c) for c in columns]

    @classmethod
    def get_sheet_name(cls, a_dict):
        doc_type = cls.get_doc_type(a_dict)
        return to_sheet_name(doc_type)

    @classmethod
    def create(cls, name: str):
        try:
            return DocType(name.upper() if name else None)
        except ValueError:
            pass


CALL_VARIANT_SET = {DocType.CALL.value, DocType.VARIANT.value}
CALL_VARIANT_KEYS = {"chr", "start", "ref", "alt"}


def is_call_or_variant(doc):
    return DocType.is_one(CALL_VARIANT_SET, doc) or not (
        CALL_VARIANT_KEYS - doc.keys()
    )


def is_not_skipped_call(doc):
    return DocType.SKIPPED_CALL.is_not(doc)


def is_header(doc):
    return DocType.HEADER.is_not(doc)


def is_annotated_call(doc):
    return DocType.ANNOTATED_CALL.is_a(doc)


@curry
def filter_out_ref_unknown(doc, keep_ref_unknown_calls=False):
    if not keep_ref_unknown_calls:
        return DocType.REF_CALL.is_not(doc) and DocType.UNKNOWN_CALL.is_not(
            doc
        )
    return True


DEFAULT_COLUMNS = {
    DocType.GENE.value: ["chromosome", "start", "end", "gene"],
    DocType.CALL.value: [
        "sample_name",
        "chr",
        "start",
        "ref",
        "alt",
        "ref_depth",
        "alt_depth",
        "vaf",
        "quality",
    ],
    DocType.ANNOTATED_CALL.value: [
        "sample_name",
        "annotations.hgvs_g",
        "annotations.canonical_c_dot",
        "annotations.canonical_alteration",
        "annotations.canonical_mutation_type",
        "annotations.canonical_gene",
        "annotations.GNOMAD__AF__mfloat",
        "annotations.ExAC__AF__float",
        "annotations.clinvar__CLNSIG__string",
        "ref_depth",
        "alt_depth",
        "vaf",
        "quality",
    ],
    DocType.ALTERATION.value: [
        "name",
        "mutation_type",
        "genes",
        "coordinates",
        "file_path",
    ],
}

COLUMN_TO_HEADER = {
    "annotations.hgvs_g": "hgvs (g.)",
    "annotations.canonical_c_dot": "hgvs (c.)",
    "annotations.canonical_alteration": "alteration",
    "annotations.canonical_mutation_type": "mutation type",
    "annotations.canonical_gene": "gene",
    "annotations.GNOMAD__AF__mfloat": "GNOMAD pop. freq.",
    "annotations.ExAC__AF__float": "ExAC pop. freq.",
}

TYPE_TO_SHEET = {}


def to_header(column):
    return COLUMN_TO_HEADER.setdefault(
        column, column.split(".")[-1].replace("_", " ")
    )


def to_sheet_name(doc_type):
    return TYPE_TO_SHEET.setdefault(
        doc_type, doc_type.replace("_", " ").title() + "s"
    )
