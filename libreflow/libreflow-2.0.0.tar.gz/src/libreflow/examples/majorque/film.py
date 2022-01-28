import os
import gazu

from kabaret import flow
from kabaret.flow_contextual_dict import ContextualView, get_contextual_dict

from libreflow import baseflow
from .kitsu import KitsuEpisode
from .departments import Department
from .file import RenderSettingsTemplate, OutputModuleTemplate


class ShotDepartments(flow.Object):
    layout = flow.Child(Department).ui(expanded=False)
    animation = flow.Child(Department).ui(expanded=False)
    compositing = flow.Child(Department).ui(expanded=False)


class Shot(baseflow.film.Shot):

    _episode = flow.Parent(4)
    departments = flow.Child(ShotDepartments).ui(expanded=True)

    def compute_child_value(self, child_value):
        if child_value is self.kitsu_url:
            child_value.set(
                "%s/%s" % (self._episode.kitsu_url.get(), self.kitsu_id.get())
            )


class Shots(baseflow.film.Shots):

    create_shot = flow.Child(baseflow.maputils.SimpleCreateAction)
    with flow.group("Kitsu"):
        toggle_kitsu_settings = flow.Child(baseflow.film.DisplayKitsuSettings)
        update_kitsu_settings = flow.Child(baseflow.film.UpdateItemsKitsuSettings)

    @classmethod
    def mapped_type(cls):
        return Shot


class Sequence(baseflow.film.Sequence):

    _episode = flow.Parent(2)
    shots = flow.Child(Shots).ui(default_height=420, expanded=True)
    compositing = flow.Child(Department).ui(expanded=True)

    def compute_child_value(self, child_value):
        if child_value is self.kitsu_url:
            child_value.set(
                "%s/shots?search=%s" % (self._episode.kitsu_url.get(), self.name())
            )


class Sequences(baseflow.film.Sequences):

    ICON = ("icons.flow", "sequence")

    _episode = flow.Parent()

    create_sequence = flow.Child(baseflow.maputils.SimpleCreateAction)
    clear_sequences = flow.Child(baseflow.film.ClearSequencesAction).ui(hidden=True)
    update_kitsu_settings = flow.Child(baseflow.film.UpdateItemsKitsuSettings)

    @classmethod
    def mapped_type(cls):
        return Sequence

    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            return self._episode.get_default_contextual_edits(context_name)


class RenderOperation(flow.values.ChoiceValue):

    CHOICES = ["Rendering", "Preview"]


class RenderAfterEffectsAnimations(flow.Action):

    _episode = flow.Parent()

    operation = flow.Param("Rendering", RenderOperation)

    template_label = flow.Label("<b>Templates:</b>")
    render_settings = flow.Param("majorque_rendu_output", RenderSettingsTemplate)
    output_module = flow.Param("majorque_output", OutputModuleTemplate)

    def run(self, button):
        for seq in self._episode.sequences.mapped_items():
            for shot in seq.shots.mapped_items():
                try:
                    gazu.shot.get_shot(shot.kitsu_id.get())
                except gazu.exception.RouteNotFoundException:
                    pass

                rendering_task_type = gazu.task.get_task_type_by_name("Rendering")
                rendering_task = gazu.task.get_task_by_entity(shot.kitsu_id.get(), rendering_task_type)

                if rendering_task is not None:
                    rendering_task_status = gazu.task.get_task_status(rendering_task["task_status_id"])

                    if rendering_task_status["name"] == "INV":
                        try:
                            anim_file = shot.departments.animation.files["animationA_aep"]
                        except flow.exceptions.MappedNameError:
                            print("No animationA.aep in %s" % shot.departments.animation.oid())
                        else:
                            head_revision = anim_file.get_head_revision()

                            if self.operation.get() == "Rendering":
                                action = head_revision.make_render
                            else:
                                action = head_revision.make_preview
                            
                            action.render_settings.set(self.render_settings.get())
                            action.output_module.set(self.output_module.get())
                            action.run(None)
                            return


class Episode(KitsuEpisode):

    ICON = ("icons.flow", "film")

    settings = flow.Child(ContextualView).ui(hidden=True)
    sequences = flow.Child(Sequences).ui(default_height=420, expanded=True)
    compositing = flow.Child(Department).ui(expanded=False)

    render_aftereffects_animations = flow.Child(RenderAfterEffectsAnimations)

    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            return dict(episode=self.name())


class Episodes(flow.Map):

    ICON = ("icons.flow", "film")

    create_episode = flow.Child(baseflow.maputils.SimpleCreateAction)

    @classmethod
    def mapped_type(cls):
        return Episode

    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            return dict(file_category="PROD")
