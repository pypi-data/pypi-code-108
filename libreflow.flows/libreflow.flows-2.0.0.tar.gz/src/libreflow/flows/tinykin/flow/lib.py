import os
import shutil

from kabaret import flow
from kabaret.flow_contextual_dict import ContextualView, get_contextual_dict
from kabaret.subprocess_manager.flow import RunAction

from libreflow import baseflow
from libreflow.utils.flow import get_context_value
from .file import FileSystemMap


class Department(baseflow.departments.Department):
    _short_name = flow.Param(None)
    _file_prefix = flow.Computed(cached=True)
    file_prefix = flow.Param('{dept}').ui(
        hidden=True,
        editable=False,
    )
    file_path = flow.Param('{department}').ui(
        hidden=True,
        editable=False,
    )
    
    def compute_child_value(self, child_value):
        if child_value is self.path:
            path = get_context_value(self, 'file_path', delim='/')
            self.path.set(path)
        elif child_value is self._file_prefix:
            prefix = get_context_value(self, 'file_prefix', delim='_')
            self._file_prefix.set(prefix + '_')
    
    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            return dict(
                department=self.name(),
                dept=self._short_name.get() if self._short_name.get() else self.name(),
                context='asset',
            )


class DesignDepartment(Department):
    _short_name = flow.Param("dsn")


class ModelingDepartment(Department):
    _short_name = flow.Param("mod")


class ShadingDepartment(Department):
    _short_name = flow.Param("sha")


class RiggingDepartment(Department):
    _short_name = flow.Param("rig")


class CompDepartment(Department):
    _short_name = flow.Param("comp")


class Util(flow.Object):

    _util_map = flow.Parent()
    _short_name = flow.Param(None)
    files = flow.Child(FileSystemMap)
    file_prefix = flow.Param('{util}').ui(
        hidden=True,
        editable=False,
    )
    file_path = flow.Param('{util}').ui(
        hidden=True,
        editable=False,
    )

    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            name = self._short_name.get()
            if name is None:
                name = self.name()

            return dict(util=name)


class UtilMap(flow.Map):

    _short_name = flow.Param(None)
    create = flow.Child(baseflow.maputils.SimpleCreateAction)
    file_prefix = flow.Param('{util_type}').ui(
        hidden=True,
        editable=False,
    )
    file_path = flow.Param('{util_type}').ui(
        hidden=True,
        editable=False,
    )
    
    @classmethod
    def mapped_type(cls):
        return Util

    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            name = self._short_name.get() or self.name()
            return dict(util_type=name)


class SkinningUtils(UtilMap):
    
    _short_name = flow.Param("skinning")


class RigModuleUtils(Util):
    
    _short_name = flow.Param("rigmod")


class MiscUtils(Util):
    
    _short_name = flow.Param("misc")


class Utils(flow.Object):
    
    skinning = flow.Child(SkinningUtils).ui(
        expanded=True,
        show_filter=True,
    )
    rig_modules = flow.Child(RigModuleUtils).ui(
        expanded=True,
        show_filter=True,
    )
    miscellaneous = flow.Child(MiscUtils).ui(
        expanded=True,
        show_filter=True,
    )
    file_prefix = flow.Param('utils').ui(
        hidden=True,
        editable=False,
    )
    file_path = flow.Param('utils').ui(
        hidden=True,
        editable=False,
    )


class AssetDepartments(flow.Object):
    design = flow.Child(DesignDepartment)
    modeling = flow.Child(ModelingDepartment)
    rigging = flow.Child(RiggingDepartment)
    shading = flow.Child(ShadingDepartment)
    compositing = flow.Child(CompDepartment)


class RevisionType(flow.values.ChoiceValue):
    
    CHOICES = ["working copy", "new publication"]


class SetAssetFilePublishComment(flow.Action):

    _file = flow.Parent()
    _files = flow.Parent(2)
    comment = flow.SessionParam("")

    def get_buttons(self):
        src_path = self._file.source_path.get()
        self.comment.set(
            "Created from %s" % os.path.basename(src_path)
        )

        return ["Confirm", "Cancel"]
    
    def run(self, button):
        if button == "Cancel":
            return self.get_result(next_action=self._file.configure.oid())
        
        self._file.publish_comment.set(self.comment.get())
        self._file.ready.set(True)
        self._files.touch()


