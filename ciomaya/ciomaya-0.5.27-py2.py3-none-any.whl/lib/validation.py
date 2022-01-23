import sys
import os


import traceback



import pymel.core as pm
from ciopath.gpath import Path
from ciopath.gpath_list import GLOBBABLE_REGEX, PathList
from ciocore.validator import Validator, ValidationError
from ciocore import data as coredata
from ciomaya.lib import renderman_path_utils
from ciomaya.lib import scraper_utils
from ciomaya.lib import const as k
from ciomaya.lib import layer_utils
from ciomaya.lib import asset_cache
from ciomaya.lib import software
from ciomaya.lib import node_utils

RENDERER_PACKAGE_REQUIREMENTS = {
    "arnold": "arnold-maya",
    "vray": "v-ray-maya",
    "renderman": "renderman-maya",
    "redshift": "redshift-maya",
}

WARNING_ICON = "ConductorWarning_18x18.png"
INFO_ICON = "ConductorInfo_18x18.png"
ERROR_ICON = "ConductorError_18x18.png"


class ValidateCamera(Validator):
    def run(self, _):
        if not any(cam.attr("renderable").get() for cam in pm.ls(type="camera")):
            self.add_warning(
                "No renderable cameras. You may want to make at least one camera renderable in Render Settings."
            )


class ValidateUploadDaemon(Validator):
    def run(self, _):
        use_daemon = self._submitter.attr("useUploadDaemon").get()
        if not use_daemon:
            return

        msg = 'This submission expects an uploader daemon to be running.\n After you press submit you can open a shell and enter: conductor uploader'

        location = (self._submitter.attr("locationTag").get() or "").strip()
        if location:
            msg = 'This submission expects an uploader daemon to be running and set to a specific location tag.\nAfter you press submit you can open a shell and type: conductor uploader --location {}'.format(location
            )

        msg += "\nIf you are not comfortable setting up an uploader daemon, simply switch off 'Use Upload Daemon' in the submitter UI and press Continue."
        msg += "\nCheck the script editor for details."
        self.add_notice(msg)
        # By also printing the message, the user can copy paste
        # `conductor uploader --location blah` from the console.
        pm.displayInfo(msg)


class ValidateTaskCount(Validator):
    def run(self, _):
        count = self._submitter.attr("taskCount").get()
        if count > 1000:
            self.add_notice(
                "This submission contains over 1000 tasks ({}). Are you sure this is correct?".format(
                    count
                )
            )


class ValidateSelectedRenderer(Validator):
    def run(self, layername):
        """
        Ensure selected renderer is valid and the selection is not wasteful.

        Permutations:

        1. Using Maya builtin: Warn if there are any cost-inducing renderer plugins (e.g. arnold).
        2. Using plugin such as arnold:
            Warn if there are any cost-inducing renderer plugins (e.g. redshift).
            Error if arnold is not selected.
        """
        # There's a bug in Maya 2022/Pymel, where the first time we attempt to get the array plug it
        # fails. The remedy is to get it twice.
        self._submitter.attr("pluginSoftware").get()

        plugins = [p.split(" ")[0] for p in self._submitter.attr("pluginSoftware").get() if p]
        all_renderer_packages = list(RENDERER_PACKAGE_REQUIREMENTS.values())
        renderer_plugins = [p for p in plugins if p in all_renderer_packages]
        current_renderer = pm.PyNode("defaultRenderGlobals").attr("currentRenderer").get()

        try:
            required_package = RENDERER_PACKAGE_REQUIREMENTS[current_renderer]
            if required_package not in plugins:
                self.add_error(
                    "The renderer for layer '{}' is set to '{}' but no versions of the plugin software '{}' are selected in the submitter. Are you sure this is correct?".format(
                        layername, current_renderer, required_package
                    )
                )
        except KeyError:
            # Probably Maya's builtin renderer
            pass

        # warn if renderer plugins selected that do not match the current renderer
        redundant_renderer_plugins = [
            p for p in renderer_plugins if RENDERER_PACKAGE_REQUIREMENTS.get(current_renderer) != p
        ]
        if len(redundant_renderer_plugins):
            msg = "You have one or more renderer plugins selected that do not match the current renderer. This is likely to incur unexpected costs. You can manage renderer plugins in the software section of the submitter."
            msg += " If you want to use a different renderer for each layer, use one renderer entry and override the renderer and version with a layer override."
            self.add_warning(msg)


