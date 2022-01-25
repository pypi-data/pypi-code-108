"""Utility functions for working and reporting on gene data reports."""
from typing import List
from ncbi.datasets.openapi.models import V1GeneMatch
from ncbi.datasets.openapi.models import V1GeneDescriptor


def print_gene_warning_or_error(gene: V1GeneMatch):
    """Reports gene warnings and/or errors per query term

    Args:
        gene: A single gene metadata record returned by the API

    Returns:
        None

    Side Effects:
        Prints report to stdout.
    """
    message = {"query": gene.query}
    if gene.warnings:
        message["warning"] = gene.warnings[0].gene_warning_code
    if gene.errors:
        message["error"] = gene.errors[0].gene_error_code
    print(message)


def gene_values_by_fields(gene_descriptor: V1GeneDescriptor, fields=List[str]):
    """Filters gene descriptor for provided `fields`

    Args:
        gene_descriptor: A single gene metadata record returned by the API
        fields: List of fields to allow into returned dict

    Returns:
        dict of supplied fields to their values

    Side Effects:
        Prints report to stdout.
    """
    all_available_fields = {
        "gene_id": gene_descriptor.gene_id,
        "symbol": gene_descriptor.symbol,
    }
    return dict(filter(lambda i: i[0] in fields, all_available_fields.items()))


def print_gene_metadata_by_fields(gene: V1GeneMatch, fields=List[str]):
    """Reports selected fields for a V1GeneMatch object to stdout

    Warning/Error code will be printed if the supplied gene object does not contain a gene field.

    Args:
        gene: A single gene metadata record returned by the API
        fields: A list of field names to display.  If set to None, print the entire object.

    Returns:
        None

    Side Effects:
        Prints report to stdout.
    """
    if not gene.gene:
        print_gene_warning_or_error(gene)
        return

    gene_descriptor = gene.gene

    gene_metadata = {"query": gene.query}
    if fields is None:
        gene_metadata["gene"] = gene_descriptor
    else:
        gene_metadata.update(gene_values_by_fields(gene_descriptor, fields=fields))
    print(gene_metadata)
