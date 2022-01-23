import os
import c4d
import sys
from ciopath.gpath import Path
from ciopath.gpath_list import GLOBBABLE_REGEX, PathList
from ciocore.validator import ValidationError, Validator
from cioc4d import const as k
from ciocore import data as coredata
from cioc4d import utils

DASHES = "-" * 30


class ValidateUploadDaemon(Validator):
    def run(self, _):
        dialog = self._submitter
        use_daemon = dialog.section("UploadOptionsSection").use_daemon_widget.get_value()
        if not use_daemon:
            return

        msg = "This submission expects an uploader daemon to be running.\n"
        msg += 'After you press submit you can open a shell and type:\n"{}" uploader'.format(
            k.CONDUCTOR_COMMAND_PATH
        )

        location = (dialog.section("LocationSection").widget.get_value() or "").strip()
        if location:
            msg = "This submission expects an uploader daemon to be running and set to a specific location tag."
            msg += 'After you press OK you can open a shell and type:\n"{}" uploader --location "{}"\n'.format(
                k.CONDUCTOR_COMMAND_PATH, location
            )
        # By also writing the message to the console, the user can copy paste
        # `conductor uploader --location blah`.
        c4d.WriteConsole(msg)
        c4d.WriteConsole("\n")

        msg += " \nYou'll also find this information in the console.\n"

        self.add_notice(msg)


class ValidateTaskCount(Validator):
    def run(self, _):
        dialog = self._submitter
        count = dialog.section("InfoSection").frame_count
        if count > 1000:
            self.add_notice(
                "This submission contains over 1000 tasks ({}). Are you sure this is correct?".format(
                    count
                )
            )


class ValidateGPU(Validator):
    """
    Validate the suitability of the chosen instance type.

    If the renderer configuration requires a GPU but no GPU-enabled instance type is selected, add a validation error.
    If a GPU instance type is selected, but the renderer doesn't require it, add a validation warning.
    """

    def run(self, _):
        dialog = self._submitter

        document = c4d.documents.GetActiveDocument()
        render_data = document.GetActiveRenderData()
        renderer = render_data[c4d.RDATA_RENDERENGINE]

        description = dialog.section("GeneralSection").instance_types_widget.get_selected_value()

        instance_type = next(
            (it for it in coredata.data()["instance_types"] if it["description"] == description),
            None,
        )

        if renderer == k.RENDERERS["redshift"]:

            if not (instance_type and instance_type["gpu"]):
                msg = "The Redshift renderer is not compatible with the instance type: '{}' as it has no graphics card.\n".format(
                    description
                )
                msg += "Please select a machine with a graphics card in the General section of the submitter. The submission is blocked as it would incur unexpected costs."
                self.add_error(msg)
            return

        # Not Redshift
        if instance_type and instance_type["gpu"]:

            msg = "You have selected an instance type with a graphics card: '{}', yet the chosen renderer in RenderSettings does not benefit from a GPU.".format(
                description
            )
            msg += " This could incur extra costs. Do not continue unless you are absolutely sure."
            self.add_warning(msg)


class ValidateDestinationDirectoryClash(Validator):
    def run(self, _):
        dialog = self._submitter
        bad_dest_msg = "There was an error while trying to resolve the destination directory."

        tasks_section = dialog.section("TaskSection")
        is_override = tasks_section.override_widget.get_value()

        if is_override:
            try:
                bad_dest_msg += (
                    "Please check the value for the destination folder in the submitter."
                )
                dest = tasks_section.get_custom_destination()
                dest_path = Path(dest).fslash(with_drive=False)
            except BaseException:
                self.add_error(bad_dest_msg)
                return
        else:
            try:
                bad_dest_msg += (
                    "Please check that your image paths all save to the same filesystem."
                )
                dest = utils.get_common_render_output_destination()
                dest_path = Path(dest).fslash(with_drive=False)
            except BaseException:
                self.add_error(bad_dest_msg)
                return

        path_list = dialog.section("AssetsSection").get_assets_path_list()

        for gpath in path_list:
            asset_path = gpath.fslash(with_drive=False)
            # NOTE: It's a gpath, so "startswith" is synonymous with "is contained in"
            if asset_path.startswith(dest_path):
                c4d.WriteConsole(
                    "Some of your upload assets exist in the specified output destination directory\n. {} contains {}.".format(
                        dest_path, asset_path
                    )
                )
                self.add_error(
                    "The destination directory for rendered output ({}) contains assets that are in the upload list. This can cause your render to fail. See the script editor for details.".format(
                        dest_path
                    )
                )
                break
            if dest_path.startswith(asset_path):
                c4d.WriteConsole(
                    "You are trying to upload a directory that contains your destination directory.\n. {} contains {}\n".format(
                        asset_path, dest_path
                    )
                )
                self.add_error(
                    "One of your assets is a directory that contains the specified output destination directory. This will cause your render to fail. See the script editor for details.\n"
                )
                break


