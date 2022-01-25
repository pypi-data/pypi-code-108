import sys
import typing
has_joystick: bool = None
''' True if the BGE has been built with joystick support.
'''

has_physics: bool = None
''' True if the BGE has been built with physics support.
'''

has_texture_ffmpeg: bool = None
''' True if the BGE has been built with FFmpeg support, enabling use of ~bge.texture.ImageFFmpeg and ~bge.texture.VideoFFmpeg .
'''

upbge_version: tuple = None
''' The UPBGE version as a tuple of 3 ints, eg. (0, 0, 3).
'''

upbge_version_string: str = None
''' The UPBGE version formatted as a string, eg. "0.0 (sub 3)".
'''

version: tuple = None
''' The Blender/BGE version as a tuple of 3 ints, eg. (2, 75, 1).
'''

version_char: str = None
''' The Blender/BGE version character (for minor releases).
'''

version_string: str = None
''' The Blender/BGE version formatted as a string, eg. "2.75 (sub 1)".
'''
