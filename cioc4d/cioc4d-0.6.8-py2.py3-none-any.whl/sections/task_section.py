import c4d
import os
import re
from ciopath.gpath_list import PathList
from ciopath.gpath import Path
from cioc4d.widgets.hidable_text_field_grp import HidableTextFieldGrp
from cioc4d.widgets.text_field_grp import TextFieldGrp
from cioc4d.conductor_store import DEFAULT_TASK_TEMPLATE
from cioc4d.widgets.checkbox_grp import CheckboxGrp
from cioc4d.sections.collapsible_section import CollapsibleSection
from cioc4d import utils

RX_DOLLAR_VAR = re.compile(r"\$([a-z]+)")
UNRESOLVED = "UNRESOLVED"


class TaskSection(CollapsibleSection):
    """
    The task section consists of an override for the task and output path.

    It allows the advanced user to enter custom render commands. If they do so,
    then they could set custom output images with the oimage flag, and for this
    reason it must be their responsibility to specify the writable destination
    (output_path). As such, the two fields are either both active or both inactive.

    In the case they are inactive, the command is resolved based on the values
    we find in render settings.
    """

    ORDER = 50

    def __init__(self, dialog):
        self.widget = None
        self.destination_widget = None
        super(TaskSection, self).__init__(dialog, "Task Template", collapse=True)

    def build(self):
        """Creates the two widgets."""

        self.override_widget = CheckboxGrp(self.dialog, "Override Templates")
        self.widget = TextFieldGrp(self.dialog, label="Task Template")
        self.destination_widget = TextFieldGrp(self.dialog, label="Destination")

    def populate_from_store(self):
        """See CollapsibleSection::populate_from_store"""
        store = self.dialog.store
        visible = store.override_task_template()

        self.override_widget.set_value(visible)

        self.widget.set_value(store.task_template())
        self.widget.set_visible(visible)

        self.destination_widget.set_value(store.destination())
        self.destination_widget.set_visible(visible)

    def save_to_store(self):
        """See CollapsibleSection::save_to_store"""
        store = self.dialog.store
        store.set_task_template(self.widget.get_value())
        store.set_override_task_template(self.override_widget.get_value())
        store.set_destination(self.destination_widget.get_value())

        store.commit()

    def get_preview_affectors(self):
        """See CollapsibleSection::get_preview_affectors"""
        return [
            self.widget.text_field_id,
            self.override_widget.checkbox_id,
            self.destination_widget.text_field_id,
        ]

    def on_plugin_message(self, widget_id, msg):
        """See CollapsibleSection::on_plugin_message"""
        if widget_id == self.override_widget.checkbox_id:

            visible = self.override_widget.get_value()

            self.widget.set_visible(visible)
            self.destination_widget.set_visible(visible)

        if widget_id in self._store_affectors:
            self.save_to_store()

    def resolve(self, expander, **kwargs):
        """
        Resolve tasks_data, scout_frames,  and the output_path.

        expander is a template replacement object. kwargs is not used.

        Pull sequence info from the frames section and combine it with the template.

        If the widget is visible, then we are in custom mode, otherwise we autogenerate everything.


        NOTE: Sequence spec can be invalid as you type. 1-10 is valid, but 1- is not. Those events
        cause this function to update, therefore we catch the errors and add an INVALID entry in the
        resolved submission object.
        """
        if self.override_widget.get_value():
            dest_path = self.get_custom_destination()
            template = self.widget.get_value()
        else:
            dest_path = utils.get_common_render_output_destination()
            if not dest_path:
                c4d.WriteConsole(
                    "[Conductor] Can't resolve output image paths. Please check render settings.\n"
                )
                dest_path = ""
            template = DEFAULT_TASK_TEMPLATE
        result = {"output_path": dest_path}

        frames_section = self.dialog.section("FramesSection")

        try:
            main_sequence = frames_section.get_sequence()
            scout_sequence = frames_section.get_scout_sequence(main_sequence)
        except (ValueError, TypeError):
            return {
                "tasks_data": "INVALID SEQUENCE - Check frames section! Enter a valid frame-spec such as: 1-10 or 1-10x2 or 1,3,5-10",
            }

        result.update(self._resolve_tasks(template, main_sequence, scout_sequence))

        return result

    def _resolve_tasks(self, template, main_sequence, scout_sequence):
        """
        Create the tasks and scout frame definition.

        Returns an object that can be merged into the submission.
        """
        tasks = []
        chunks = main_sequence.chunks()

        try:
            template = c4d.modules.tokensystem.StringConvertTokens(template, utils.rpd())
        except SystemError:
            pass

        doc = c4d.documents.GetActiveDocument()

        ciodoc = os.path.join(doc.GetDocumentPath(), doc.GetDocumentName())
        if ciodoc:
            ciodoc = Path(ciodoc).fslash(with_drive=False)
        else:
            ciodoc = "UNTITLED"

        for chunk in chunks:
            context = {
                "ciostart": str(chunk.start),
                "cioend": str(chunk.end),
                "ciostep": str(chunk.step),
                "ciodoc": ciodoc,
            }

            tasks.append({"command": _expand_dollar_vars(template, context), "frames": str(chunk)})

        return {
            "tasks_data": tasks,
            "scout_frames": ",".join([str(s) for s in scout_sequence or []]),
        }

    def get_custom_destination(self):
        """Get the destination from the field.

        The string can be treated as a template and resolve the context.
        """

        dest_path = self.destination_widget.get_value()
        if not dest_path:
            c4d.WriteConsole(
                "No destination folder. If you override the task template, you must manually provide a common destination folder.\n"
            )
            return ""

        try:
            dest_path = c4d.modules.tokensystem.FilenameConvertTokens(dest_path, utils.rpd())
        except SystemError:
            dest_path = ""

        if not dest_path:
            c4d.WriteConsole(
                "No destination folder after token replacemnent. If you override the task template, you must manually provide a valid destination folder.\n"
            )
            return ""

        if Path(dest_path).relative:
            doc = c4d.documents.GetActiveDocument()
            docdir = doc.GetDocumentPath()
            if not docdir:
                c4d.WriteConsole(
                    "Can't determine document location and the custom destination path is relative. Maybe you didn't save the document yet?.\n"
                )
                return ""
            dest_path = os.path.join(docdir, dest_path)

        return Path(dest_path).fslash()


# TODO: Figure out how to register c4d tokens. Then remove this
def _expand_dollar_vars(path, context):
    """
    Replace $ variables in strings.

    Some $vars are not handled by c4d token system, so we deal with them here.
    """
    result = path
    if context:
        for match in RX_DOLLAR_VAR.finditer(path):
            key = match.group(1)
            replacement = context.get(key)
            if replacement is not None:
                result = result.replace("${}".format(key), replacement)
    return result
