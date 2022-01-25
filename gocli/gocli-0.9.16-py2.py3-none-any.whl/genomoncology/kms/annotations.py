import re
from functools import partial
from typing import Iterable

from cytoolz.curried import curry, assoc

from gosdk import logger
from genomoncology.parse import (
    is_call_or_variant,
    __TYPE__,
    DocType,
    __CHILD__,
)
from genomoncology.parse.ensures import ensure_collection
from genomoncology.pipeline.converters import obj_to_dict
from gosdk.models import AnnotationList, AnnotationMatchList

from genomoncology.cli.const import GRCh37


@curry
def hotspot_annotate(data, data_set, data_set_version, sdk=None):
    annotated_hotspots = annotate_hotspots(data)

    annotations_list = sdk.call_with_retry(
        sdk.annotations.load_annotations,
        data_set=data_set,
        data_set_version=data_set_version,
        data=annotated_hotspots,
    )

    return annotations_list


EXCLUDE_BUILD_FIELDS = ["is_gene_annotation"]


@curry
async def async_annotate_match(
    data,
    sdk=None,
    delete_if_exists=False,
    build=GRCh37,
    annotation_bundle_version=None,
):
    csra_batch = convert_to_csra([{**d, "build": build} for d in data])

    if csra_batch:
        annotations_list = await sdk.call_with_retry(
            sdk.annotations.post_annotations_match,
            batch=csra_batch,
            delete_if_exists=delete_if_exists,
            build=build,
        )
    else:
        annotations_list = None

    annotated_calls = annotate_match_calls(
        annotations_list, data, annotation_bundle_version
    )

    logger.get_logger().debug(
        "async_annotate_match",
        call_count=len(data),
        first_call=data[:1],
        csra_batch=csra_batch[:4],
        annotated_count=len(annotated_calls),
        first_annotated=annotated_calls[:1],
    )

    return annotated_calls


@curry
def sync_annotate_match(
    data,
    sdk=None,
    delete_if_exists=False,
    build=GRCh37,
    annotation_bundle_version=None,
):
    csra_batch = convert_to_csra([{**d, "build": build} for d in data])

    annotations_list = (
        sdk.call_with_retry(
            sdk.annotations.post_annotations_match,
            batch=csra_batch,
            delete_if_exists=delete_if_exists,
            build=build,
        )
        if csra_batch
        else None
    )

    annotated_calls = annotate_match_calls(
        annotations_list, data, annotation_bundle_version
    )

    logger.get_logger().debug(
        "sync_annotate_match",
        call_count=len(data),
        call_first=data[:1],
        csra_batch=csra_batch[:4] if csra_batch else None,
        annotated_count=len(annotated_calls),
        annotated_first=annotated_calls[:1],
    )

    return annotated_calls


@curry
async def async_annotate(
    data,
    sdk=None,
    fields=None,
    delete_if_exists=False,
    build=GRCh37,
    filter_anns=None,
    annotation_bundle_version=None,
):
    csra_batch = convert_to_csra([{**d, "build": build} for d in data])

    if csra_batch:
        annotations_list = await sdk.call_with_retry(
            sdk.annotations.post_annotations,
            batch=csra_batch,
            delete_if_exists=delete_if_exists,
            build=build,
        )
    else:
        annotations_list = None

    annotated_calls = annotate_calls(
        annotations_list,
        data,
        fields,
        annotation_bundle_version,
        filter_anns=filter_anns,
    )

    logger.get_logger().debug(
        "async_annotate",
        call_count=len(data),
        first_call=data[:1],
        csra_batch=csra_batch[:4],
        annotated_count=len(annotated_calls),
        first_annotated=annotated_calls[:1],
    )

    return annotated_calls


@curry
def sync_annotate(
    data,
    sdk=None,
    fields=None,
    delete_if_exists=False,
    build=GRCh37,
    filter_anns=None,
    annotation_bundle_version=None,
):
    csra_batch = convert_to_csra([{**d, "build": build} for d in data])

    annotations_list = (
        sdk.call_with_retry(
            sdk.annotations.post_annotations,
            batch=csra_batch,
            delete_if_exists=delete_if_exists,
            build=build,
        )
        if csra_batch
        else None
    )

    annotated_calls = annotate_calls(
        annotations_list,
        data,
        fields,
        annotation_bundle_version,
        filter_anns=filter_anns,
    )

    logger.get_logger().debug(
        "sync_annotate",
        call_count=len(data),
        call_first=data[:1],
        csra_batch=csra_batch[:4] if csra_batch else None,
        annotated_count=len(annotated_calls),
        annotated_first=annotated_calls[:1],
    )

    return annotated_calls