class ConfigureAssetFileAction(flow.Action):

    _file = flow.Parent()
    _files = flow.Parent(2)

    path = flow.Param("").ui(
        label="Source path",
        placeholder="Drop here a valid file/folder"
    )
    create_as = flow.Param("new publication", RevisionType).ui(
        label="Create as"
    )

    def get_buttons(self):
        self.message.set("")
        self.path.revert_to_default()
        return ["Confirm", "Cancel"]

    def run(self, button):
        if button == "Cancel":
            return
        
        path = self.path.get()
        ext = self._file.file_extension.get()

        if not os.path.exists(path):
            self.message.set(f"<font color=#D5000D>Invalid source path.</font>")
            return self.get_result(close=False)
        
        source_ext = os.path.splitext(path)[1][1:]

        if not ext and source_ext:
            self.message.set(f"<font color=#D5000D>Source must be a <b>folder</b>.</font>")
            return self.get_result(close=False)
        
        if source_ext != ext:
            self.message.set(f"<font color=#D5000D>File extension must be <b>{ext}</b>.</font>")
            return self.get_result(close=False)
        
        revision_type = self.create_as.get()
        self._file.create_as.set(revision_type)
        self._file.source_path.set(path)

        if revision_type == "new publication":
            return self.get_result(next_action=self._file.set_publish_comment.oid())

        self._file.ready.set(True)
        self._files.touch()


class AssetFile(flow.Object):

    _files = flow.Parent()
    _asset = flow.Parent(3)

    file_name = flow.Computed()
    file_extension = flow.Computed()
    file_department = flow.Computed()
    # file_oid = flow.SessionParam("").ui(editable=False)
    ready = flow.SessionParam(False).ui(editor="bool")
    
    source_path = flow.SessionParam("").ui(editable=False)
    create_as = flow.SessionParam("").ui(editable=False)
    publish_comment = flow.SessionParam("").ui(editable=False)

    configure = flow.Child(ConfigureAssetFileAction)
    set_publish_comment = flow.Child(SetAssetFilePublishComment)

    def department_from_short_name(self, short_name):
        dept_name = self._files.department_names(short_name)
        dept_oid = self._asset.oid() + "/departments/" + dept_name
        
        return self.root().get_object(dept_oid)

    def create(self):
        if not self.ready.get():
            return

        department = self.department_from_short_name(self.file_department.get())
        files = department.files
        file_name = self.file_name.get()
        file_extension = self.file_extension.get()

        # Get file's mapped name
        mapped_name = file_name
        if file_extension:
            mapped_name += "_" + file_extension

        if files.has_mapped_name(mapped_name):
            file = files[mapped_name]
        else:
            if file_extension:
                file = self._create_file(file_name, file_extension, department)
            else:
                file = self._create_folder(file_name, department)
        
        working_copy = self._create_working_copy(file, self.source_path.get(), is_folder=not bool(file_extension))

        if self.create_as.get() == "new publication":
            self._publish_file(file, self.publish_comment.get())
    
    def _create_file(self, name, format, department):
        files = department.files
        files.create_file.file_name.set(name)
        files.create_file.file_format.set(format)
        files.create_file.run(None)
        
        return files["%s_%s" % (name, format)]
    
    def _create_folder(self, name, department):
        files = department.files
        files.create_folder.folder_name.set(name)
        files.create_folder.run(None)
        
        return files[name]

    def _create_working_copy(self, file, source_path=None, is_folder=False):
        file.create_working_copy_action.from_revision.set("")
        file.create_working_copy_action.run(None)
        working_copy = file.get_working_copy()

        if source_path:
            working_copy_path = working_copy.get_path()

            if is_folder:
                shutil.rmtree(working_copy_path)
                shutil.copytree(source_path, working_copy_path)
            else:
                os.remove(working_copy_path)
                shutil.copy2(source_path, working_copy_path)

        return working_copy
    
    def _publish_file(self, file, comment):
        file.publish_action.comment.set(comment)
        file.publish_action.upload_after_publish.set(True)
        file.publish_action.keep_editing.set(False)
        file.publish_action.run("Publish")
        
        return file.get_head_revision()
    
    def head_revision(self):
        if not self.exists():
            return None
        
        file = self.root().get_object(self.file_oid.get())
        return file.get_head_revision()
    
    def compute_child_value(self, child_value):
        file_data = self._files._files_data[self.name()]
        
        if child_value is self.file_name:
            self.file_name.set(file_data["name"])
        elif child_value is self.file_extension:
            self.file_extension.set(file_data["extension"])
        elif child_value is self.file_department:
            self.file_department.set(file_data["department"])


