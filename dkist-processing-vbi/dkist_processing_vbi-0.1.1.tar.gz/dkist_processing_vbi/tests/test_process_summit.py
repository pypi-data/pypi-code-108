from itertools import chain

import numpy as np
import pytest
from astropy.io import fits
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.constants import BudName

from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.tasks.process_summit_processed import GenerateL1SummitData
from dkist_processing_vbi.tests.conftest import ensure_all_inputs_used
from dkist_processing_vbi.tests.conftest import FakeGQLClient
from dkist_processing_vbi.tests.conftest import generate_214_l0_fits_frame
from dkist_processing_vbi.tests.conftest import Vbi122DarkFrames
from dkist_processing_vbi.tests.conftest import Vbi122SummitObserveFrames

RNG = np.random.default_rng()


@pytest.fixture(scope="function")
def process_summit_processed(tmp_path, recipe_run_id):
    with GenerateL1SummitData(
        recipe_run_id=recipe_run_id,
        workflow_name="vbi_process_summit_processed",
        workflow_version="VX.Y",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        task.num_steps = 4
        task.num_exp_per_step = 1
        task.constants[BudName.spectral_line.value] = "VBI TEST LINE"
        ds = Vbi122SummitObserveFrames(
            array_shape=(1, 10, 10),
            num_steps=task.num_steps,
            num_exp_per_step=task.num_exp_per_step,
            num_dsps_repeats=1,
        )
        dsd = Vbi122DarkFrames(
            array_shape=(1, 10, 10),
            num_steps=task.num_steps,
            num_exp_per_step=task.num_exp_per_step,
        )
        header_generator = (d.header() for d in ds)
        dark_header_generator = (d.header() for d in dsd)
        for p in range(1, task.num_steps + 1):
            for e in range(task.num_exp_per_step):
                header = next(header_generator)
                data = np.ones((10, 10)) * p
                hdul = generate_214_l0_fits_frame(s122_header=header, data=data)
                task.fits_data_write(
                    hdu_list=hdul,
                    tags=[
                        VbiTag.input(),
                        VbiTag.task("Observe"),
                        VbiTag.spatial_step(p),
                        VbiTag.frame(),
                    ],
                )
                dark_header = next(dark_header_generator)
                hdul = generate_214_l0_fits_frame(s122_header=dark_header, data=np.ones((10, 10)))
                task.fits_data_write(
                    hdu_list=hdul,
                    tags=[
                        VbiTag.input(),
                        VbiTag.task("Dark"),
                        VbiTag.frame(),
                    ],
                )
        ensure_all_inputs_used(header_generator)
        yield task
        task.scratch.purge()
        task.constants.purge()


def test_process_summit_data(process_summit_processed, mocker):
    """
    Given: a set of parsed input frames of summit-processed data and a GenerateL1SummitData task
    When: the task is run
    Then: the correct data-dependent L1 headers are added, an output tag is applied to each frame, and the input tag is removed
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    process_summit_processed()

    # Make sure the input tag was removed
    assert len(list(process_summit_processed.read(tags=[VbiTag.input(), VbiTag.output()]))) == 0

    for step in range(1, process_summit_processed.num_steps + 1):
        files = list(
            process_summit_processed.read(
                tags=[
                    VbiTag.calibrated(),
                    VbiTag.frame(),
                    VbiTag.spatial_step(step),
                    VbiTag.stokes("I"),
                ]
            )
        )
        assert len(files) == process_summit_processed.num_exp_per_step
        hdu = fits.open(files[0])[0]
        assert np.mean(hdu.data) == step
        for filepath in files:
            assert filepath.exists()
