import c4d
import os
import re
from ciopath.gpath_list import PathList
from ciopath.gpath import Path


def rpd():
    """Get the render path data object, required for token replacement."""
    document = c4d.documents.GetActiveDocument()
    render_data = document.GetActiveRenderData()
    return {
        "_doc": document,
        "_rData": render_data,
        "_rBc": render_data.GetData(),
        "_take": document.GetTakeData().GetCurrentTake(),
    }


def get_common_render_output_destination():
    """
    Use common path of the outputs for destination directory.
    """

    out_paths = get_active_output_paths()

    if not out_paths:
        c4d.WriteConsole("No render output paths. Can't determine a common destination folder.\n")
        return ""

    out_dirs = [os.path.dirname(p.fslash()) for p in out_paths]

    try:
        common_path = PathList(*out_dirs).common_path()
    except BaseException:
        c4d.WriteConsole(
            "An error occurred while trying to determine a common destination folder.\n"
        )
        return ""

    return truncate_path_to_unresolved_token(common_path.fslash())


def get_active_output_paths():
    """Get image paths as absolute gpath.Path objects."""
    document = c4d.documents.GetActiveDocument()
    doc_path = document.GetDocumentPath()

    result = get_image_paths()
    return [
        Path(os.path.join(doc_path, pth)) if Path(pth).relative else Path(pth) for pth in result
    ]


def truncate_path_to_unresolved_token(in_path):
    """
    Make sure the path contains no unresolved tokens (dollar signs).

    If it does, truncate the path up to the component containing the dollar sign.

    Args:
        in_path (str): The path to examine.

    Returns:
        [str]: Possibly truncated path
    """

    result = in_path
    while True:
        if not "$" in result:
            return result
        result = os.path.dirname(result)


def get_image_paths():
    """A list containing paths of active output images."""

    document = c4d.documents.GetActiveDocument()
    render_data = document.GetActiveRenderData()

    return list(
        filter(
            None,
            [
                get_image_path(render_data, c4d.RDATA_PATH),
                get_image_path(render_data, c4d.RDATA_MULTIPASS_FILENAME),
            ],
        )
    )


def set_image_path(render_data, path_key, value):
    render_data[path_key] = value


def get_image_path(render_data, path_key):
    """Return the output image path as string if it is active.

    path_key determines whether we are dealing at single image field or multipass image.

    We convert any C4D tokens that are in context.
    """
    save_enabled = render_data[c4d.RDATA_GLOBALSAVE]
    if not save_enabled:
        return

    if path_key == c4d.RDATA_MULTIPASS_FILENAME:
        do_image_save = render_data[c4d.RDATA_MULTIPASS_SAVEIMAGE]
    else:
        do_image_save = render_data[c4d.RDATA_SAVEIMAGE]

    if not do_image_save:
        return

    try:
        image_path = c4d.modules.tokensystem.FilenameConvertTokens(render_data[path_key], rpd())
    except SystemError:
        return

    return image_path
