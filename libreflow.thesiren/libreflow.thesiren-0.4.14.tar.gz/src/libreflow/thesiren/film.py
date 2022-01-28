import os
import gazu
import shutil
import glob
import time
import re

import kabaret.app.resources as resources
from kabaret import flow
from kabaret.flow_contextual_dict import ContextualView, get_contextual_dict
from kabaret.subprocess_manager.flow import RunAction

from libreflow import baseflow

from libreflow.utils.b3d import wrap_python_expr
from libreflow.utils.flow import get_context_value

from .file import FileSystemMap


class Department(baseflow.departments.Department):
    _short_name = flow.Param(None)
    _file_prefix = flow.Computed(cached=True)
    _shot = flow.Parent(2)
    _sequence = flow.Parent(4)
    
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
                context='shot',
            )

    def get_dependency_template(self):
        casting = self.root().project().kitsu_bindings().get_shot_casting(
            self._shot.name(),
            self._sequence.name())
        
        return self.name(), self._shot.oid(), casting


class AssetStatus(flow.values.ChoiceValue):

    CHOICES = ["NotAvailable", "Downloadable", "Available"]


class LayoutDependency(flow.Object):

    _parent = flow.Parent()
    
    asset_type = flow.Computed(store_value=False)
    asset_family = flow.Computed(store_value=False)
    asset_number = flow.Computed(store_value=False)
    asset_path = flow.Computed(store_value=False)
    asset_file_oid = flow.Computed(store_value=False)
    asset_revision_oid = flow.Computed(store_value=False)
    available = flow.Computed(store_value=False)

    def compute_child_value(self, child_value):
        asset_data = self._parent.asset_data(self.name())

        if child_value is self.asset_type:
            child_value.set(asset_data['asset_type'])
        elif child_value is self.asset_family:
            child_value.set(asset_data['asset_family'])
        elif child_value is self.asset_number and 'asset_number' in asset_data:
            child_value.set(asset_data['asset_number'])
        elif child_value is self.asset_file_oid:
            asset_type = self.asset_type.get()
            asset = None

            if self.name().startswith("audio") or self.name() == "board":
                asset = self._parent._shot
            else:
                asset_family = self.asset_family.get()
                asset_name = self.name()
                asset_oid = self.root().project().oid() + f"/asset_lib/asset_types/{asset_type}/asset_families/{asset_family}/assets/{asset_name}"

                if self.root().session().cmds.Flow.exists(asset_oid):
                    asset = self.root().get_object(asset_oid)
                else:
                    self.root().session().log_warning(
                        f"Asset {asset_oid} not found"
                    )

            if not asset:
                child_value.set(None)
                return

            file_name = self._parent.asset_type_file_name(asset_type)
            files = self._parent.files_from_asset_type(asset, asset_type)
            
            if not files.has_mapped_name(file_name):
                child_value.set(None)
            else:
                child_value.set(files[file_name].oid())
        elif child_value is self.asset_revision_oid:
            asset_file_oid = self.asset_file_oid.get()
            
            if asset_file_oid:
                file = self.root().get_object(asset_file_oid)
                rev = file.get_head_revision()

                if rev and rev.exists():
                    child_value.set(rev.oid())
                else:
                    child_value.set(None)
            else:
                child_value.set(None)
        elif child_value is self.asset_path:
            asset_revision_oid = self.asset_revision_oid.get()
            asset_type = self.asset_type.get()

            if not asset_revision_oid:
                child_value.set(None)
            else:
                rev = self.root().get_object(asset_revision_oid)
                if not rev.exists():
                    child_value.set(None)
                else:
                    if asset_type == "sets":
                        child_value.set(rev.path.get())
                    else:
                        child_value.set(rev.get_path())
        elif child_value is self.available:
            asset_path = self.asset_path.get()

            if self.asset_revision_oid.get():
                child_value.set("Available")
            elif self.asset_file_oid.get():
                child_value.set("Downloadable")
            else:
                child_value.set("NotAvailable")