class ValidateInstanceType(Validator):
    def run(self, layername):

        instance_type_name = self._submitter.attr("instanceTypeName").get()
        instance_type = next(
            (it for it in coredata.data()["instance_types"] if it["name"] == instance_type_name),
            None,
        )
        if not instance_type:
            self.add_error("No instance type. Please make sure a valid instance type is selected.")


class ValidateGPU(Validator):
    def run(self, layername):
        """
        Validate the suitability of the chosen instance type.

        If the renderer configuration requires a GPU but no GPU-enabled instance type is selected, add a validation error.
        If a GPU instance type is selected, but the renderer doesn't require it, add a validation warning.
        """
        current_renderer = pm.PyNode("defaultRenderGlobals").attr("currentRenderer").get()
        instance_type_name = self._submitter.attr("instanceTypeName").get()
        instance_type = next(
            (it for it in coredata.data()["instance_types"] if it["name"] == instance_type_name),
            None,
        )
        if not instance_type:
            return

        if "redshift" == current_renderer:
            self.validate_redshift(instance_type)
            return
        elif "arnold" == current_renderer:
            self.validate_arnold(instance_type)
        else:
            self.validate_other(instance_type)

    def validate_redshift(self, instance_type):

        description = instance_type.get("description")

        if not instance_type["gpu"]:
            msg = "The Redshift renderer is not compatible with the instance type: '{}' as it has no graphics card.".format(
                description
            )
            msg += " Please select a machine with a graphics card in the General section of the submitter. The submission is blocked as it would incur unexpected costs."
            self.add_error(msg)
            return

    def validate_arnold(self, instance_type):

        description = instance_type.get("description")

        arnold_gpu = pm.PyNode("defaultArnoldRenderOptions").attr("renderDevice").get()
        if (arnold_gpu and instance_type["gpu"]) or (
            (not arnold_gpu) and (not instance_type["gpu"])
        ):
            return

        if arnold_gpu and not instance_type["gpu"]:
            msg = "Arnold is in GPU mode and is not compatible with the instance type: '{}' as it has no graphics card.".format(
                description
            )
            msg += " Please select a machine with a graphics card in the General section of the submitter. The submission is blocked as it would incur unexpected costs."
            self.add_error(msg)

        if instance_type["gpu"] and not arnold_gpu:
            msg = "Arnold is in CPU mode, but you have selected an instance type with a graphics card: '{}'.".format(
                description
            )
            msg += " This could incur extra costs. Do not continue unless you are absolutely sure."
            self.add_warning(msg)

    def validate_other(self, instance_type):

        current_renderer = pm.PyNode("defaultRenderGlobals").attr("currentRenderer").get()
        description = instance_type.get("description")

        if instance_type["gpu"]:

            msg = "You have selected an instance type with a graphics card: '{}', yet the chosen renderer '{}' does not benefit from a GPU.".format(
                description, current_renderer
            )
            msg += " This could incur extra costs. Do not continue unless you are absolutely sure."
            self.add_warning(msg)


class ValidateArnoldTiledTextures(Validator):
    def run(self, _):

        if not pm.PyNode("defaultRenderGlobals").attr("currentRenderer").get() == "arnold":
            return
        try:
            render_options = pm.PyNode("defaultArnoldRenderOptions")
        except pm.MayaNodeError:
            self.add_warning(
                "Current renderer is set to Arnold, but there's no defaultArnoldRenderOptions node. Open the Render Settings window and it will be created."
            )
            return

        msg = "It is recommended to generate Arnold Tiled Textures (TX files) locally as they can't be generated efficiently on the render nodes.\n"
        msg += "Use the Arnold Texture Manager to generate tx files, then set the following attributes in the Arnold tab of Render Settings.\n"
        msg += "Switch Auto Convert Textures to Off\n"
        msg += "Switch Use Existing TX Textures to On\n"

        auto_tx = render_options.attr("autotx").get()
        use_existing = render_options.attr("use_existing_tiled_textures").get()

        if auto_tx or not use_existing:
            self.add_warning(msg)