class AssetFiles(flow.DynamicMap):

    _asset = flow.Parent(2)

    def mapped_names(self, page_num=0, page_size=None):
        names = []
        self._files_data = {}

        for dept_files in self.asset_file_names().items():
            dept_name = dept_files[0]

            for name in dept_files[1]:
                file_name, file_ext = os.path.splitext(name)
                key = dept_name + "_" + name.replace(".", "_")

                self._files_data[key] = {
                    "name": file_name,
                    "extension": file_ext[1:],
                    "department": dept_name,
                }
                names.append(key)
        
        return names    
    
    def department_names(self, short_name):
        return {
            "dsn": "design",
            "mod": "modeling",
            "rig": "rigging",
            "sha": "shading",
        }[short_name]
    
    def asset_file_names(self):
        asset_type = self._asset._asset_type.name()
        if asset_type == "sets":
            return {
                "dsn": ["design.ai", "layers", "layers_add"],
            }
        else:
            files = {
                "mod": ["modelisation_export.fbx", "modelisation_export.obj", "modelisation.blend"],
                "rig": ["rig.blend", "rig_ok.blend"],
                "sha": ["textures"],
            }
            
            if asset_type == 'props':
                files['dsn'] = ['design.ai']
            
            return files
    
    def file_data(self, mapped_name):
        return self._files_data[mapped_name]
    
    @classmethod
    def mapped_type(cls):
        return AssetFile
    
    def columns(self):
        return ["File/folder", "Department"]
    
    def _fill_row_cells(self, row, item):
        name = item.file_name.get()
        ext = item.file_extension.get()
        if ext:
            name += "." + ext

        row["File/folder"] = name
        row["Department"] = self.department_names(item.file_department.get())
    
    def _fill_row_style(self, style, item, row):
        style["icon"] = ('icons.gui', 'check' if item.ready.get() else 'check-box-empty')
        style["activate_oid"] = item.configure.oid()


class ConfigureAssetAction(flow.Action):

    _asset = flow.Parent()
    files = flow.Child(AssetFiles)

    def get_buttons(self):
        self.message.set("<h2>Configure asset files</h2>")
        return ["Confirm", "Reset", "Cancel"]

    def run(self, button):
        if button == "Cancel":
            return
        
        if button == "Reset":
            for file in self.files.mapped_items():
                file.ready.set(False)
            
            self.files.touch()
            return self.get_result(close=False)
        
        for file in self.files.mapped_items():
            file.create()
        
        return self.get_result(goto=self._asset.oid())


class GotoAsset(flow.Action):

    _asset = flow.Parent()

    def needs_dialog(self):
        return False
    
    def allow_context(self, context):
        return False
    
    def run(self, button):
        return self.get_result(goto=self._asset.oid())


class Asset(baseflow.lib.Asset):
    _asset_family = flow.Parent(2)
    _asset_type = flow.Parent(4)
    departments = flow.Child(AssetDepartments).ui(expanded=True)
    configure_action = flow.Child(ConfigureAssetAction)
    goto_action = flow.Child(GotoAsset)
    file_prefix = flow.Param('{asset_name}').ui(
        hidden=True,
        editable=False,
    )
    file_path = flow.Param('{asset_name}').ui(
        hidden=True,
        editable=False,
    )

    def compute_child_value(self, child_value):
        if child_value is self.kitsu_url:
            child_value.set(
                "%s/episodes/all/assets/%s"
                % (self.root().project().kitsu_url.get(), self.kitsu_id.get())
            )


