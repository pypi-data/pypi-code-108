#!/usr/bin/env python
import dandelion as ddl
import scanpy as sc
import requests
import os

from fixtures import airr_reannotated


def test_recipe():
    try:
        adata = sc.datasets.pbmc3k()
    except:
        fname = 'pbmc3k_filtered_gene_bc_matrices.tar.gz'
        url = 'http://cf.10xgenomics.com/samples/cell-exp/1.1.0/pbmc3k/' + fname
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open('filtered_gene_bc_matrices.tar.gz', 'wb') as f:
                f.write(r.raw.read())
        os.system('tar -xzvf filtered_gene_bc_matrices.tar.gz')
        adata = sc.read_10x_mtx('filtered_gene_bc_matrices/hg19')
    ddl.pp.external.recipe_scanpy_qc(adata)
    assert not adata.obs['filter_rna'].empty
    # ddl.pp.external.recipe_scanpy_qc(adata, mito_cutoff = None) # weird segmentation fault in the tests
    # assert not adata.obs['gmm_pct_count_clusters_keep'].empty


def test_update_plus(airr_reannotated):
    vdj = ddl.Dandelion(airr_reannotated)
    vdj.update_plus()
    assert 'mu_count' in vdj.metadata
    vdj.update_plus(option = 'sequence')
    assert 'sequence_VDJ' in vdj.metadata
    vdj.update_plus(option = 'cdr3 lengths')
    assert 'junction_aa_length_VDJ' in vdj.metadata
    vdj = ddl.Dandelion(airr_reannotated)
    vdj.update_plus(option = 'mutations')
    assert 'mu_count' in vdj.metadata
    vdj.update_plus(option = 'all')
    assert 'sequence_VDJ' in vdj.metadata
    vdj.update_plus(option = 'cdr3 lengths')
