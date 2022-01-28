import json
import os
import dandelion as ddl

from fixtures import (json_10x_cr6, dummy_adata_cr6, create_testfolder)


def test_filtercontigs(create_testfolder, dummy_adata_cr6, json_10x_cr6):
    json_file = str(create_testfolder) + "/test_all_contig_annotations.json"
    out_file = str(create_testfolder) + "/test_filtered.tsv"
    with open(json_file, 'w') as outfile:
        json.dump(json_10x_cr6, outfile)
    vdj = ddl.read_10x_vdj(str(create_testfolder), filename_prefix='test_all')
    vdj2, adata = ddl.pp.filter_contigs(vdj, dummy_adata_cr6)
    assert vdj.data.shape[0] == 26
    assert vdj2.data.shape[0] == 14
    assert adata.obs.shape[0] == 10
    vdj2, adata = ddl.pp.filter_contigs(vdj,
                                        dummy_adata_cr6,
                                        productive_only=False)
    assert vdj.data.shape[0] == 26
    assert vdj2.data.shape[0] == 23
    assert adata.obs.shape[0] == 10
    vdj2, adata = ddl.pp.filter_contigs(vdj,
                                        dummy_adata_cr6,
                                        productive_only=True,
                                        simple=True)
    assert vdj.data.shape[0] == 26
    assert vdj2.data.shape[0] == 26
    assert adata.obs.shape[0] == 10
    vdj2, adata = ddl.pp.filter_contigs(vdj,
                                        dummy_adata_cr6,
                                        productive_only=False,
                                        simple=True)
    assert vdj.data.shape[0] == 26
    assert vdj2.data.shape[0] == 26
    assert adata.obs.shape[0] == 10
    vdj2, adata = ddl.pp.filter_contigs(vdj,
                                        dummy_adata_cr6,
                                        productive_only=True,
                                        filter_vj_chains=False)
    assert vdj.data.shape[0] == 26
    assert vdj2.data.shape[0] == 17
    assert adata.obs.shape[0] == 10
    vdj2, adata = ddl.pp.filter_contigs(vdj,
                                        dummy_adata_cr6,
                                        filter_vj_chains=False,
                                        keep_highest_umi=False)
    assert vdj.data.shape[0] == 26
    assert vdj2.data.shape[0] == 17
    assert adata.obs.shape[0] == 10
    vdj2, adata = ddl.pp.filter_contigs(vdj,
                                        dummy_adata_cr6,
                                        filter_rna = True)
    assert vdj.data.shape[0] == 26
    assert vdj2.data.shape[0] == 14
    assert adata.obs.shape[0] == 9
    vdj2, adata = ddl.pp.filter_contigs(vdj,
                                        dummy_adata_cr6,
                                        productive_only=False,
                                        filter_poorqualitycontig = True)
    assert vdj.data.shape[0] == 26
    assert vdj2.data.shape[0] == 23
    assert adata.obs.shape[0] == 10
    vdj2, adata = ddl.pp.filter_contigs(vdj, dummy_adata_cr6, save = out_file)
    assert os.path.exists(out_file)


def test_filtercontigs_no_adata(create_testfolder):
    json_file = str(create_testfolder) + "/test_all_contig_annotations.json"
    vdj = ddl.read_10x_vdj(str(create_testfolder), filename_prefix='test_all')
    vdj2 = ddl.pp.filter_contigs(vdj)
    assert vdj.data.shape[0] == 26
    assert vdj2.data.shape[0] == 14