class Assets(flow.Map):
    _asset_family = flow.Parent()
    _asset_type = flow.Parent(3)
    create_asset = flow.Child(baseflow.maputils.SimpleCreateAction)

    @classmethod
    def mapped_type(cls):
        return Asset

class AssetFamily(flow.Object):
    assets = flow.Child(Assets).ui(
        expanded=True,
        show_filter=True,
    )
    file_prefix = flow.Param('{asset_family}').ui(
        hidden=True,
        editable=False,
    )
    file_path = flow.Param('{asset_family}').ui(
        hidden=True,
        editable=False,
    )

    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            return dict(asset_family=self.name())

class AssetFamilies(flow.Map):
    create_asset_family = flow.Child(baseflow.maputils.SimpleCreateAction)

    @classmethod
    def mapped_type(cls):
        return AssetFamily

class AssetType(flow.Object):

    asset_families = flow.Child(AssetFamilies).ui(
        expanded=True,
        show_filter=True,
    )
    utils = flow.Child(Utils).ui(expanded=False)
    file_prefix = flow.Param('{asset_type}').ui(
        hidden=True,
        editable=False,
    )
    file_path = flow.Param('{asset_type}').ui(
        hidden=True,
        editable=False,
    )

    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            return dict(asset_type=self.name())


class AssetTypes(flow.Map):

    create_asset_type = flow.Child(baseflow.maputils.SimpleCreateAction)

    @classmethod
    def mapped_type(cls):
        return AssetType


class RevisionType(flow.values.ChoiceValue):

    CHOICES = ["working copy", "first publication"]


class CreateAssetAction(flow.Action):

    ICON = ("icons.gui", "plus-sign-in-a-black-circle")

    asset_name = flow.SessionParam("").watched().ui(
        label="Name",
        placeholder="Kitsu asset name"
    )
    type = flow.Computed()
    family = flow.Computed()
    
    _asset_oid = flow.Computed()

    def asset_type_short_name(self, name):
        return {
            "Characters": "chars",
            "Props": "props",
            "Sets": "sets",
        }[name]
    
    def asset_family_short_name(self, name):
        return name
    
    def child_value_changed(self, child_value):
        if child_value is self.asset_name:
            self.type.touch()
            self.family.touch()
    
    def compute_child_value(self, child_value):
        self.message.set("<h2>Create an asset</h2>")

        if child_value in [self.type, self.family]:
            asset_name = self.asset_name.get()

            if not asset_name:
                self.message.set(self.message.get() + "<br>")
                child_value.set("")
                return
            
            kitsu_api = self.root().project().kitsu_api()
            asset_data = kitsu_api.get_asset_data(asset_name)
            asset_type = kitsu_api.get_asset_type(asset_name)

            if not asset_data:
                msg = f"No asset named {asset_name} in Kitsu."
                msg = f"<font color=#D5000D>{msg}</font><br>"
                self.message.set(self.message.get() + msg)
                child_value.set("")
                return
            
            self.message.set(self.message.get() + "<br>")

            if child_value is self.type:
                self.type.set(self.asset_type_short_name(asset_type["name"]) if asset_type else "")
            elif child_value is self.family:
                self.family.set(self.asset_family_short_name(asset_data["data"]["family"]) if asset_data else "")
    
    def _asset_oid(self):
        return self.root().project().oid() + "/asset_lib/asset_types/%s/asset_families/%s/assets/%s" % (
            self.type.get(),
            self.family.get(),
            self.asset_name.get()
        )
    
    def get_buttons(self):
        self.message.set("<h2>Create an asset</h2><br>")
        self.asset_name.revert_to_default()
        return ["Create", "Cancel"]
    
    def run(self, button):
        if button == "Cancel":
            return

        # Asset already exists, next step is configuration
        asset_oid = self._asset_oid()

        if self.root().session().cmds.Flow.exists(asset_oid):
            asset = self.root().get_object(asset_oid)
            return self.get_result(next_action=asset.configure_action.oid())

        asset_name = self.asset_name.get()
        asset_type_name = self.type.get()
        asset_family_name = self.family.get()

        # Warn if asset isn't registered in Kitsu
        if not asset_type_name or not asset_family_name:
            if not asset_name:
                msg = "Asset name must not be empty."
            else:
                msg = f"No asset named <b>{asset_name}</b> in Kitsu."

            self.message.set((
                "<h2>Create an asset</h2>"                
                f"<font color=#D5000D>{msg}</font><br>"
            ))
            return self.get_result(close=False)

        # Get/create asset type and family
        asset_lib = self.root().project().asset_lib

        if not asset_lib.asset_types.has_mapped_name(asset_type_name):
            asset_type = asset_lib.asset_types.add(asset_type_name)
        else:
            asset_type = asset_lib.asset_types[asset_type_name]

        if not asset_type.asset_families.has_mapped_name(asset_family_name):
            asset_family = asset_type.asset_families.add(asset_family_name)
        else:
            asset_family = asset_type.asset_families[asset_family_name]

        asset = asset_family.assets.add(asset_name)
        asset_family.assets.touch()

        return self.get_result(next_action=asset.configure_action.oid())


