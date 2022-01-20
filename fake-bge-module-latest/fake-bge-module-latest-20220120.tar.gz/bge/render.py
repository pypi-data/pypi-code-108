import sys
import typing


def autoDebugList(enable: bool):
    ''' Enable or disable auto adding debug properties to the debug list.

    :type enable: bool
    '''

    pass


def clearDebugList():
    ''' Clears the debug property list.

    '''

    pass


def disableMotionBlur():
    ''' Disable the motion blur effect.

    '''

    pass


def drawLine(fromVec: list, toVec: list, color: list):
    ''' Draw a line in the 3D scene.

    :param fromVec: the origin of the line
    :type fromVec: list
    :param toVec: the end of the line
    :type toVec: list
    :param color: the color of the line
    :type color: list
    '''

    pass


def enableMotionBlur(factor: float):
    ''' Enable the motion blur effect.

    :param factor: the ammount of motion blur to display.
    :type factor: float
    '''

    pass


def enableVisibility(visible):
    ''' 

    '''

    pass


def getAnisotropicFiltering():
    ''' Get the anisotropic filtering level used for textures.

    '''

    pass


def getDisplayDimensions():
    ''' Get the display dimensions, in pixels, of the display (e.g., the monitor). Can return the size of the entire view, so the combination of all monitors; for example, (3840, 1080) for two side-by-side 1080p monitors.

    '''

    pass


def getEyeSeparation():
    ''' Gets the current eye separation for stereo mode.

    '''

    pass


def getFocalLength():
    ''' Gets the current focal length for stereo mode.

    '''

    pass


def getFullScreen():
    ''' Returns whether or not the window is fullscreen.

    '''

    pass


def getGLSLMaterialSetting(setting):
    ''' 

    '''

    pass


def getMaterialMode(mode):
    ''' 

    '''

    pass


def getMipmapping():
    ''' Get the current mipmapping setting.

    :return: ~bge.render.RAS_MIPMAP_LINEAR
    '''

    pass


def getStereoEye() -> typing.Union['LEFT_EYE', 'RIGHT_EYE']:
    ''' Gets the current stereoscopy eye being rendered. This function is mainly used in a :attr: bge.types.KX_Scene.pre_draw callback function to customize the camera projection matrices for each stereoscopic eye.

    :rtype: typing.Union['LEFT_EYE', 'RIGHT_EYE']
    :return: ~bge.render.RIGHT_EYE .
    '''

    pass


def getVsync():
    ''' Get the current vsync value

    :return: ~bge.render.VSYNC_ADAPTIVE
    '''

    pass


def getWindowHeight():
    ''' Gets the height of the window (in pixels)

    '''

    pass


def getWindowWidth():
    ''' Gets the width of the window (in pixels)

    '''

    pass


def makeScreenshot(filename: str):
    ''' Writes an image file with the displayed image at the frame end. The image is written to *'filename'*. The path may be absolute (eg. /home/foo/image ) or relative when started with // (eg. //image ). Note that absolute paths are not portable between platforms. If the filename contains a # , it will be replaced by an incremental index so that screenshots can be taken multiple times without overwriting the previous ones (eg. image-# ). Settings for the image are taken from the render settings (file format and respective settings, gamma and colospace conversion, etc). The image resolution matches the framebuffer, meaning, the window size and aspect ratio. When running from the standalone player, instead of the embedded player, only PNG files are supported. Additional color conversions are also not supported.

    :param filename: path and name of the file to write
    :type filename: str
    '''

    pass


def setAnisotropicFiltering(level):
    ''' Set the anisotropic filtering level for textures.

    :param level: The new anisotropic filtering level to use
    '''

    pass


def setBackgroundColor(rgba):
    ''' 

    '''

    pass


def setEyeSeparation(eyesep: float):
    ''' Sets the eye separation for stereo mode. Usually Focal Length/30 provides a confortable value.

    :param eyesep: The distance between the left and right eye.
    :type eyesep: float
    '''

    pass


def setFocalLength(focallength: float):
    ''' Sets the focal length for stereo mode. It uses the current camera focal length as initial value.

    :param focallength: The focal length.
    :type focallength: float
    '''

    pass


def setFullScreen(enable: bool):
    ''' Set whether or not the window should be fullscreen.

    :param enable: True to set full screen, False to set windowed.
    :type enable: bool
    '''

    pass


def setGLSLMaterialSetting(setting, enable):
    ''' 

    '''

    pass


def setMaterialMode(mode):
    ''' 

    '''

    pass


def setMipmapping(value):
    ''' Change how to use mipmapping.

    :param value: ~bge.render.RAS_MIPMAP_LINEAR
    '''

    pass


def setMousePosition(x, y):
    ''' Sets the mouse cursor position.

    :param x: X-coordinate in screen pixel coordinates.
    :param y: Y-coordinate in screen pixel coordinates.
    '''

    pass


def setVsync(value):
    ''' Set the vsync value

    :param value: ~bge.render.VSYNC_ADAPTIVE
    '''

    pass


def setWindowSize(width, height):
    ''' Set the width and height of the window (in pixels). This also works for fullscreen applications.

    :param width: width in pixels
    :param height: height in pixels
    '''

    pass


def showFramerate(enable: bool):
    ''' Show or hide the framerate.

    :type enable: bool
    '''

    pass


def showMouse(visible: bool):
    ''' Enables or disables the operating system mouse cursor.

    :type visible: bool
    '''

    pass


def showProfile(enable: bool):
    ''' Show or hide the profile.

    :type enable: bool
    '''

    pass


def showProperties(enable: bool):
    ''' Show or hide the debug properties.

    :type enable: bool
    '''

    pass


KX_BLENDER_GLSL_MATERIAL = None

KX_BLENDER_MULTITEX_MATERIAL = None

KX_TEXFACE_MATERIAL = None

LEFT_EYE = None
''' Left eye being used during stereoscopic rendering.
'''

RAS_MIPMAP_LINEAR = None
''' Applies mipmap filtering with nearest linear interpolation.
'''

RAS_MIPMAP_NEAREST = None
''' Applies mipmap filtering with nearest neighbour interpolation.
'''

RAS_MIPMAP_NONE = None
''' Disables Mipmap filtering.
'''

RIGHT_EYE = None
''' Right eye being used during stereoscopic rendering.
'''

VSYNC_ADAPTIVE = None
''' Enables adaptive vsync if supported. Adaptive vsync enables vsync if the framerate is above the monitors refresh rate. Otherwise, vsync is diabled if the framerate is too low.
'''

VSYNC_OFF = None
''' Disables vsync
'''

VSYNC_ON = None
''' Enables vsync
'''
