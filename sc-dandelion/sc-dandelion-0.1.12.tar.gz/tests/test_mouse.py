#!/usr/bin/env python
import pandas as pd
import dandelion as ddl
from pathlib import Path

from fixtures_mouse import (fasta_10x_mouse, annotation_10x_mouse,
                            database_paths_mouse, dummy_adata_mouse,
                            balbc_ighg_primers)
from fixtures import (processed_files, create_testfolder)


def test_write_fasta(create_testfolder, fasta_10x_mouse):
    out_fasta = str(create_testfolder) + "/filtered_contig.fasta"
    fh = open(out_fasta, "w")
    fh.close()
    out = ''
    for l in fasta_10x_mouse:
        out = '>' + l + '\n' + fasta_10x_mouse[l] + '\n'
        ddl.utl.Write_output(out, out_fasta)
    assert len(list(create_testfolder.iterdir())) == 1


def test_write_annotation(create_testfolder, annotation_10x_mouse):
    out_file = str(create_testfolder) + "/filtered_contig_annotations.csv"
    annotation_10x_mouse.to_csv(out_file, index=False)
    assert len(list(create_testfolder.iterdir())) == 2


def test_formatfasta(create_testfolder):
    ddl.pp.format_fastas(str(create_testfolder))
    assert len(list((create_testfolder / 'dandelion').iterdir())) == 2


def test_reannotategenes(create_testfolder, database_paths_mouse):
    ddl.pp.reannotate_genes(str(create_testfolder),
                            igblast_db=database_paths_mouse['igblast_db'],
                            germline=database_paths_mouse['germline'],
                            org='mouse')
    assert len(list((create_testfolder / 'dandelion/tmp').iterdir())) == 3


def test_reassignalleles(create_testfolder, database_paths_mouse):
    ddl.pp.reassign_alleles(str(create_testfolder),
                            combined_folder='test_mouse',
                            germline=database_paths_mouse['germline'],
                            org='mouse',
                            novel=True,
                            plot=False)
    assert len(list((create_testfolder / 'dandelion/tmp').iterdir())) == 6


def test_updateblastdb(database_paths_mouse):
    ddl.utl.makeblastdb(database_paths_mouse['blastdb_fasta'])
    assert len(list(Path(database_paths_mouse['blastdb']).iterdir())) == 10


def test_assignsisotypes(create_testfolder, database_paths_mouse,
                         balbc_ighg_primers):
    ddl.pp.assign_isotypes(str(create_testfolder),
                           blastdb=database_paths_mouse['blastdb_fasta'],
                           correction_dict=balbc_ighg_primers,
                           plot=False)
    assert len(list((create_testfolder / 'dandelion').iterdir())) == 4


def test_create_germlines(create_testfolder, processed_files,
                          database_paths_mouse):
    f = create_testfolder / str('dandelion/' + processed_files['filtered'])
    ddl.pp.create_germlines(f, germline=database_paths_mouse['germline'])
    f2 = create_testfolder / str('dandelion/' +
                                 processed_files['germline-dmask'])
    dat = pd.read_csv(f2, sep='\t')
    assert not dat['germline_alignment_d_mask'].empty


def test_filtercontigs(create_testfolder, processed_files, dummy_adata_mouse):
    f = create_testfolder / str('dandelion/' + processed_files['filtered'])
    dat = pd.read_csv(f, sep='\t')
    vdj, adata = ddl.pp.filter_contigs(dat, dummy_adata_mouse)
    assert dat.shape[0] == 1287
    assert vdj.data.shape[0] == 787
    assert vdj.metadata.shape[0] == 395
    assert adata.n_obs == 547
    f1 = create_testfolder / "test.h5"
    f2 = create_testfolder / "test.h5ad"
    vdj.write_h5(f1)
    adata.write_h5ad(f2)


def test_generate_network(create_testfolder):
    f = create_testfolder / "test.h5"
    vdj = ddl.read_h5(f)
    ddl.tl.find_clones(vdj)
    ddl.tl.generate_network(vdj)
    assert vdj.distance is not None
    assert vdj.edges is not None
    assert vdj.n_obs == 395
    assert vdj.layout is not None
    assert vdj.graph is not None