class LayoutDependencies(flow.DynamicMap):

    _shot = flow.Parent(4)
    _sequence = flow.Parent(6)
    _updated = flow.BoolParam(False)

    def __init__(self, parent, name):
        super(LayoutDependencies, self).__init__(parent, name)
        self._assets_data_time = time.time()
        self._assets_data = None

    def mapped_names(self, page_num=0, page_size=None):
        if not self._assets_data or time.time() - self._assets_data_time > 30.0:
            self._assets_data = self._get_assets_data()
            self._assets_data_time = time.time()

        return list(self._assets_data.keys())

    def _get_assets_data(self):
        kitsu_api = self.root().project().kitsu_api()
        kitsu_casting = kitsu_api.get_shot_casting(self._shot.name(), self._sequence.name())
        casting = dict()
        
        # Kitsu assets
        for asset in kitsu_casting:
            asset_name = asset['asset_name']
            asset_type = asset['asset_type_name']
            asset_family = kitsu_api.get_asset_data(asset_name)['data']['family']

            casting[asset_name] = dict(
                asset_type=self.asset_type_short_name(asset_type),
                asset_family=self.asset_family_short_name(asset_family),
                asset_number=asset['nb_occurences']
            )
        
        # Audio file and storyboard
        for asset_name in ['audio', 'audio_voices', 'audio_effects', 'board']:
            casting[asset_name] = dict(
                asset_type=asset_name,
                asset_family='misc',
            )
        
        return casting

    def asset_data(self, asset_name):
        return self._assets_data[asset_name]

    @classmethod
    def mapped_type(cls):
        return LayoutDependency

    def columns(self):
        return ["Name", "Type", "Family", "Revision"]
    
    def asset_type_file_name(self, asset_type):
        return {
            "sets": "layers",
            "chars": "rig_ok_blend",
            "props": "rig_ok_blend",
            "audio": "audio_wav",
            "audio_voices": "audio_voices_wav",
            "audio_effects": "audio_effects_wav",
            "board": "board_mp4",
        }[asset_type]
    
    def files_from_asset_type(self, asset, asset_type):
        if asset_type == "sets":
            return asset.departments.design.files
        elif asset_type.startswith('audio') or asset_type == 'board':
            return asset.departments.misc.files
        else:
            return asset.departments.rigging.files
    
    def asset_type_short_name(self, name):
        return {
            "Characters": "chars",
            "Props": "props",
            "Sets": "sets",
        }[name]
    
    def asset_family_short_name(self, name):
        if name == "3d":
            return "secondary"
        
        return name
    
    def _fill_row_cells(self, row, item):
        row["Name"] = item.name()
        row["Type"] = item.asset_type.get()
        row["Family"] = item.asset_family.get()
        
        rev_oid = item.asset_revision_oid.get()
        rev_name = rev_oid.split("/")[-1] if rev_oid else ""
        row["Revision"] = rev_name
    
    def _fill_row_style(self, style, item, row):
        icon_by_status = {
            "NotAvailable": ("icons.libreflow", "cross-mark-on-a-black-circle-background-colored"),
            "Downloadable": ("icons.libreflow", "exclamation-sign-colored"),
            "Available": ("icons.libreflow", "checked-symbol-colored"),
        }
        style["icon"] = icon_by_status[item.available.get()]


