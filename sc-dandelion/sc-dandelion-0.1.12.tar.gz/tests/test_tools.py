#!/usr/bin/env python
import pytest
import json
import pandas as pd
import dandelion as ddl
import scanpy as sc
from pathlib import Path

from fixtures import (airr_reannotated, dummy_adata, create_testfolder,
                      json_10x_cr6, dummy_adata_cr6)


def test_setup(create_testfolder, airr_reannotated, dummy_adata):
    vdj, adata = ddl.pp.filter_contigs(airr_reannotated, dummy_adata)
    assert airr_reannotated.shape[0] == 9
    assert vdj.data.shape[0] == 7
    assert vdj.metadata.shape[0] == 4
    assert adata.n_obs == 5
    f = create_testfolder / "test.h5"
    vdj.write_h5(f)
    assert len(list(create_testfolder.iterdir())) == 1
    vdj2 = ddl.read_h5(f)
    assert vdj2.metadata is not None


def test_find_clones(create_testfolder):
    f = create_testfolder / "test.h5"
    vdj = ddl.read_h5(f)
    ddl.tl.find_clones(vdj)
    assert not vdj.data.clone_id.empty
    assert not vdj.metadata.clone_id.empty
    assert len(set(x for x in vdj.metadata['clone_id'] if pd.notnull(x))) == 4
    vdj.write_h5(f)


def test_clone_size(create_testfolder):
    f = create_testfolder / "test.h5"
    vdj = ddl.read_h5(f)
    ddl.tl.clone_size(vdj)
    assert not vdj.metadata.clone_id_size.empty
    ddl.tl.clone_size(vdj, max_size=3)
    assert not vdj.metadata.clone_id_size.empty


@pytest.mark.parametrize(
    "resample,expected",
    [pytest.param(None, 4), pytest.param(3, 3)])
def test_generate_network(create_testfolder, resample, expected):
    f = create_testfolder / "test.h5"
    vdj = ddl.read_h5(f)
    if resample is not None:
        vdj = ddl.tl.generate_network(vdj, downsample=resample)
    else:
        ddl.tl.generate_network(vdj)
    assert vdj.distance is not None
    assert vdj.edges is None
    assert vdj.n_obs == expected
    assert vdj.layout is not None
    assert vdj.graph is not None
    vdj.data['clone_id'] = '1'
    vdj = ddl.Dandelion(vdj.data)
    assert vdj.data.clone_id.dtype == 'object'
    ddl.tl.generate_network(vdj)
    assert vdj.edges is not None


def test_find_clones_key(create_testfolder):
    f = create_testfolder / "test.h5"
    vdj = ddl.read_h5(f)
    ddl.tl.find_clones(vdj, key_added='test_clone')
    assert not vdj.metadata.test_clone.empty
    assert vdj.data.test_clone.dtype == 'object'
    ddl.tl.generate_network(vdj, clone_key='test_clone')
    assert vdj.distance is not None
    assert vdj.edges is None
    assert vdj.layout is not None
    assert vdj.graph is not None


def test_transfer(create_testfolder, dummy_adata):
    f = create_testfolder / "test.h5"
    vdj = ddl.read_h5(f)
    vdj, adata = ddl.pp.filter_contigs(vdj, dummy_adata)
    ddl.tl.transfer(dummy_adata, vdj)
    assert 'clone_id' in dummy_adata.obs
    ddl.tl.generate_network(vdj)
    ddl.tl.transfer(dummy_adata, vdj)
    assert 'X_vdj' in dummy_adata.obsm
    f2 = create_testfolder / "test.h5ad"
    dummy_adata.write_h5ad(f2)


def test_diversity_gini(create_testfolder):
    f = create_testfolder / "test.h5"
    vdj = ddl.read_h5(f)
    ddl.tl.clone_diversity(vdj, groupby='sample_id')
    assert not vdj.metadata.clone_network_vertex_size_gini.empty
    assert not vdj.metadata.clone_network_cluster_size_gini.empty
    ddl.tl.generate_network(vdj)
    ddl.tl.clone_diversity(vdj, groupby='sample_id', metric='clone_centrality')
    assert not vdj.metadata.clone_centrality_gini.empty
    assert not vdj.metadata.clone_size_gini.empty


def test_diversity_gini(create_testfolder):
    f = create_testfolder / "test.h5"
    vdj = ddl.read_h5(f)
    ddl.tl.clone_diversity(vdj, groupby='sample_id')


def test_diversity_gini_simple(create_testfolder):
    f = create_testfolder / "test.h5"
    vdj = ddl.read_h5(f)


