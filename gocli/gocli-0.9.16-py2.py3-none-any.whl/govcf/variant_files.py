import os
import collections
import related

from pysam import VariantFile

from .calculate_vaf import find as find_vaf_map
from .bed_filter import ValidChromosomeFilter


def iterate_vcf_files(
    file_paths,
    include_vaf=True,
    bed_filter=None,
    build=None,
    keep_ref_unknown_calls=False,
):
    assert not isinstance(file_paths, str), "Requires list or iterator of str."
    for file_path in file_paths:
        for call in iterate_vcf_calls(
            file_path,
            include_vaf=include_vaf,
            bed_filter=bed_filter,
            build=build,
            keep_ref_unknown_calls=keep_ref_unknown_calls,
        ):
            yield call


def iterate_vcf_calls(
    file_path,
    include_vaf=True,
    bed_filter=None,
    build=None,
    keep_ref_unknown_calls=False,
):
    vcf_iter = create_vcf_iter(file_path)

    header = create_header_dict(next(vcf_iter), include_vaf, file_path)
    yield header

    vaf_map = find_vaf_map(header.get("types").keys()) if include_vaf else None

    bed_filter = bed_filter or ValidChromosomeFilter()

    for record in filter(bed_filter, vcf_iter):
        samples = get_samples(record)

        for sample in samples:
            # if GT not specified, then assume single alt
            allele_indices, zyg, is_ref_unknown = get_allele_indices_and_zyg(
                sample
            )

            for allele_index in allele_indices:
                alt = get_alt(record, allele_index)
                info = capture_info(header, record, sample, allele_index)

                # VCF 4.2: '*' indicates allele missing due to upstream del
                if alt in ["*", "."]:
                    yield create_skipped_call_dict(
                        record, sample, alt, info.get("GT")
                    )
                elif keep_ref_unknown_calls or not is_ref_unknown:
                    vaf_dict = (
                        vaf_map(info, allele_index, alt) if vaf_map else {}
                    )
                    yield create_call_dict(
                        record, sample, alt, zyg, info, vaf_dict, build
                    )


# private methods


@related.immutable()
class SampleSubstitute(object):
    name = related.StringField(default="sample")
    allele_indices = related.SequenceField(int, default=[1])
    alleles = related.SequenceField(str, default=["?"])
    phased = related.BooleanField(default=False)

    @staticmethod
    def iteritems():
        return []

    @property
    def allele_indices(self):
        return range(len(self.alleles))


substitute_sample = SampleSubstitute()


def get_alt(record, allele_index):
    try:
        alt = record.alleles[allele_index]
    except IndexError:
        alt = "."
    return alt


def get_samples(record):
    samples = list(record.samples.itervalues())
    if not samples:
        samples = [SampleSubstitute(alleles=record.alleles)]
    return samples


def create_vcf_iter(file_path):
    vcf = VariantFile(file_path)
    yield vcf.header

    for vcf_record in vcf.fetch():
        yield vcf_record


def create_header_dict(header, include_vaf, file_path):
    return dict(
        __type__="HEADER",
        __child__="CALL",
        __record__=str(header),
        file_path=os.path.realpath(file_path),
        config=dict(include_vaf=include_vaf),
        types=capture_solr_types(header),
        info=create_meta_dict(header.info.items()),
        formats=create_meta_dict(header.formats.items()),
    )


def iter_attrs(obj, include_private=False, type_filter=None):
    for attr_name in dir(obj):
        if include_private or not attr_name.startswith("_"):
            attr_value = getattr(obj, attr_name)
            if not type_filter or isinstance(attr_value, type_filter):
                yield attr_name, attr_value


def create_meta_dict(items, meta_types=(int, str, bool, float)):
    meta = {}
    for (key, value) in items:
        meta[key] = dict(iter_attrs(value, type_filter=meta_types))
    return meta


def map_chr(chromosome):
    if chromosome == "M":
        return "MT"
    return chromosome