class BuildBlenderScene(baseflow.file.GenericRunAction):

    _department = flow.Parent()
    _shot = flow.Parent(3)
    _sequence = flow.Parent(5)

    dependencies = flow.Child(LayoutDependencies).ui(expanded=True)

    def runner_name_and_tags(self):
        return "Blender", []
    
    def get_run_label(self):
        return 'Build scene'

    def get_buttons(self):
        # Make build action behave as base RunAction by default
        return RunAction.get_buttons(self)

    def needs_dialog(self):
        return True
    
    def allow_context(self, context):
        return context and context.endswith(".inline")

    def extra_env(self):
        return {
            "ROOT_PATH": self.root().project().get_root()
        }
    
    def target_file_extension(self):
        return 'blend'
    
    def _ensure_file(self, name, format, to_edit=False, src_path=None, publish_comment=""):
        files = self._department.files
        file_name = "%s_%s" % (name, format)

        if not files.has_mapped_name(file_name):
            files.create_file.file_name.set(name)
            files.create_file.file_format.set(format)
            files.create_file.run(None)
        
        file = files[file_name]

        if not to_edit and not src_path:
            return None
        
        if to_edit:
            revision = file.create_working_copy(source_path=src_path)
        else:
            revision = file.publish(source_path=src_path, comment=publish_comment)
        
        file.set_current_user_on_revision(revision.name())

        return revision.get_path()

    def _ensure_folder(self, name, to_edit=False, publish_comment=""):
        files = self._department.files

        if not files.has_mapped_name(name):
            files.create_folder.folder_name.set(name)
            files.create_folder.run(None)

        folder = files[name]

        if folder.has_working_copy(from_current_user=True):
            revision = folder.get_working_copy()
        else:
            revision = folder.create_working_copy()

        if not to_edit:
            revision = folder.publish(comment=publish_comment)

        folder.set_current_user_on_revision(revision.name())

        return revision.get_path()

    def _blender_cmd(self, operator, **kwargs):
        '''
        Returns Blender scene builder operator command as a string.

        Operator must be one of the following: `setup`, `setup_anim`,
                                               `add_asset`, `add_set`, `add_audio`, `add_board`,
                                               `update_audio", "update_storyboard`,
                                               `export_ae`,
                                               `cleanup`, `save`.
        '''

        blender_operators = {
            "setup": {'operator_command': "bpy.ops.pipeline.scene_builder_setup",
                      'args': "frame_start={frame_start}, frame_end={frame_end}, resolution_x={resolution_x}, resolution_y={resolution_y}, fps={fps}"},
            "setup_anim": {'operator_command': "bpy.ops.pipeline.scene_builder_setup_animation",
                           'args': 'alembic_filepath="{alembic_filepath}", assets={assets}, do_automate={do_automate}'},

            "add_asset": {'operator_command': 'bpy.ops.pipeline.scene_builder_import_asset',
                          'args': 'filepath="{filepath}", asset_name="{asset_name}", target_collection="{asset_type}"'},
            "add_set": {'operator_command': 'bpy.ops.pipeline.scene_builder_import_set',
                        'args': 'directory="{set_dir}", files={set_dicts}'},
            "add_audio": {'operator_command': 'bpy.ops.pipeline.scene_builder_import_audio',
                          'args': 'filepath="{filepath}"'},
            "add_board": {'operator_command': 'bpy.ops.pipeline.scene_builder_import_storyboard',
                          'args': 'filepath="{filepath}", use_corner={use_corner}'},

            "update_audio": {'operator_command': 'bpy.ops.pipeline.scene_builder_update_audio',
                             'args' :''},
            "update_board": {'operator_command': 'bpy.ops.pipeline.scene_builder_update_storyboard',
                             'args' :'filepath="{filepath}"'},

            "export_ae": {'operator_command': 'bpy.ops.pipeline.scene_builder_export_ae',
                          'args' :'filepath="{filepath}"'},

            "setup_render": {'operator_command': "bpy.ops.pipeline.scene_builder_setup_render",
                             'args': 'kitsu_duration={kitsu_duration}'},

            "cleanup": {'operator_command': 'bpy.ops.pipeline.scene_builder_cleanup',
                               'args': ''},
            "save": {'operator_command': 'bpy.ops.wm.save_mainfile',
                     'args': 'filepath="{filepath}", compress=True'},
        }

        op = blender_operators[operator]
        operator_command = op['operator_command']
        args = op['args'].format(**kwargs)
        command = f"if {operator_command}.poll(): {operator_command}({args})\n"
        return command


