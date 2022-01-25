"""
Presubmission script to export ass files.

To write your own presubmission script, use this as a jumping off point and
consult the Conductor Max reference documentation.
https://docs.conductortech.com/reference/max/#pre-submission-script
"""

from contextlib import contextmanager
from pymxs import runtime as rt
import os
from ciopath.gpath import Path
 

@contextmanager
def preserve_state():
    """
    Remember, and then reset all the properties we change.
    """
    rend_time_type = rt.rendTimeType
    rend_pickup_frames = rt.rendPickupFrames
    rend_nth_frame = rt.rendNThFrame
    rend_export_to_ass = rt.renderers.current.export_to_ass
    rend_ass_file_path = rt.renderers.current.ass_file_path
    try:
        yield
    finally:
        rt.rendTimeType = rend_time_type
        rt.rendPickupFrames = rend_pickup_frames
        rt.rendNThFrame = rend_nth_frame
        rt.renderers.current.export_to_ass = rend_export_to_ass
        rt.renderers.current.ass_file_path = rend_ass_file_path


def main(dialog, *args):
    """
    Export assets needed for a ass render.

    We need the ass files, and we need file that defines mappings between the
    Windows paths and linux paths on the render nodes. This mapping is always
    simply removing a drive letter.
    """
    prefix = args[0]
    export_ass_files(dialog, prefix)
    write_remap_file(dialog, prefix)

    return amendments(dialog, *args)

def amendments(dialog, *args):
    """
    Return payload amendments only.

    Payload amendments consist of ass filenames, a remap file, and an environment variable that
    points to the remap file.
    """
    prefix = args[0]
    remap_filename ="{}.json".format(prefix.strip("."))

    main_sequence = dialog.main_tab.section("FramesSection").main_sequence
    ass_filenames = main_sequence.expand(
            "{}####.ass".format(prefix))

    upload_paths = ass_filenames + [remap_filename]

    # NOTE environment must be the following object list, not: bash, i.e. NAME=value1:value2
    # merge_policy can be exclusive|append
    environment = [{
        "name": "ARNOLD_PATHMAP",
        "value": Path(remap_filename).fslash(with_drive=False),
        "merge_policy": "exclusive",
    }]

    return  {
        "upload_paths": upload_paths,
        "environment": environment
    }
 

def export_ass_files(dialog, ass_file_prefix):
    """
    Write ass files with the given porefix.

    NOTE The prefix should probably include a trailing dot since kick doesn't
    add one before the frame numbers.
    """
    render_scope = dialog.render_scope
    if not render_scope.__class__.__name__ == "ArnoldRenderScope":
        raise TypeError(
            "If you want to export ass files, please set the current renderer to Arnold.")

    main_sequence = dialog.main_tab.section("FramesSection").main_sequence

    camera_name = dialog.main_tab.section(
        "GeneralSection").camera_component.combobox.currentText()
    print("Set the current view to look through camera: {}", format(
        camera_name))
    rt.viewport.setCamera(rt.getNodeByName(camera_name))
 

    print("Ensure directory is available for ass files")
    _ensure_directory_for(ass_file_prefix)

    print("Closing render setup window if open...")
    if rt.renderSceneDialog.isOpen():
        rt.renderSceneDialog.close()

    with preserve_state():
        print("Setting render time type to use a specified sequence...")
        rt.rendTimeType = 4

        print("Setting the frame range...")
        rt.rendPickupFrames = "{}-{}".format(
            main_sequence.start, main_sequence.end)

        print("Setting the by frame to 1...")
        rt.rendNThFrame = 1

        print("Setting ass export to on...")
        rt.renderers.current.export_to_ass = True

        print("Setting the ass filepath to", "{}.ass".format(ass_file_prefix))
        rt.renderers.current.ass_file_path = "{}.ass".format(ass_file_prefix)

        print("Exporting ass files...")
        rt.render(fromFrame=main_sequence.start,
                  toFrame=main_sequence.end, vfb=False)

        # return list of ass files
        print("Done writing ass files")
        ass_filenames = main_sequence.expand(
            "{}####.ass".format(ass_file_prefix))

    return ass_filenames


def write_remap_file(_, prefix):
    """
    Write a json file that tells Arnold to strip drive letters.

    This was introduced in Arnold 6.0.4.0 (mtoa 4.0.4). The file is pointed to
    by the ARNOLD_PATHMAP environment variable.
    """

    remap_filename = "{}.json".format(prefix.strip("."))

    lines = []
    lines.append("{\n")
    lines.append('\t"linux": {\n')
    lines.append('\t\t"^[A-Za-z]:": "",\n')
    lines.append('\t\t"^//":"/"\n')
    lines.append('\t}\n')
    lines.append('}\n')

    with open(remap_filename, "w") as fn:
        fn.writelines(lines)

    print("Wrote Arnold remapPathFile file to", remap_filename)

    return remap_filename


def _ensure_directory_for(path):
    """
    Ensure that the parent directory of `path` exists
    """
    dirname = os.path.dirname(path)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
