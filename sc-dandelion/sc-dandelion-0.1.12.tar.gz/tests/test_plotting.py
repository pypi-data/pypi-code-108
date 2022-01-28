#!/usr/bin/env python
import pytest
import dandelion as ddl
import scanpy as sc

from fixtures import (airr_reannotated, dummy_adata, create_testfolder)


def test_setup(create_testfolder, airr_reannotated, dummy_adata):
    vdj, adata = ddl.pp.filter_contigs(airr_reannotated, dummy_adata)
    assert airr_reannotated.shape[0] == 9
    assert vdj.data.shape[0] == 7
    assert vdj.metadata.shape[0] == 4
    assert adata.n_obs == 5
    vdj.data['clone_id'] = ['A', 'A', 'A', 'A', 'A', 'A', 'A']
    vdj = ddl.Dandelion(vdj.data)
    ddl.tl.generate_network(vdj)
    ddl.tl.transfer(adata, vdj)
    assert 'clone_id' in adata.obs
    assert 'X_vdj' in adata.obsm
    f1 = create_testfolder / "test.h5"
    f2 = create_testfolder / "test.h5ad"
    vdj.write_h5(f1)
    adata.write_h5ad(f2)


def test_plot_network(create_testfolder):
    f = create_testfolder / "test.h5ad"
    adata = sc.read_h5ad(f)
    ddl.pl.clone_network(adata,
                         color=['isotype'],
                         show=False,
                         return_fig=False)


@pytest.mark.parametrize("sort,norm", [
    pytest.param(True, True),
    pytest.param(True, False),
    pytest.param(False, True),
    pytest.param(False, False)
])
def test_plot_bar(create_testfolder, sort, norm):
    f = create_testfolder / "test.h5"
    vdj = ddl.read_h5(f)
    ax = ddl.pl.barplot(vdj, color='v_call_genotyped_VDJ')
    assert ax is not None
    ax = ddl.pl.barplot(vdj,
                        color='v_call_genotyped_VDJ',
                        sort_descending=sort)
    assert ax is not None
    ax = ddl.pl.barplot(vdj, color='v_call_genotyped_VDJ', normalize=norm)
    assert ax is not None


@pytest.mark.parametrize("norm", [True, False])
def test_plot_stackedbar(create_testfolder, norm):
    f = create_testfolder / "test.h5"
    vdj = ddl.read_h5(f)
    ax = ddl.pl.stackedbarplot(vdj,
                               color='v_call_genotyped_VDJ',
                               groupby='isotype',
                               normalize=norm)
    assert ax is not None


def test_plot_spectratype(create_testfolder):
    f = create_testfolder / "test.h5"
    vdj = ddl.read_h5(f)
    ax = ddl.pl.spectratype(vdj,
                            color='junction_length',
                            groupby='c_call',
                            locus='IGH')
    assert ax is not None