class RefreshAssets(flow.Action):

    ICON = ('icons.libreflow', 'refresh')

    _asset_browser = flow.Parent()

    def needs_dialog(self):
        return False
    
    def run(self, button):
        self._asset_browser.refresh_assets()
        self._asset_browser.touch()


class AssetBrowser(flow.DynamicMap):

    _asset_lib = flow.Parent()
    _asset_data = flow.Param({}).ui(editor='textarea')
    refresh = flow.Child(RefreshAssets).ui(label='Refresh list')

    def __init__(self, parent, name):
        super(AssetBrowser, self).__init__(parent, name)
        self._cache_names = None
        self._cache_data = None

    def mapped_names(self, page_num=0, page_size=None):
        names, _ = self._ensure_asset_data()
        return names
    
    def refresh_assets(self):
        self._cache_names = None
        self._cache_data = None
        data = {}

        for at in self._asset_lib.asset_types.mapped_items():
            for af in at.asset_families.mapped_items():
                mapped_names = af.assets.mapped_names()
                data.update(dict.fromkeys(mapped_names, (at.name(), af.name())))

        self._asset_data.set(data)
    
    def _ensure_asset_data(self):
        if self._cache_names is None:
            self._cache_data = self._asset_data.get()
            self._cache_names = sorted(self._cache_data.keys())
        
        return self._cache_names, self._cache_data
    
    def _get_asset_data(self, name):
        _, data = self._ensure_asset_data()
        return data[name]

    def columns(self):
        return ['Name', 'Type', 'Family']
    
    def rows(self):
        # Manually fill rows to avoid a huge number of calls to get_mapped
        rows = []
        asset_names, asset_data = self._ensure_asset_data()
        project_name = self.root().project().name()
        oid_format = '/{project}/asset_lib/asset_types/{type}/asset_families/{family}/assets/{asset}'

        for name in asset_names:
            data = asset_data[name]
            oid = oid_format.format(project=project_name, type=data[0], family=data[1], asset=name)
            style = {
                'activate_oid': oid + '/goto_action'
            }
            rows.append((oid, {
                'Name': name,
                'Type': data[0],
                'Family': data[1],
                '_style': style,
            }))
        
        return rows


class AssetLib(flow.Object):

    asset_types = flow.Child(AssetTypes).ui(
        expanded=True,
        default_height=150)
    browse_assets = flow.Child(AssetBrowser).ui(
        expanded=True,
        show_filter=True)
    add_asset = flow.Child(CreateAssetAction).ui(
        label="Add asset"
    )
    file_prefix = flow.Param('lib').ui(
        hidden=True,
        editable=False,
    )
    file_path = flow.Param('lib').ui(
        hidden=True,
        editable=False,
    )

    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            return dict(file_category="LIB")

    def _fill_ui(self, ui):
        if self.root().project().show_login_page():
            ui["custom_page"] = "libreflow.baseflow.LoginPageWidget"
