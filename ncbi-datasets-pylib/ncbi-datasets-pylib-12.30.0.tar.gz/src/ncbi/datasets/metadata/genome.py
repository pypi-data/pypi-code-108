"""Utility functions for working and reporting on assembly data descriptors."""
from typing import List, Union
from ncbi.datasets.openapi.models import V1AssemblyMatch
from ncbi.datasets.openapi.models import V1AssemblyDatasetDescriptor
from ncbi.datasets.openapi import ApiClient as DatasetsApiClient
from ncbi.datasets.openapi import ApiException as DatasetsApiException
from ncbi.datasets.openapi.api.genome_api import GenomeApi as DatasetsGenomeApi

PAGE_SIZE_MAX = 1000


def print_assembly_warning_or_error(assembly_match: V1AssemblyMatch):
    """Reports assembly warnings and/or errors per query term

    Args:
        assembly_match: A single assembly metadata record returned by the API

    Returns:
        None

    Side Effects:
        Prints report to stdout.
    """
    print(assembly_match.messages)


def assembly_values_by_fields(assembly: V1AssemblyDatasetDescriptor, fields=List[str]):
    """Filters assembly descriptor for provided `fields`

    Args:
        assembly_descriptor: A single assembly descriptor record returned by the API
        fields: List of top-level fields to allow into returned dict

    Returns:
        dict of supplied fields to their values

    Side Effects:
        Prints report to stdout.
    """
    asm_descriptor_dict = assembly.to_dict()

    if not fields:
        return asm_descriptor_dict

    return {fld: asm_descriptor_dict[fld] for fld in fields if fld in asm_descriptor_dict}


def print_assembly_metadata_by_fields(assembly_match: V1AssemblyMatch, fields=List[str]):
    """Reports selected fields for a V1AssemblyMatch object to stdout

    Warning/Error code will be printed if the supplied assembly object does not contain a assembly field.

    Args:
        assembly_match: A single assembly metadata record returned by the API
        fields: A list of top-level field names to display.  If set to None, print the entire object.

    Returns:
        None

    Side Effects:
        Prints report to stdout.
    """
    if not assembly_match.assembly:
        print_assembly_warning_or_error(assembly_match)
        return

    assembly_descriptor = assembly_match.assembly
    assembly_metadata = assembly_values_by_fields(assembly_descriptor, fields=fields)
    print(assembly_metadata)


def get_assembly_metadata_by_taxon(taxon: Union[str, int], **kwargs):
    """Return iterable assembly metadata for a taxon

    Warning/Error code will be printed if the supplied taxon has no assembly.

    Args:
        taxon

    Returns:
        iterable assemblies

    Side Effects:
        Prints error to stdout.
    """
    with DatasetsApiClient() as api_client:
        genome_api = DatasetsGenomeApi(api_client)
        yield from iterate_reply(genome_api.assembly_descriptors_by_taxon, str(taxon), **kwargs)


def get_assembly_metadata_by_asm_accessions(genome_assembly_accessions: List[str], **kwargs):
    """Return iterable assembly metadata for a list of assembly accessions

    Warning/Error code will be printed if the supplied accessions are invalid.

    Args:
        genome_assembly_accessions: A list of NCBI assembly accessions

    Returns:
        iterable assemblies

    Side Effects:
        Prints error to stdout.
    """
    with DatasetsApiClient() as api_client:
        genome_api = DatasetsGenomeApi(api_client)
        yield from iterate_reply(
            genome_api.assembly_descriptors_by_accessions,
            genome_assembly_accessions,
            **kwargs,
        )


def get_assembly_metadata_by_bioproject_accessions(bioproject_accessions: List[str], **kwargs):
    """Return iterable assembly metadata for a list of BioProject accessions

    Warning/Error code will be printed if the supplied BioProject has no assembly.

    Args:
        bioproject_accessions: A list of NCBI bioproject accessions

    Returns:
        iterable assemblies

    Side Effects:
        Prints error to stdout.
    """
    with DatasetsApiClient() as api_client:
        genome_api = DatasetsGenomeApi(api_client)
        yield from iterate_reply(
            genome_api.assembly_descriptors_by_bioproject,
            bioproject_accessions,
            **kwargs,
        )


def iterate_reply(genome_api_func, func_arg, **kwargs):
    page_token = None
    try:
        while True:
            assembly_reply = genome_api_func(func_arg, page_size=PAGE_SIZE_MAX, page_token=page_token, **kwargs)
            if not assembly_reply.assemblies:
                print(f"No assemblies found for {func_arg}")
                return
            yield from assembly_reply.assemblies
            if assembly_reply.next_page_token:
                page_token = assembly_reply.next_page_token
            else:
                return
    except DatasetsApiException as e:
        print(f"Exception when calling GenomeApi: {e}\n")
