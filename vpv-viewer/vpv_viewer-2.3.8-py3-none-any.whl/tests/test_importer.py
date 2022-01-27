from vpv.ui.controllers import importer
from pathlib import Path
import pytest

def test_folder_filter():
    #path: str, folder_include_pattern: str
    assert importer.folder_filter('/mnt/bit_nfs/neil/mutants/output/jag2/20150409_JAG2_E14.5_13.3f_HOM_XX_REC_scaled_4.6823_pixel_14.0001/output/registrations/deformable_192_to_10/20150409_JAG2_E14.5_13.3f_HOM_XX_REC_scaled_4.6823_pixel_14.0001/20150409_JAG2_E14.5_13.3f_HOM_XX_REC_scaled_4.6823_pixel_14.0001.nrrd')