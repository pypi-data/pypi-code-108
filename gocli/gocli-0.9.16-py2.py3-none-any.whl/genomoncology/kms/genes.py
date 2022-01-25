from functools import partial

from cytoolz.curried import curry

from genomoncology.pipeline.converters import obj_to_dict
from genomoncology.parse.ensures import ensure_collection
from genomoncology.parse.doctypes import DocType
from genomoncology.cli.const import GRCh37


@curry
def sync_genes(data, sdk=None, fields=("chromosome", "start", "end", "name")):
    batch = ensure_collection(data)
    kwargs = dict(name=batch, fields=fields, page_size=len(batch))
    gene_list = sdk.call_with_retry(sdk.genes.get_genes, **kwargs)
    func = partial(obj_to_dict, fields, __type__=DocType.GENE.value)
    return list(map(func, gene_list.results))


@curry
def sync_boundaries(
    data, sdk=None, fields=("chromosome", "start", "end", "gene"), build=GRCh37
):
    batch = ensure_collection(data)
    kwargs = dict(name=batch, build=build)
    gene_list = sdk.call_with_retry(sdk.genes.gene_boundaries, **kwargs)
    func = partial(obj_to_dict, fields, __type__=DocType.GENE.value)
    formatted_results = list(map(func, gene_list.results))
    if gene_list.not_found:
        message = "The following genes could not be found: " + ", ".join(
            gene_list.not_found
        )
        formatted_results.append(message)
    return formatted_results
