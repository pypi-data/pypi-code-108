"""
Encapsulation of a c4d container.

The purpose of the store is to make it possible to persist the state of the
dialog (settings) in the scene file. 

It is NOT the single source of truth while dialog is open. The widgets are.

So the flow is:

Starting from a new scene or loaded scene or maybe dialog is open already as
part of saved layout.
- User opens dialog:
- Check if scene has an instance of the conductor_container.
- If not, make one and reset it to factory defaults.
- If it does have one, populate the UI from it.

If dialog open and user loads a scene, then a EV MSG CHANGE event will fire, so
we want to repopulate the UI with the new container (if the loaded scene has
one).

Problem is, the same event fires in many situations. So in order to determine
whether the scene really did change, we maintain a MODIFIED timestamp on the
store object, AND in the container. MODIFIED is updated when we commit a change.
Each time the event fires we compare those timestamps. In theory, the only time
they will be different is when a new scene is loaded.

"""
import c4d
import os
import json
import cioc4d.const as k
import time
from cioc4d import utils

DEFAULT_TASK_TEMPLATE = 'Commandline -render "$ciodoc" -frame $ciostart $cioend $ciostep'
DEFAULT_AUTOSAVE_TEMPLATE = "cio_$prj"
DEFAULT_TITLE = "C4D $prj $take"
# IDS: NOTE Always add to the end - Don't insert! Don't ever reorder or remove
# entries, even if an attribute becomes redundant. If you do it will make old
# scenes incompatible.
X = 2000
TAKES = X = X + 1
TITLE = X = X + 1
PROJECT = X = X + 1
DESTINATION = X = X + 1
EXTRA_ASSETS = X = X + 1
INSTANCE_TYPE = X = X + 1
PREEMPTIBLE = X = X + 1
CHUNK_SIZE = X = X + 1
USE_CUSTOM_RANGE = X = X + 1
CUSTOM_RANGE = X = X + 1
USE_SCOUT_FRAMES = X = X + 1
SCOUT_FRAMES = X = X + 1
TASK_TEMPLATE = X = X + 1
EXTRA_ENVIRONMENT = X = X + 1
METADATA = X = X + 1
USE_UPLOAD_DAEMON = X = X + 1
UPLOAD_ONLY = X = X + 1
RETRIES_WHEN_PREEMPTED = X = X + 1
RETRIES_WHEN_FAILED = X = X + 1
USE_AUTOSAVE = X = X + 1
AUTOSAVE_FILENAME = X = X + 1
AUTOSAVE_CLEANUP = X = X + 1
LOCATION_TAG = X = X + 1
SHOW_TRACEBACKS = X = X + 1
HOST_VERSION = X = X + 1
RENDERER_VERSION = X = X + 1
EMAILS = X = X + 1
USE_EMAILS = X = X + 1
PREVIEW_MAX_TASKS = X = X + 1
USE_FIXTURES = X = X + 1
MODIFIED = X = X + 1
OVERRIDE_DESTINATION = X = X + 1
OVERRIDE_TASK_TEMPLATE = X = X + 1


