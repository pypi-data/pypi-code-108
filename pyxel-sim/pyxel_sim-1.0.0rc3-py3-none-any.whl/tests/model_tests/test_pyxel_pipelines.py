"""Functional tests for the Pyxel pipelines."""
#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

# import os
# import shutil
# import pytest
# import numpy as np
# from astropy.io import fits
# from pyxel.run import run


# @pytest.mark.parametrize('yaml, expected_image, seed, outfile',
#                          [
#                              ('tests/data/photon_transfer_function.yaml', 'tests/data/uniform_1000.fits', 1111,
#                               'run_01/image_01.fits'),
#                              ('tests/data/pipeline_01.yaml', 'tests/data/expected_pipeline_01.fits', 1111,
#                               'run_02/image_01.fits'),
#                              ('tests/data/pipeline_02.yaml', 'tests/data/expected_pipeline_01.fits', 1111,
#                               'run_03/image_01.fits'),
#                          ])
# def test_pyxel_pipeline(yaml, expected_image, seed, outfile):
#     """Test """
#     outdir = 'tests/data'
#     if os.path.exists(outdir+'/'+outfile[:6]):
#         shutil.rmtree(outdir+'/'+outfile[:6])      # TODO: THIS DOES NOT WORK FOR 2ND TIME!!!!
#
#     run(input_filename=yaml, output_directory=outdir, random_seed=seed)
#     image = fits.getdata(outdir+'/'+outfile)
#     expected_image = fits.getdata(expected_image)
#     np.testing.assert_array_equal(image, expected_image)
