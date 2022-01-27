import attr
import typing as ty
from pydra import ShellCommandTask
from pydra.engine.specs import (
    Path, File, SpecInfo, ShellOutSpec)
from .base import MRTrix3BaseSpec


MRConvertInputSpec = SpecInfo(
    name="MRConvertInputs",
    fields=[
        (
            "in_file",
            attr.ib(
                type=Path,
                metadata={
                    "argstr": "{in_file}",
                    "position": 1,
                    "help_string": "input image",
                    "mandatory": True,
                },
            ),
        ),
        (
            "out_file",
            attr.ib(
                type=str,
                metadata={
                    "argstr": "{out_file}",
                    "position": -1,
                    "help_string": "output image",
                },
            ),
        ),
        (
            "coord",
            attr.ib(
                type=ty.List[float],
                metadata={
                    "argstr": "-coord",
                    "help_string": "extract data at the specific coordinatest",
                },
            ),
        ),
        (
            "vox",
            attr.ib(
                type=ty.List[float],
                metadata={
                    "argstr": "-vox",
                    "help_string": "change the voxel dimensions",
                },
            ),
        ),
        (
            "axes",
            attr.ib(
                type=ty.List[int],
                metadata={
                    "argstr": "-axes",
                    "help_string": "specify the axes that will be used",
                },
            ),
        ),
        (
            "scaling",
            attr.ib(
                type=ty.List[float],
                metadata={
                    "argstr": "-scaling",
                    "help_string": "specify the data scaling parameter",
                },
            ),
        ),
        (
            "export_grad",
            attr.ib(
                type=str,
                metadata={
                    "argstr": "-export_grad_mrtrix",
                    "help_string": "export new gradient files in mrtrix3 format",
                },
            ),
        ),
        (
            "export_json",
            attr.ib(
                type=str,
                metadata={
                    "argstr": "-json_export",
                    "help_string": "export image headet to JSON file",
                },
            ),
        ),
    ],
    bases=(MRTrix3BaseSpec,),
)

MRConvertOutputSpec = SpecInfo(
    name="MRConvertOutputs",
    fields=[
        (
            "out_file",
            attr.ib(
                type=File,
                metadata={
                    "help_string": "output image",
                    "output_file_template": "dwi.mif",
                },
            ),
        ),
        (
            "out_bfile",
            attr.ib(
                type=File,
                metadata={
                    "help_string": "output .b gradient file in mrtrix3 format",
                    "output_file_template": "dwi.b",
                },
            ),
        ),
        (
            "out_json",
            attr.ib(
                type=File,
                metadata={
                    "help_string": "output JSON file of image header",
                    "output_file_template": "dwi.json",
                },
            ),
        ),
    ],
    bases=(ShellOutSpec,),
)


class MRConvert(ShellCommandTask):
    """
    Example
    ------
    >>> task = MRConvert()
    >>> task.inputs.in_file = "test_dwi.nii.gz"
    >>> task.inputs.grad_fsl = ["test.bvec", "test.bval"]
    >>> task.inputs.export_grad = "test.b"
    >>> task.inputs.out_file = "test.mif"
    >>> task.cmdline
    'mrconvert test_dwi.nii.gz -fslgrad test.bvec test.bval -export_grad_mrtrix test.b test.mif'
    """

    input_spec = MRConvertInputSpec
    output_spec = MRConvertOutputSpec
    executable = "mrconvert"
