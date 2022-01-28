from kabaret import flow
from kabaret.flow_contextual_dict import get_contextual_dict

import os
import fnmatch

from libreflow.baseflow.file import (
    FileFormat,
    Revision,
    TrackedFile, TrackedFolder,
    FileSystemMap,
    PublishFileAction,
    CreateTrackedFileAction, CreateFileAction,
    CreateTrackedFolderAction, CreateFolderAction,
    AddFilesFromExisting,
    FileRevisionNameChoiceValue,
)
from libreflow.baseflow.dependency import GetDependenciesAction
from libreflow.utils.flow import get_context_value
from libreflow.baseflow.users import PresetSessionValue

from .runners import (CHOICES, CHOICES_ICONS)


class FileFormat(flow.values.ChoiceValue):

    CHOICES = CHOICES


class CreateTrackedFileAction(CreateTrackedFileAction):

    ICON = ("icons.gui", "plus-sign-in-a-black-circle")

    _files = flow.Parent()

    file_name = flow.Param("")
    file_format = flow.Param("blend", FileFormat).ui(
        choice_icons=CHOICES_ICONS
    )

    def run(self, button):
        if button == "Cancel":
            return

        settings = get_contextual_dict(self, "settings")
        name = self.file_name.get()
        prefix = self._files.default_file_prefix.get()

        self.root().session().log_debug(
            "Creating file %s.%s" % (name, self.file_format.get())
        )

        self._files.add_tracked_file(name, self.file_format.get(), prefix + name)
        self._files.touch()


class CreateTrackedFolderAction(CreateTrackedFolderAction):

    ICON = ("icons.gui", "plus-sign-in-a-black-circle")

    _files = flow.Parent()
    _department = flow.Parent(2)


    folder_name = flow.Param("")


    def run(self, button):
        if button == "Cancel":
            return

        settings = get_contextual_dict(self, "settings")
        
        name = self.folder_name.get()
        prefix = self._files.default_file_prefix.get()

        self.root().session().log_debug(
            "Creating folder %s" % name
        )

        self._files.add_tracked_folder(name, prefix + name)
        self._files.touch()


class Revision(Revision):
    def compute_child_value(self, child_value):
        if child_value is self.file_name:
            name = "{filename}.{ext}".format(
                filename=self._file.complete_name.get(),
                ext=self._file.format.get(),
            )
            child_value.set(name)
        else:
            super(Revision, self).compute_child_value(child_value)


class PublishOKAction(flow.Action):

    _file = flow.Parent()
    _files = flow.Parent(2)
    comment = flow.SessionParam('', PresetSessionValue)
    revision_name = flow.Param(None, FileRevisionNameChoiceValue).watched()
    upload_after_publish = flow.SessionParam(False, PresetSessionValue).ui(editor='bool')

    def check_file(self):
        # In an ideal future, this method will check
        # the given revision of the file this action is parented to

        source_display_name = self._file.display_name.get()
        target_display_name = source_display_name.replace(".", "_ok.")
        msg = f"<h2>Publish in <font color=#fff>{target_display_name}</font></h2>"
        
        target_name, ext = self._target_name_and_ext()
        target_mapped_name = target_name + '_' + ext
        revision_name = self.revision_name.get()

        if self._files.has_mapped_name(target_mapped_name):
            target_file = self._files[target_mapped_name]

            if target_file.has_revision(revision_name):
                msg += (
                    "<font color=#D5000D>"
                    f"File {target_display_name} already has a revision {revision_name}."
                )
                self.message.set(msg)

                return False
        
        self.message.set((
            f"{msg}<font color='green'>"
            f"Revision {revision_name} of file {source_display_name} looks great !"
            "</font>"
        ))

        return True
    
    def allow_context(self, context):
        return context and self._file.enable_publish_ok.get()
    
    def child_value_changed(self, child_value):
        if child_value is self.revision_name:
            self.check_file()
    
    def _target_name_and_ext(self):
        split = self._file.name().split('_')
        name = '_'.join(split[:-1])
        ext = split[-1]

        return "%s_ok" % name, ext
    
    def apply_presets(self):
        self.comment.apply_preset()
        self.upload_after_publish.apply_preset()
    
    def update_presets(self):
        self.comment.update_preset()
        self.upload_after_publish.update_preset()
    
    def get_buttons(self):
        self.check_file()
        self.apply_presets()

        return ["Publish", "Cancel"]

    def run(self, button):
        if button == "Cancel":
            return
        
        self.update_presets()
        
        if not self.check_file():
            return self.get_result(close=False)

        target_name, ext = self._target_name_and_ext()
        target_mapped_name = target_name + '_' + ext
        revision_name = self.revision_name.get()
        
        # Create validation file if needed
        if not self._files.has_mapped_name(target_mapped_name):
            self._files.create_file.file_name.set(target_name)
            self._files.create_file.file_format.set(ext)
            self._files.create_file.run(None)
        
        target_file = self._files[target_mapped_name]

        self._file.publish_into_file.target_file.set(target_file)
        self._file.publish_into_file.source_revision_name.set(revision_name)
        self._file.publish_into_file.comment.set(self.comment.get())
        self._file.publish_into_file.upload_after_publish.set(self.upload_after_publish.get())
        self._file.publish_into_file.run(None)


class PublishFileAction(PublishFileAction):

    _files = flow.Parent(2)
    publish_ok = flow.SessionParam(False, PresetSessionValue).ui(editor='bool')

    def check_default_values(self):
        super(PublishFileAction, self).check_default_values()
        self.publish_ok.apply_preset()
    
    def update_presets(self):
        super(PublishFileAction, self).update_presets()
        self.publish_ok.update_preset()

    def run(self, button):
        super(PublishFileAction, self).run(button)

        if not self._file.enable_publish_ok.get():
            return
        
        if self.publish_ok.get():
            self._file.publish_ok.comment.set(self.comment.get())
            self._file.publish_ok.revision_name.set(self._file.get_head_revision().name())
            
            return self.get_result(next_action=self._file.publish_ok.oid())


