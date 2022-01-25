

from PySide2 import QtWidgets, QtGui
from cioseq.sequence import Sequence
from ciomax.sections.collapsible_section import CollapsibleSection
from ciomax.components.text_field_grp import TextFieldGrp


class InfoSection(CollapsibleSection):
    ORDER = 40

    def __init__(self, dialog):
        super(InfoSection, self).__init__(dialog, "Info" )

        self.frame_info_component = TextFieldGrp(
            label="Frame info")
        self.scout_info_component = TextFieldGrp(
            label="Scout info")

        self.frame_info_component.field.setEnabled(False)
        self.scout_info_component.field.setEnabled(False)

        self.content_layout.addWidget(self.frame_info_component)
        self.content_layout.addWidget(self.scout_info_component)

    def update(self, main_sequence, scout_sequence):

        if not main_sequence:
            self.frame_info_component.field.setText("INVALID SEQUENCE")
            self.scout_info_component.field.setText("INVALID SEQUENCE")
            return

        frame_count = len(main_sequence)
        task_count = main_sequence.chunk_count()

        frames_info = "spec:{} --- tasks:{:d} --- frames:{:d}".format(
            main_sequence, task_count, frame_count)

        scout_info = "No scout tasks. All tasks will start."

        scout_task_count = 0

        scout_tasks_sequence = None
        if scout_sequence:
            scout_chunks = main_sequence.intersecting_chunks(scout_sequence)
            if scout_chunks:
                scout_tasks_sequence = Sequence.create(
                    ",".join(str(chunk) for chunk in scout_chunks))
                scout_task_count = len(scout_chunks)
                scout_frame_count = len(scout_tasks_sequence)
                scout_info = "spec:{} --- tasks:{:d} --- frames:{:d}".format(
                    scout_tasks_sequence, scout_task_count, scout_frame_count)

        self.frame_info_component.field.setText(frames_info)
        self.scout_info_component.field.setText(scout_info)


    def populate(self, frame_info, scout_info):
        self.frame_info_component.field.setText(frame_info)
        self.scout_info_component.field.setText(scout_info)

    def populate_from_store(self):
        store = self.dialog.store
        super(InfoSection, self).populate_from_store(store )