class BuildLayoutScene(BuildBlenderScene):

    def get_run_label(self):
        return 'Build layout scene'

    def extra_argv(self):
        # Get scene builder arguments
        frame_start = 101
        frame_end = 101 + self._shot_data.get("nb_frames", 0) - 1
        resolution_x = 2048
        resolution_y = 858
        fps = 24

        assets = self._shot_data.get("assets_data", [])
        sets = self._shot_data.get("sets_data", [])
        audio_paths = self._shot_data.get("audio_paths", [])
        board_path = self._shot_data.get("board_path", None)
        layout_path = self._shot_data["layout_path"] # Mandatory
        template_path = resources.get("file_templates", "template.blend")

        # Build Blender Python expression
        python_expr = "import bpy\n"
        python_expr += self._blender_cmd("setup", frame_start=frame_start, frame_end=frame_end, resolution_x=resolution_x, resolution_y=resolution_y, fps=fps)
        python_expr += self._blender_cmd("save", filepath=layout_path)
        
        for name, path, asset_type, asset_number in assets:
            for i in range(asset_number):
                python_expr += self._blender_cmd("add_asset", filepath=path, asset_name=name, asset_type=asset_type)
        for set_dir, set_dicts in sets:
            python_expr += self._blender_cmd("add_set", set_dir=set_dir, set_dicts=set_dicts)
        
        for audio_path in audio_paths:
            python_expr += self._blender_cmd("add_audio", filepath=audio_path)
        
        if board_path:
            python_expr += self._blender_cmd("add_board", filepath=board_path,
                                             use_corner=True)

        # python_expr += self._blender_cmd("cleanup")
        python_expr += self._blender_cmd("save", filepath=layout_path)

        return [
            "-b", template_path,
            "--addons", "io_import_images_as_planes,camera_plane,lfs_scene_builder,add_camera_rigs",
            "--python-expr", wrap_python_expr(python_expr)
        ]

    def get_buttons(self):
        msg = "<h2>Configure layout shot</h2>"

        for dep in self.dependencies.mapped_items():
            if dep.available.get() in ["Downloadable", "NotAvailable"]:
                msg += (
                    "<h3><font color=#D66700>"
                    "Some dependencies are still missing, either because they do not already exists or need to be downloaded on your site.\n"
                    "You can build the scene anyway, but you will have to manually update it when missing dependencies will be available."
                    "</font></h3>"
                )
                break
        
        self.message.set(msg)

        return ["Build and edit", "Build and publish", "Cancel"]
    
    def run(self, button):
        if button == "Cancel":
            return
        
        if button == "Refresh":
            self.dependencies.touch()
            return self.get_result(refresh=True, close=False)

        shot_name = self._shot.name()
        sequence_name = self._sequence.name()

        # Get shot data
        kitsu_api = self.root().project().kitsu_api()
        shot_data = kitsu_api.get_shot_data(shot_name, sequence_name)

        # Store dependencies file paths for Blender script building
        self._shot_data = {}
        self._shot_data["nb_frames"] = shot_data["nb_frames"]
        self._shot_data["assets_data"] = []
        self._shot_data["sets_data"] = []
        self._shot_data["audio_paths"] = []

        for dep in self.dependencies.mapped_items():
            if dep.available.get() != "Available":
                continue

            asset_type = dep.asset_type.get()
            asset_number = dep.asset_number.get()
            path = dep.asset_path.get().replace("\\", "/")
            
            if asset_type in ["chars", "props"]:
                self._shot_data["assets_data"].append((dep.name(), path, asset_type, asset_number))
            elif asset_type == "sets":
                set_names = list(map(os.path.basename, glob.glob("%s/*.png" % path)))

                self._shot_data["sets_data"].append(
                    (path, [{"name": name} for name in set_names])
                )
            elif asset_type == "board":
                self._shot_data["board_path"] = path
            elif asset_type.startswith("audio"):
                self._shot_data["audio_paths"].append(path)

        # Configure layout file
        layout_path = self._ensure_file(
            name='layout',
            format='blend',
            to_edit=(button == 'Build and edit'),
            src_path=resources.get("file_templates", "template.blend"),
            publish_comment="Created with scene builder"
        )
        
        self._department.files.touch()

        # Store layout output path
        self._shot_data["layout_path"] = layout_path.replace("\\", "/")

        # Build
        super(BuildLayoutScene, self).run(button)


class LayoutDepartment(Department):
    _short_name = flow.Param("lay")

    build_layout_scene = flow.Child(BuildLayoutScene).ui(
        label="Build layout scene"
    )