@pytest.mark.parametrize("resample", [True, False])
def test_diversity_chao(create_testfolder, resample):
    f = create_testfolder / "test.h5"
    vdj = ddl.read_h5(f)
    if resample:
        ddl.tl.clone_diversity(vdj,
                               groupby='sample_id',
                               method='chao1',
                               resample=resample,
                               downsample=6)
    else:
        ddl.tl.clone_diversity(vdj,
                               groupby='sample_id',
                               method='chao1',
                               resample=resample)
    assert not vdj.metadata.clone_size_chao1.empty


@pytest.mark.parametrize("method,diversitykey", [
    pytest.param('chao1', None),
    pytest.param('chao1', 'test_diversity_key'),
    pytest.param('shannon', None),
    pytest.param('shannon', 'test_diversity_key'),
])
def test_diversity_anndata(create_testfolder, method, diversitykey):
    f = create_testfolder / "test.h5ad"
    adata = sc.read_h5ad(f)
    ddl.tl.clone_diversity(adata,
                           groupby='sample_id',
                           method=method,
                           diversity_key=diversitykey)
    if diversitykey is None:
        assert 'diversity' in adata.uns
    else:
        assert 'test_diversity_key' in adata.uns


@pytest.mark.parametrize("resample,normalize", [
    pytest.param(True, True),
    pytest.param(False, True),
    pytest.param(True, False),
    pytest.param(False, False),
])
def test_diversity_shannon(create_testfolder, resample, normalize):
    f = create_testfolder / "test.h5"
    vdj = ddl.read_h5(f)
    if resample:
        ddl.tl.clone_diversity(vdj,
                               groupby='sample_id',
                               method='shannon',
                               resample=resample,
                               normalize=normalize,
                               downsample=6)
    else:
        ddl.tl.clone_diversity(vdj,
                               groupby='sample_id',
                               method='shannon',
                               resample=resample,
                               normalize=normalize)
    if normalize:
        assert not vdj.metadata.clone_size_normalized_shannon.empty
    else:
        assert not vdj.metadata.clone_size_shannon.empty


def test_setup2(create_testfolder, json_10x_cr6, dummy_adata_cr6):
    json_file = str(create_testfolder) + "/test_all_contig_annotations.json"
    with open(json_file, 'w') as outfile:
        json.dump(json_10x_cr6, outfile)
    vdj = ddl.read_10x_vdj(str(create_testfolder))
    vdj, adata = ddl.pp.filter_contigs(vdj, dummy_adata_cr6)
    assert vdj.data.shape[0] == 14
    assert vdj.data.shape[1] == 50
    assert vdj.metadata.shape[0] == 7
    assert vdj.metadata.shape[1] == 28
    ddl.tl.find_clones(vdj)
    ddl.tl.generate_network(vdj, key='sequence')
    ddl.tl.transfer(adata, vdj)
    f = create_testfolder / "test.h5"
    vdj.write_h5(f)
    f2 = create_testfolder / "test.h5ad"
    adata.write_h5ad(f2)


def test_diversity_rarefaction(create_testfolder):
    f = create_testfolder / "test.h5ad"
    adata = sc.read_h5ad(f)
    ddl.tl.clone_rarefaction(adata, groupby='sample_id')
    assert 'diversity' in adata.uns
    ddl.tl.clone_rarefaction(adata,
                             groupby='sample_id',
                             diversity_key='test_diversity_key')
    assert 'test_diversity_key' in adata.uns
    p = ddl.pl.clone_rarefaction(adata, color='sample_id')
    assert p is not None


def test_diversity_rarefaction2(create_testfolder):
    f = create_testfolder / "test.h5ad"
    adata = sc.read_h5ad(f)
    ddl.tl.clone_rarefaction(adata, groupby='sample_id', clone_key='clone_id')
    assert 'diversity' in adata.uns
    p = ddl.pl.clone_rarefaction(adata, color='sample_id')
    assert p is not None
    adata = sc.read_h5ad(f)
    p = ddl.pl.clone_rarefaction(adata, color='sample_id')
    assert p is not None


def test_diversity_rarefaction3(create_testfolder):
    f = create_testfolder / "test.h5"
    vdj = ddl.read_h5(f)
    vdj.data['sample_id'] = 'sample_test'
    vdj.data['contig_QC_pass'] = 'True'
    ddl.update_metadata(vdj,
                        retrieve=['sample_id', 'contig_QC_pass'],
                        retrieve_mode=['merge and unique only', 'merge and unique only'])
    df = ddl.tl.clone_rarefaction(vdj, groupby='sample_id')
    assert isinstance(df, dict)
    p = ddl.pl.clone_rarefaction(vdj, color='sample_id')
    assert p is not None