def get_call_type(zyg, allele_indices):
    call_type = "CALL"
    if zyg == "homozygous" and all(
        [allele_index == 0 for allele_index in allele_indices]
    ):
        call_type = "REF_CALL"
    if zyg == "unknown" and all(
        [allele_index is None for allele_index in allele_indices]
    ):
        call_type = "UNKNOWN_CALL"
    return call_type


def create_call_dict(record, sample, alt, zyg, info, vaf_dict, build):
    call_type = get_call_type(zyg, sample.allele_indices)
    return dict(
        __type__=call_type,
        __record__=str(record),
        chr=map_chr(record.chrom.replace("chr", "")),
        start=record.pos,
        end=record.stop,
        ref=record.ref,
        alt=alt,
        sample_name=sample.name,
        alleles=sample.alleles,
        allele_indices=sample.allele_indices,
        zyg=zyg,
        is_phased=sample.phased,
        quality=record.qual,
        id=record.id,
        filters=list(record.filter),
        info=info,
        build=build,
        **vaf_dict,
    )


def create_skipped_call_dict(record, sample, alt, gt):
    return dict(
        __type__="SKIPPED_CALL",
        __record__=str(record),
        chr=map_chr(record.chrom.replace("chr", "")),
        start=record.pos,
        end=record.stop,
        ref=record.ref,
        alt=alt,
        GT=gt,
        sample_name=sample.name,
        alleles=sample.alleles,
        allele_indices=sample.allele_indices,
    )


def get_allele_indices_and_zyg(sample):
    allele_indices = sample.allele_indices or [1]
    zyg = determine_zyg(allele_indices)
    allele_indices = sorted(set(filter(None, allele_indices)))

    # keep all the 0/0 and ./. calls (will filter them out later)
    if not allele_indices:
        return [1], zyg, True

    return allele_indices, zyg, False


def capture_value(value, meta, allele_index):
    if meta:
        number = meta.get("number")

        # todo: additional thought required here and impact to calc vaf mappers
        # todo: for example, "R" might best return 2 values: REF + *THIS* ALT
        if number == "A":
            idx = allele_index - 1
            value = ensure_collection(value)
            value = value[idx] if idx < len(value) else value
    return value


def capture_by_section(iteritems, meta, allele_index):
    info = {}

    try:
        for (name, value) in iteritems:
            field_meta = meta.get(name)
            value = capture_value(value, field_meta, allele_index)
            info[name] = value

    except ValueError:
        # Note: https://github.com/pysam-developers/pysam/issues/593
        pass

    return info


def capture_info(header, record, sample, allele_index):

    info = capture_by_section(
        record.info.iteritems(), header.get("info"), allele_index
    )

    info.update(
        capture_by_section(
            sample.iteritems(), header.get("formats"), allele_index
        )
    )

    info["GT"] = format_GT(info, sample)

    return info


def capture_solr_types(header):
    def to_solr_type(meta):
        multi = "" if meta.number in {0, 1, "A"} else "m"
        meta_type = TYPES.get(meta.type, "string")
        return multi + meta_type

    solr_t = dict([(m.name, to_solr_type(m)) for m in header.info.values()])
    solr_t.update([(m.name, to_solr_type(m)) for m in header.formats.values()])
    return solr_t


def ensure_collection(x):
    """ Ensures the parameter provided is an iterable """

    if x is None:
        x = []

    elif isinstance(x, collections.Iterator):
        x = list(x)

    elif not isinstance(x, (list, tuple, set)):
        x = [x]

    return x


def determine_zyg(allele_indicies):
    if len(allele_indicies) == 1:
        zyg = "hemizygous"
    elif None in allele_indicies:
        zyg = "unknown"

    elif allele_indicies[0] != allele_indicies[1]:
        zyg = "heterozygous"

    elif allele_indicies[0] == allele_indicies[1]:
        zyg = "homozygous"

    else:
        zyg = "unknown"

    return zyg


def format_GT(info, sample):
    gt = info.get("GT")
    if gt:
        sep = "|" if sample.phased else "/"
        gt = map(lambda g: "." if g is None else str(g), gt)
        return sep.join(gt)


# constants

TYPES = dict(Integer="int", Float="float", Flag="boolean")