class BuildBlockingScene(BuildBlenderScene):

    _department = flow.Parent()
    _shot = flow.Parent(3)
    _sequence = flow.Parent(5)
    do_automate = flow.SessionParam(True).ui(editor='bool')
    
    def get_run_label(self):
        return 'Build blocking scene'
    
    def extra_argv(self):
        # Get scene builder arguments
        anim_path = self._shot_data.get("anim_path", None)
        alembic_path = self._shot_data.get("alembic_path", None)
        assets_data = self._shot_data.get("assets_data", [])
        assets = []
        do_automate = self.do_automate.get()

        for name, path, asset_type, asset_number in assets_data:
            for i in range(asset_number):
                assets.append({"name": name,
                                "filepath": path,
                                "target_collection": asset_type})
        
        board_path = self._shot_data.get("board_path", None)

        # Build Blender Python expression
        python_expr = "import bpy\n"
        python_expr += self._blender_cmd("setup_anim",
                                         alembic_filepath=alembic_path, assets=assets, do_automate=do_automate)

        # Update reference files

        python_expr += self._blender_cmd("update_audio")
        
        if board_path:
            python_expr += self._blender_cmd("update_board", filepath=board_path)

        python_expr += self._blender_cmd("cleanup")
        python_expr += self._blender_cmd("save", filepath=anim_path)

        return [
            "-b", anim_path,
            "--addons", "io_import_images_as_planes,camera_plane,lfs_scene_builder,add_camera_rigs",
            "--python-expr", wrap_python_expr(python_expr)
        ]

    def get_buttons(self):
        latest_revision = None
        files = self._shot.departments.layout.files

        if "layout_blend" in files.mapped_names():
            latest_revision = files["layout_blend"].get_head_revision()

        if (latest_revision is None or latest_revision.get_sync_status() != 'Available'):
            msg = "<h2><font color=#D5000D>Last revision of layout file not available</font></h2>"
            buttons =  ["Cancel"]
        else:
            msg = "<h2>Configure animation shot</h2>"
            buttons = ["Build and edit", "Cancel"]

        self.message.set(msg)

        return buttons

    def run(self, button):
        if button == 'Cancel':
            return

        if button == "Refresh":
            self.dependencies.touch()
            return self.get_result(refresh=True, close=False)

        shot_name = self._shot.name()
        sequence_name = self._sequence.name()

        # Store dependencies file paths for Blender script building
        self._shot_data = {}
        self._shot_data["assets_data"] = []

        for dep in self.dependencies.mapped_items():
            if dep.available.get() != "Available":
                continue

            asset_type = dep.asset_type.get()
            path = dep.asset_path.get().replace("\\", "/")
            asset_number = dep.asset_number.get()

            if asset_type in ["chars", "props"]:
                self._shot_data["assets_data"].append((dep.name(), path, asset_type + '-new', asset_number))
            elif asset_type == "board":
                self._shot_data["board_path"] = path
            # Ignore audio files here, as they will be updated from the ones
            # already present in the original layout scene

        # Configure anim file
        latest_revision = self._shot.departments.layout.files["layout_blend"].get_head_revision()
        layout_path = latest_revision.get_path()

        # Create empty file
        anim_path = self._ensure_file(
            name='blocking',
            format='blend',
            to_edit=True,
            src_path=layout_path,
            publish_comment="Created with anim scene builder"
        )

        # Configure alembic file
        alembic_path = self._ensure_file(
            name='ref_layout',
            format='abc',
            src_path=resources.get("file_templates", "template.abc"),
            publish_comment="Created with anim scene builder"
        )

        self._department.files.touch()

        # Store anim and alembic output path
        self._shot_data["anim_path"] = anim_path.replace("\\", "/")
        self._shot_data["alembic_path"] = alembic_path.replace("\\", "/")

        # Build
        super(BuildBlockingScene, self).run(button)


class BlockingRevisionName(baseflow.file.FileRevisionNameChoiceValue):
    
    def get_file(self):
        blocking_file_name = self.action.blocking_scene.get()
        if blocking_file_name is None:
            return None
        
        mapped_name = blocking_file_name.replace('.', '_')
        return self.action._department.files[mapped_name]


class CreateAnimationScene(flow.Action):
    
    _department = flow.Parent()
    blocking_scene = flow.Computed()
    revision_name = flow.Param(None, BlockingRevisionName)
    
    def get_buttons(self):
        self.revision_name.revert_to_default()
        return ['Create', 'Cancel']
    
    def needs_dialog(self):
        return (
            self.blocking_scene.get() is not None
            and self.revision_name.choices()
        )
    
    def _ensure_file(self, name, format):
        files = self._department.files
        mapped_name = '%s_%s' % (name, format)
        
        if not files.has_mapped_name(mapped_name):
            files = self._department.files
            files.create_file.file_name.set(name)
            files.create_file.file_format.set(format)
            files.create_file.run(None)
        
        return files[mapped_name]
    
    def compute_child_value(self, child_value):
        if child_value is self.blocking_scene:
            files = self._department.files
            name = None
            
            if files.has_mapped_name('blocking_blend') and \
                 files['blocking_blend'].get_head_revision() is not None:
                name = 'blocking.blend'
            elif files.has_mapped_name('breakdown_blend') and \
                 files['breakdown_blend'].get_head_revision() is not None:
                name = 'breakdown.blend'
            
            self.blocking_scene.set(name)
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        # Ensure animation scene is created
        files = self._department.files
        anim_file = self._ensure_file('animation', 'blend')
        
        # Check for a blocking scene
        blocking_file_name = self.blocking_scene.get()
        if blocking_file_name is None:
            files.touch()
            return
        
        mapped_name = blocking_file_name.replace('.', '_')
        blocking_file = files[mapped_name]

        # Create a working copy from it
        revisions = blocking_file.get_revisions()
        revision_name = self.revision_name.get()
        
        if not revisions.has_mapped_name(revision_name):
            files.touch()
            return
        
        working_copy = anim_file.create_working_copy(
            source_path=revisions[revision_name].get_path()
        )
        anim_file.set_current_user_on_revision(working_copy.name())
        anim_file.touch()
        
        files.touch()