class ConductorStore(object):
    """
    The store is used to persist a submission recipe in the scene file, and to
    repopulate the dialog when it's rebuilt.
    """

    CONTAINER_ID = k.PLUGIN_ID

    def __init__(self):

        self._modified = None
        self._container = None
        doc = c4d.documents.GetActiveDocument()
        if doc is None:  # Not even sure if its possible for doc to be None
            return
        doc_container = doc.GetDataInstance()
        self._container = doc_container[self.CONTAINER_ID]

        if self._container is None:
            self._container = c4d.BaseContainer()
            self.reset()
            self.commit()

    def on_scene_change(self):
        """
        If there's a scene changed event, it may be because the user loaded a
        new scene. In that case we have to use that new scene's
        conductor_container - if it has one.
        """

        # get the potentially different document
        doc = c4d.documents.GetActiveDocument()
        if doc is None:  # Not even sure if its possible for doc to be None
            return
        doc_container = doc.GetDataInstance()
        conductor_container = doc_container[self.CONTAINER_ID]
        if conductor_container is None:

            # Since this new doc has no conductor_container of its own, we use
            # the store's container. We reset its values and then commit it
            # (attach it to the new doc).
            self.reset()
            self.commit()
            return True

        else:
            # There is a conductor_container. If it's timestamp is different to
            #  the store, then the event must have been triggered from loading a new file.
            if conductor_container[MODIFIED] != self._modified:

                #  We set this container as the store's member data and sync
                #  it's timestamp.
                self._container = conductor_container
                self._modified = conductor_container[MODIFIED]
                return True
            else:
                return False

    def commit(self):
        timestamp = int(time.time() * 1000)
        doc = c4d.documents.GetActiveDocument()
        self.set_modified(timestamp)
        self._modified = timestamp

        doc[self.CONTAINER_ID] = self._container

    def clear(self):
        self._container.FlushAll()

    def modified(self):
        return self._container[MODIFIED]

    def set_modified(self, value):
        self._container.SetInt64(MODIFIED, value)

    def takes(self):
        return self._container[TAKES]

    def set_takes(self, value):
        self._container.SetString(TAKES, value)

    def title(self):
        return self._container[TITLE]

    def set_title(self, value):
        self._container.SetString(TITLE, (value))

    def project(self):
        return self._container[PROJECT]

    def set_project(self, value):
        self._container.SetString(PROJECT, value)

    def instance_type(self):
        return self._container[INSTANCE_TYPE]

    def set_instance_type(self, value):
        self._container.SetString(INSTANCE_TYPE, value)

    def preemptible(self):
        return self._container[PREEMPTIBLE]

    def set_preemptible(self, value):
        self._container.SetBool(PREEMPTIBLE, value)

    def override_destination(self):
        return self._container[OVERRIDE_DESTINATION]

    def set_override_destination(self, value):
        self._container.SetBool(OVERRIDE_DESTINATION, value)

    def destination(self):
        return self._container[DESTINATION]

    def set_destination(self, value):
        self._container.SetString(DESTINATION, (value))

    def chunk_size(self):
        return self._container[CHUNK_SIZE]

    def set_chunk_size(self, value):
        self._container.SetInt32(CHUNK_SIZE, value)

    def use_custom_range(self):
        return self._container[USE_CUSTOM_RANGE]

    def set_use_custom_range(self, value):
        self._container.SetBool(USE_CUSTOM_RANGE, value)

    def custom_range(self):
        return self._container[CUSTOM_RANGE]

    def set_custom_range(self, value):
        self._container.SetString(CUSTOM_RANGE, (value))

    def use_scout_frames(self):
        return self._container[USE_SCOUT_FRAMES]

    def set_use_scout_frames(self, value):
        self._container.SetBool(USE_SCOUT_FRAMES, value)

    def scout_frames(self):
        return self._container[SCOUT_FRAMES]

    def set_scout_frames(self, value):
        self._container.SetString(SCOUT_FRAMES, (value))

    def override_task_template(self):
        return self._container[OVERRIDE_TASK_TEMPLATE]

    def set_override_task_template(self, value):
        self._container.SetBool(OVERRIDE_TASK_TEMPLATE, value)

    def task_template(self):
        return self._container[TASK_TEMPLATE]

    def set_task_template(self, value):
        self._container.SetString(TASK_TEMPLATE, (value))

    def extra_environment(self):
        return json.loads(self._container[EXTRA_ENVIRONMENT]) or []

    def set_extra_environment(self, obj={}):
        self._container.SetString(EXTRA_ENVIRONMENT, json.dumps(obj))

    def metadata(self):
        return json.loads(self._container[METADATA]) or []

    def set_metadata(self, obj):
        self._container.SetString(METADATA, json.dumps(obj))

    def use_upload_daemon(self):
        return self._container[USE_UPLOAD_DAEMON]

    def set_use_upload_daemon(self, value):
        self._container.SetBool(USE_UPLOAD_DAEMON, value)

    def retries_when_preempted(self):
        return self._container[RETRIES_WHEN_PREEMPTED]

    def set_retries_when_preempted(self, value):
        self._container.SetInt32(RETRIES_WHEN_PREEMPTED, value)

    def retries_when_failed(self):
        return self._container[RETRIES_WHEN_FAILED]

    def set_retries_when_failed(self, value):
        self._container.SetInt32(RETRIES_WHEN_FAILED, value)

    def use_autosave(self):
        return self._container[USE_AUTOSAVE]

    def set_use_autosave(self, value):
        self._container.SetBool(USE_AUTOSAVE, value)

    def autosave_filename(self):
        return self._container[AUTOSAVE_FILENAME]

    def set_autosave_filename(self, value):
        self._container.SetString(AUTOSAVE_FILENAME, (value))

    def autosave_cleanup(self):
        return self._container[AUTOSAVE_CLEANUP]

    def set_autosave_cleanup(self, value):
        self._container.SetBool(AUTOSAVE_CLEANUP, value)

    def location_tag(self):
        return self._container[LOCATION_TAG]

    def set_location_tag(self, value):
        self._container.SetString(LOCATION_TAG, (value))

    def show_tracebacks(self):
        return self._container[SHOW_TRACEBACKS]

    def set_show_tracebacks(self, value):
        self._container.SetBool(SHOW_TRACEBACKS, value)

    def use_fixtures(self):
        return self._container[USE_FIXTURES]

    def set_use_fixtures(self, value):
        self._container.SetBool(USE_FIXTURES, value)

    def host_version(self):
        return self._container[HOST_VERSION]

    def set_host_version(self, value):
        self._container.SetString(HOST_VERSION, value)

    def use_emails(self):
        return self._container[USE_EMAILS]

    def set_use_emails(self, value):
        self._container.SetBool(USE_EMAILS, value)

    def emails(self):
        return self._container[EMAILS]

    def set_emails(self, value):
        self._container.SetString(EMAILS, (value))

    def renderer_version(self):
        return self._container[RENDERER_VERSION]

    def set_renderer_version(self, value):
        self._container.SetString(RENDERER_VERSION, value)

    def assets(self):
        return [(item[1]) for item in self._container.GetContainerInstance(EXTRA_ASSETS)]

    def set_assets(self, assets=[]):

        assets_container = self._container.GetContainerInstance(EXTRA_ASSETS)
        assets_container.FlushAll()
        for i, asset in enumerate(assets):
            assets_container.SetFilename(i, (asset))

    def reset(self):

        self.clear()

        assets_container = c4d.BaseContainer()
        self._container.SetContainer(EXTRA_ASSETS, assets_container)

        self.set_takes("Main")

        self.set_title(DEFAULT_TITLE)

        self.set_project("default")
        self.set_instance_type("unknowable")
        self.set_preemptible(True)
        self.set_chunk_size(1)
        self.set_use_custom_range(False)
        self.set_custom_range("1-10")
        self.set_use_scout_frames(True)
        self.set_scout_frames("auto:3")

        self.set_destination(utils.get_common_render_output_destination())
        self.set_override_destination(False)

        self.set_task_template(DEFAULT_TASK_TEMPLATE)
        self.set_override_task_template(False)
        self.set_extra_environment()
        self.set_metadata([("submitter", "cioc4d {}".format(k.VERSION))])

        self.set_use_upload_daemon(False)
        self.set_retries_when_preempted(1)
        self.set_retries_when_failed(1)
        self.set_use_autosave(True)
        self.set_autosave_filename(DEFAULT_AUTOSAVE_TEMPLATE)
        self.set_autosave_cleanup(True)

        self.set_location_tag("")
        self.set_emails("artist@example.com, producer@example.com")
        self.set_use_emails(False)

        self.set_show_tracebacks(False)
        self.set_use_fixtures(False)

        self.set_assets()

        self.set_host_version("unknown")
        self.set_renderer_version("default")