@curry
async def async_load_annotations(
    data, sdk=None, data_set=None, data_set_version=None, build=GRCh37
):
    # do not add the build field (or set it equal to None)
    # if certain fields are present
    if len(data) > 0 and any(
        [key in EXCLUDE_BUILD_FIELDS for key in data[0].keys()]
    ):
        build = None
    response = await sdk.call_with_retry(
        sdk.annotations.load_annotations,
        data=override_hgvs([{**d, "build": build} for d in data]),
        data_set=data_set,
        data_set_version=data_set_version,
    )

    logger.get_logger().debug(
        "async_load_annotations", call_count=len(data), first_record=data[:1]
    )

    # response of warehouse is blank, returning data for downstream processing
    return data, response


@curry
def sync_refresh(data, sdk=None, recalculate_hgvs=False, batch_size=50):
    chromosome, start, end = format_chromosome_start_end(data)

    cursor_mark = "*"
    has_more = True

    while has_more:
        future = sdk.annotations.refresh_annotations(
            cursor_mark=cursor_mark,
            rows=batch_size,
            recalculate_hgvs=recalculate_hgvs,
            chromosome=chromosome,
            start=start,
            end=end,
        )

        result = future.result()
        has_more = result.more
        cursor_mark = result.next_cursor_mark

        # echo message
        msg = [result.rows, has_more, result.last_hgvs, cursor_mark]
        print("  /  ".join(map(str, msg)))


# private methods
def override_hgvs(data):
    data = ensure_collection(data)
    return list(map(up_build, data))


def convert_to_csra(data, add_build=True):
    # create batch of CSRA strings for calling HGVS API
    data = ensure_collection(data)
    calls_only = filter(is_call_or_variant, data)
    csra_batch = list(
        to_csra(call, add_build=add_build) for call in calls_only
    )
    return csra_batch


def get_mutation_type(record):
    if "*" in record["Residue"]:
        return ["Nonstop Extension"]
    elif "X" in record["Residue"]:
        return ["Splice Donor Site", "Splice Acceptor Site"]
    elif "*" in record["Variants"] and "|" in record["Variants"]:
        return ["Substitution - Missense", "Substitution - Nonsense"]
    elif "*" in record["Variants"]:
        return ["Substitution - Nonsense"]
    else:
        return ["Substitution - Missense"]


def annotate_hotspots(data):
    print(data)
    annotations = []
    num_pattern = re.compile("[0-9]+")
    alpha_pattern = re.compile("[a-zA-Z]+")
    for record in data:
        ann = {}
        ann["gene"] = record["Gene"]
        ann["is_hotspot_annotation"] = True
        if record["Type"] == "single residue":
            ref_aa = num_pattern.sub("", record["Residue"])
            pos = alpha_pattern.sub("", record["Residue"])
            if ref_aa != "X":
                ann["codon_start"] = pos
                ann["codon_end"] = pos
                ann["ref_aa_start"] = ref_aa
                ann["ref_aa_end"] = ref_aa
            else:
                ann["nearest_codon"] = pos
            ann["hotspot_mutation_type"] = get_mutation_type(record)
        elif record["Type"] == "in-frame indel":
            start_end = record["Residue"].split("-")
            ann["codon_start"] = start_end[0]
            ann["codon_end"] = start_end[1]
            ann["hotspot_mutation_type"] = [
                "Insertion - In frame",
                "Deletion - In frame",
                "Complex - insertion inframe",
                "Complex - deletion inframe",
                "Complex - compound substitution",
            ]

        annotations.append(ann)

    return annotations


def annotate_match_calls(annotations_list, data, annotation_bundle_version):
    func = partial(
        add_annotation_match, annotations_list, annotation_bundle_version
    )
    annotated_calls = list(map(func, data))
    return annotated_calls


def add_annotation_match(
    annotations_list: AnnotationMatchList, expected_bundle_version, call: dict
):  # pragma: no mccabe

    if annotations_list and is_call_or_variant(call):
        csra = to_csra(call)
        annotations = (
            obj_to_dict(None, annotations_list.get_annotation(csra)) or {}
        )

        # if the annotation_bundle does not match, raise an exception
        if expected_bundle_version is not None:

            actual_bundle_version = (
                annotations.get("annotation_bundle_version")
                or expected_bundle_version
            )

            if expected_bundle_version != actual_bundle_version:
                msg = (
                    "Annotations Process Terminated due to "
                    "annotations_bundle_version "
                    "changing during a run. \n"
                    "Expected annotation bundle version: {expected} \n"
                    "Actual annotation bundle version: {actual}".format(
                        expected=expected_bundle_version,
                        actual=actual_bundle_version,
                    )
                )
                raise AnnBundleVersionAssertionError(msg)

        call["annotations"] = annotations
        call[__TYPE__] = f"ANNOTATED_MATCH_{call.get(__TYPE__, 'CALL')}"

    elif DocType.HEADER.is_a(call):
        call[__CHILD__] = f"ANNOTATED_MATCH_{call.get(__CHILD__, 'CALL')}"

    return call