class AnimationDepartment(Department):
    _short_name = flow.Param("ani")

    build_blocking_scene = flow.Child(BuildBlockingScene)
    create_anim_scene = flow.Child(CreateAnimationScene)


class RefreshMap(flow.Action):

    ICON = ('icons.libreflow', 'refresh')

    _map = flow.Parent()

    def needs_dialog(self):
        return False
    
    def run(self, button):
        self._map.update_dependencies_data()
        self._map.touch()


class OpenHistory(flow.Action):

    ICON = ("icons.gui", "ui-layout")

    _item = flow.Parent()

    def needs_dialog(self):
        return False
    
    def run(self, button):
        revision_oid = self._item.revision_oid.get()
        history_oid = self.root().session().cmds.Flow.resolve_path(revision_oid+'/../..')
        
        return self.get_result(goto=history_oid)


class RenderDependencyItemFile(baseflow.dependency.DependencyItemFile):

    goto_history = flow.Child(OpenHistory).ui(label='Show in history')


class RenderDependencyView(baseflow.dependency.DependencyView):

    ICON = ('icons.libreflow', 'dependencies')

    refresh = flow.Child(RefreshMap)

    def get_site_name(self):
        return None
    
    def get_revision_name(self):
        return None
    
    def columns(self):
        return ['Dependency', 'Last revision']
    
    def _get_mapped_item_type(self, mapped_name):
        if re.match(r'.*_\d\d\d$', mapped_name):
            return RenderDependencyItemFile
        else:
            return super(RenderDependencyView, self)._get_mapped_item_type(mapped_name)
    
    def _fill_row_cells(self, row, item):
        row['Dependency'] = item.dependency_name.get()
        row['Last revision'] = item.revision.get()
    
    def _fill_row_style(self, style, item, row):
        super(RenderDependencyView, self)._fill_row_style(style, item, row)

        if item.status.get() == 'Available':
            style['Last revision_foreground-color'] = '#45cc3d'
        else:
            style['Last revision_foreground-color'] = '#d5000d'
        
        style['icon'] = ('icons.libreflow', 'blank')


class BuildRenderScene(BuildBlenderScene):

    _department = flow.Parent()
    _shot = flow.Parent(3)
    _sequence = flow.Parent(5)

    dependencies = flow.Child(RenderDependencyView).ui(expanded=True)
    predictive_only = flow.Param(True).ui(hidden=True)

    def extra_argv(self):
        # Get scene builder arguments
        render_path = self._shot_data.get("render_path", None)
        anim_movie_path = self._shot_data.get("anim_movie_path", None)
        jsx_path = self._shot_data.get("jsx_path", None)
        shot_duration = self._shot_data.get("nb_frames", 0)

        # Build Blender Python expression
        python_expr = "import bpy\n"
        python_expr += self._blender_cmd("setup_render", kitsu_duration=shot_duration)
        python_expr += self._blender_cmd("cleanup")
        python_expr += self._blender_cmd("cleanup")

        if anim_movie_path:
            python_expr += self._blender_cmd("add_board",
                                             filepath=anim_movie_path, use_corner=False)
        python_expr += self._blender_cmd("save", filepath=render_path)

        python_expr += self._blender_cmd("export_ae", filepath=jsx_path)


        return [
            "-b", render_path,
            "--addons", "io_export_after_effects,lfs_scene_builder",
            "--python-expr", wrap_python_expr(python_expr)
        ]

    def get_buttons(self):
        latest_revision = None
        files = self._shot.departments.animation.files

        if "animation_blend" in files.mapped_names():
            latest_revision = files["animation_blend"].get_head_revision()
        elif "Animation_blend" in files.mapped_names():
            latest_revision = files["Animation_blend"].get_head_revision()
        elif "blocking_blend" in files.mapped_names():
            latest_revision = files["blocking_blend"].get_head_revision()
        elif "breakdown_blend" in files.mapped_names():
            latest_revision = files["breakdown_blend"].get_head_revision()

        if (latest_revision is None or latest_revision.get_sync_status() != 'Available'):
            msg = "<h2><font color=#D5000D>Last revision of animation file not available</font></h2>"
            buttons =  ["Cancel"]
        else:
            msg = "<h2>Configure render shot</h2>"
            buttons = ["Build and edit", "Cancel"]
            self.latest_revision = latest_revision

        self.message.set(msg)

        return buttons

    def run(self, button):
        if button == 'Cancel':
            return

        if button == "Refresh":
            self.dependencies.touch()
            return self.get_result(refresh=True, close=False)

        shot_name = self._shot.name()
        sequence_name = self._sequence.name()

        # Store dependencies file paths for Blender script building
        self._shot_data = {}

        # Get animation movie
        anim_movie_file = None
        if "animation_movie_mov" in self._shot.departments.animation.files.mapped_names():
            anim_movie_file = self._shot.departments.animation.files["animation_movie_mov"]
        elif "blocking_movie_mov" in self._shot.departments.animation.files.mapped_names():
            anim_movie_file = self._shot.departments.animation.files["blocking_movie_mov"]

        if anim_movie_file is not None:
            anim_movie_latest_revision = anim_movie_file.get_head_revision()

            if anim_movie_latest_revision is not None:
                self._shot_data["anim_movie_path"] = anim_movie_latest_revision.get_path().replace("\\", "/")

        # Configure comp file
        anim_path = self.latest_revision.get_path()

        # Create empty file
        render_path = self._ensure_file(
            name='render',
            format='blend',
            to_edit=True,
            src_path=anim_path,
        )

        # Configure jsx file
        jsx_path = self._ensure_file(
            name='compositing',
            format='jsx',
            src_path=resources.get("file_templates", "template.jsx"),
            publish_comment="Export from Blender"
        )

        # Configure AE file
        aep_path = self._ensure_file(
            name='compositing',
            format='aep',
            to_edit=True,
            src_path=resources.get("file_templates", "template.aep"),
        )

        # Configure render dir
        self._ensure_folder(
            name='passes',
            publish_comment="Render"
        )

        self._department.files.touch()

        # Store anim and jsx output path
        self._shot_data["render_path"] = render_path.replace("\\", "/")
        self._shot_data["jsx_path"] = jsx_path.replace("\\", "/")

        # Store Kitsu reference duration
        shot_data = self.root().project().kitsu_api().get_shot_data(
            shot_name,
            sequence_name
        )
        self._shot_data["nb_frames"] = shot_data["nb_frames"]

        # Build
        super(BuildRenderScene, self).run(button)


