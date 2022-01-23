import json
import os

import c4d
from ciocore import data as coredata
from ciocore.validator import ValidationError
from ciopath.gpath import Path
from ciotemplate.expander import Expander

import cioc4d.const as k
from cioc4d import const as k
from cioc4d import submit, validation
from cioc4d.conductor_store import ConductorStore
from cioc4d.foot_grp import FootGroup
from cioc4d.head_grp import HeadGroup

# NOTE: SECTIONS MUST BE IMPORTED, EVEN THOUGH THEY ARE NOT CALLED BY NAME
from cioc4d.sections.assets_section import AssetsSection
from cioc4d.sections.autosave_section import AutosaveSection
from cioc4d.sections.collapsible_section import CollapsibleSection
from cioc4d.sections.diagnostics_section import DiagnosticsSection
from cioc4d.sections.environment_section import EnvironmentSection
from cioc4d.sections.frames_section import FramesSection
from cioc4d.sections.general_section import GeneralSection
from cioc4d.sections.info_section import InfoSection
from cioc4d.sections.location_section import LocationSection
from cioc4d.sections.metadata_section import MetadataSection
from cioc4d.sections.notification_section import NotificationSection
from cioc4d.sections.preview_section import PreviewSection
from cioc4d.sections.retries_section import RetriesSection
from cioc4d.sections.software_section import SoftwareSection
from cioc4d.sections.task_section import TaskSection
from cioc4d.sections.upload_options_section import UploadOptionsSection



