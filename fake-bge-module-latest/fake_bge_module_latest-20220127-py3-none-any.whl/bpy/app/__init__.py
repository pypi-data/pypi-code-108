import sys
import typing
from . import translations
from . import handlers
from . import icons
from . import timers

alembic = None
''' Constant value bpy.app.alembic(supported=False, version=(0, 0, 0), version_string='Unknown')
'''

autoexec_fail = None
''' Undocumented, consider contributing <https://developer.blender.org/T51061> __.
'''

autoexec_fail_message = None
''' Undocumented, consider contributing <https://developer.blender.org/T51061> __.
'''

autoexec_fail_quiet = None
''' Undocumented, consider contributing <https://developer.blender.org/T51061> __.
'''

background = None
''' Boolean, True when blender is running without a user interface (started with -b)
'''

binary_path = None
''' The location of Blender's executable, useful for utilities that open new instances
'''

build_branch = None
''' The branch this blender instance was built from
'''

build_cflags = None
''' C compiler flags
'''

build_commit_date = None
''' The date of commit this blender instance was built
'''

build_commit_time = None
''' The time of commit this blender instance was built
'''

build_commit_timestamp = None
''' The unix timestamp of commit this blender instance was built
'''

build_cxxflags = None
''' C++ compiler flags
'''

build_date = None
''' The date this blender instance was built
'''

build_hash = None
''' The commit hash this blender instance was built with
'''

build_linkflags = None
''' Binary linking flags
'''

build_options = None
''' Constant value bpy.app.build_options(bullet=True, codec_avi=True, codec_ffmpeg=True, codec_sndfile=False, compositor=True, cycles=False, gameengine=False, cycles_osl=True, freestyle=True, image_cineon=True, image_dds=True, image_hdr=True, image_openexr=True, image_openjpeg=False, image_tiff=True, input_ndof=False, audaspace=True, international=True, openal=False, opensubdiv=False, sdl=False, sdl_dynload=False, coreaudio=False, jack=False, pulseaudio=False, wasapi=False, libmv=True, mod_oceansim=False, mod_remesh=True, player=False, collada=False, opencolorio=False, openmp=True, openvdb=False, alembic=False, usd=False, fluid=True, xr_openxr=False, potrace=False, pugixml=False, haru=False)
'''

build_platform = None
''' The platform this blender instance was built for
'''

build_system = None
''' Build system used
'''

build_time = None
''' The time this blender instance was built
'''

build_type = None
''' The type of build (Release, Debug)
'''

debug = None
''' Boolean, for debug info (started with --debug / --debug_* matching this attribute name)
'''

debug_depsgraph = None
''' Boolean, for debug info (started with --debug / --debug_* matching this attribute name)
'''

debug_depsgraph_build = None
''' Boolean, for debug info (started with --debug / --debug_* matching this attribute name)
'''

debug_depsgraph_eval = None
''' Boolean, for debug info (started with --debug / --debug_* matching this attribute name)
'''

debug_depsgraph_pretty = None
''' Boolean, for debug info (started with --debug / --debug_* matching this attribute name)
'''

debug_depsgraph_tag = None
''' Boolean, for debug info (started with --debug / --debug_* matching this attribute name)
'''

debug_depsgraph_time = None
''' Boolean, for debug info (started with --debug / --debug_* matching this attribute name)
'''

debug_events = None
''' Boolean, for debug info (started with --debug / --debug_* matching this attribute name)
'''

debug_ffmpeg = None
''' Boolean, for debug info (started with --debug / --debug_* matching this attribute name)
'''

debug_freestyle = None
''' Boolean, for debug info (started with --debug / --debug_* matching this attribute name)
'''

debug_handlers = None
''' Boolean, for debug info (started with --debug / --debug_* matching this attribute name)
'''

debug_io = None
''' Boolean, for debug info (started with --debug / --debug_* matching this attribute name)
'''

debug_python = None
''' Boolean, for debug info (started with --debug / --debug_* matching this attribute name)
'''

debug_simdata = None
''' Boolean, for debug info (started with --debug / --debug_* matching this attribute name)
'''

debug_value = None
''' Short, number which can be set to non-zero values for testing purposes
'''

debug_wm = None
''' Boolean, for debug info (started with --debug / --debug_* matching this attribute name)
'''

driver_namespace = None
''' Dictionary for drivers namespace, editable in-place, reset on file load (read-only)
'''

factory_startup = None
''' Boolean, True when blender is running with --factory-startup)
'''

ffmpeg = None
''' Constant value bpy.app.ffmpeg(supported=True, avcodec_version=(58, 54, 100), avcodec_version_string='58, 54, 100', avdevice_version=(58, 8, 100), avdevice_version_string='58, 8, 100', avformat_version=(58, 29, 100), avformat_version_string='58, 29, 100', avutil_version=(56, 31, 100), avutil_version_string='56, 31, 100', swscale_version=(5, 5, 100), swscale_version_string=' 5, 5, 100')
'''

ocio = None
''' Constant value bpy.app.ocio(supported=False, version=(0, 0, 0), version_string='Unknown')
'''

oiio = None
''' Constant value bpy.app.oiio(supported=False, version=(0, 0, 0), version_string='Unknown')
'''

opensubdiv = None
''' Constant value bpy.app.opensubdiv(supported=False, version=(0, 0, 0), version_string='Unknown')
'''

openvdb = None
''' Constant value bpy.app.openvdb(supported=False, version=(0, 0, 0), version_string='Unknown')
'''

render_icon_size = None
''' Reference size for icon/preview renders (read-only)
'''

render_preview_size = None
''' Reference size for icon/preview renders (read-only)
'''

sdl = None
''' Constant value bpy.app.sdl(supported=False, version=(0, 0, 0), version_string='Unknown', available=False)
'''

tempdir = None
''' String, the temp directory used by blender (read-only)
'''

usd = None
''' Constant value bpy.app.usd(supported=False, version=(0, 0, 0), version_string='Unknown')
'''

use_event_simulate = None
''' Boolean, for application behavior (started with --enable-* matching this attribute name)
'''

use_userpref_skip_save_on_exit = None
''' Boolean, for application behavior (started with --enable-* matching this attribute name)
'''

version = None
''' The Blender version as a tuple of 3 numbers. eg. (2, 83, 1)
'''

version_char = None
''' Deprecated, always an empty string
'''

version_cycle = None
''' The release status of this build alpha/beta/rc/release
'''

version_file = None
''' The Blender version, as a tuple, last used to save a .blend file, compatible with bpy.data.version . This value should be used for handling compatibility changes between Blender versions
'''

version_string = None
''' The Blender version formatted as a string
'''