class ValidateArnoldRenderOptions(Validator):
    def run(self, _):
        if not pm.PyNode("defaultRenderGlobals").attr("currentRenderer").get() == "arnold":
            return

        try:
            render_options = pm.PyNode("defaultArnoldRenderOptions")
        except pm.MayaNodeError:
            self.add_warning(
                "Current renderer is set to Arnold, but there's no defaultArnoldRenderOptions node"
            )
            return

        if not render_options.attr("threads_autodetect").get():
            self.add_warning(
                "Autodetect-Threads is turned off which could cause suboptimal machine usage and incur unnecessary costs. You may want to switch it back on in the Render Settings window, System tab."
            )

        if render_options.attr("denoiseBeauty").get():
            self.add_error(
                'You have the Optix denoiser turned on. This will not work unless you also select a machine with a capable GPU. Also note, the Optix denoiser is not temporally coherent. To turn off Optix denoiser, enter the following in the MEL script editor: setAttr "defaultArnoldRenderOptions.denoiseBeauty" 0;'
            )


class ValidateRendermanWindowsPaths(Validator):
    def run(self, _):

        if not sys.platform == "win32":
            return
        if not pm.PyNode("defaultRenderGlobals").attr("currentRenderer").get() == "renderman":
            return
        if self._submitter.attr("autosave").get():
            return

        path_dicts = scraper_utils.get_paths(renderman_path_utils.ATTRS)
        for p in path_dicts:
            match = renderman_path_utils.DRIVE_LETTER_RX.match(p["path"])
            if match:
                self.add_warning(
                    "We have to change some Renderman texture paths for the scene to render correctly on Windows. These paths are reverted after you submit, but the submitted scene which is saved in disk with adjustments may not work correctly when opened on Windows."
                )
                break


class ValidateScoutFrames(Validator):
    def run(self, _):
        """
        Add a validation warning for a potentially costly scout frame configuration.
        """
        scout_count = self._submitter.attr("scoutFrameCount").get()
        frame_count = self._submitter.attr("frameCount").get()
        chunk_size = self._submitter.attr("chunkSize").get()

        if frame_count < 5:
            return

        if scout_count < 5 and scout_count > 0:
            return

        if scout_count == 0 or scout_count == frame_count:
            msg = "All tasks will start rendering."
            msg += " To avoid unexpected costs, we strongly advise you to configure scout frames so that most tasks are initially put on hold. This allows you to check a subset of frames and estimate costs before you commit a whole sequence."
            self.add_warning(msg)

        if chunk_size > 1:
            msg = "You have chunk size set higher than 1."
            msg += " This can cause more scout frames to be rendered than you might expect. ({} scout frames).".format(
                scout_count
            )
            self.add_warning(msg)


class ValidateMissingAssets(Validator):
    def run(self, _):

        path_list = PathList()

        for gpath in asset_cache.data(self._submitter):

            # we can assunme that all globbable paths, (those containing glob
            # characters) cannot possibly represent missing files because they are
            # literally resolved  by checking what matches on disk. Ignore them.
            if not GLOBBABLE_REGEX.search(gpath.fslash()):
                path_list.add(gpath)

        # path_list has taken care of deduplication
        missing = []
        for gpath in path_list:
            pp = gpath.fslash()
            if not os.path.exists(pp):
                missing.append(pp)

        if missing:
            self.add_warning(
                "Some assets do not exist on disk. See the script editor for details. You can continue if you don't need them."
            )

            pm.displayInfo("----- Conductor Asset Validation -------")
            for asset in missing:
                pm.displayInfo("Not on disk: {}".format(asset))


class ValidateDestinationDirectory(Validator):
    def run(self, _):
        dest_directory = Path(self._submitter.attr("destinationDirectory").get()).fslash(
            with_drive=False
        )

        current_images_path = Path(node_utils.calc_dest_path()).fslash(with_drive=False)
        if not current_images_path == dest_directory:
            self.add_warning(
                "The selected destination directory for output '{}' does not match the images file rule '{}'. Are you sure this is what you want?".format(
                    dest_directory, current_images_path
                )
            )
        for gpath in asset_cache.data(self._submitter):
            asset_path = gpath.fslash(with_drive=False)
            if asset_path.startswith(dest_directory):
                pm.displayInfo(
                    "Some of your upload assets exist in the specified output destination directory\n. {} contains {}".format(
                        dest_directory, asset_path
                    )
                )
                self.add_error(
                    "The destination directory for output files contains assets that are in the upload list. This will cause your render to fail. See the script editor for details."
                )
                break
            if dest_directory.startswith(asset_path):
                pm.displayInfo(
                    "You are trying to upload a directory that contains your destination directory.\n. {} contains {}".format(
                        asset_path, dest_directory
                    )
                )
                self.add_error(
                    "One of your assets is a directory that contains the specified output destination directory. This will cause your render to fail. See the script editor for details."
                )
                break