def annotate_calls(
    annotations_list, data, fields, annotation_bundle_version, filter_anns=None
):
    # todo: determine if it makes sense to not return all annotations....
    fields = None  # resolve_fields(fields)
    func = partial(
        add_annotation,
        annotations_list,
        fields,
        annotation_bundle_version,
        filter_anns=filter_anns,
    )
    annotated_calls = list(map(func, data))
    return annotated_calls


def add_annotation(
    annotations_list: AnnotationList,
    fields,
    expected_bundle_version,
    call: dict,
    filter_anns=None,
):  # pragma: no mccabe

    if annotations_list and is_call_or_variant(call):
        csra = to_csra(call)
        annotations = (
            obj_to_dict(fields, annotations_list.get_annotation(csra)) or {}
        )

        # if the annotation_bundle does not match, raise an exception
        if expected_bundle_version is not None:

            actual_bundle_version = (
                annotations.get("annotation_bundle_version")
                or expected_bundle_version
            )

            if expected_bundle_version != actual_bundle_version:
                msg = (
                    "Annotations Process Terminated due to "
                    "annotations_bundle_version "
                    "changing during a run. \n"
                    "Expected annotation bundle version: {expected} \n"
                    "Actual annotation bundle version: {actual}".format(
                        expected=expected_bundle_version,
                        actual=actual_bundle_version,
                    )
                )
                raise AnnBundleVersionAssertionError(msg)

        # filter the annotations if there was a filter file passed in
        if filter_anns is not None and isinstance(filter_anns, list):
            annotations = handle_filtering_annotations(
                annotations, filter_anns
            )

        call["annotations"] = annotations
        call[__TYPE__] = f"ANNOTATED_{call.get(__TYPE__, 'CALL')}"

    elif DocType.HEADER.is_a(call):
        call[__CHILD__] = f"ANNOTATED_{call.get(__CHILD__, 'CALL')}"

    return call


def handle_filtering_annotations(annotations, filter_anns):
    gene_annotations = []
    for gene_ann in annotations.get("gene_annotations", []):
        gene_ann_filtered = {
            k: v
            for k, v in gene_ann.items()
            if k in filter_anns or k == "gene"
        }
        if len(gene_ann_filtered) > 0:
            gene_annotations.append(gene_ann_filtered)
    annotations["gene_annotations"] = gene_annotations
    annotations = {
        k: v
        for k, v in annotations.items()
        if k in filter_anns or k == "gene_annotations"
    }
    return annotations


def up_build(call: dict):
    hgvs_g = call.get("hgvs_g")
    build = call.get("build")
    has_both = hgvs_g is not None and build is not None

    if has_both and not hgvs_g.endswith(f"|{build}"):
        hgvs_parts = hgvs_g.split("|")
        if len(hgvs_parts) >= 4:
            hgvs_parts = hgvs_parts[:4] + [build]
            call = assoc(call, "hgvs_g", "|".join(hgvs_parts))

    return call


def to_csra(call: dict, add_build=True, add_chr=True):
    chromosome = f"chr{call.get('chr')}" if add_chr else call.get("chr")
    csra_data = (
        chromosome,
        str(call.get("start")),
        call.get("ref") or "-",
        call.get("alt") or "-",
        call.get("build") or GRCh37,
    )
    return "|".join(csra_data[0:] if add_build else csra_data[0:4])


def resolve_fields(fields: Iterable[str] = None) -> Iterable[str]:
    fields = ensure_collection(fields)
    if fields == ["*"]:
        fields = None
    else:
        fields = ANNOTATIONS + [f for f in fields if f not in ANNOTATIONS_SET]
    return fields


def format_chromosome_start_end(data):
    if data is None:
        return None, None, None
    data = [None if not str(x).strip() else x for x in data]
    return data[0], data[1], data[2]


async def get_annotation_bundle_version_async(sdk):
    annotation_bundle_version = await sdk.call_with_retry(
        sdk.info.get_annotation_bundle_version
    )
    return annotation_bundle_version.annotation_bundle_version


def get_annotation_bundle_version(sdk):
    annotation_bundle_version = sdk.call_with_retry(
        sdk.info.get_annotation_bundle_version
    )
    return annotation_bundle_version.annotation_bundle_version


class AnnBundleVersionAssertionError(AssertionError):
    pass


ANNOTATIONS = [
    "GNOMAD__AF__mfloat",
    "ExAC__AF__float",
    "canonical_alteration",
    "canonical_c_dot",
    "canonical_gene",
    "canonical_mutation_type",
    "canonical_p_dot",
    "clinvar__CLNSIG__string",
    "display",
    "mutation_type",
    "representations",
    "hgvs_g",
    "alteration",
    "gene_annotations",
]

ANNOTATIONS_SET = set(ANNOTATIONS)
