import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Callable
from typing import Optional

import numpy as np
from astropy.io import fits
from dkist_header_validator import spec122_validator
from dkist_header_validator import spec214_validator
from dkist_processing_common.manual import ManualProcessing
from dkist_processing_common.tasks import ParsedL0InputTaskBase
from dkist_processing_common.tasks import QualityL0Metrics
from dkist_processing_common.tasks import QualityL1Metrics
from dkist_processing_common.tasks import WorkflowDataTaskBase
from dkist_processing_common.tasks.mixin.metadata_store import MetadataStoreMixin
from dkist_processing_common.tasks.mixin.quality import QualityMixin

from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.parsers.vbi_l0_fits_access import VbiL0FitsAccess
from dkist_processing_vbi.tasks.assemble_movie import AssembleVbiMovie
from dkist_processing_vbi.tasks.dark import DarkCalibration
from dkist_processing_vbi.tasks.gain import GainCalibration
from dkist_processing_vbi.tasks.make_movie_frames import MakeVbiMovieFrames
from dkist_processing_vbi.tasks.parse import ParseL0VbiInputData
from dkist_processing_vbi.tasks.process_summit_processed import GenerateL1SummitData
from dkist_processing_vbi.tasks.science import ScienceCalibration
from dkist_processing_vbi.tasks.write_l1 import VbiWriteL1Frame
from dkist_processing_vbi.vbi_base import VbiScienceTask

INV = False
try:
    from dkist_inventory.asdf_generator import dataset_from_fits

    INV = True
except ModuleNotFoundError:
    # Bitbucket pipelines won't have dkist-inventory installed
    logging.warning("Could not load dkist-inventory. This is OK on Bitbucket.")
    pass

QRM = False
try:
    from quality_report_maker.libraries import report
    from quality_report_maker.libraries.json_encoder import datetime_json_object_hook
    from quality_report_maker.libraries.json_encoder import DatetimeEncoder

    QRM = True
except ModuleNotFoundError:
    logging.warning("Could not find quality_report_maker (must be installed manually)")
if QRM:
    import matplotlib.pyplot as plt

    plt.ioff()


class TagInputs(WorkflowDataTaskBase):
    def run(self) -> None:
        logging.info(f"Looking in {os.path.abspath(self.scratch.workflow_base_path)}")
        for file in self.scratch.workflow_base_path.glob("*.FITS"):
            logging.info(f"Found {file}")
            self.tag(path=file, tags=[VbiTag.input(), VbiTag.frame()])


class Translate122To214L0(WorkflowDataTaskBase):
    def run(self) -> None:
        raw_dir = Path(self.scratch.scratch_base_path) / f"VBI{self.recipe_run_id:03n}"
        if not os.path.exists(self.scratch.workflow_base_path):
            os.makedirs(self.scratch.workflow_base_path)
        for file in raw_dir.glob("*.FITS"):
            translated_file_name = Path(self.scratch.workflow_base_path) / os.path.basename(file)
            logging.info(f"Translating {file} -> {translated_file_name}")
            hdl = fits.open(file)

            header = spec122_validator.validate_and_translate_to_214_l0(
                hdl[0].header, return_type=fits.HDUList
            )[0].header
            hdl[0].header = header

            hdl.writeto(translated_file_name, overwrite=True)
            hdl.close()
            del hdl


class ShowExposureTimes(VbiScienceTask):
    def run(self) -> None:
        logging.info(f"{self.dark_exposure_times = }")
        logging.info(f"{self.gain_exposure_times = }")
        logging.info(f"{self.observe_exposure_times = }")


class FloatifyInputData(VbiScienceTask):
    # Needed because VbiWriteL1Frame will bork with integer data
    def run(self) -> None:
        for f in self.read(tags=[VbiTag.input(), VbiTag.frame()]):
            hdl = fits.open(f, mode="update")
            old_type = hdl[0].data.dtype
            hdl[0].data = hdl[0].data * 1.0
            new_type = hdl[0].data.dtype
            logging.info(f"{f}: {old_type} -> {new_type}")
            hdl.flush()
            hdl.close()


class ExposeOutputData(VbiScienceTask):
    def run(self) -> None:
        for step in range(self.num_spatial_steps):
            output_access_list = list(
                self.fits_data_read_fits_access(
                    tags=[VbiTag.output(), VbiTag.frame(), VbiTag.spatial_step(step)],
                    cls=VbiL0FitsAccess,
                )
            )
            logging.info(f"found {len(output_access_list)} outputs for step {step}")
            fits.PrimaryHDU(output_access_list[0].data).writeto(f"comp_{step}.FITS", overwrite=True)


class SubmitAndExposeQuality(ParsedL0InputTaskBase, QualityMixin, MetadataStoreMixin):
    """ A direct copy paste of SumbitQuality with an additional step of writing the report to disk"""

    def run(self):
        logging.info("Building quality report")
        report_str = self.quality_build_report()
        logging.info("Submitting quality report")
        self.metadata_store_add_quality_report(
            dataset_id=self.dataset_id, quality_report=report_str
        )

        if QRM:
            doc_path = self.scratch.workflow_base_path / "quality_report.json"
            report_container = {
                "datasetId": self.dataset_id,
                "qualityReport": json.dumps(report_str, cls=DatetimeEncoder),
            }
            json_str = json.dumps(report_container)
            with open(doc_path, "w") as f:
                f.write(json_str)
            logging.info(f"Wrote report to {doc_path}")