class CompDepartment(Department):
    _short_name = flow.Param("comp")

    build_render_scene = flow.Child(BuildRenderScene)

    def get_default_contextual_edits(self, context_name):
        if context_name == 'environment':
            return dict(BLENDER_VERSION='2.93')
        else:
            return super(CompDepartment, self).get_default_contextual_edits(context_name)


class MiscDepartment(Department):
    _short_name = flow.Param("misc")

class ShotDepartments(flow.Object):
    layout = flow.Child(LayoutDepartment).ui(expanded=False)
    animation = flow.Child(AnimationDepartment).ui(expanded=False)
    compositing = flow.Child(CompDepartment).ui(expanded=False)
    misc = flow.Child(MiscDepartment).ui(expanded=False)


class Shot(baseflow.film.Shot):

    _film = flow.Parent(4)
    departments = flow.Child(ShotDepartments).ui(expanded=True)
    file_prefix = flow.Param('{shot}').ui(
        hidden=True,
        editable=False,
    )
    file_path = flow.Param('{shot}').ui(
        hidden=True,
        editable=False,
    )

    def compute_child_value(self, child_value):
        if child_value is self.kitsu_url:
            child_value.set(
                "%s/%s" % (self._film.kitsu_url.get(), self.kitsu_id.get())
            )


class Shots(baseflow.film.Shots):

    create_shot = flow.Child(baseflow.maputils.SimpleCreateAction)

    @classmethod
    def mapped_type(cls):
        return Shot


class ShotToPlayblastDepartment(flow.Object):
    
    _shot = flow.Parent()
    _shots = flow.Parent(2)
    to_render = flow.SessionParam(False).ui(editor='bool')
    
    def _file_mapped_name(self):
        return self.name() + '_blend'
    
    def get_file(self):
        oid = "%s/shots/%s/departments/%s/files/%s" % (
            self._shots.sequence.oid(),
            self._shot.name(),
            self.name(),
            self._file_mapped_name(),
        )
        
        if not self.root().session().cmds.Flow.exists(oid):
            return None
        
        file_object = self.root().get_object(oid)
        return file_object
    
    def get_icon(self):
        return ('icons.gui', self.to_render.get() and 'check' or 'check-box-empty')