class PublishOKItem(flow.Object):

    enable_publish_ok = flow.Computed(cached=True)

    def name_to_match(self):
        raise NotImplementedError(
            "Must return the name used to check if publish OK is enabled."
        )

    def publish_ok_enabled(self):
        settings = self.root().project().admin.project_settings
        patterns = settings.publish_ok_files.get().split(",")

        if not patterns:
            return True

        for pattern in patterns:
            pattern = pattern.encode('unicode-escape').decode().replace(" ", "")
            if fnmatch.fnmatch(self.name_to_match(), pattern):
                return True
        
        return False


class TrackedFile(TrackedFile, PublishOKItem):

    publish_ok = flow.Child(PublishOKAction).ui(group='Advanced')
    get_dependencies = flow.Child(GetDependenciesAction).ui(group='Advanced')

    def get_name(self):
        # Two remarks:
        # We redefined this method to lighten a bit tracked file's directory name for projects built with this flow.
        # Why the name of this method has been left totally confusing, is an excellent question.
        return self.name()
    
    def name_to_match(self):
        return self.display_name.get()
    
    def compute_child_value(self, child_value):
        if child_value is self.enable_publish_ok:
            self.enable_publish_ok.set(self.publish_ok_enabled())
        elif child_value is self.path:
            parent_path = self._map.default_file_path.get()
            path = os.path.join(parent_path, self.get_name())
            self.path.set(path)
        else:
            super(TrackedFile, self).compute_child_value(child_value)

    def get_dependency_template(self):
        kitsu_bindings = self.root().project().kitsu_bindings()
        settings = get_contextual_dict(self, 'settings')
        file_category = settings['file_category']
        casting = dict()

        if file_category == 'PROD':
            shot = settings['shot']
            sequence = settings['sequence']
            film = settings['film']
            casting = kitsu_bindings.get_shot_casting(shot, sequence)
            entity_oid = self.root().project().oid()
            entity_oid += f"/films/{film}/sequences/{sequence}/shots/{shot}"
        elif file_category == 'LIB':
            asset_name = settings['asset_name']
            asset_family = settings['asset_family']
            asset_type = settings['asset_type']
            entity_oid = self.root().project().oid()
            entity_oid += f"/asset_lib/asset_types/{asset_type}/asset_families/{asset_family}/assets/{asset_name}"

        dependency_template = settings.get('dependency_template', self.name())

        return dependency_template, entity_oid, casting

    def get_real_dependencies(self, revision_name=None):
        if revision_name is None:
            revision = self.get_head_revision()
        else:
            revision = self.get_revision(revision_name)

        # Return if revision does not exist
        if not revision:
            return []
        
        dependencies = revision.dependencies.get()
        
        # Return if no dependency has been reported for this revision
        if not dependencies:
            return []

        deps_file_paths = set()
        
        for dep_path, file_paths in dependencies.items():
            deps_file_paths.add(dep_path)
            dep_dir = os.path.dirname(dep_path)
            
            for path in file_paths:
                resolved_path = os.path.normpath(os.path.join(dep_dir, path))
                deps_file_paths.add(resolved_path)

        return list(deps_file_paths)


class TrackedFolder(TrackedFolder, PublishOKItem):
    
    publish_ok = flow.Child(PublishOKAction).ui(group='Advanced')

    def name_to_match(self):
        return self.display_name.get()

    def compute_child_value(self, child_value):
        if child_value is self.enable_publish_ok:
            self.enable_publish_ok.set(self.publish_ok_enabled())
        elif child_value is self.path:
            parent_path = self._map.default_file_path.get()
            path = os.path.join(parent_path, self.get_name())
            self.path.set(path)
        else:
            super(TrackedFolder, self).compute_child_value(child_value)


class CreateFolderAction(CreateFolderAction):

    def allow_context(self, context):
        return False


class CreateFileAction(CreateFileAction):

    def allow_context(self, context):
        return False


class AddFilesFromExisting(AddFilesFromExisting):

    def allow_context(self, context):
        return False


class FileSystemMap(FileSystemMap):
    
    _parent = flow.Parent()
    
    create_untracked_folder = flow.Child(CreateFolderAction)
    create_untracked_file = flow.Child(CreateFileAction)
    add_files_from_existing = flow.Child(AddFilesFromExisting)
    default_file_prefix = flow.Computed(cached=True)
    default_file_path = flow.Computed(cached=True)

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
    
    def add_tracked_folder(self, name, complete_name):
        folder = self.add(name, object_type=TrackedFolder)
        folder.format.set("zip")
        folder.complete_name.set(complete_name)

        # Create file folder
        try:
            self.root().session().log_debug(
                "Create tracked folder '{}'".format(folder.get_path())
            )
            os.makedirs(folder.get_path())
        except OSError:
            self.root().session().log_error(
                "Creation of tracked folder '{}' failed.".format(folder.get_path())
            )
            pass

        # Create current revision folder
        current_revision_folder = os.path.join(folder.get_path(), "current")

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

        return folder

    def compute_child_value(self, child_value):
        if child_value is self.default_file_prefix:
            self.default_file_prefix.set(
                get_context_value(self._parent, 'file_prefix', delim='_') + '_'
            )
        elif child_value is self.default_file_path:
            self.default_file_path.set(
                get_context_value(self._parent, 'file_path', delim='/') + '/'
            )
