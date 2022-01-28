#!/usr/bin/env python
import os
import json
import pytest
import dandelion as ddl

from fixtures import (create_testfolder, airr_reannotated, airr_10x, fasta_10x,
                      annotation_10x, fasta_10x_cr6, annotation_10x_cr6,
                      json_10x_cr6)


def test_write_airr(create_testfolder, airr_10x):
    out_file = str(create_testfolder) + "/test_airr_rearrangements.tsv"
    airr_10x.to_csv(out_file, sep='\t', index=False)
    assert len(list(create_testfolder.iterdir())) == 1


def test_write_annotated(create_testfolder, airr_reannotated):
    out_file = str(create_testfolder) + "/test_airr_reannotated.tsv"
    airr_reannotated.to_csv(out_file, sep='\t', index=False)
    assert not airr_reannotated.np1_length.empty
    assert not airr_reannotated.np2_length.empty
    assert not airr_reannotated.junction_length.empty


def test_readwrite_h5(create_testfolder):
    out_file1 = str(create_testfolder) + "/test_airr_reannotated.tsv"
    out_file2 = str(create_testfolder) + "/test_airr_reannotated.h5"
    vdj = ddl.Dandelion(out_file1)
    assert not vdj.data.np1_length.empty
    assert not vdj.data.np2_length.empty
    assert not vdj.data.junction_length.empty
    vdj.write_h5(out_file2)
    vdj2 = ddl.read_h5(out_file2)
    assert not vdj2.data.np1_length.empty
    assert not vdj2.data.np2_length.empty
    assert not vdj2.data.junction_length.empty


def test_readwrite10xairr(create_testfolder):
    airr_file = str(create_testfolder) + "/test_airr_rearrangements.tsv"
    airr_file2 = str(create_testfolder) + "/test_airr_rearrangements2.tsv"
    vdj = ddl.read_10x_airr(airr_file)
    assert vdj.data.shape[0] == 9
    assert vdj.data.shape[1] == 32
    assert vdj.metadata.shape[0] == 5
    assert vdj.metadata.shape[1] == 26
    vdj.write_airr(airr_file2)
    vdj2 = ddl.read_10x_airr(airr_file2)
    assert vdj2.data.shape[0] == 9
    assert vdj2.data.shape[1] == 32
    assert vdj2.metadata.shape[0] == 5
    assert vdj2.metadata.shape[1] == 26
    os.remove(airr_file2)


def test_read10xvdj_json(create_testfolder, json_10x_cr6):
    json_file = str(create_testfolder) + "/test_all_contig_annotations.json"
    with open(json_file, 'w') as outfile:
        json.dump(json_10x_cr6, outfile)
    vdj = ddl.read_10x_vdj(json_file)
    assert vdj.data.shape[0] == 26
    assert vdj.data.shape[1] == 49
    assert vdj.metadata.shape[0] == 10
    assert vdj.metadata.shape[1] == 30
    os.remove(json_file)


def test_read10xvdj_cr6(create_testfolder, json_10x_cr6, annotation_10x_cr6,
                        fasta_10x_cr6):
    fasta_file = str(create_testfolder) + "/test_filtered_contig.fasta"
    json_file = str(create_testfolder) + "/test_all_contig_annotations.json"
    annot_file = str(
        create_testfolder) + "/test_filtered_contig_annotations.csv"
    annotation_10x_cr6.to_csv(annot_file, index=False)
    vdj = ddl.read_10x_vdj(annot_file)
    assert vdj.data.shape[0] == 26
    assert vdj.data.shape[1] == 31
    assert vdj.metadata.shape[0] == 10
    assert vdj.metadata.shape[1] == 30
    with open(json_file, 'w') as outfile:
        json.dump(json_10x_cr6, outfile)
    vdj = ddl.read_10x_vdj(annot_file)
    assert vdj.data.shape[0] == 26
    assert vdj.data.shape[1] == 49
    assert vdj.metadata.shape[0] == 10
    assert vdj.metadata.shape[1] == 30
    assert not vdj.data.sequence.empty
    os.remove(json_file)
    fh = open(fasta_file, "w")
    fh.close()
    out = ''
    for l in fasta_10x_cr6:
        out = '>' + l + '\n' + fasta_10x_cr6[l] + '\n'
        ddl.utl.Write_output(out, fasta_file)
    vdj = ddl.read_10x_vdj(annot_file)
    assert vdj.data.shape[0] == 26
    assert vdj.data.shape[1] == 32
    assert vdj.metadata.shape[0] == 10
    assert vdj.metadata.shape[1] == 30
    assert not vdj.data.sequence.empty
    os.remove(fasta_file)


def test_read10xvdj(create_testfolder, annotation_10x, fasta_10x):
    fasta_file = str(create_testfolder) + "/test_filtered_contig.fasta"
    annot_file = str(
        create_testfolder) + "/test_filtered_contig_annotations.csv"
    annotation_10x.to_csv(annot_file, index=False)
    vdj = ddl.read_10x_vdj(annot_file)
    assert vdj.data.shape[0] == 9
    assert vdj.data.shape[1] == 18
    assert vdj.metadata.shape[0] == 5
    assert vdj.metadata.shape[1] == 28
    fh = open(fasta_file, "w")
    fh.close()
    out = ''
    for l in fasta_10x:
        out = '>' + l + '\n' + fasta_10x[l] + '\n'
        ddl.utl.Write_output(out, fasta_file)
    vdj = ddl.read_10x_vdj(annot_file)
    assert vdj.data.shape[0] == 9
    assert vdj.data.shape[1] == 19
    assert vdj.metadata.shape[0] == 5
    assert vdj.metadata.shape[1] == 28
    assert not vdj.data.sequence.empty
    os.remove(fasta_file)