class ValidateGeneralRenderSettings(Validator):
    def run(self, _):
        if pm.PyNode("defaultRenderGlobals").attr("modifyExtension").get():
            self.add_warning(
                "You have 'renumber frames' turned on in render settings. All your files will be renamed to frame 1. We strongly recommend that you turn this setting OFF."
            )


class ValidateYeti(Validator):
    def run(self, _):
        #
        if not (software.detect_yeti() and pm.about(ntOS=True) and pm.ls(type="pgYetiMaya")):
            return

        msg = """You have the YETI plugin loaded and Yeti nodes in your scene.

Since Conductor render nodes run on Linux, you must ensure that every Yeti asset
can be found on the Linux filesystem. To do this, you should define the
PG_IMAGE_PATH variable and make sure it contains an entry for every directory
where your assets are, but with the drive letter removed and backslashes
replaced with forward slashes. Specifically, in the Submitter UI, open the Extra
Environment section and add an entry for each directory like the following
example:

Suppose you have these assets
C:\\Users\\roberto\\textures\\texture.1.tif
C:\\Users\\roberto\\textures\\texture.2.tif
W:\\Production\\assets\\textures\\texture.3.tif

Then add these extra environment entries.

PG_IMAGE_PATH /Users/roberto/textures
PG_IMAGE_PATH /Production/assets/textures
"""
        self.add_notice("{}\nThis information has been printed to the script editor.".format(msg))

        pm.displayInfo(msg)


class ValidateXgen(Validator):
    def run(self, _):
        if not pm.pluginInfo("xgenToolkit", q=True, loaded=True):
            return

        palettes = pm.ls(type="xgmPalette")
        if not palettes:
            return

        if not self._submitter.attr("autosave").get():
            return

        template = self._submitter.attr("autosaveTemplate").get()

        if template.strip().lower() == "<scene>":
            return

        msg = """It looks like you are rendering with Xgen. If not, ignore this message.

When you use XGen's alembic cache export, there's no option to change the name.
It is named the same as the scene file with the extension .abc. When the scene
is opened for rendering, it looks for that alembic filename. This means, if you want
to use the cache, you must submit your scene with the same name as when you exported
the abc files.

Currently, you have autosave turned on in the submitter, and the naming template '{}'
means the scene name will be changed, and the abc files will not be found.

To remedy this, either turn off autosave, in which case you'll be asked to save the scene
manually before submission. Or enter <Scene> in the autosave template so that it saves
with the same name.
""".format(
            template
        )

        self.add_notice("{}\nThis information has been printed to the script editor.".format(msg))

        pm.displayInfo(msg)


# Implement more validators here
####################################


def run(node, dry_run=False):

    errors, warnings, notices = _run_validators(node)

    if not dry_run and not (errors + warnings + notices):
        return

    dialog_result = pm.layoutDialog(
        ui=pm.Callback(result_window, errors, warnings, notices, dry_run), title="Validation"
    )

    if dialog_result == "abort":
        msg = "Submission cancelled by user."
        raise ValidationError(msg)

    if dialog_result == "errors":
        msg = "Submission couldn't continue."
        raise ValidationError(msg)


