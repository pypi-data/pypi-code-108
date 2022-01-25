from ciotemplate.expander import Expander
import re
from PySide2 import QtWidgets, QtGui
from pymxs import runtime as rt
from cioseq.sequence import Sequence
from ciomax.sections.collapsible_section import CollapsibleSection
from ciomax.components.text_field_grp import TextFieldGrp
from ciomax.components.int_field_grp import IntFieldGrp
SCOUT_AUTO_REGEX = re.compile(r"^auto[, :]+(\d+)$")


class FramesSection(CollapsibleSection):
    ORDER = 30

    def __init__(self, dialog):
        super(FramesSection, self).__init__(dialog, "Frames")

        self.main_sequence = None
        self.scout_sequence = None

        self.chunk_size_component = IntFieldGrp(
            label="Chunk size", default=1, minimum=1)
        self.custom_range_component = TextFieldGrp(
            label="Use custom range", hidable=True)
        self.scout_frames_component = TextFieldGrp(
            label="Use scout frames", enablable=True)

        self.content_layout.addWidget(self.chunk_size_component)
        self.content_layout.addWidget(self.custom_range_component)
        self.content_layout.addWidget(self.scout_frames_component)

        self.configure_signals()

    def configure_signals(self):
        """Write to store when values change"""
        self.chunk_size_component.field.valueChanged.connect(
            self.on_chunk_size_change)

        self.custom_range_component.field.editingFinished.connect(
            self.on_custom_range_change)

        self.custom_range_component.display_checkbox.stateChanged.connect(
            self.on_use_custom_range_change)

        self.scout_frames_component.field.editingFinished.connect(
            self.on_scout_frames_change)

        self.scout_frames_component.display_checkbox.stateChanged.connect(
            self.on_use_scout_frames_change)

    def on_chunk_size_change(self, value):
        self.dialog.store.set_chunk_size(value)
        self._set_sequences()

    def on_custom_range_change(self):
        self.dialog.store.set_custom_range(
            self.custom_range_component.field.text())
        self._set_sequences()

    def on_use_custom_range_change(self, value):
        self.dialog.store.set_use_custom_range(value > 0)
        self._set_sequences()

    def on_scout_frames_change(self):
        self.dialog.store.set_scout_frames(
            self.scout_frames_component.field.text())
        self._set_sequences()

    def on_use_scout_frames_change(self, value):
        self.dialog.store.set_use_scout_frames(value > 0)
        self._set_sequences()

    def _set_sequences(self):
        """Convert all the frames parameters into two Sequence objects.

        self.main_sequence
        self.scout_sequence
        """
        chunk_size = self.chunk_size_component.field.value()
        if self.custom_range_component.display_checkbox.isChecked():
            frame_spec = self.custom_range_component.field.text().strip()
        else:
            frame_spec = scene_frame_spec()
        try:
            self.main_sequence = Sequence.create(
                frame_spec, chunk_size=chunk_size, chunk_strategy="progressions")
        except (ValueError, TypeError):
            self.main_sequence = None

        if self.scout_frames_component.display_checkbox.isChecked():
            scout_spec = self.scout_frames_component.field.text().strip()
            match = SCOUT_AUTO_REGEX.match(scout_spec)
            if match:
                samples = int(match.group(1))

                self.scout_sequence = self.main_sequence.subsample(samples)
            else:
                try:
                    self.scout_sequence = Sequence.create(scout_spec)
                except (ValueError, TypeError):
                    self.scout_sequence = None
        else:
            self.scout_sequence = None

        if self.dialog.main_tab:
            self.dialog.main_tab.section("InfoSection").update(
                self.main_sequence, self.scout_sequence)

    def populate_from_store(self):
        store = self.dialog.store
        super(FramesSection, self).populate_from_store(store )
 
        self.chunk_size_component.field.setValue(store.chunk_size())

        self.custom_range_component.set_active(store.use_custom_range())
        self.custom_range_component.field.setText(store.custom_range())

        self.scout_frames_component.set_active(store.use_scout_frames())
        self.scout_frames_component.field.setText(store.scout_frames())

        self._set_sequences()

    def resolve(self, expander, **kwargs):
        advanced_section = self.dialog.main_tab.section("AdvancedSection")
        template_component = advanced_section.task_template_component
        self._set_sequences()

        tasks = []
        max_tasks = kwargs.get("max_tasks", -1)

        template = template_component.field.text()

        truncate = max_tasks > -1

        chunks = self.main_sequence.chunks()

        context = expander.context

        for i, chunk in enumerate(chunks):
            if truncate and i >= max_tasks:
                break

            task_context = {
                "start": chunk.start,
                "end": chunk.end,
                "step": chunk.step,
                "chunk_length": len(chunk)
            }
            context_copy = context.copy()
            context_copy.update(task_context)
            this_expander = Expander(safe=True, **context_copy)

            tasks.append({
                "command": this_expander.evaluate(template),
                "frames": str(chunk)
            })

        return {
            "tasks_data": tasks,
            "scout_frames": ",".join([str(s) for s in self.scout_sequence or []])
        }


def scene_frame_spec():
    """Get the 3ds_max_frame_range as a spec."""
    frame_range = rt.animationRange
    return "{:d}-{:d}".format(
        int(frame_range.start),
        int(frame_range.end)
    )