class ValidateCustomTaskTemplate(Validator):
    def run(self, _):
        dialog = self._submitter
        tasks_section = dialog.section("TaskSection")
        if not tasks_section.override_widget.get_value():
            return

        self.add_notice(
            """If you set any absolute paths here (e.g. -oimage or -omultipass), make sure they do not have drive letters since the tasks are be executed on Linux filesystems."""
        )
        self.add_notice(
            """Please ensure the destination folder is an ancestor of all the output images. This is important, since it defines the only writable location on the Linux filesystem."""
        )


class ValidateMissingAssets(Validator):
    def run(self, _):
        """
        Display a list of dependency assets that are not on disk.

        Don't include c4d files in the list because the doc itself may not have been saved yet.
        """
        document = c4d.documents.GetActiveDocument()
        docpath = document.GetDocumentPath()
        missing_extra_assets = []
        assets_section = self._submitter.section("AssetsSection")
        for gpath in assets_section.pathlist:
            pp = gpath.fslash()
            if not os.path.exists(pp):
                missing_extra_assets.append(pp)

        if missing_extra_assets:
            self.add_warning(
                "Some of the assets specified in the Extra Assets section do not exist on disk. See the console for details. You can continue if you don't need them."
            )

        scraped_assets = assets_section.get_all_scraped_assets()

        missing_scraped_assets = []
        for a in scraped_assets:
            if a["exists"]:
                continue
            fn = a["filename"]
            if not fn or not fn.strip():
                continue

            try:
                Path(fn)
            except ValueError:
                # Empty or invalid path, ignore
                continue
            
                # It might exist, but c4d doesn't know that due to a relative path bug
            if Path(fn).relative:
                fn = os.path.join(docpath, fn)
                if os.path.exists(fn):
                    continue

            # possible bug where c4d may not treat the c4d file as an asset
            if fn.endswith(".c4d"):
                continue
            missing_scraped_assets.append(fn)

        if missing_scraped_assets:
            self.add_warning(
                "Some of the scraped assets do not exist on disk. See the console for details. You can continue if you don't need them."
            )
        if missing_scraped_assets or missing_extra_assets:
            c4d.WriteConsole("----- Conductor Asset Validation -------\n")

            for asset in missing_scraped_assets:
                c4d.WriteConsole("Missing scraped asset: {}\n".format(asset))

            for asset in missing_extra_assets:
                c4d.WriteConsole("Missing extra asset: {}\n".format(asset))


class ValidateAbsoluteWindowsPaths(Validator):

    PRESAVE = True

    def run(self, _):
        if not sys.platform == "win32":
            return

        self.validate_asset_paths()
        self.validate_output_paths()

    def validate_asset_paths(self):

        document = c4d.documents.GetActiveDocument()
        if k.C4D_VERSION < 22:
            assets = c4d.documents.GetAllAssets(document, False, "")
        else:
            assets = []
            success = c4d.documents.GetAllAssetsNew(
                document, False, "", flags=c4d.ASSETDATA_FLAG_WITHCACHES, assetList=assets
            )

        has_abs_paths = False
        console_msg = ""
        for asset in assets:
            assetname = asset["assetname"]
            if assetname:
                if os.path.isabs(assetname):
                    has_abs_paths = True
                    ob = asset["owner"]
                    console_msg += "'{}': '{}'\n".format(ob.GetName(), assetname)

        if has_abs_paths:
            msg = "Some assets appear to have absolute paths and may need to be localized.\n"
            msg += (
                "You can use Render->Make Portable to make all asset and output paths relative.\n"
            )
            msg += "See the console for a list of paths to check. If you are sure these paths are already localized you can continue."
            self.add_warning(msg)
            c4d.WriteConsole("{}\n{}\n{}\n{}".format(DASHES, msg, console_msg, DASHES))

    def validate_output_paths(self):
        tasks_section = self._submitter.section("TaskSection")
        is_override = tasks_section.override_widget.get_value()
        if is_override:  # If user overrides the task template, assume they know what they're doing.
            return

        console_msg = ""
        has_abs_paths = False
        for out_path in utils.get_image_paths():
            if os.path.isabs(out_path):
                has_abs_paths = True
                console_msg += "'{}'\n".format(out_path)

        if has_abs_paths:
            msg = "Some output render paths are absolute and need to be localized.\n"
            msg += (
                "You can use Render->Make Portable to make all asset and output paths relative.\n"
            )
            msg += "See the console for a list of paths that need to be addressed."
            self.add_error(msg)
            c4d.WriteConsole("{}\n{}\n{}\n{}".format(DASHES, msg, console_msg, DASHES))


