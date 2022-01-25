
"""
Encapsulation of a max dummy object to use as a settings store.

The purpose of the store is to make it possible to persist the state of the
dialog (settings) in the scene file.

The Object IDs are abstracted here.
Therefore we can present a public API containing the following methods for each setting:
def attribute():
def set_attribute(value):

The store is NOT the single source of truth while dialog is open. The widgets are.

So the flow is:

- User opens dialog:
- Check if scene has an instance of the conductor_store.
    - If not, make one and reset it to factory defaults.
- Populate the UI from the store.

When the user changes some value, persist it to the store.

"""
 

import os
import json
from pymxs import runtime as rt


DEFAULT_TITLE = "3dsmax <upper renderer> <scenenamex>"

STORE_NAME = "ConductorStore"

DEFAULT_DESTINATION = '<project>/renders'

# IDS: 

# Each setting is accessed by ID. 
# 
# NOTE Always add to the end - Don't insert! Don't ever reorder or remove
# entries, even if an attribute becomes redundant. If you do it will make old
# scenes incompatible.

X = 2000
TITLE = X = X+1
PROJECT = X = X+1
DESTINATION = X = X+1
EXTRA_ASSETS = X = X+1
INSTANCE_TYPE = X = X+1
PREEMPTIBLE = X = X+1
CHUNK_SIZE = X = X+1
USE_CUSTOM_RANGE = X = X+1
CUSTOM_RANGE = X = X+1
USE_SCOUT_FRAMES = X = X+1
SCOUT_FRAMES = X = X+1
TASK_TEMPLATE = X = X+1
EXTRA_ENVIRONMENT = X = X+1
METADATA = X = X+1
USE_UPLOAD_DAEMON = X = X+1
UPLOAD_ONLY = X = X+1
RETRIES_WHEN_PREEMPTED = X = X+1
USE_AUTOSAVE = X = X+1
AUTOSAVE_FILENAME = X = X+1
AUTOSAVE_CLEANUP = X = X+1
LOCATION_TAG = X = X+1
SHOW_TRACEBACKS = X = X+1
HOST_VERSION = X = X+1
RENDERER_VERSION = X = X+1
EMAILS = X = X+1
USE_EMAILS = X = X+1
USE_FIXTURES = X = X+1
FIXTURES_PATH = X = X+1
OVERRIDE_DESTINATION = X = X+1
DEFAULT_TASK_TEMPLATE = X = X+1
OVERRIDE_TEMPLATES = X = X+1
SCRIPT_FILENAME = X = X+1
CAMERA = X = X+1

SECTIONS_OPEN = {}
SECTIONS_OPEN["GeneralSection"] = X = X+1
SECTIONS_OPEN["SoftwareSection"] = X = X+1
SECTIONS_OPEN["FramesSection"] = X = X+1
SECTIONS_OPEN["InfoSection"] = X = X+1
SECTIONS_OPEN["EnvironmentSection"] = X = X+1
SECTIONS_OPEN["MetadataSection"] = X = X+1
SECTIONS_OPEN["ExtraAssetsSection"] = X = X+1
SECTIONS_OPEN["AdvancedSection"] = X = X+1


