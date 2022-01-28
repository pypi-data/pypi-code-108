#!/usr/bin/env python
import dandelion as ddl
import pandas as pd
from pathlib import Path

from fixtures import (airr_travdv, fasta_10x_travdv, annotation_10x_travdv,
                      create_testfolder, database_paths, dummy_adata_travdv)


def test_loadtravdv(airr_travdv):
    temp = ddl.utilities._utilities.check_travdv(airr_travdv)
    assert temp.shape[0] == 6
    assert all([i == 'TRA' for i in airr_travdv['locus']])
    assert all([i == 'TRD' for i in temp['locus']])


def test_loadtravdv2(airr_travdv):
    vdj = ddl.Dandelion(airr_travdv)
    assert vdj.data.shape[0] == 6
    assert all([i == 'TRD' for i in vdj.data['locus']])


def test_write_fasta_tr(create_testfolder, fasta_10x_travdv):
    out_fasta = str(create_testfolder) + "/filtered_contig.fasta"
    fh = open(out_fasta, "w")
    fh.close()
    out = ''
    for l in fasta_10x_travdv:
        out = '>' + l + '\n' + fasta_10x_travdv[l] + '\n'
        ddl.utl.Write_output(out, out_fasta)
    assert len(list(create_testfolder.iterdir())) == 1


def test_write_annotation_tr(create_testfolder, annotation_10x_travdv):
    out_file = str(create_testfolder) + "/filtered_contig_annotations.csv"
    annotation_10x_travdv.to_csv(out_file, index=False)
    assert len(list(create_testfolder.iterdir())) == 2


def test_formatfasta(create_testfolder):
    ddl.pp.format_fastas(str(create_testfolder))
    assert len(list((create_testfolder / 'dandelion').iterdir())) == 2


def test_reannotategenes(create_testfolder, database_paths):
    ddl.pp.reannotate_genes(str(create_testfolder),
                            igblast_db=database_paths['igblast_db'],
                            germline=database_paths['germline'],
                            loci='tr')
    assert len(list((create_testfolder / 'dandelion/tmp').iterdir())) == 3
    assert len(list((create_testfolder / 'dandelion').iterdir())) == 4


def test_loadtravdv_reannotated(create_testfolder):
    vdj = ddl.Dandelion(
        str(create_testfolder) +
        '/dandelion/filtered_contig_igblast_db-pass.tsv')
    assert vdj.data.shape[0] == 6
    assert all([i == 'TRD' for i in vdj.data['locus']])


def test_travdv_filter(create_testfolder, dummy_adata_travdv):
    vdj = ddl.Dandelion(
        str(create_testfolder) +
        '/dandelion/filtered_contig_igblast_db-pass.tsv')
    assert vdj.data.shape[0] == 6
    assert all([i == 'TRD' for i in vdj.data['locus']])
    vdj2, adata = ddl.pp.filter_contigs(vdj, dummy_adata_travdv)
    assert vdj2.data.shape[0] == 6