def test_read10xvdj_cr6_folder(create_testfolder, json_10x_cr6,
                               annotation_10x_cr6, fasta_10x_cr6):
    fasta_file = str(create_testfolder) + "/test_filtered_contig.fasta"
    json_file = str(create_testfolder) + "/test_all_contig_annotations.json"
    annot_file = str(
        create_testfolder) + "/test_filtered_contig_annotations.csv"
    annotation_10x_cr6.to_csv(annot_file, index=False)
    vdj = ddl.read_10x_vdj(str(create_testfolder))
    assert vdj.data.shape[0] == 26
    assert vdj.data.shape[1] == 31
    assert vdj.metadata.shape[0] == 10
    assert vdj.metadata.shape[1] == 30
    with open(json_file, 'w') as outfile:
        json.dump(json_10x_cr6, outfile)
    vdj = ddl.read_10x_vdj(str(create_testfolder))
    assert vdj.data.shape[0] == 26
    assert vdj.data.shape[1] == 49
    assert vdj.metadata.shape[0] == 10
    assert vdj.metadata.shape[1] == 30
    assert not vdj.data.sequence.empty
    os.remove(json_file)
    fh = open(fasta_file, "w")
    fh.close()
    out = ''
    for l in fasta_10x_cr6:
        out = '>' + l + '\n' + fasta_10x_cr6[l] + '\n'
        ddl.utl.Write_output(out, fasta_file)
    vdj = ddl.read_10x_vdj(str(create_testfolder))
    assert vdj.data.shape[0] == 26
    assert vdj.data.shape[1] == 32
    assert vdj.metadata.shape[0] == 10
    assert vdj.metadata.shape[1] == 30
    assert not vdj.data.sequence.empty
    os.remove(fasta_file)


def test_read10xvdj_folder(create_testfolder, annotation_10x, fasta_10x):
    fasta_file = str(create_testfolder) + "/test_filtered_contig.fasta"
    annot_file = str(
        create_testfolder) + "/test_filtered_contig_annotations.csv"
    annotation_10x.to_csv(annot_file, index=False)
    vdj = ddl.read_10x_vdj(str(create_testfolder))
    assert vdj.data.shape[0] == 9
    assert vdj.data.shape[1] == 18
    assert vdj.metadata.shape[0] == 5
    assert vdj.metadata.shape[1] == 28
    fh = open(fasta_file, "w")
    fh.close()
    out = ''
    for l in fasta_10x:
        out = '>' + l + '\n' + fasta_10x[l] + '\n'
        ddl.utl.Write_output(out, fasta_file)
    vdj = ddl.read_10x_vdj(str(create_testfolder))
    assert vdj.data.shape[0] == 9
    assert vdj.data.shape[1] == 19
    assert vdj.metadata.shape[0] == 5
    assert vdj.metadata.shape[1] == 28
    assert not vdj.data.sequence.empty
    os.remove(fasta_file)


def test_to_scirpy(create_testfolder, annotation_10x, fasta_10x):
    fasta_file = str(create_testfolder) + "/test_filtered_contig.fasta"
    annot_file = str(
        create_testfolder) + "/test_filtered_contig_annotations.csv"
    annotation_10x.to_csv(annot_file, index=False)
    vdj = ddl.read_10x_vdj(str(create_testfolder))
    assert vdj.data.shape[0] == 9
    assert vdj.data.shape[1] == 18
    assert vdj.metadata.shape[0] == 5
    assert vdj.metadata.shape[1] == 28
    adata = ddl.to_scirpy(vdj)
    assert adata.obs.shape[0] == 5
    assert adata.obs.shape[1] == 43
    fh = open(fasta_file, "w")
    fh.close()
    out = ''
    for l in fasta_10x:
        out = '>' + l + '\n' + fasta_10x[l] + '\n'
        ddl.utl.Write_output(out, fasta_file)
    vdj = ddl.read_10x_vdj(str(create_testfolder))
    assert vdj.data.shape[0] == 9
    assert vdj.data.shape[1] == 19
    assert vdj.metadata.shape[0] == 5
    assert vdj.metadata.shape[1] == 28
    assert not vdj.data.sequence.empty
    adata = ddl.to_scirpy(vdj)
    assert adata.obs.shape[0] == 5
    assert adata.obs.shape[1] == 43
    os.remove(fasta_file)
    vdjx = ddl.from_scirpy(adata)
    assert vdjx.data.shape[0] == 9


def test_tofro_scirpy_cr6(create_testfolder, annotation_10x_cr6, json_10x_cr6):
    json_file = str(create_testfolder) + "/test_all_contig_annotations.json"
    annot_file = str(create_testfolder) + "/test_all_contig_annotations.csv"
    annotation_10x_cr6.to_csv(annot_file, index=False)
    with open(json_file, 'w') as outfile:
        json.dump(json_10x_cr6, outfile)
    vdj = ddl.read_10x_vdj(str(create_testfolder), filename_prefix='test_all')
    assert vdj.data.shape[0] == 26
    assert vdj.data.shape[1] == 31
    assert vdj.metadata.shape[0] == 10
    assert vdj.metadata.shape[1] == 30
    adata = ddl.to_scirpy(vdj)
    assert adata.obs.shape[0] == 10
    assert adata.obs.shape[1] == 43
    vdjx = ddl.from_scirpy(adata)
    assert vdjx.data.shape[0] == 26
