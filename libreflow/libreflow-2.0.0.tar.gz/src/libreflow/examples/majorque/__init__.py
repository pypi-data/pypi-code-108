from kabaret import flow

from libreflow import baseflow, examples
from .film import Episodes, Shots
from .lib import AssetLib
from .file import CreateTrackedFileAction, FileSystemMap, Revisions
from .kitsu import SyncFromKitsu
from .runners import (
    AfterEffect,
    AfterEffectRender,
    Photoshop,
)
from .users import Bookmark


class Project(baseflow.Project, flow.InjectionProvider):
    episodes = flow.Child(Episodes).ui(default_height=420, expanded=True)
    asset_lib = flow.Child(AssetLib).ui(expanded=True)
    admin = flow.Child(baseflow.Admin)

    sequences = flow.Child(baseflow.film.Sequences).ui(hidden=True)

    def _register_runners(self):
        super(Project, self)._register_runners()
        self._RUNNERS_FACTORY.ensure_runner_type(AfterEffect)
        self._RUNNERS_FACTORY.ensure_runner_type(AfterEffectRender)
        self._RUNNERS_FACTORY.ensure_runner_type(Photoshop)

    @classmethod
    def _injection_provider(cls, slot_name, default_type):
        if slot_name == "libreflow.baseflow.file.CreateTrackedFileAction":
            return CreateTrackedFileAction
        elif slot_name == "libreflow.baseflow.kitsu.SyncFromKitsu":
            return SyncFromKitsu
        elif slot_name == "libreflow.baseflow.file.FileSystemMap":
            return FileSystemMap
        elif slot_name == "libreflow.baseflow.file.Revisions":
            return Revisions
        elif slot_name == "libreflow.baseflow.users.Bookmark":
            return Bookmark

    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            defaultContextualEdits = baseflow.Project.get_default_contextual_edits(
                self, "settings"
            )
            defaultContextualEdits.update(
                dict(
                    default_shot_layout_files="@{sequence}_{shot}_layout.psd, @{sequence}_{shot}_layout.aep",
                    default_shot_animation_files="{sequence}_{shot}_animationB.blend, {sequence}_{shot}_animationA.aep, @render, @preview",
                    default_shot_compositing_files="{sequence}_{shot}_compositing.aep, @render",
                    default_asset_design_files="{asset_type}_{asset_name}_design.psd,{asset_type}_{asset_name}_design.png, @ref",
                    default_asset_cycle_files="{asset_type}_{asset_name}_cycle.blend, @render, @preview",
                )
            )
            return defaultContextualEdits