def _run_validators(node):

    meta_warnings = set()
    layer_policy = node.attr("renderLayers").get()
    validators = [plugin(node) for plugin in Validator.plugins()]
    if layer_policy == k.CURRENT_LAYER:
        layers = [pm.editRenderLayerGlobals(q=True, currentRenderLayer=True)]
    else:
        layers = layer_utils.get_renderable_legacy_layers()
    for layer in layers:
        layername = layer_utils.get_layer_name(layer)
        with layer_utils.layer_context(layer):
            for validator in validators:
                try:
                    validator.run(layername)
                except BaseException as ex:
                    meta_warnings.add(
                        "[{}]:\nValidator failed to run. Don't panic, it's probably due to an unsupported feature and can be ignored. If you are worried, see the stack trace in the script editor.\n{}".format(
                            validator.title(), str(ex)
                        )
                    )
                    pm.displayWarning(traceback.format_exc())


    errors = list(set.union(*[validator.errors for validator in validators]))
    warnings = list(set.union(*[validator.warnings for validator in validators])) + list(
        meta_warnings
    )
    notices = list(set.union(*[validator.notices for validator in validators]))
    return errors, warnings, notices


def result_window(errors, warnings, notices, dry_run):
    """
    Show errors, warnings and notices.

    Logic:
    If we are in dry run mode:
        There's no continue button.
        The window will be displayed even if there are no messages at all.
        There will be one button - Close.

    If we are in submit mode:
        If there are errors
            There's no continue button.
            There will be one button - Close.
        The window will NOT be displayed if there are no messages.
        There will be 2 buttons - Close and Submit.

    """
    form = pm.setParent(q=True)

    can_continue = not (errors or dry_run)
    submit_has_errors = errors and not dry_run

    if errors:
        text = pm.text(label="Errors are preventing the submission")
    elif warnings:
        text = pm.text(
            label="You may continue, but please read the warnings to avoid unexpected results!"
        )
    elif notices:
        text = pm.text(label="Please read the notices!")
    else:
        text = pm.text(label="There are no errors or warnings.")

    if can_continue:
        cancel_button = pm.button(
            label="Cancel", command=pm.Callback(pm.layoutDialog, dismiss="abort")
        )

    okay_label = "Submit" if can_continue else "Close"

    okay_value = "errors" if submit_has_errors else "okay"

    okay_button = pm.button(
        label=okay_label, command=pm.Callback(pm.layoutDialog, dismiss=okay_value)
    )

    scroll = pm.scrollLayout(bv=True)
    pm.setParent("..")

    pm.formLayout(form, edit=True, width=600)
    form.attachForm(text, "left", 2)
    form.attachForm(text, "right", 2)
    form.attachForm(text, "top", 2)
    form.attachNone(text, "bottom")

    form.attachForm(scroll, "left", 2)
    form.attachForm(scroll, "right", 2)
    form.attachControl(scroll, "top", 2, text)
    form.attachControl(scroll, "bottom", 2, okay_button)

    if can_continue:
        form.attachForm(cancel_button, "left", 2)
        form.attachNone(cancel_button, "top")
        form.attachForm(cancel_button, "bottom", 2)
        form.attachPosition(cancel_button, "right", 2, 50)

        form.attachPosition(okay_button, "left", 2, 50)
    else:
        form.attachForm(okay_button, "left", 2)

    form.attachForm(okay_button, "right", 2)
    form.attachNone(okay_button, "top")
    form.attachForm(okay_button, "bottom", 2)

    pm.setParent(scroll)
    col = pm.columnLayout(adj=True)

    for error in errors:
        _create_notice_widget(col, error, ERROR_ICON)
        pm.setParent(col)
        pm.separator(height=8, style="in")
    for warning in warnings:
        _create_notice_widget(col, warning, WARNING_ICON)
        pm.setParent(col)
        pm.separator(height=8, style="in")
    for notice in notices:
        _create_notice_widget(col, notice, INFO_ICON)
        pm.setParent(col)
        pm.separator(height=8, style="in")
    pm.setParent(form)


def _create_notice_widget(column, notice, image):

    pm.setParent(column)

    form = pm.formLayout(nd=100, width=600)
    icon = pm.iconTextStaticLabel(style="iconOnly", image1=image)
    text = pm.text(label=notice.strip(), ww=True, align="left")

    form.attachForm(icon, "left", 2)
    form.attachNone(icon, "right")
    form.attachForm(icon, "top", 4)
    form.attachForm(icon, "bottom", 4)

    form.attachControl(text, "left", 10, icon)
    form.attachForm(text, "right", 2)
    form.attachForm(text, "top", 4)
    form.attachForm(text, "bottom", 4)