@pytest.mark.parametrize(
    "metric", ['clone_network', None, 'clone_degree', 'clone_centrality'])
def test_diversity_gini2(create_testfolder, metric):
    f = create_testfolder / "test.h5"
    vdj = ddl.read_h5(f)
    vdj.data['sample_id'] = 'sample_test'
    vdj.data['contig_QC_pass'] = 'True'
    ddl.update_metadata(vdj,
                        retrieve=['sample_id', 'contig_QC_pass'],
                        retrieve_mode=['merge and unique only', 'merge and unique only'])
    ddl.tl.clone_diversity(vdj,
                           groupby='sample_id',
                           resample=True,
                           downsample=6,
                           key='sequence',
                           n_resample=5,
                           metric=metric)
    if metric == 'clone_network' or metric is None:
        assert not vdj.metadata.clone_network_cluster_size_gini.empty
        assert not vdj.metadata.clone_network_vertex_size_gini.empty
    if metric == 'clone_degree':
        assert not vdj.metadata.clone_degree.empty
        assert not vdj.metadata.clone_size_gini.empty
        assert not vdj.metadata.clone_degree_gini.empty
    if metric == 'clone_centrality':
        assert not vdj.metadata.clone_centrality.empty
        assert not vdj.metadata.clone_centrality_gini.empty


def test_diversity2a(create_testfolder):
    f = create_testfolder / "test.h5"
    vdj = ddl.read_h5(f)
    vdj.data['sample_id'] = 'sample_test'
    vdj.data['contig_QC_pass'] = 'True'
    ddl.update_metadata(vdj,
                        retrieve=['sample_id', 'contig_QC_pass'],
                        retrieve_mode=['merge and unique only', 'merge and unique only'])
    ddl.tl.clone_diversity(vdj,
                           groupby='sample_id',
                           reconstruct_network=False,
                           key='sequence')
    assert not vdj.metadata.clone_network_cluster_size_gini.empty
    assert not vdj.metadata.clone_network_vertex_size_gini.empty


def test_diversity2b(create_testfolder):
    f = create_testfolder / "test.h5"
    vdj = ddl.read_h5(f)
    vdj.data['sample_id'] = 'sample_test'
    vdj.data['contig_QC_pass'] = 'True'
    ddl.update_metadata(vdj,
                        retrieve=['sample_id', 'contig_QC_pass'],
                        retrieve_mode=['merge and unique only', 'merge and unique only'])
    ddl.tl.clone_diversity(vdj,
                           groupby='sample_id',
                           use_contracted=True,
                           key='sequence')
    assert not vdj.metadata.clone_network_cluster_size_gini.empty
    assert not vdj.metadata.clone_network_vertex_size_gini.empty


def test_diversity2c(create_testfolder):
    f = create_testfolder / "test.h5"
    vdj = ddl.read_h5(f)
    vdj.data['sample_id'] = 'sample_test'
    vdj.data['contig_QC_pass'] = 'True'
    ddl.update_metadata(vdj,
                        retrieve=['sample_id', 'contig_QC_pass'],
                        retrieve_mode=['merge and unique only', 'merge and unique only'])
    x = ddl.tl.clone_diversity(vdj,
                               groupby='sample_id',
                               key='sequence',
                               update_obs_meta=False)
    assert isinstance(x, pd.DataFrame)


def test_overlap1(create_testfolder):
    f = create_testfolder / "test.h5ad"
    adata = sc.read_h5ad(f)
    ddl.tl.clone_overlap(adata, groupby='group3', colorby='group2')
    assert 'clone_overlap' in adata.uns
    assert isinstance(adata.uns['clone_overlap'], pd.DataFrame)
    ddl.pl.clone_overlap(adata, groupby='group3', colorby='group2')


def test_overlap2(create_testfolder):
    f = create_testfolder / "test.h5ad"
    adata = sc.read_h5ad(f)
    ddl.pl.clone_overlap(adata, groupby='group3', colorby='group2')


def test_extract_edge_weights(create_testfolder):
    f = create_testfolder / "test.h5"
    vdj = ddl.read_h5(f)
    x = ddl.tl.extract_edge_weights(vdj)
    assert x is None
    x = ddl.tl.extract_edge_weights(vdj, expanded_only=True)
    assert x is None
