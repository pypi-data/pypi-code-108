
import re

import c4d
from cioc4d.sections.collapsible_section import CollapsibleSection
from cioc4d.widgets.hidable_text_field_grp import HidableTextFieldGrp
from cioc4d.widgets.int_field_grp import IntFieldGrp
from cioseq.sequence import Sequence
 
class FramesSection(CollapsibleSection):
    ORDER = 30

    def __init__(self, dialog):

        self.chunk_size_widget = None
        self.custom_range_widget = None
        self.scout_frames_widget = None

        super(FramesSection, self).__init__(dialog, "Frames", collapse=False)

    def build(self):

        self.chunk_size_widget = IntFieldGrp(self.dialog, "Chunk Size")

        self.custom_range_widget = HidableTextFieldGrp(
            self.dialog, "Use Custom Range",
            placeholder="e.g. 1-50x2")

        self.scout_frames_widget = HidableTextFieldGrp(
            self.dialog, "Use Scout Frames",
            placeholder="e.g. auto:3")

    def populate_from_store(self):
        store = self.dialog.store
        self.chunk_size_widget.set_value(store.chunk_size())
        self.custom_range_widget.set_value(store.custom_range())
        self.custom_range_widget.set_visible(store.use_custom_range())
        self.scout_frames_widget.set_value(store.scout_frames())
        self.scout_frames_widget.set_visible(store.use_scout_frames())

    def save_to_store(self):
        store = self.dialog.store
        store.set_chunk_size(self.chunk_size_widget.get_value())
        store.set_custom_range(self.custom_range_widget.get_value())
        store.set_use_custom_range(self.custom_range_widget.get_visible() )
        store.set_scout_frames(self.scout_frames_widget.get_value())
        store.set_use_scout_frames(self.scout_frames_widget.get_visible() )
        store.commit()

    def on_plugin_message(self, widget_id, msg):

        if widget_id == self.chunk_size_widget.int_field_id:
            self.sanitize_chunk_size()
        elif widget_id == self.custom_range_widget.checkbox_id:
            self.custom_range_widget.set_visible()

        elif widget_id == self.scout_frames_widget.checkbox_id:
            self.scout_frames_widget.set_visible()

        if widget_id in self._store_affectors:
            self.save_to_store()

    def sanitize_chunk_size(self):
        if self.chunk_size_widget.get_value() < 1:
            self.chunk_size_widget.set_value(1)

    def get_sequence(self):
        """Get a sequence object that represents the c4d frame range.

        If overridden with a custon range, get that instead.
        """
        chunk_size = self.chunk_size_widget.get_value()
        use_custom_range = self.custom_range_widget.get_visible()
        if use_custom_range:
            custom_range = self.custom_range_widget.get_value()
            return Sequence.create(custom_range, chunk_size=chunk_size, chunk_strategy="progressions")

        document = c4d.documents.GetActiveDocument()
        render_data = document.GetActiveRenderData()
        fps = document.GetFps()
        start_frame = render_data[c4d.RDATA_FRAMEFROM].GetFrame(fps)
        end_frame = render_data[c4d.RDATA_FRAMETO].GetFrame(fps)
        frame_step = render_data[c4d.RDATA_FRAMESTEP]

        return Sequence.create(start_frame, end_frame, frame_step, chunk_size=chunk_size, chunk_strategy="progressions")

    def get_scout_sequence(self, main_sequence):
        """Get a sequence object that represents scout frames if enabled."""
        use_scout_frames = self.scout_frames_widget.get_visible()
        if not use_scout_frames:
            return
        scout_frames = self.scout_frames_widget.get_value()

        match = re.compile(r"^auto[, :]+(\d+)$").match(scout_frames)
        if match:
            num_samples = int(match.group(1))
            return main_sequence.subsample(num_samples)

        try:
            return Sequence.create(scout_frames)
        except (ValueError, TypeError):
            return

    def get_preview_affectors(self):
        return [
            self.chunk_size_widget.int_field_id,
            self.custom_range_widget.checkbox_id,
            self.custom_range_widget.text_field_id,
            self.scout_frames_widget.checkbox_id,
            self.scout_frames_widget.text_field_id,
        ]
 