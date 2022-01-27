import attr
import typing as ty
from pydra.engine.specs import ShellSpec, File


@attr.s(auto_attribs=True, kw_only=True)
class MRTrix3BaseSpec(ShellSpec):
    """mrtrix3 command standard input specs
    - includes: nthreads, grad_file, grad_fsl, force, quiet
    """

    # number of threads
    nthreads: ty.Optional[int] = attr.ib(
        default=None,
        metadata={
            "help_string": "number of CPU threads to use for multi-threading",
            "argstr": "-nthreads",
        },
    )

    # gradient files in mrtrix3 format
    grad_file: File = attr.ib(
        metadata={
            "help_string": "MRTrix3 format gradient file",
            "argstr": "-grad",
            "xor": "grad_fsl",
        }
    )

    # gradient files in FSL format
    grad_fsl: ty.List[File] = attr.ib(
        metadata={
            "help_string": "FSL format gradient files [bvecs, bvals]",
            "argstr": "-fslgrad",
            "xor": "grad_file",
        }
    )

    # force outputs
    force: ty.Optional[bool] = attr.ib(
        metadata={
            "help_string": "force & replace output if one already exists",
            "argstr": "-force",
        }
    )

    # progress & information messages
    quiet: ty.Optional[bool] = attr.ib(
        metadata={
            "help_string": "Whether to display progress and information messages",
            "argstr": "-quiet",
        }
    )
