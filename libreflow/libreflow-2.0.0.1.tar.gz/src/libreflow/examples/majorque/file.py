import re
import os
from pathlib import Path
import shutil
from distutils.dir_util import copy_tree

from kabaret import flow
from kabaret.flow_contextual_dict import get_contextual_dict
from kabaret.subprocess_manager.flow import RunAction

from libreflow import baseflow


def remove_files(root_path):
    """
    Removes the files contained in a folder with a given path.
    https://stackoverflow.com/a/185941
    """
    if not os.path.exists(root_path):
        print('Failed to delete %s. Reason: Folder does not exists' % (root_path))
        return
    for filename in os.listdir(root_path):
        file_path = os.path.join(root_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            # elif os.path.isdir(file_path):
            #     shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def move_files(src_path, dst_path):
    for filename in os.listdir(src_path):
        src_file_path = os.path.join(src_path, filename)
        dst_file_path = os.path.join(dst_path, filename)
        try:
            if os.path.isfile(src_file_path) or os.path.islink(src_file_path):
                shutil.move(src_file_path, dst_file_path)
        except Exception as e:
            print('Failed to move %s to %s. Reason: %s' % (src_file_path, dst_file_path, e))


class RenderSettingsTemplate(flow.values.ChoiceValue):

    CHOICES = ["majorque_rendu_preview", "majorque_rendu_output"]


class OutputModuleTemplate(flow.values.ChoiceValue):

    CHOICES = ["majorque_preview", "majorque_output"]


class RenderWithAfterEffect(RunAction):

    _revision = flow.Parent()
    _files = flow.Parent(5)

    template_label = flow.Label("Templates:")
    render_settings = flow.Param("majorque_rendu_output", RenderSettingsTemplate)
    output_module = flow.Param("majorque_output", OutputModuleTemplate)

    def get_buttons(self):
        return ["Render", "Cancel"]

    def runner_name_and_tags(self):
        return "AfterEffectRender", []

    def get_run_label(self):
        return 'Render'

    @classmethod
    def supported_extensions(cls):
        return ["aep"]
    
    def allow_context(self, context):
        return (
            context
            and self._revision._file.format.get() in self.supported_extensions()
        )


class MakeAfterEffectPreview(RenderWithAfterEffect):

    render_settings = flow.Param("majorque_rendu_preview", RenderSettingsTemplate)
    output_module = flow.Param("majorque_preview", OutputModuleTemplate)

    def extra_argv(self):
        settings = get_contextual_dict(self._revision, "settings")
        file = self._revision._file

        return [
            "-project", self._revision.get_path(),
            "-comp", "%s_%s_output" % (settings["sequence"], settings["shot"]),
            # "-s", "%s" % start,
            # "-e", "%s" % end,
            "-RStemplate", self.render_settings.get(),
            # "-OMtemplate", self.output_module.get(),
            "-output", "%s/%s_%s_anim_%s.mov" % (
                file.get_playblast_folder(),
                settings["sequence"],
                settings["shot"],
                self._revision.name(),
            ),
        ]
    
    def run(self, button):
        if button == "Cancel":
            return

        if not self._files.has_mapped_name("preview"):
            self._files.add_folder("preview")
            self._files.touch()
        
        super(MakeAfterEffectPreview, self).run(button)


class MakeAfterEffectRender(RenderWithAfterEffect):

    def extra_argv(self):
        settings = get_contextual_dict(self._revision, "settings")
        file = self._revision._file

        return [
            "-project", self._revision.get_path(),
            "-comp", "%s_%s_output" % (settings["sequence"], settings["shot"]),
            # "-s", "%s" % start,
            # "-e", "%s" % end,
            "-RStemplate", self.render_settings.get(),
            "-OMtemplate", self.output_module.get(),
            "-output", "%s/%s_%s_anim.[####].png" % (
                file.get_render_path(),
                settings["sequence"],
                settings["shot"],
            ),
        ]
    
    def run(self, button):
        if button == "Cancel":
            return

        render_path = self._revision._file.get_render_path()

        if not self._files.has_mapped_name("render"):
            self._files.add_folder("render")
            self._files.touch()
        if not os.path.exists("%s/tmp" % render_path):
            os.makedirs("%s/tmp" % render_path)
        if not os.path.exists("%s/previous" % render_path):
            os.makedirs("%s/previous" % render_path)
        
        remove_files("%s/previous" % render_path)
        move_files(render_path, "%s/previous" % render_path)
        
        super(MakeAfterEffectRender, self).run(button)


class Revision(baseflow.file.Revision):

    playblast_path = flow.Computed()

    make_preview = flow.Child(MakeAfterEffectPreview)
    make_render = flow.Child(MakeAfterEffectRender)

    def has_playblast(self):
        return os.path.exists(self.playblast_path.get())

    def compute_child_value(self, child_value):
        if child_value is self.playblast_path:
            child_value.set(
                os.path.join(
                    self._file.get_playblast_folder(),
                    "%s_%s-movie.mov" % (self._file.complete_name.get(), self.name()),
                )
            )
        else:
            super(Revision, self).compute_child_value(child_value)


class Revisions(baseflow.file.Revisions):
    @classmethod
    def mapped_type(cls):
        return Revision


class CreateTrackedFileAction(baseflow.file.CreateTrackedFileAction):
    def run(self, button):
        if button == "Cancel":
            return

        settings = get_contextual_dict(self, "settings")
        file_category = settings.get("file_category", None)

        name = self.file_name.get()
        prefix = ""

        if file_category is not None:
            if file_category == "PROD":
                prefix = "{episode}_{sequence}_{shot}_{department}_"
            elif file_category == "LIB":
                prefix = "{asset_name}_{department}_"

            prefix = prefix.format(**settings)

        self.root().session().log_debug(
            "Creating file %s.%s" % (name, self.file_format.get())
        )

        self._files.create_file(name, extension=self.file_format.get(), base_name=prefix+name)
        self._files.touch()


class PublishAndRenderPlayblast(baseflow.file.PublishFileAction):
    def run(self, button):
        if button == "Cancel":
            return self.get_result(next_action=self._file.render_blender_playblast.oid())

        super(PublishAndRenderPlayblast, self).run(button)
        published_revision = self._file.get_head_revision()

        self._file.render_blender_playblast.revision_name.set(published_revision.name())

        return self._file.render_blender_playblast.run("Render")


class TrackedFile(baseflow.file.TrackedFile):

    with flow.group("Playblast"):
        render_blender_playblast = flow.Child(baseflow.file.RenderBlenderPlayblast)
        publish_and_playblast_blender = flow.Child(PublishAndRenderPlayblast)

    with flow.group("Open with"):
        open_with_blender = flow.Child(baseflow.file.OpenWithBlenderAction).ui(
            label="Blender"
        )
        open_with_krita = flow.Child(baseflow.file.OpenWithKritaAction).ui(
            label="Krita"
        )
        open_with_vscodium = flow.Child(baseflow.file.OpenWithVSCodiumAction).ui(
            label="VSCodium"
        )
        open_with_notepadpp = flow.Child(baseflow.file.OpenWithNotepadPPAction).ui(
            label="Notepad++"
        )

    def has_playblast(self):
        for rev in self.get_revisions().mapped_items():
            if rev.has_playblast():
                return True

        return False

    def get_playblast_folder(self):
        return os.path.join(
            self.root().project().get_root(),
            self._department.path.get(),
            "preview"
        )
    
    def get_render_path(self):
        return os.path.join(
            self.root().project().get_root(),
            self._department.path.get(),
            "render"
        )


class FileSystemMap(baseflow.file.FileSystemMap):
    def add_tracked_file(self, name, extension, complete_name):
        key = "%s_%s" % (name, extension)
        file = self.add(key, object_type=TrackedFile)
        file.format.set(extension)
        file.complete_name.set(complete_name)

        # Create file folder
        try:
            self.root().session().log_debug(
                "Create file folder '{}'".format(file.get_path())
            )
            os.makedirs(file.get_path())
        except OSError:
            self.root().session().log_error(
                "Creation of file folder '{}' failed.".format(file.get_path())
            )
            pass

        # Create current revision folder
        current_revision_folder = os.path.join(file.get_path(), "current")

        try:
            self.root().session().log_debug(
                "Create current revision folder '{}'".format(
                    current_revision_folder
                )
            )
            os.mkdir(current_revision_folder)
        except OSError:
            self.root().session().log_error(
                "Creation of current revision folder '{}' failed".format(
                    current_revision_folder
                )
            )
            pass

        return file