def print_ids():
    print("TITLE ID:", TITLE)
    print("PROJECT ID:", PROJECT)
    print("DESTINATION ID:", DESTINATION)
    print("EXTRA_ASSETS ID:", EXTRA_ASSETS)
    print("INSTANCE_TYPE ID:", INSTANCE_TYPE)
    print("PREEMPTIBLE ID:", PREEMPTIBLE)
    print("CHUNK_SIZE ID:", CHUNK_SIZE)
    print("USE_CUSTOM_RANGE ID:", USE_CUSTOM_RANGE)
    print("CUSTOM_RANGE ID:", CUSTOM_RANGE)
    print("USE_SCOUT_FRAMES ID:", USE_SCOUT_FRAMES)
    print("SCOUT_FRAMES ID:", SCOUT_FRAMES)
    print("TASK_TEMPLATE ID:", TASK_TEMPLATE)
    print("EXTRA_ENVIRONMENT ID:", EXTRA_ENVIRONMENT)
    print("METADATA ID:", METADATA)
    print("USE_UPLOAD_DAEMON ID:", USE_UPLOAD_DAEMON)
    print("UPLOAD_ONLY ID:", UPLOAD_ONLY)
    print("RETRIES_WHEN_PREEMPTED ID:", RETRIES_WHEN_PREEMPTED)
    print("USE_AUTOSAVE ID:", USE_AUTOSAVE)
    print("AUTOSAVE_FILENAME ID:", AUTOSAVE_FILENAME)
    print("AUTOSAVE_CLEANUP ID:", AUTOSAVE_CLEANUP)
    print("LOCATION_TAG ID:", LOCATION_TAG)
    print("SHOW_TRACEBACKS ID:", SHOW_TRACEBACKS)
    print("HOST_VERSION ID:", HOST_VERSION)
    print("RENDERER_VERSION ID:", RENDERER_VERSION)
    print("EMAILS ID:", EMAILS)
    print("USE_EMAILS ID:", USE_EMAILS)
    print("USE_FIXTURES ID:", USE_FIXTURES)
    print("OVERRIDE_DESTINATION ID:", OVERRIDE_DESTINATION)
    print("DEFAULT_TASK_TEMPLATE ID:", DEFAULT_TASK_TEMPLATE)
    print("OVERRIDE_TEMPLATES:", OVERRIDE_TEMPLATES)
    print("SCRIPT_FILENAME:", SCRIPT_FILENAME)
    print("CAMERA:",CAMERA)

