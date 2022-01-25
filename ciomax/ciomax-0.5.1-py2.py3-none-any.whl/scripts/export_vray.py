
"""
Presubmission script to export vrscene files.

To write your own presubmission script, use this as a jumping off point and
consult the Conductor Max reference documentation.
https://docs.conductortech.com/reference/max/#pre-submission-script
"""
 
import os
 
from ciopath.gpath_list import PathList
from ciopath.gpath import Path
from pymxs import runtime as rt
 
from contextlib import contextmanager


@contextmanager
def maintain_save_state():
    required = rt.getSaveRequired()
    yield
    rt.setSaveRequired(required)


@contextmanager
def preserve_state():
    """
    Remember and reset all the properties we change.
    """
    rend_time_type = rt.rendTimeType
    rend_pickup_frames = rt.rendPickupFrames
    rend_nth_frame = rt.rendNThFrame
    try:
        yield
    finally:
        rt.rendTimeType = rend_time_type
        rt.rendPickupFrames = rend_pickup_frames
        rt.rendNThFrame = rend_nth_frame


def main(dialog, *args):
    """
    Export assets needed for a vray render.

    Return an object containing the list of generated assets.
    """
    prefix = os.path.splitext(args[0])[0]

    vray_scene = export_vrscene(dialog, prefix)

    remap_file = write_remap_file(prefix, vray_scene)

    return amendments(dialog, *args)

def amendments(dialog, *args):
    """
    Return payload amendments only.

    Payload amendments consist of a vrscene filenames, and a remap filename.
    """
    prefix = os.path.splitext(args[0])[0]

    remap_filename  = "{}.xml".format(prefix)
    vray_scene = "{}.vrscene".format(prefix)

    return  {
        "upload_paths": [remap_filename, vray_scene]
    }
 

def export_vrscene(dialog, vrscene_prefix):

    render_scope = dialog.render_scope
    valid_renderers = ["VrayGPURenderScope", "VraySWRenderScope"]

    if not render_scope.__class__.__name__ in valid_renderers:
        raise TypeError(
            "If you want to export Vray files, please set the current renderer to one of: {}".format(valid_renderers))

    main_sequence = dialog.main_tab.section("FramesSection").main_sequence

    camera_name = dialog.main_tab.section(
        "GeneralSection").camera_component.combobox.currentText()
    print("Set the current view to look through camera: {}", format(
        camera_name))

    rt.viewport.setCamera(rt.getNodeByName(camera_name))

    print("Ensure directory is available for vrscene_file")
    _ensure_directory_for(vrscene_prefix)

    print("Closing render setup window if open...")
    if rt.renderSceneDialog.isOpen():
        rt.renderSceneDialog.close()

    with preserve_state():
        print("Setting render time type to use a specified sequence...")
        rt.rendTimeType = 4

        print("Setting the frame range...")
        rt.rendPickupFrames = "{}-{}".format(main_sequence.start,
                                             main_sequence.end)

        print("Setting the by frame to 1...")
        rt.rendNThFrame = 1

        print("Exporting vrscene files")
        error = 0
        with maintain_save_state():
            error = rt.vrayExportRTScene(
                vrscene_prefix,
                startFrame=main_sequence.start,
                endFrame=main_sequence.end)

        vray_scene = "{}.vrscene".format(vrscene_prefix)
        if os.path.exists(vray_scene):
            if error:
                print("Scene was exported, but there were errors during export. Check %temp%/vraylog.txt")
            else:
                print("Scene was exported successfully")
        else:
            raise ValueError(
                "Vray scene export failed. Check %temp%/vraylog.txt")

        # return list of extra dependencies
        print("Completed vrscene export..")

    return vray_scene


def write_remap_file(prefix, vray_scene):
    """
    Write a xml file that tells Vray to strip drive letters.

    The file is referenced in the task command. 
    """
 
    num_assets = rt.AssetManager.getNumAssets()
    assets = [rt.AssetManager.getAssetByIndex(i).getFileName() for i in range(1,num_assets+1)]
    assets += [vray_scene]
    pathlist = PathList(*assets)

    prefix_set = set()

    for p in pathlist:
        prefix_set.add(Path(p.all_components[:2]).fslash())

    remap_filename = "{}.xml".format(prefix)

    lines = []
    lines.append("<RemapPaths>\n")
    for p in prefix_set:
        pth = Path(p)
        lines.append("\t<RemapItem>\n")
        lines.append("\t\t<From>{}</From>\n".format(pth.fslash()))
        lines.append(
            "\t\t<To>{}</To>\n".format(pth.fslash(with_drive=False)))
        lines.append("\t</RemapItem>\n")
    lines.append("</RemapPaths>\n")
    with open(remap_filename, "w") as fn:
        fn.writelines(lines)

    print("Wrote Vray remapPathFile file to", remap_filename)

    return remap_filename


def _ensure_directory_for(path):
    """Ensure that the parent directory of `path` exists"""
    dirname = os.path.dirname(path)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