class ConductorDialog(c4d.gui.GeDialog):
    """
    A dialog composed of sections of UI.

    In between a header and a footer, the dialog displays all sections inherited
    from CollapsibleSection according to their ORDER property. See
    cioc4d.sections.collapsible_section for inheritance requirements.

    Sections are designed to keep their logic in one place.
    """

    def __init__(self):
        """Initialize the dialog with a list of section classes to be instantiated."""
        self.AddGadget(c4d.DIALOG_NOMENUBAR, 0)
        self.head_grp = None
        self.foot_grp = None
        self.next_id = 20000

        self._section_classes = sorted(CollapsibleSection.__subclasses__(), key=lambda x: x.ORDER)

        self.sections = []
        self.store = None

        coredata.init(product="cinema4d")

    # c4d method

    def add_separator(self):
        """
        AddSeparatorH function signature changed S23 -> S24
        """
        try:
            self.AddSeparatorH(inith=0)
        except BaseException:
            self.AddSeparatorH(initw=0,  flags=c4d.BFH_FIT)

    def CreateLayout(self):
        """
        Called by c4d to build the layout.

        We instantiate all collapsible sections, and put all except the preview
        section in a scroll layout. They are passed a reference to this dialog
        so they may register widgets and so on.
        """
        self.sections = []
        self.SetTitle("Conductor Render")
        self.head_grp = HeadGroup(self)
        self.add_separator()
        scroll_grp = self.ScrollGroupBegin(
            id=self.register(),
            flags=c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT,
            scrollflags=c4d.SCROLLGROUP_VERT,
        )
        if scroll_grp:
            main_grp = self.GroupBegin(
                id=self.register(),
                flags=c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT,
                title="",
                rows=1,
                cols=1,
                groupflags=0,
            )

            if main_grp:
                self.GroupBorderSpace(4, 4, 4, 4)
                self.sections = [
                    cls(self) for cls in self._section_classes if cls.__name__ != "PreviewSection"
                ]
            self.GroupEnd()  # manin
        self.GroupEnd()  # scroll

        self.add_separator()

        self.sections.append(PreviewSection(self))

        self.add_separator()

        self.foot_grp = FootGroup(self)

        return True

    # c4d method
    def InitValues(self):
        """Call each section's populate_from_store method."""
        self.store = ConductorStore()
        self.populate_all_sections()
        if coredata.valid():
            self.foot_grp.enable_submit(True)

        return True

    # c4d method
    def Command(self, widget_id, msg):
        """

        Receive all events from this plugin.

        Tell the preview section the list of affectors that can influence it.
        This must be the first step in this Command callback because some
        on_plugin_message() functions may delete widgets, meaning those
        widget_ids won't be available to query later by
        PreviewSection::on_plugin_message().

              2.It could be optimized to only care about dynamic widgets!!
        if widget_id == self.foot_grp.save_button_id:
            self.save_to_store()
            return
        """
        if widget_id == self.foot_grp.submit_button_id:
            self.on_submit()
            return True
        if widget_id == self.foot_grp.validate_button_id:
            self.on_validate()
            return True

        for section in self.sections:
            section.set_store_affectors()

        self.section("PreviewSection").set_affectors()

        if widget_id == self.foot_grp.connect_button_id:
            self.on_connect()

        if widget_id == self.foot_grp.reset_button_id:
            self.on_reset()

        # Let all sections know about the event
        for section in self.sections:
            section.on_plugin_message(widget_id, msg)

        return True

    # c4d method
    def CoreMessage(self, msg_id, msg):
        """
        All the sections receive all EVMSG_CHANGE events from c4d and they decide what to do with them.
        """

        if msg_id == c4d.EVMSG_CHANGE:

            document_was_changed = self.store.on_scene_change()

            if document_was_changed:

                self.populate_all_sections()

            for section in self.sections:
                section.on_core_message(msg_id, msg)

        return super(ConductorDialog, self).CoreMessage(msg_id, msg)

    # c4d method
    def Message(self, msg, result):
        """
        All the sections receive mouse events from c4d and they decide what to do with them.
        """
        should_handle_ids = [c4d.BFM_INPUT]
        msg_id = msg.GetId()
        if msg_id in should_handle_ids:
            for section in self.sections:
                section.on_message(msg_id, msg)

        return super(ConductorDialog, self).Message(msg, result)

    # c4d method
    def AskClose(self):
        return False

    def section(self, classname):
        """
        Convenience to allow sections to find other sections by name.

        See how the InfoSection finds the FramesSection so it can call it's methods.
        """
        return next(s for s in self.sections if s.__class__.__name__ == classname)

    def register(self):
        """
        Register a UI Element and keep track of the next available ID.

        This, in conjunction with the object oriented structure, avoids the
        tedious job of tracking explicit IDs.
        """
        current_id = self.next_id
        self.next_id += 1
        return current_id

    def calculate_submission(self, **kwargs):
        """
        Ask each section to contribute to the submission object.
        """

        context = self.get_context()
        expander = Expander(safe=True, **context)
        submission = {}

        for section in self.sections:
            submission.update(section.resolve(expander, **kwargs))

        return submission

    def get_context(self):
        doc = c4d.documents.GetActiveDocument()
        docname = doc.GetDocumentName()
        docnamex, ext = os.path.splitext(doc.GetDocumentName())
        docdir = doc.GetDocumentPath()
        if docdir:
            docdir = Path(docdir).fslash(with_drive=False)
        docfile = Path(os.path.join(docdir, docname)).fslash(with_drive=False)
        try:
            takename = doc.GetTakeData().GetCurrentTake().GetName()
        except AttributeError:
            takename = "Main"
        result = {
            "docname": docname,
            "docnamex": docnamex,
            "docext": ext,
            "docdir": docdir,
            "docfile": docfile,
            "takename": takename,
        }
        return result

    def populate_all_sections(self):
        for section in self.sections:
            section.populate_from_store()
        self.section("InfoSection").calculate_info()
        self.section("PreviewSection").set_submission_preview()

    def on_connect(self):

        use_fixtures = self.section("DiagnosticsSection").fixture_widget.get_value()
        fixtures_dir = k.FIXTURES_DIR if use_fixtures else None
        coredata.set_fixtures_dir(fixtures_dir)
        try:
            coredata.data(force=True)
            self.foot_grp.enable_submit(True)
            return
        except BaseException:
            c4d.WriteConsole(
                "Try again after deleting your credentials file (~/.config/conductor/credentials)\n"
            )
            raise
   
    def on_reset(self):
        self.store.reset()
        self.store.commit()
        self.populate_all_sections()

    def on_submit(self):
        submit.submit(self)

    def on_validate(self):
        try:
            validation.run(self, submitting=False)
        except ValidationError as ex:
            c4d.WriteConsole(str(ex))
            c4d.WriteConsole("\n")