class ShotToPlayblast(flow.Object):
    
    layout = flow.Child(ShotToPlayblastDepartment)
    blocking = flow.Child(ShotToPlayblastDepartment)
    animation = flow.Child(ShotToPlayblastDepartment)


class ShotsToPlayblast(flow.DynamicMap):
    
    sequence = flow.Parent(2)
    
    @classmethod
    def mapped_type(cls):
        return ShotToPlayblast
    
    def mapped_names(self, page_num=0, page_size=None):
        return self.sequence.shots.mapped_names()
    
    def columns(self):
        return ['Name', 'Layout', 'Blocking', 'Animation']
    
    def _fill_row_cells(self, row, item):
        row['Name'] = item.name()
        row['Layout'] = ''
        row['Blocking'] = ''
        row['Animation'] = ''
    
    def _fill_row_style(self, style, item, row):
        style["Layout_icon"] = item.layout.get_icon()
        style["Blocking_icon"] = item.blocking.get_icon()
        style["Animation_icon"] = item.animation.get_icon()


class RenderSequencePlayblasts(flow.Action):
    
    shots = flow.Child(ShotsToPlayblast).ui(
        expanded=True,
        # action_submenus=True,
        items_action_submenus=True,
    )
    
    def add_to_render_pool(self, file, revision_name=None, use_simplify=False, reduce_textures=False, target_texture_width=4096):
        if revision_name is None:
            rev = file.get_head_revision()
            if rev is None or rev.get_sync_status() != 'Available':
                self.root().session().log_error(
                    'File %s has no head revision' % file.oid()
                )
                return
            
            revision_name = rev.name()

        file.render_blender_playblast.revision_name.set(revision_name)
        file.render_blender_playblast.use_simplify.set(use_simplify)
        file.render_blender_playblast.reduce_textures.set(reduce_textures)
        file.render_blender_playblast.target_texture_width.set(target_texture_width)
        file.render_blender_playblast.run('Add to render pool')
    
    def run(self, button):
        for shot in self.shots.mapped_items():
            if shot.layout.to_render.get():
                f_layout = shot.layout.get_file()
                if f_layout is not None:
                    self.add_to_render_pool(f_layout)
            
            if shot.blocking.to_render.get():
                f_blocking = shot.blocking.get_file()
                if f_blocking is not None:
                    self.add_to_render_pool(f_blocking)
            
            if shot.animation.to_render.get():
                f_animation = shot.animation.get_file()
                if f_animation is not None:
                    self.add_to_render_pool(f_animation)


class Sequence(baseflow.film.Sequence):

    _film = flow.Parent(2)
    shots = flow.Child(Shots).ui(
        default_height=420,
        expanded=True,
        show_filter=True,
    )
    file_prefix = flow.Param('{sequence}').ui(
        hidden=True,
        editable=False,
    )
    file_path = flow.Param('{sequence}').ui(
        hidden=True,
        editable=False,
    )
    misc = flow.Child(MiscDepartment)
    # render_playblasts = flow.Child(RenderSequencePlayblasts)

    def compute_child_value(self, child_value):
        if child_value is self.kitsu_url:
            child_value.set(
                "%s/shots?search=%s" % (self._film.kitsu_url.get(), self.name())
            )


class Sequences(baseflow.film.Sequences):

    ICON = ("icons.flow", "sequence")

    _film = flow.Parent()

    create_sequence = flow.Child(baseflow.maputils.SimpleCreateAction)
    update_kitsu_settings = flow.Child(baseflow.film.UpdateItemsKitsuSettings)

    @classmethod
    def mapped_type(cls):
        return Sequence

    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            return self._film.get_default_contextual_edits(context_name)



class Film(flow.Object):

    ICON = ("icons.flow", "film")

    sequences = flow.Child(Sequences).ui(
        default_height=420,
        expanded=True,
        show_filter=True,
    )
    file_prefix = flow.Param('{film}').ui(
        hidden=True,
        editable=False,
    )
    file_path = flow.Param('{film}').ui(
        hidden=True,
        editable=False,
    )
    
    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            return dict(film=self.name())

    def _fill_ui(self, ui):
        if self.root().project().show_login_page():
            ui["custom_page"] = "libreflow.baseflow.LoginPageWidget"


class Films(flow.Map):

    ICON = ("icons.flow", "film")

    create_film = flow.Child(baseflow.maputils.SimpleCreateAction)

    @classmethod
    def mapped_type(cls):
        return Film

    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            return dict(file_category="PROD")


# TODO

# file_category a corriger