class ValidateDontSaveVideoPosts(Validator):

    GI_AUTOSAVE_ID = 3804
    AO_AUTOSAVE_ID = 2204
    AO_USE_CACHE_ID = 2000

    def run(self, _):
        document = c4d.documents.GetActiveDocument()
        render_data = document.GetActiveRenderData()
        vp = render_data.GetFirstVideoPost()
        while vp:
            if vp.CheckType(c4d.VPglobalillumination):
                self._validate_video_post(vp, "Global Illumination", self.GI_AUTOSAVE_ID)
            elif vp.CheckType(c4d.VPambientocclusion):
                self._validate_video_post(
                    vp, "Ambient occlusion", self.AO_AUTOSAVE_ID, self.AO_USE_CACHE_ID
                )
            vp = vp.GetNext()

    def _validate_video_post(self, vp, label, *ids):
        if vp.GetBit(c4d.BIT_VPDISABLED):
            return
        container = vp.GetDataInstance()
        for element_id in ids:
            if not container[element_id]:
                return

        self.add_warning(
            "{} Auto Save is set to ON. You should turn it off for the render, otherwise it may try to write files in a read-only directory and cause the render to fail".format(
                label
            )
        )


class ValidateScoutFrames(Validator):
    def run(self, _):
        """
        Add a validation warning for a potentially costly scout frame configuration.
        """
        info_section = self._submitter.section("InfoSection")

        scout_count = info_section.scout_frame_count
        frame_count = info_section.frame_count

        if frame_count < 5:
            return

        if scout_count < 5 and scout_count > 0:
            return

        if scout_count == 0 or scout_count == frame_count:
            msg = "All tasks will start rendering."
            msg += " To avoid unexpected costs, we strongly advise you to configure scout frames so that most tasks are initially put on hold. This allows you to check a subset of frames and estimate costs before you commit a whole sequence."
            self.add_warning(msg)

        if info_section.task_count != info_section.frame_count:
            msg = "You have chunking set higher than 1."
            msg += " This can cause more scout frames to be rendered than you might expect. ({} scout frames).".format(
                scout_count
            )
            self.add_warning(msg)


# Implement more validators here
####################################
####################################


def run(dialog, submitting=True):

    errors, warnings, notices = _run_validators(dialog)
    msg = ""
    if errors:
        errstr = "\n\n".join(errors)
        msg += "\nSome errors would cause the submission to fail:\n\n{}\n".format(errstr)
        c4d.gui.MessageDialog(msg, type=c4d.GEMB_OK)
        raise ValidationError(msg)
    if notices or warnings:
        if submitting:
            msg += "Would you like to continue this submission?\n\n"
            dialog_type = c4d.GEMB_OKCANCEL
        else:
            msg = "Validate only.\n\n"
            dialog_type = c4d.GEMB_OK

        if warnings:
            msg += (
                "Please check the warnings below:\n\n"
                + "\n\n".join(["[WARN]:{}".format(w) for w in warnings])
                + "\n\n"
            )
        if notices:
            msg += (
                "Please check the notices below:\n\n"
                + "\n\n".join(["[INFO]:{}".format(n) for n in notices])
                + "\n\n"
            )

        result = c4d.gui.MessageDialog(msg, type=dialog_type)
        if result != c4d.GEMB_R_OK:
            c4d.WriteConsole("[Conductor] Submission cancelled by user.\n")
            raise ValidationError(msg)
    else:
        if not submitting:
            msg = "No issues found!"
            result = c4d.gui.MessageDialog(msg, type=c4d.GEMB_OK)


def _run_validators(dialog):

    takename = "Main"
    validators = [plugin(dialog) for plugin in Validator.plugins()]
    for validator in validators:
        validator.run(takename)

    errors = list(set.union(*[validator.errors for validator in validators]))
    warnings = list(set.union(*[validator.warnings for validator in validators]))
    notices = list(set.union(*[validator.notices for validator in validators]))
    return errors, warnings, notices