class ValidateL1Output(VbiScienceTask):
    def run(self) -> None:
        files = self.read(tags=[VbiTag.output(), VbiTag.frame()])
        for f in files:
            logging.info(f"Validating {f}")
            spec214_validator.validate(f, extra=False)


def compare_to_sv_data(sv_file_name: str) -> bool:

    sv_hdl = fits.open(sv_file_name)
    for i, sv_h in enumerate(sv_hdl[1:]):
        dc_data = fits.open(f"comp_{i}.FITS")[0].data
        if not np.allclose(sv_h.data[0], dc_data, atol=1e-5, rtol=1e-5):
            return False

    return True


def l0_processing_workflow(manual_processing_run: ManualProcessing) -> None:
    manual_processing_run.run_task(task=DarkCalibration)
    manual_processing_run.run_task(task=GainCalibration)
    manual_processing_run.run_task(task=ScienceCalibration)


def summit_data_processing_workflow(manual_processing_run: ManualProcessing) -> None:
    manual_processing_run.run_task(task=FloatifyInputData)
    manual_processing_run.run_task(task=GenerateL1SummitData)


def make_pdf_report(scratch_path: str, recipe_run_id: int) -> None:
    if not QRM:
        logging.info(
            "Did NOT make quality report pdf because quality_report_maker is not installed"
        )
        return

    json_file = os.path.join(scratch_path, str(recipe_run_id), "quality_report.json")
    pdf_file = os.path.join(scratch_path, str(recipe_run_id), "quality_report.pdf")
    with open(json_file, "r") as f:
        report_container = json.load(f)
        dataset_id = report_container["datasetId"]
        report_str = json.loads(
            report_container["qualityReport"], object_hook=datetime_json_object_hook
        )

    pdf_bytes = report.format_report(report_str, f"GROGU_TEST_{dataset_id}")
    with open(pdf_file, "wb") as f:
        f.write(pdf_bytes)

    logging.info(f"Wrote quality report PDF to {pdf_file}")


def make_dataset_asdf(scratch_path, recipe_run_id):
    if not INV:
        logging.warning("Did NOT make dataset asdf file because dkist_inventory is not installed")
        return

    output_dir = os.path.join(scratch_path, str(recipe_run_id))
    asdf_name = f"dataset_{recipe_run_id:03n}.asdf"
    logging.info(f"Creating ASDF file from {output_dir} and saving to {asdf_name}")
    dataset_from_fits(output_dir, asdf_name, hdu=1)


def main(
    scratch_path="/media/FastPipelin/vbi/scratch",
    recipe_run_id=4,
    sv_file_to_test: Optional[str] = None,
    skip_translation: bool = False,
    only_translate: bool = False,
    science_workflow: Callable = l0_processing_workflow,
):
    with ManualProcessing(
        workflow_path=scratch_path, recipe_run_id=recipe_run_id, testing=True
    ) as manual_processing_run:
        if not skip_translation:
            manual_processing_run.run_task(task=Translate122To214L0)
        if only_translate:
            return
        manual_processing_run.run_task(task=TagInputs)
        manual_processing_run.run_task(task=ParseL0VbiInputData)
        manual_processing_run.run_task(task=QualityL0Metrics)
        manual_processing_run.run_task(task=ShowExposureTimes)
        manual_processing_run.run_task(task=QualityL0Metrics)
        science_workflow(manual_processing_run)
        manual_processing_run.run_task(task=VbiWriteL1Frame)
        manual_processing_run.run_task(task=QualityL1Metrics)
        manual_processing_run.run_task(task=SubmitAndExposeQuality)
        manual_processing_run.run_task(task=ValidateL1Output)

        # Put this here because the movie stuff takes a long time
        make_dataset_asdf(scratch_path, recipe_run_id)
        make_pdf_report(scratch_path, recipe_run_id)

        manual_processing_run.run_task(task=MakeVbiMovieFrames)
        manual_processing_run.run_task(task=AssembleVbiMovie)

        if sv_file_to_test:
            manual_processing_run.run_task(task=ExposeOutputData)
            assert compare_to_sv_data(sv_file_to_test)
            logging.info("DC output matches SV output!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run an end-to-end test of the VBI DC Science pipeline"
    )
    parser.add_argument("scratch_path", help="Location to use as the DC 'scratch' disk")
    parser.add_argument(
        "-W",
        "--workflow_name",
        help="Name of VBI workflow to test",
        choices=["l0_processing", "summit_data_processed"],
        default="l0_processing",
    )
    parser.add_argument(
        "-i",
        "--run-id",
        help="Which subdir to use. This will become the recipe run id",
        type=int,
        default=4,
    )
    parser.add_argument(
        "-S",
        "--sv-file-to-test",
        help="If given, the result of the DC pipeline will be checked against this file on a pixel-by-pixel basis",
        type=str,
    )
    parser.add_argument(
        "-T",
        "--skip-translation",
        help="Skip the translation of raw 122 l0 frames to 214 l0",
        action="store_true",
    )
    parser.add_argument(
        "-t", "--only-translate", help="Do ONLY the translation step", action="store_true"
    )
    args = parser.parse_args()

    science_func_dict = {
        "l0_processing": l0_processing_workflow,
        "summit_data_processed": summit_data_processing_workflow,
    }
    science_func = science_func_dict[args.workflow_name]
    sys.exit(
        main(
            scratch_path=args.scratch_path,
            recipe_run_id=args.run_id,
            sv_file_to_test=args.sv_file_to_test,
            skip_translation=args.skip_translation,
            only_translate=args.only_translate,
            science_workflow=science_func,
        )
    )
