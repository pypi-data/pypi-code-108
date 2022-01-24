# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""Miscellaneous utilities."""


def check_deps(workflow):
    """Make sure dependencies are present in this system."""
    from nipype.utils.filemanip import which
    return sorted(
        (node.interface.__class__.__name__, node.interface._cmd)
        for node in workflow._get_all_nodes()
        if (hasattr(node.interface, '_cmd')
            and which(node.interface._cmd.split()[0]) is None))


def fips_enabled():
    """
    Check if FIPS is enabled on the system.

    For more information, see:
    https://github.com/nipreps/fmriprep/issues/2480#issuecomment-891199276
    """
    from pathlib import Path
    fips = Path("/proc/sys/crypto/fips_enabled")
    return fips.exists() and fips.read_text()[0] != "0"