class ConductorStore(object):
    """
    The store is used to persist a submission recipe in the scene file, and to
    repopulate the dialog when it's rebuilt.
    """

    def __init__(self):
        self.node = rt.getNodeByName(STORE_NAME)
        if not self.node:
            self.node = rt.dummy()
            self.node.name =STORE_NAME
            self.reset()
            self.set_use_fixtures(False)


    def clear(self):
        rt.clearAllAppData(self.node)

    def reset(self):

        self.clear()

        self.set_title(DEFAULT_TITLE)

        self.set_project("default")
        self.set_camera("")
        
        self.set_instance_type("n1-highcpu-8")
        self.set_preemptible(True)
        self.set_chunk_size(1)
        self.set_use_custom_range(False)
        self.set_custom_range("1-10")
        self.set_use_scout_frames(True)
        self.set_scout_frames("auto:3")

        self.set_destination(DEFAULT_DESTINATION)
     

        self.set_task_template("")
        # self.set_DEFAULT_task_template(True)
        self.set_extra_environment()
        self.set_metadata()

        self.set_use_upload_daemon(False)
        self.set_upload_only(False)
        self.set_retries_when_preempted(1)

        self.set_location_tag("")
        self.set_emails("artist@example.com, producer@example.com")
        self.set_use_emails(False)

        self.set_show_tracebacks(False)
        

        self.set_assets()
        self.set_renderer_version("")

        self.set_override_templates(False)
        self.set_script_filename("")

        self.set_section_open("GeneralSection", True)
        self.set_section_open("SoftwareSection", True)
        self.set_section_open("FramesSection", False)
        self.set_section_open("InfoSection", True)
        self.set_section_open("EnvironmentSection", False)
        self.set_section_open("MetadataSection", False)
        self.set_section_open("ExtraAssetsSection", False)
        self.set_section_open("AdvancedSection", False)
 
    def _get_string(self, key, default=""):
        return rt.getAppData(self.node, key) or default
  

    def _get_bool(self, key, default=False):
        value = rt.getAppData(self.node, key)
        return json.loads(value) if value is not None else default
  
    def _get_int(self, key, default=0):
        value = rt.getAppData(self.node, key)
        return json.loads(value) if value is not None else default
    
    def _get_list(self, key, default=[]):
        value = rt.getAppData(self.node, key)
        return json.loads(value) if value else default

    def title(self):
        return self._get_string(TITLE)

    def set_title(self, value):
        try:
            rt.deleteAppdata(self.node,TITLE)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, TITLE, value)

    def project(self):
        return self._get_string(PROJECT)

    def set_project(self, value):
        try:
            rt.deleteAppdata(self.node,PROJECT)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, PROJECT, value)

    def camera(self):
        return self._get_string(CAMERA)

    def set_camera(self, value):
        try:
            rt.deleteAppdata(self.node,CAMERA)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, CAMERA, value)

    def instance_type(self):
        return self._get_string(INSTANCE_TYPE)

    def set_instance_type(self, value):
        try:
            rt.deleteAppdata(self.node,INSTANCE_TYPE)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, INSTANCE_TYPE, value)

    def preemptible(self):
        return self._get_bool(PREEMPTIBLE, True)
 
    def set_preemptible(self, value):
        try:
            rt.deleteAppdata(self.node,PREEMPTIBLE)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, PREEMPTIBLE, json.dumps(value))

    def destination(self):
        return self._get_string(DESTINATION)

    def set_destination(self, value):
        try:
            rt.deleteAppdata(self.node,DESTINATION)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, DESTINATION, value)

    def chunk_size(self):
        return self._get_int(CHUNK_SIZE, 1)
  
    def set_chunk_size(self, value):
        try:
            rt.deleteAppdata(self.node,CHUNK_SIZE)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, CHUNK_SIZE,  json.dumps(value))

    def use_custom_range(self):
        return self._get_bool(USE_CUSTOM_RANGE, False) 

    def set_use_custom_range(self, value):
        try:
            rt.deleteAppdata(self.node,USE_CUSTOM_RANGE)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, USE_CUSTOM_RANGE, json.dumps(value))

    def custom_range(self):
        return self._get_string(CUSTOM_RANGE, "1-10")

    def set_custom_range(self, value):
        try:
            rt.deleteAppdata(self.node,CUSTOM_RANGE)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, CUSTOM_RANGE, value)

    def use_scout_frames(self):
        return self._get_bool(USE_SCOUT_FRAMES, True)
 
    def set_use_scout_frames(self, value):
        try:
            rt.deleteAppdata(self.node,USE_SCOUT_FRAMES)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, USE_SCOUT_FRAMES, json.dumps(value))

    def scout_frames(self):
        return self._get_string(SCOUT_FRAMES, "auto:3")

    def set_scout_frames(self, value):
        try:
            rt.deleteAppdata(self.node,SCOUT_FRAMES)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, SCOUT_FRAMES, value)
 
    def task_template(self):
        return self._get_string(TASK_TEMPLATE, "")
 
    def set_task_template(self, value):
        try:
            rt.deleteAppdata(self.node,TASK_TEMPLATE)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, TASK_TEMPLATE, value)

    def extra_environment(self):
        return self._get_list(EXTRA_ENVIRONMENT)

    def set_extra_environment(self, obj=[]):
        try:
            rt.deleteAppdata(self.node,EXTRA_ENVIRONMENT)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, EXTRA_ENVIRONMENT,  json.dumps(obj))

    def metadata(self):
        return self._get_list(METADATA)

    def set_metadata(self, obj=[]):
        try:
            rt.deleteAppdata(self.node,METADATA)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, METADATA, json.dumps(obj))

    def use_upload_daemon(self):
        return self._get_bool(USE_UPLOAD_DAEMON, True)
 
    def set_use_upload_daemon(self, value):
        try:
            rt.deleteAppdata(self.node,USE_UPLOAD_DAEMON)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, USE_UPLOAD_DAEMON, json.dumps(value))

    def upload_only(self):
        return self._get_bool(UPLOAD_ONLY, True)
 
    def set_upload_only(self, value):
        try:
            rt.deleteAppdata(self.node,UPLOAD_ONLY)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, UPLOAD_ONLY,  json.dumps(value))

    def retries_when_preempted(self):
        return self._get_int(RETRIES_WHEN_PREEMPTED, 1)
  

    def set_retries_when_preempted(self, value):
        try:
            rt.deleteAppdata(self.node,RETRIES_WHEN_PREEMPTED)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, RETRIES_WHEN_PREEMPTED, json.dumps(value))

    def use_autosave(self):
        return self._get_bool(USE_AUTOSAVE, True)
 
    def set_use_autosave(self, value):
        try:
            rt.deleteAppdata(self.node,USE_AUTOSAVE)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, USE_AUTOSAVE, json.dumps(value))

    def autosave_filename(self):
        return self._get_string(AUTOSAVE_FILENAME, "")

    def set_autosave_filename(self, value):
        try:
            rt.deleteAppdata(self.node,AUTOSAVE_FILENAME)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, AUTOSAVE_FILENAME, value)

    def autosave_cleanup(self):
        return self._get_bool(AUTOSAVE_CLEANUP, True)
 
    def set_autosave_cleanup(self, value):
        try:
            rt.deleteAppdata(self.node,AUTOSAVE_CLEANUP)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, AUTOSAVE_CLEANUP, json.dumps(value))

    def location_tag(self):
        return self._get_string(LOCATION_TAG, "")

    def set_location_tag(self, value):
        try:
            rt.deleteAppdata(self.node,LOCATION_TAG)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, LOCATION_TAG, value)

    def show_tracebacks(self):
        return self._get_bool(SHOW_TRACEBACKS, False)
 
    def set_show_tracebacks(self, value):
        try:
            rt.deleteAppdata(self.node,SHOW_TRACEBACKS)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, SHOW_TRACEBACKS,  json.dumps(value))

    def use_fixtures(self): 
        return self._get_bool(USE_FIXTURES, False)
 
    def set_use_fixtures(self, value):
        try:
            rt.deleteAppdata(self.node,USE_FIXTURES)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, USE_FIXTURES, json.dumps(value))

    def host_version(self):
        return self._get_string(HOST_VERSION, "")

    def set_host_version(self, value):
        try:
            rt.deleteAppdata(self.node,HOST_VERSION)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, HOST_VERSION, value)

    def renderer_version(self):
        return self._get_string(RENDERER_VERSION, "")

    def set_renderer_version(self, value):
        try:
            rt.deleteAppdata(self.node,RENDERER_VERSION)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, RENDERER_VERSION, value)

    def use_emails(self):
         return self._get_bool(USE_EMAILS, False)
 
    def set_use_emails(self, value):
        try:
            rt.deleteAppdata(self.node,USE_EMAILS)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, USE_EMAILS, json.dumps(value))

    def emails(self):
        return self._get_string(EMAILS)

    def set_emails(self, value):
        try:
            rt.deleteAppdata(self.node,EMAILS)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, EMAILS, value)

    def assets(self):
        return self._get_list(EXTRA_ASSETS)

    def set_assets(self, assets=[]):
        try:
            rt.deleteAppdata(self.node,EXTRA_ASSETS)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, EXTRA_ASSETS, json.dumps(assets))

    def override_templates(self): 
        return self._get_bool(OVERRIDE_TEMPLATES, False)
 
    def set_override_templates(self, value):
        try:
            rt.deleteAppdata(self.node,OVERRIDE_TEMPLATES)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, OVERRIDE_TEMPLATES, json.dumps(value))

    def script_filename(self): 
        return self._get_string(SCRIPT_FILENAME)

    def set_script_filename(self, value):
        try:
            rt.deleteAppdata(self.node,SCRIPT_FILENAME)
        except RuntimeError:
            pass
        rt.setAppdata(self.node, SCRIPT_FILENAME, value)
 
    # section_open("general")
    def section_open(self, section):
        return self._get_bool(SECTIONS_OPEN[section], False)
    # set_section_open("advanced")
    def set_section_open(self, section, value):
        try:
            rt.deleteAppdata(self.node,SECTIONS_OPEN[section])
        except RuntimeError:
            pass
        rt.setAppdata(self.node, SECTIONS_OPEN[section], json.dumps(value))
