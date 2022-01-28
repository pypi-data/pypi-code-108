import os
import fnmatch
from kabaret import flow
from kabaret.flow_contextual_dict import get_contextual_dict

from libreflow.baseflow.file import (
    Revision,
    TrackedFile, TrackedFolder,
    FileSystemMap as BaseFileSystemMap,
    PublishFileAction,
    CreateFileAction as BaseCreateFileAction,
    CreateFolderAction as BaseCreateFolderAction,
    FileRevisionNameChoiceValue,
)
from libreflow.baseflow.dependency import GetDependenciesAction
from libreflow.utils.flow import get_context_value
from libreflow.baseflow.users import PresetSessionValue


class CreateFileAction(BaseCreateFileAction):

    def run(self, button):
        if button == 'Cancel':
            return

        name, extension = self.file_name.get(), self.file_format.get()
        prefix = self._files.default_file_prefix.get()

        if self._files.has_file(name, extension):
            self._warn((
                f'File {name}.{extension} already exists. '
                'Please choose another name.'
            ))
            return self.get_result(close=False)
        
        self._files.add_file(
            name,
            extension=extension,
            base_name=prefix+name,
            display_name=f'{name}.{extension}',
            tracked=self.tracked.get()
        )
        self._files.touch()


class CreateFolderAction(BaseCreateFolderAction):

    def run(self, button):
        if button == 'Cancel':
            return

        name = self.folder_name.get()
        prefix = self._files.default_file_prefix.get()

        if self._files.has_folder(name):
            self._warn((
                f'Folder {name} already exists. '
                'Please choose another name.'
            ))
            return self.get_result(close=False)
        
        self._files.add_folder(
            name,
            base_name=prefix+name,
            display_name=name,
            tracked=self.tracked.get()
        )
        self._files.touch()


class PublishOKAction(flow.Action):

    ICON = ('icons.flow', 'publish-ok')

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
        
        # Create validation file if needed
        if not self._files.has_file(target_name, ext):
            self._files.add_file(
                name=target_name,
                extension=ext,
                tracked=True
            )
        
        target_file = self._files[target_mapped_name]
        revision_name = self.revision_name.get()

        self._file.publish_into_file.target_file.set(target_file)
        self._file.publish_into_file.source_revision_name.set(revision_name)
        self._file.publish_into_file.comment.set(self.comment.get())
        self._file.publish_into_file.upload_after_publish.set(self.upload_after_publish.get())
        self._file.publish_into_file.run(None)


class PublishOKValue(PresetSessionValue):

    DEFAULT_EDITOR = 'bool'

    _file = flow.Parent(2)

    def _fill_ui(self, ui):
        super(PublishOKValue, self)._fill_ui(ui)
        ui['hidden'] = not self._file.enable_publish_ok.get()


class PublishFileAction(PublishFileAction):

    _files = flow.Parent(2)
    publish_ok = flow.SessionParam(False, PublishOKValue)

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


class FileSystemMap(BaseFileSystemMap):
    
    _parent = flow.Parent()
    
    default_file_prefix = flow.Computed(cached=True)
    default_file_path = flow.Computed(cached=True)

    create_file_action   = flow.Child(CreateFileAction).ui(label='Create file')
    create_folder_action = flow.Child(CreateFolderAction).ui(label='Create folder')

    def get_parent_path(self):
        return get_context_value(
            self._parent, 'file_path', delim='/'
        )

    def compute_child_value(self, child_value):
        if child_value is self.default_file_prefix:
            self.default_file_prefix.set(
                get_context_value(self._parent, 'file_prefix', delim='_') + '_'
            )
        elif child_value is self.default_file_path:
            self.default_file_path.set(
                get_context_value(self._parent, 'file_path', delim='/') + '/'
            )
