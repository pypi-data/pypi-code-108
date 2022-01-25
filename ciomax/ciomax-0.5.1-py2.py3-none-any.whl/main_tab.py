import os
from PySide2 import QtWidgets, QtCore, QtGui
from ciotemplate.expander import Expander
from ciomax.sections.collapsible_section import CollapsibleSection

# Import for introspection
from ciomax.sections.general_section import GeneralSection
from ciomax.sections.software_section import SoftwareSection
from ciomax.sections.frames_section import FramesSection
from ciomax.sections.info_section import InfoSection
from ciomax.sections.environment_section import EnvironmentSection
from ciomax.sections.metadata_section import MetadataSection
from ciomax.sections.extra_assets_section import ExtraAssetsSection
from ciomax.sections.advanced_section import AdvancedSection

from ciomax.components.buttoned_scroll_panel import ButtonedScrollPanel

from ciomax import submit

from ciopath.gpath import Path
from ciocore import data as coredata
from ciomax import const as k

FIXTURES_DIR = os.path.expanduser(os.path.join("~", "conductor_fixtures"))


class MainTab(ButtonedScrollPanel):
    """
    Build the tab that contains the main configuration sections.

    Also initalize core data and render scope
    coredata (projects, inst_types, software) is a singleton. We don't create it
    with force=True because it may be populated already. Fetching is expensive.

    render_scope is based on the renderer selected in render settings.
    """

    def __init__(self, dialog):
        super(MainTab, self).__init__(
            dialog,
            buttons=[
                ("close", "Close"),
                ("reconnect", "Reconnect"),
                ("reset", "Reset UI"),
                ("submit", "Validate and Submit"),
            ],
        )

        coredata.init(product="all")

        coredata.set_fixtures_dir(FIXTURES_DIR if self.dialog.store.use_fixtures() else "")
        coredata.data()

        self.dialog.set_render_scope()

        self._section_classes = sorted(CollapsibleSection.__subclasses__(), key=lambda x: x.ORDER)
        self.sections = [cls(self.dialog) for cls in self._section_classes]

        for section in self.sections:
            self.layout.addWidget(section)

        self.layout.addStretch()
        self.configure_signals()

    def populate_from_store(self):
        """
        Fetch the values that were stored when the previous session closed.

        Values were stored in a dummy object called ConductorStore. If it
        doesn't exist, ity is created with defaults when the class is accessed.
        """
        for section in self.sections:
            section.populate_from_store()

    def configure_signals(self):
        self.buttons["close"].clicked.connect(self.dialog.close)
        self.buttons["submit"].clicked.connect(self.on_submit_button)
        self.buttons["reset"].clicked.connect(self.on_reset_button)
        self.buttons["reconnect"].clicked.connect(self.on_reconnect_button)

    def on_submit_button(self):
        submit.submit(self.dialog)

    def on_reset_button(self):
        store = self.dialog.store
        store.reset()
        self.populate_from_store()

    def on_reconnect_button(self):
        store = self.dialog.store

        coredata.set_fixtures_dir(FIXTURES_DIR if store.use_fixtures() else "")
        coredata.data(force=True)

        self.dialog.set_render_scope()

        # remember the previous values as we will try to reset them
        project = store.project()
        instance_type = store.instance_type()
        full_renderer_version = store.renderer_version()
        partial_renderer_version = full_renderer_version.split("/")[-1]

        general_section = self.section("GeneralSection")
        software_section = self.section("SoftwareSection")

        general_section.set_project_model()
        general_section.set_instance_type_model()
        software_section.configure_combo_box()

        # Attempt to set remembered values.
        general_section.project_component.set_by_text(project)
        general_section.instance_type_component.set_by_text(instance_type, column=1)
        software_section.component.set_by_text(partial_renderer_version)

    def section(self, classname):
        """
        Convenience to find sections by name.

        Makes it easier to allow sections to talk to each other.
        Example: Calculate info from stuff in the frames section
            self.section("InfoSection").calculate(self.section("FramesSection"))

        """

        return next(s for s in self.sections if s.__class__.__name__ == classname)

    def resolve(self, context, **kwargs):
        """
        Resolve the submission object based on the values in the UI.

        kwargs may contain "preview_only", which indicates that this is not a full submission.
        "preview_only" tells the presubmit script that we don't want to write any files to disk. We
        just want the payload amendments: assets, variables, etc.

        We pass along the amendments to each section's resolve method so it may handle merging the
        appropriate fields.
        """
        advanced_section = self.section("AdvancedSection")
        amendments = advanced_section.run_presubmit_script(
            context, amendments_only=kwargs.get("preview_only", False)
        )

        submission = {}
        expander = Expander(safe=True, **context)
        for section in self.sections:
            submission.update(section.resolve(expander, amendments=amendments))
        return submission
