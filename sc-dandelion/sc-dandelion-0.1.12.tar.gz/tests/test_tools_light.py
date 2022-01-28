#!/usr/bin/env python
import pandas as pd
import dandelion as ddl

from fixtures import (airr_reannotated, dummy_adata, create_testfolder)


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
    ddl.tl.find_clones(vdj, full_pairing_label=True)
    assert not vdj.data.clone_id.empty
    assert not vdj.metadata.clone_id.empty
    assert len(set(x for x in vdj.metadata['clone_id'] if pd.notnull(x))) == 4
    vdj.write_h5(f)
