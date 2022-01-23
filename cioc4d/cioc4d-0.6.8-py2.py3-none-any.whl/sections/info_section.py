
import c4d
from cioc4d.sections.collapsible_section import CollapsibleSection
from cioc4d.widgets.text_grp import TextGrp
from cioseq.sequence import Sequence

VALID_KEYS = [ "frame_spec" , "task_count", "frame_count", "scout_frame_spec", "scout_task_count", "scout_frame_count" ]
class InfoSection(CollapsibleSection):
    ORDER = 40

    def __init__(self, dialog):

        self.frame_info_widget = None
        self.scout_info_widget = None

        self.reset_member_vars()

        super(InfoSection, self).__init__(dialog, "Info", collapse=False)

    def reset_member_vars(self):
        self.set_member_vars(
            frame_spec="", 
            task_count=0, 
            frame_count=0,
            scout_frame_spec="",
            scout_task_count=0,
            scout_frame_count=0
        )


    def build(self):

        self.frame_info_widget = TextGrp(
            self.dialog, label="Frame info")

        self.scout_info_widget = TextGrp(
            self.dialog, label="Scout info")

    def on_plugin_message(self, widget_id, msg):
        """
        Update info if something changed in the Frames section.
        """
        frames_section = self.dialog.section("FramesSection")

        if widget_id in frames_section.get_preview_affectors():
            self.calculate_info()

    def on_core_message(self, msg_id, msg):
        """Repopulate if EVMSG_CHANGE was emitted.

        It's possibly a result of frame range edit or loading a new file.
        """
        if msg_id in [c4d.EVMSG_CHANGE]:
            self.calculate_info()

    def calculate_info(self):
        """Build the info strings using data that came from the frames section."""
        frames_section = self.dialog.section("FramesSection")

        self.reset_member_vars()

        try:
            sequence = frames_section.get_sequence()
        except (ValueError, TypeError):
            self.frame_info_widget.set_value("INVALID SEQUENCE")
            self.scout_info_widget.set_value("INVALID SEQUENCE")
            return
        frame_count = len(sequence)
        task_count = sequence.chunk_count()

        frames_info = "frame spec:{} --- task count:{:d} --- frame count:{:d}".format(
            sequence, task_count, frame_count)
        self.set_member_vars(frame_spec=str(sequence), task_count=task_count, frame_count=frame_count)
        scout_info = "No scout tasks. All tasks will start."

        scout_task_count = 0
        try:
            scout_sequence = frames_section.get_scout_sequence(sequence)
        except (ValueError, TypeError):
            scout_sequence = None
        scout_tasks_sequence = None
        if scout_sequence:
            scout_chunks = sequence.intersecting_chunks(scout_sequence)
            if scout_chunks:
                scout_tasks_sequence = Sequence.create(
                    ",".join(str(chunk) for chunk in scout_chunks))
                scout_task_count = len(scout_chunks)

                scout_frame_count =  len(scout_tasks_sequence)
                scout_info = "frame spec:{} --- task count:{:d} --- frame count:{:d}".format(
                    scout_tasks_sequence, scout_task_count, scout_frame_count)

                self.set_member_vars(
                    scout_frame_spec=str(scout_tasks_sequence), 
                    scout_task_count=scout_task_count, 
                    scout_frame_count=scout_frame_count
                )

        self.frame_info_widget.set_value(frames_info)
        self.scout_info_widget.set_value(scout_info)
 
    def set_member_vars(self,**kwargs) :
        for key in kwargs:
            if key not in VALID_KEYS:
                continue
            setattr(self, key,kwargs[key]) 
        

       