#!/usr/bin/env python
import pandas as pd
import dandelion as ddl

from fixtures import (airr_reannotated, create_testfolder, database_paths)


def test_importrpy2():

    from rpy2.robjects.packages import importr
    from rpy2.rinterface import NULL
    from rpy2.robjects import pandas2ri
    sh = importr('shazam')

    assert sh.__module__ == 'rpy2.robjects.packages'


def test_mutation(create_testfolder, airr_reannotated):
    f = create_testfolder / "test.tsv"
    airr_reannotated.to_csv(f, sep='\t', index=False)
    ddl.pp.quantify_mutations(f)
    out = pd.read_csv(f, sep='\t')
    vdj = ddl.Dandelion(out)
    assert not vdj.data.mu_count.empty
    ddl.pp.quantify_mutations(f, frequency=True)
    assert not vdj.data.mu_freq.empty


def test_create_germlines(create_testfolder, database_paths):
    f = create_testfolder / "test.tsv"
    out = pd.read_csv(f, sep='\t')
    vdj = ddl.Dandelion(out)
    ddl.pp.create_germlines(vdj, germline=database_paths['germline'])
    assert not vdj.data.germline_alignment_d_mask.empty


def test_manual_threshold_and_define_clones(create_testfolder):
    f = create_testfolder / "test.tsv"
    out = pd.read_csv(f, sep='\t')
    vdj = ddl.Dandelion(out)
    vdj.threshold = 0.1
    ddl.tl.define_clones(vdj)
    assert not vdj.data.clone_id.empty
    ddl.tl.define_clones(vdj, key_added='changeo_clone')
    assert not vdj.data.changeo_clone.empty
