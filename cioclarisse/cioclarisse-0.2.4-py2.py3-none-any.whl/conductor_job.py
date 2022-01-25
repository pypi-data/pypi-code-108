"""
Defines ConductorJob scripted class plugin. This file is the view layer.
"""
import os
import traceback

import ix

try:
    from importlib import reload 
except ImportError:
    import reload
    

# from ix import api

# from ix.api import OfAttr

from cioclarisse.utils import ConductorError
from cioclarisse import reloader
from cioclarisse import const as k
from cioclarisse import (
    attr_docs,
    debug_ui,
    environment_ui,
    extra_uploads_ui,
    frames_ui,
    notifications_ui,
    projects_ui,
    refresh,
    submit_actions,
    upload_ui

)
from ciocore import loggeria

DEFAULT_CMD_TEMPLATE = "<temp_dir>/ciocnode <render_package> "
DEFAULT_CMD_TEMPLATE += "-image <sources> -image_frames_list <chunks> "
DEFAULT_CMD_TEMPLATE += "-tile_rendering <tiles> <tile_number> "
DEFAULT_CMD_TEMPLATE += "-license_server conductor_ilise:40500"

DEFAULT_TITLE = "My Clarisse Job"


class ConductorJob(ix.api.ModuleScriptedClassEngine):
    """
    Defines the engine that creates a ConductorJob ScriptedClass Item.
    """

    def __init__(self):
        ix.api.ModuleScriptedClassEngine.__init__(self)

    def on_action(self, action, obj, data):
        """
        Handles any button press in the Attribute Editor.

        Args:
            action (str): Name of the action is a nice version of the button label.
            obj (ConductorJob): The scripted class instance.
            data (dict): Extra information about the event
        """
        action_name = action.get_name()
        verbose_errors = obj.get_attribute("show_tracebacks").get_bool()

        # We need to wrap everything in a try/except because Clarisse
        # crashes if an exception is thrown from a scripted class. See
        # https://www.isotropix.com/user/bugtracker/363 .
        try:
            if action_name == "manage_extra_uploads":
                extra_uploads_ui.build(obj, data)
            elif action_name == "manage_extra_environment":
                environment_ui.build(obj, data)
            elif action_name == "preview":
                refresh.refresh(obj)
                submit_actions.preview(obj, data)
            elif action_name == "write_render_package":
                refresh.refresh(obj)
                submit_actions.write_render_package(obj)
            elif action_name == "submit":
                refresh.refresh(obj)
                submit_actions.submit(obj, data)
            elif action_name == "connect":
                refresh.refresh(obj, force=True)
            elif action_name == "reload":
                reload(reloader)
            else:
                pass
        except (BaseException, ValueError, AttributeError, ConductorError) as ex:
            if verbose_errors:
                ix.log_error(traceback.format_exc())
            else:
                ix.log_error(str(ex))

    def on_attribute_change(self, obj, attr, *_):
        """
        Handles attributes changing value.

        Args:
            obj (ConductorJob): The scripted class instance.
            attr (OfAttr): The attribute that changed.
        """

        attr_name = attr.get_name()
        verbose_errors = obj.get_attribute("show_tracebacks").get_bool()
        try:
            if attr_name == "conductor_project_name":
                projects_ui.handle_project(obj, attr)
            elif attr_name == "use_custom_frames":
                frames_ui.handle_use_custom_frames(obj, attr)
            elif attr_name == "use_scout_frames":
                frames_ui.handle_use_scout_frames(obj, attr)
            elif attr_name == "custom_frames":
                frames_ui.handle_custom_frames(obj, attr)
            elif attr_name == "scout_frames":
                frames_ui.handle_scout_frames(obj, attr)
            elif attr_name == "chunk_size":
                frames_ui.handle_chunk_size(obj, attr)
            elif attr_name == "images_and_layers":
                frames_ui.handle_images(obj, attr)
            elif attr_name == "notify":
                notifications_ui.notify_changed(obj, attr)
            elif attr_name == "email_addresses":
                notifications_ui.handle_email_addresses(obj, attr)
            elif attr_name == "conductor_log_level":
                debug_ui.handle_log_level(obj, attr)
            elif attr_name == "local_upload":
                upload_ui.handle_local_upload(obj, attr)
            else:
                pass
        except (BaseException, ValueError, AttributeError, ConductorError) as ex:
            if verbose_errors:
                ix.log_error(traceback.format_exc())
            else:
                ix.log_error(str(ex))

    def declare_attributes(self, s_class):
        """
        Declares all attributes and actions.

        Args:
            s_class (ScriptedClass):  The scripted class.
        """
        self.declare_actions(s_class)
        self.declare_general_attributes(s_class)
        self.declare_frames_attributes(s_class)
        self.declare_machines_attributes(s_class)
        self.declare_upload_attributes(s_class)
        self.declare_environment_attributes(s_class)
        self.declare_task_attributes(s_class)
        self.declare_packaging_attributes(s_class)
        self.declare_notification_attributes(s_class)
        self.declare_dev_attributes(s_class)

        attr_docs.set_docs(s_class)

    def declare_dev_attributes(self, s_class):
        """
        Declares developer attributes.

        Sets up log level and traceback behaviour. Also provides a reload button
        for Conductor devs by setting an env var.

        Args:
            s_class (ScriptedClass):  The scripted class.
        """
        dev_visible = os.environ.get("CONDUCTOR_MODE") == "dev"

        if dev_visible:
            self.add_action(s_class, "reload", "development")
        self.add_action(s_class, "write_render_package", "debug")

        attr = s_class.add_attribute(
            "conductor_log_level",
            ix.api.OfAttr.TYPE_LONG,
            ix.api.OfAttr.CONTAINER_SINGLE,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "debug",
        )
        attr.set_long(1)
        for i, level in enumerate(loggeria.LEVELS):
            attr.add_preset(level, str(i))

        attr = s_class.add_attribute(
            "show_tracebacks",
            ix.api.OfAttr.TYPE_BOOL,
            ix.api.OfAttr.CONTAINER_SINGLE,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "debug",
        )
        attr.set_bool(False)

    def declare_packaging_attributes(self, s_class):
        """
        Declares render package attributes.

        Render package is simply a project file that may have been manipulated
        in preparation for the render.

        localize_contexts: Like Maya's import references. Useful if renders fail
        due to the complexity of dispatching nested references.


        clean_up_render_package: Remove the render package after submission.

        Args:
            s_class (ScriptedClass):  The scripted class.
        """

        attr = s_class.add_attribute(
            "clean_up_render_package",
            ix.api.OfAttr.TYPE_BOOL,
            ix.api.OfAttr.CONTAINER_SINGLE,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "packaging",
        )
        attr.set_bool(True)

    def declare_actions(self, s_class):
        """
        Creates connect, preview, and submit buttons.

        Args:
            s_class (ScriptedClass):  The scripted class.
        """
        self.add_action(s_class, "connect", "actions")
        # self.add_action(s_class, "validate", "actions")
        self.add_action(s_class, "preview", "actions")
        self.add_action(s_class, "submit", "actions")

    def declare_general_attributes(self, s_class):
        """
        Creates commonly accessed attributes.

        Job title, project, and images to be rendered.

        Args:
            s_class (ScriptedClass):  The scripted class.
        """
        attr = s_class.add_attribute(
            "title",
            ix.api.OfAttr.TYPE_STRING,
            ix.api.OfAttr.CONTAINER_SINGLE,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "general",
        )
        attr.set_string(DEFAULT_TITLE)

        attr = s_class.add_attribute(
            "images_and_layers",
            ix.api.OfAttr.TYPE_REFERENCE,
            ix.api.OfAttr.CONTAINER_LIST,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "general",
        )
        filters = ix.api.CoreStringVector(0)
        filters.add("Layer")
        filters.add("Image")
        attr.set_object_filters(filters)

        attr = s_class.add_attribute(
            "conductor_project_name",
            ix.api.OfAttr.TYPE_LONG,
            ix.api.OfAttr.CONTAINER_SINGLE,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "general",
        )
        attr.set_long(0)
        attr.add_preset(k.NOT_CONNECTED,  "0")

        attr = s_class.add_attribute(
            "last_project",
            ix.api.OfAttr.TYPE_STRING,
            ix.api.OfAttr.CONTAINER_SINGLE,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "general",
        )
        attr.set_hidden(True)

        attr = s_class.add_attribute(
            "clarisse_version",
            ix.api.OfAttr.TYPE_LONG,
            ix.api.OfAttr.CONTAINER_SINGLE,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "general",
        )
        attr.set_long(0)

    def declare_frames_attributes(self, s_class):
        """
        Creates attributes related to the frame range.

        Args:
            s_class (ScriptedClass):  The scripted class.
        """

        attr = s_class.add_attribute(
            "use_custom_frames",
            ix.api.OfAttr.TYPE_BOOL,
            ix.api.OfAttr.CONTAINER_SINGLE,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "frames",
        )
        attr.set_bool(False)

        attr = s_class.add_attribute(
            "custom_frames",
            ix.api.OfAttr.TYPE_STRING,
            ix.api.OfAttr.CONTAINER_SINGLE,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "frames",
        )
        attr.set_hidden(True)
        attr.set_string("2,4-8,10-50x2")

        attr = s_class.add_attribute(
            "chunk_size",
            ix.api.OfAttr.TYPE_LONG,
            ix.api.OfAttr.CONTAINER_SINGLE,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "frames",
        )
        attr.set_long(5)
        attr.set_numeric_range_min(1)

        attr = s_class.add_attribute(
            "use_scout_frames",
            ix.api.OfAttr.TYPE_BOOL,
            ix.api.OfAttr.CONTAINER_SINGLE,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "frames",
        )
        attr.set_bool(False)

        attr = s_class.add_attribute(
            "scout_frames",
            ix.api.OfAttr.TYPE_STRING,
            ix.api.OfAttr.CONTAINER_SINGLE,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "frames",
        )
        attr.set_hidden(True)
        attr.set_string("2,4-8,10-50x2")

        attr = s_class.add_attribute(
            "tiles",
            ix.api.OfAttr.TYPE_LONG,
            ix.api.OfAttr.CONTAINER_SINGLE,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "frames",
        )
        attr.set_long(1)
        for i in range(1, 11):
            [attr.add_preset("{}x{}={}".format(i, i, i * i), str(i))]

        attr = s_class.add_attribute(
            "frames_info",
            ix.api.OfAttr.TYPE_STRING,
            ix.api.OfAttr.CONTAINER_SINGLE,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "frames",
        )
        attr.set_read_only(True)
        attr.set_string("- Please click connect -")

    def declare_machines_attributes(self, s_class):
        """
        Creates attributes to define the render node spec.

        Args:
            s_class (ScriptedClass):  The scripted class.
        """
        attr = s_class.add_attribute(
            "preemptible",
            ix.api.OfAttr.TYPE_BOOL,
            ix.api.OfAttr.CONTAINER_SINGLE,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "machines",
        )
        attr.set_bool(True)

        attr = s_class.add_attribute(
            "instance_type",
            ix.api.OfAttr.TYPE_LONG,
            ix.api.OfAttr.CONTAINER_SINGLE,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "machines",
        )
        attr.set_long(0)
        attr.add_preset(k.NOT_CONNECTED,  "0")

        attr = s_class.add_attribute(
            "retries",
            ix.api.OfAttr.TYPE_LONG,
            ix.api.OfAttr.CONTAINER_SINGLE,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "machines",
        )
        attr.set_long(3)

        attr = s_class.add_attribute(
            "last_instance_type",
            ix.api.OfAttr.TYPE_STRING,
            ix.api.OfAttr.CONTAINER_SINGLE,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "machines",
        )
        attr.set_hidden(True)

    def declare_upload_attributes(self, s_class):
        """
        Creates attributes to specify options for dependency scanning.

        No-scan: use only cached uploads.

        Glob-scan: If filenames contain "##" or <UDIM>. They will be globbed.

        Smart-scan If filenames contain "##" or $<?>F the hashes will be
        replaced with frame numbers that are being used.

        Args:
            s_class (ScriptedClass):  The scripted class.
        """

        attr = s_class.add_attribute(
            "local_upload",
            ix.api.OfAttr.TYPE_BOOL,
            ix.api.OfAttr.CONTAINER_SINGLE,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "upload",
        )
        attr.set_bool(True)

        attr = s_class.add_attribute(
            "upload_only",
            ix.api.OfAttr.TYPE_BOOL,
            ix.api.OfAttr.CONTAINER_SINGLE,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "upload",
        )
        attr.set_bool(False)

        self.add_action(s_class, "manage_extra_uploads", "upload")

        attr = s_class.add_attribute(
            "extra_uploads",
            ix.api.OfAttr.TYPE_STRING,
            ix.api.OfAttr.CONTAINER_LIST,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "cached_upload_list",
        )
        attr.set_read_only(True)

    def declare_task_attributes(self, s_class):
        """
        Creates task command template.

        By default it contain tokens that will be replaced while
        generating tasks.

        Args:
            s_class (ScriptedClass):  The scripted class.
        """
        attr = s_class.add_attribute(
            "task_template",
            ix.api.OfAttr.TYPE_STRING,
            ix.api.OfAttr.CONTAINER_SINGLE,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "task",
        )
        attr.set_string(DEFAULT_CMD_TEMPLATE)

    def declare_environment_attributes(self, s_class):
        """
        Sets up any extra environment.

        Vars set here will be merged with the package environments.

        Args:
            s_class (ScriptedClass):  The scripted class.
        """
        self.add_action(s_class, "manage_extra_environment", "environment")

        attr = s_class.add_attribute(
            "extra_environment",
            ix.api.OfAttr.TYPE_STRING,
            ix.api.OfAttr.CONTAINER_LIST,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "environment",
        )
        attr.set_read_only(True)

    def declare_notification_attributes(self, s_class):
        """
        Sets email addresses to be notified on job completion.

        Args:
            s_class (ScriptedClass):  The scripted class.
        """
        attr = s_class.add_attribute(
            "notify",
            ix.api.OfAttr.TYPE_BOOL,
            ix.api.OfAttr.CONTAINER_SINGLE,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "notifications",
        )
        attr.set_bool(False)

        attr = s_class.add_attribute(
            "email_addresses",
            ix.api.OfAttr.TYPE_STRING,
            ix.api.OfAttr.CONTAINER_SINGLE,
            ix.api.OfAttr.VISUAL_HINT_DEFAULT,
            "notifications",
        )
        attr.set_read_only(True)
