import sys
import typing
import bge.types


def LibFree(name: str):
    ''' Frees a library, removing all objects and meshes from the currently active scenes.

    :param name: The name of the library to free (the name used in LibNew)
    :type name: str
    '''

    pass


def LibList():
    ''' Returns a list of currently loaded libraries.

    '''

    pass


def LibLoad(blend: str,
            type: str,
            data: bytes,
            load_actions: bool = False,
            verbose: bool = False,
            load_scripts: bool = True,
            asynchronous: bool = False,
            scene: typing.Union[str, 'bge.types.KX_Scene'] = None):
    ''' Converts the all of the datablocks of the given type from the given blend.

    :param blend: The path to the blend file (or the name to use for the library if data is supplied)
    :type blend: str
    :param type: The datablock type (currently only "Action", "Mesh" and "Scene" are supported)
    :type type: str
    :param data: Binary data from a blend file (optional)
    :type data: bytes
    :param load_actions: Search for and load all actions in a given Scene and not just the "active" actions (Scene type only)
    :type load_actions: bool
    :param verbose: Scene")
    :type verbose: bool
    :param load_scripts: Whether or not to load text datablocks as well (can be disabled for some extra security)
    :type load_scripts: bool
    :param asynchronous: Whether or not to do the loading asynchronously (in another thread). Only the "Scene" type is currently supported for this feature.
    :type asynchronous: bool
    :param scene: Scene to merge loaded data to, if None use the current scene.
    :type scene: typing.Union[str, 'bge.types.KX_Scene']
    '''

    pass


def LibNew(name: str, type: str, data: list):
    ''' Uses existing datablock data and loads in as a new library.

    :param name: A unique library name used for removal later
    :type name: str
    :param type: The datablock type (currently only "Mesh" is supported)
    :type type: str
    :param data: A list of names of the datablocks to load
    :type data: list
    '''

    pass


def NextFrame():
    ''' Render next frame (if Python has control)

    '''

    pass


def PrintGLInfo():
    ''' Prints GL Extension Info into the console

    '''

    pass


def PrintMemInfo():
    ''' Prints engine statistics into the console

    '''

    pass


def addScene(name: str, overlay=1):
    ''' Loads a scene into the game engine.

    :param name: The name of the scene
    :type name: str
    :param overlay: Overlay or underlay (optional)
    '''

    pass


def endGame():
    ''' Ends the current game.

    '''

    pass


def expandPath(path: str) -> str:
    ''' Converts a blender internal path into a proper file system path. Use / as directory separator in path You can use '//' at the start of the string to define a relative path; Blender replaces that string by the directory of the current .blend or runtime file to make a full path name. The function also converts the directory separator to the local file system format.

    :param path: The path string to be converted/expanded.
    :type path: str
    :rtype: str
    :return: The converted string
    '''

    pass


def getAverageFrameRate() -> float:
    ''' Gets the estimated/average framerate for all the active scenes, not only the current scene.

    :rtype: float
    :return: The estimated average framerate in frames per second
    '''

    pass


def getBlendFileList(path=' "//"') -> list:
    ''' Returns a list of blend files in the same directory as the open blend file, or from using the option argument.

    :param path: Optional directory argument, will be expanded (like expandPath) into the full path.
    :type path: str
    :rtype: list
    :return: A list of filenames, with no directory prefix
    '''

    pass


def getClockTime():
    ''' Get the current BGE render time, in seconds. The BGE render time is the simulation time corresponding to the next scene that will be rendered.

    '''

    pass


def getCurrentController():
    ''' Gets the Python controller associated with this Python script.

    '''

    pass


def getCurrentScene():
    ''' Gets the current Scene.

    '''

    pass


def getExitKey() -> int:
    ''' Gets the key used to exit the game engine

    :rtype: int
    :return: bge.events.ESCKEY )
    '''

    pass


def getFrameTime():
    ''' Get the current BGE frame time, in seconds. The BGE frame time is the simulation time corresponding to the current call of the logic system. Generally speaking, it is what the user is interested in.

    '''

    pass


def getGraphicsCardVendor():
    ''' Returns the graphics card vendor name. Very useful to make different setups depending on the graphic card used by the user.

    '''

    pass


def getInactiveSceneNames():
    ''' Gets a list of the scene's names not loaded in the game engine.

    '''

    pass


def getLogicTicRate() -> float:
    ''' Gets the logic update frequency.

    :rtype: float
    :return: The logic frequency in Hz
    '''

    pass


def getMaxLogicFrame():
    ''' Gets the maximum number of logic frames per render frame.

    :return: The maximum number of logic frames per render frame
    '''

    pass


def getMaxPhysicsFrame():
    ''' Gets the maximum number of physics frames per render frame.

    :return: The maximum number of physics frames per render frame
    '''

    pass


def getPhysicsTicRate() -> float:
    ''' Gets the physics update frequency

    :rtype: float
    :return: The physics update frequency in Hz
    '''

    pass


def getProfileInfo():
    ''' Returns a Python dictionary that contains the same information as the on screen profiler. The keys are the profiler categories and the values are tuples with the first element being time taken (in ms) and the second element being the percentage of total time.

    '''

    pass


def getRandomFloat():
    ''' Returns a random floating point value in the range [0 - 1)

    '''

    pass


def getRealTime():
    ''' Get the number of real (system-clock) seconds elapsed since the beginning of the simulation.

    '''

    pass


def getRender() -> bool:
    ''' Get the current value of the global render flag

    :rtype: bool
    :return: The flag value
    '''

    pass


def getSceneList():
    ''' Gets a list of the current scenes loaded in the game engine. Since 0.3, it contains only the current KX_Scene.

    '''

    pass


def getSpectrum():
    ''' Returns a 512 point list from the sound card. This only works if the fmod sound driver is being used.

    '''

    pass


def getTimeScale():
    ''' Get the time multiplier between real-time and simulation time. The default value is 1.0. A value greater than 1.0 means that the simulation is going faster than real-time, a value lower than 1.0 means that the simulation is going slower than real-time.

    '''

    pass


def getUseExternalClock():
    ''' Get if the BGE use the inner BGE clock, or rely or on an external clock. The default is to use the inner BGE clock.

    '''

    pass


def loadGlobalDict():
    ''' Loads bge.logic.globalDict from a file.

    '''

    pass


def restartGame():
    ''' Restarts the current game by reloading the .blend file (the last saved version, not what is currently running).

    '''

    pass


def saveGlobalDict():
    ''' Saves bge.logic.globalDict to a file.

    '''

    pass


def sendMessage(subject: str,
                body: str = "",
                to: str = "",
                message_from: str = ""):
    ''' Sends a message to sensors in any active scene.

    :param subject: The subject of the message
    :type subject: str
    :param body: The body of the message (optional)
    :type body: str
    :param to: The name of the object to send the message to (optional)
    :type to: str
    :param message_from: The name of the object that the message is coming from (optional)
    :type message_from: str
    '''

    pass


def setClockTime(new_time):
    ''' Set the next value of the simulation clock. It is preferable to use this method from a custom main function in python, as calling it in the logic block can easily lead to a blocked system (if the time does not advance enough to run at least the next logic step).

    '''

    pass


def setExitKey(key: int):
    ''' Sets the key used to exit the game engine

    :param key: bge.events
    :type key: int
    '''

    pass


def setGravity(gravity):
    ''' Sets the world gravity.

    :param gravity: gravity vector
    '''

    pass


def setLogicTicRate(ticrate: float):
    ''' Sets the logic update frequency. The logic update frequency is the number of times logic bricks are executed every second. The default is 60 Hz.

    :param ticrate: The new logic update frequency (in Hz).
    :type ticrate: float
    '''

    pass


def setMaxLogicFrame(maxlogic):
    ''' Sets the maximum number of logic frames that are executed per render frame. This does not affect the physic system that still runs at full frame rate.

    :param maxlogic: 1..5
    '''

    pass


def setMaxPhysicsFrame(maxphysics):
    ''' Sets the maximum number of physics timestep that are executed per render frame. Higher value allows physics to keep up with realtime even if graphics slows down the game. Physics timestep is fixed and equal to 1/tickrate (see setLogicTicRate) maxphysics/ticrate is the maximum delay of the renderer that physics can compensate.

    :param maxphysics: 1..5.
    '''

    pass


def setPhysicsTicRate(ticrate: float):
    ''' Sets the physics update frequency The physics update frequency is the number of times the physics system is executed every second. The default is 60 Hz.

    :param ticrate: The new update frequency (in Hz).
    :type ticrate: float
    '''

    pass


def setRender(render: bool):
    ''' Sets the global flag that controls the render of the scene. If True, the render is done after the logic frame. If False, the render is skipped and another logic frame starts immediately.

    :param render: the render flag
    :type render: bool
    '''

    pass


def setTimeScale(time_scale):
    ''' Set the time multiplier between real-time and simulation time. A value greater than 1.0 means that the simulation is going faster than real-time, a value lower than 1.0 means that the simulation is going slower than real-time. Note that a too large value may lead to some physics instabilities.

    '''

    pass


def setUseExternalClock(use_external_clock):
    ''' Set if the BGE use the inner BGE clock, or rely or on an external clock. If the user selects the use of an external clock, he should call regularly the setClockTime method.

    '''

    pass


def startGame(blend: str):
    ''' Loads the blend file.

    :param blend: The name of the blend file
    :type blend: str
    '''

    pass


BL_DST_ALPHA = None

BL_DST_COLOR = None

BL_ONE = None

BL_ONE_MINUS_DST_ALPHA = None

BL_ONE_MINUS_DST_COLOR = None

BL_ONE_MINUS_SRC_ALPHA = None

BL_ONE_MINUS_SRC_COLOR = None

BL_SRC_ALPHA = None

BL_SRC_ALPHA_SATURATE = None

BL_SRC_COLOR = None

BL_ZERO = None

CAM_POS = None
''' Current camera position
'''

CONSTANT_TIMER = None

CONSTRAINT_IK_COPYPOSE = None
''' constraint is trying to match the position and eventually the rotation of the target. :value: 0
'''

CONSTRAINT_IK_DISTANCE = None
''' Constraint is maintaining a certain distance to target subject to ik_mode :value: 1
'''

CONSTRAINT_IK_FLAG_POS = None
''' Set when the constraint tries to match the position of the target. :value: 32
'''

CONSTRAINT_IK_FLAG_ROT = None
''' Set when the constraint tries to match the orientation of the target :value: 2
'''

CONSTRAINT_IK_FLAG_STRETCH = None
''' Set when the armature is allowed to stretch (only the bones with stretch factor > 0.0) :value: 16
'''

CONSTRAINT_IK_FLAG_TIP = None
''' Set when the constraint operates on the head of the bone and not the tail :value: 1
'''

CONSTRAINT_IK_MODE_INSIDE = None
''' The constraint tries to keep the bone within ik_dist of target :value: 0
'''

CONSTRAINT_IK_MODE_ONSURFACE = None
''' The constraint tries to keep the bone exactly at ik_dist of the target. :value: 2
'''

CONSTRAINT_IK_MODE_OUTSIDE = None
''' The constraint tries to keep the bone outside ik_dist of the target :value: 1
'''

CONSTRAINT_TYPE_CLAMPTO = None

CONSTRAINT_TYPE_DISTLIMIT = None

CONSTRAINT_TYPE_KINEMATIC = None

CONSTRAINT_TYPE_LOCKTRACK = None

CONSTRAINT_TYPE_LOCLIKE = None

CONSTRAINT_TYPE_MINMAX = None

CONSTRAINT_TYPE_ROTLIKE = None

CONSTRAINT_TYPE_SIZELIKE = None

CONSTRAINT_TYPE_STRETCHTO = None

CONSTRAINT_TYPE_TRACKTO = None

CONSTRAINT_TYPE_TRANSFORM = None

EYE = None
''' User a timer for the uniform value.
'''

KX_ACTIONACT_FLIPPER = None

KX_ACTIONACT_LOOPEND = None

KX_ACTIONACT_LOOPSTOP = None

KX_ACTIONACT_PINGPONG = None

KX_ACTIONACT_PLAY = None

KX_ACTIONACT_PROPERTY = None

KX_ACTION_BLEND_ADD = None
''' Adds the layers together :value: 1
'''

KX_ACTION_BLEND_BLEND = None
''' Blend layers using linear interpolation :value: 0
'''

KX_ACTION_MODE_LOOP = None
''' Loop the action (repeat it). :value: 1
'''

KX_ACTION_MODE_PING_PONG = None
''' Play the action one direct then back the other way when it has completed. :value: 2
'''

KX_ACTION_MODE_PLAY = None
''' Play the action once. :value: 0
'''

KX_ACT_ARMATURE_DISABLE = None
''' Disable the constraint (runtime constraint values are not updated). :value: 2
'''

KX_ACT_ARMATURE_ENABLE = None
''' Enable the constraint. :value: 1
'''

KX_ACT_ARMATURE_RUN = None
''' Just make sure the armature will be updated on the next graphic frame. This is the only persistent mode of the actuator: it executes automatically once per frame until stopped by a controller :value: 0
'''

KX_ACT_ARMATURE_SETINFLUENCE = None
''' Change influence of constraint. :value: 5
'''

KX_ACT_ARMATURE_SETTARGET = None
''' Change target and subtarget of constraint. :value: 3
'''

KX_ACT_ARMATURE_SETWEIGHT = None
''' Change weight of constraint (IK only). :value: 4
'''

KX_ACT_MOUSE_OBJECT_AXIS_X = None

KX_ACT_MOUSE_OBJECT_AXIS_Y = None

KX_ACT_MOUSE_OBJECT_AXIS_Z = None

KX_ARMSENSOR_LIN_ERROR_ABOVE = None
''' Detect that the constraint linear error is below a threshold :value: 2
'''

KX_ARMSENSOR_LIN_ERROR_BELOW = None
''' Detect that the constraint linear error is above a threshold :value: 1
'''

KX_ARMSENSOR_ROT_ERROR_ABOVE = None
''' Detect that the constraint rotation error is below a threshold :value: 4
'''

KX_ARMSENSOR_ROT_ERROR_BELOW = None
''' Detect that the constraint rotation error is above a threshold :value: 3
'''

KX_ARMSENSOR_STATE_CHANGED = None
''' Detect that the constraint is changing state (active/inactive) :value: 0
'''

KX_CONSTRAINTACT_DIRNX = None
''' Set distance along negative X axis
'''

KX_CONSTRAINTACT_DIRNY = None
''' Set distance along negative Y axis
'''

KX_CONSTRAINTACT_DIRNZ = None
''' Set distance along negative Z axis
'''

KX_CONSTRAINTACT_DIRPX = None
''' Set distance along positive X axis
'''

KX_CONSTRAINTACT_DIRPY = None
''' Set distance along positive Y axis
'''

KX_CONSTRAINTACT_DIRPZ = None
''' Set distance along positive Z axis
'''

KX_CONSTRAINTACT_DISTANCE = None
''' Activate distance control
'''

KX_CONSTRAINTACT_DOROTFH = None
''' Force field act on rotation as well
'''

KX_CONSTRAINTACT_FHNX = None
''' Set force field along negative X axis
'''

KX_CONSTRAINTACT_FHNY = None
''' Set force field along negative Y axis
'''

KX_CONSTRAINTACT_FHNZ = None
''' Set force field along negative Z axis
'''

KX_CONSTRAINTACT_FHPX = None
''' Set force field along positive X axis
'''

KX_CONSTRAINTACT_FHPY = None
''' Set force field along positive Y axis
'''

KX_CONSTRAINTACT_FHPZ = None
''' Set force field along positive Z axis
'''

KX_CONSTRAINTACT_LOCAL = None
''' Direction of the ray is along the local axis
'''

KX_CONSTRAINTACT_LOCX = None
''' Limit X coord.
'''

KX_CONSTRAINTACT_LOCY = None
''' Limit Y coord
'''

KX_CONSTRAINTACT_LOCZ = None
''' Limit Z coord
'''

KX_CONSTRAINTACT_MATERIAL = None
''' Detect material rather than property
'''

KX_CONSTRAINTACT_NORMAL = None
''' Activate alignment to surface
'''

KX_CONSTRAINTACT_ORIX = None
''' Set orientation of X axis
'''

KX_CONSTRAINTACT_ORIY = None
''' Set orientation of Y axis
'''

KX_CONSTRAINTACT_ORIZ = None
''' Set orientation of Z axis
'''

KX_CONSTRAINTACT_PERMANENT = None
''' No deactivation if ray does not hit target
'''

KX_CONSTRAINTACT_ROTX = None
''' Limit X rotation
'''

KX_CONSTRAINTACT_ROTY = None
''' Limit Y rotation
'''

KX_CONSTRAINTACT_ROTZ = None
''' Limit Z rotation
'''

KX_DYN_DISABLE_DYNAMICS = None

KX_DYN_DISABLE_RIGID_BODY = None

KX_DYN_ENABLE_RIGID_BODY = None

KX_DYN_RESTORE_DYNAMICS = None

KX_DYN_SET_MASS = None

KX_FALSE = None
''' False value used by some modules.
'''

KX_GAME_LOAD = None

KX_GAME_LOADCFG = None

KX_GAME_QUIT = None

KX_GAME_RESTART = None

KX_GAME_SAVECFG = None

KX_GAME_START = None

KX_INPUT_ACTIVE = None

KX_INPUT_JUST_ACTIVATED = None

KX_INPUT_JUST_RELEASED = None

KX_INPUT_NONE = None

KX_MOUSE_BUT_BUTTON4 = None

KX_MOUSE_BUT_BUTTON5 = None

KX_MOUSE_BUT_BUTTON6 = None

KX_MOUSE_BUT_BUTTON7 = None

KX_MOUSE_BUT_LEFT = None

KX_MOUSE_BUT_MIDDLE = None

KX_MOUSE_BUT_RIGHT = None

KX_PARENT_REMOVE = None

KX_PARENT_SET = None

KX_PROPSENSOR_CHANGED = None
''' Activate when the property changes :value: 4
'''

KX_PROPSENSOR_EQUAL = None
''' Activate when the property is equal to the sensor value. :value: 1
'''

KX_PROPSENSOR_EXPRESSION = None
''' Activate when the expression matches :value: 5
'''

KX_PROPSENSOR_GREATERTHAN = None
''' Activate when the property is greater than the sensor value :value: 7
'''

KX_PROPSENSOR_INTERVAL = None
''' Activate when the property is between the specified limits. :value: 3
'''

KX_PROPSENSOR_LESSTHAN = None
''' Activate when the property is less than the sensor value :value: 6
'''

KX_PROPSENSOR_NOTEQUAL = None
''' Activate when the property is not equal to the sensor value. :value: 2
'''

KX_RADAR_AXIS_NEG_X = None

KX_RADAR_AXIS_NEG_Y = None

KX_RADAR_AXIS_NEG_Z = None

KX_RADAR_AXIS_POS_X = None

KX_RADAR_AXIS_POS_Y = None

KX_RADAR_AXIS_POS_Z = None

KX_RANDOMACT_BOOL_BERNOUILLI = None

KX_RANDOMACT_BOOL_CONST = None

KX_RANDOMACT_BOOL_UNIFORM = None

KX_RANDOMACT_FLOAT_CONST = None

KX_RANDOMACT_FLOAT_NEGATIVE_EXPONENTIAL = None

KX_RANDOMACT_FLOAT_NORMAL = None

KX_RANDOMACT_FLOAT_UNIFORM = None

KX_RANDOMACT_INT_CONST = None

KX_RANDOMACT_INT_POISSON = None

KX_RANDOMACT_INT_UNIFORM = None

KX_RAY_AXIS_NEG_X = None

KX_RAY_AXIS_NEG_Y = None

KX_RAY_AXIS_NEG_Z = None

KX_RAY_AXIS_POS_X = None

KX_RAY_AXIS_POS_Y = None

KX_RAY_AXIS_POS_Z = None

KX_SCENE_ADD_BACK_SCENE = None

KX_SCENE_ADD_FRONT_SCENE = None

KX_SCENE_REMOVE_SCENE = None

KX_SCENE_RESTART = None

KX_SCENE_RESUME = None

KX_SCENE_SET_CAMERA = None

KX_SCENE_SET_SCENE = None

KX_SCENE_SUSPEND = None

KX_SENSOR_ACTIVE = None

KX_SENSOR_INACTIVE = None

KX_SENSOR_JUST_ACTIVATED = None

KX_SENSOR_JUST_DEACTIVATED = None

KX_SOUNDACT_LOOPBIDIRECTIONAL = None
''' :value: 5
'''

KX_SOUNDACT_LOOPBIDIRECTIONAL_STOP = None
''' :value: 6
'''

KX_SOUNDACT_LOOPEND = None
''' :value: 4
'''

KX_SOUNDACT_LOOPSTOP = None
''' :value: 3
'''

KX_SOUNDACT_PLAYEND = None
''' :value: 2
'''

KX_SOUNDACT_PLAYSTOP = None
''' :value: 1
'''

KX_STATE1 = None

KX_STATE10 = None

KX_STATE11 = None

KX_STATE12 = None

KX_STATE13 = None

KX_STATE14 = None

KX_STATE15 = None

KX_STATE16 = None

KX_STATE17 = None

KX_STATE18 = None

KX_STATE19 = None

KX_STATE2 = None

KX_STATE20 = None

KX_STATE21 = None

KX_STATE22 = None

KX_STATE23 = None

KX_STATE24 = None

KX_STATE25 = None

KX_STATE26 = None

KX_STATE27 = None

KX_STATE28 = None

KX_STATE29 = None

KX_STATE3 = None

KX_STATE30 = None

KX_STATE4 = None

KX_STATE5 = None

KX_STATE6 = None

KX_STATE7 = None

KX_STATE8 = None

KX_STATE9 = None

KX_STATE_OP_CLR = None
''' Substract bits to state mask :value: 0
'''

KX_STATE_OP_CPY = None
''' Copy state mask :value: 1
'''

KX_STATE_OP_NEG = None
''' Invert bits to state mask :value: 2
'''

KX_STATE_OP_SET = None
''' Add bits to state mask :value: 3
'''

KX_STEERING_FLEE = None
''' :value: 2
'''

KX_STEERING_PATHFOLLOWING = None
''' :value: 3
'''

KX_STEERING_SEEK = None
''' :value: 1
'''

KX_TRACK_TRAXIS_NEG_X = None

KX_TRACK_TRAXIS_NEG_Y = None

KX_TRACK_TRAXIS_NEG_Z = None

KX_TRACK_TRAXIS_POS_X = None

KX_TRACK_TRAXIS_POS_Y = None

KX_TRACK_TRAXIS_POS_Z = None

KX_TRACK_UPAXIS_POS_X = None

KX_TRACK_UPAXIS_POS_Y = None

KX_TRACK_UPAXIS_POS_Z = None

KX_TRUE = None
''' True value used by some modules.
'''

MODELMATRIX = None

MODELMATRIX_INVERSE = None

MODELMATRIX_INVERSETRANSPOSE = None

MODELMATRIX_TRANSPOSE = None

MODELVIEWMATRIX = None

MODELVIEWMATRIX_INVERSE = None

MODELVIEWMATRIX_INVERSETRANSPOSE = None

MODELVIEWMATRIX_TRANSPOSE = None

RAS_2DFILTER_BLUR = None
''' :value: 2
'''

RAS_2DFILTER_CUSTOMFILTER = None
''' Customer filter, the code code is set via shaderText property. :value: 12
'''

RAS_2DFILTER_DILATION = None
''' :value: 4
'''

RAS_2DFILTER_DISABLED = None
''' Disable the filter that is currently active :value: -1
'''

RAS_2DFILTER_ENABLED = None
''' Enable the filter that was previously disabled :value: -2
'''

RAS_2DFILTER_EROSION = None
''' :value: 5
'''

RAS_2DFILTER_GRAYSCALE = None
''' :value: 9
'''

RAS_2DFILTER_INVERT = None
''' :value: 11
'''

RAS_2DFILTER_LAPLACIAN = None
''' :value: 6
'''

RAS_2DFILTER_MOTIONBLUR = None
''' Create and enable preset filters :value: 1
'''

RAS_2DFILTER_NOFILTER = None
''' Disable and destroy the filter that is currently active :value: 0
'''

RAS_2DFILTER_PREWITT = None
''' :value: 8
'''

RAS_2DFILTER_SEPIA = None
''' :value: 10
'''

RAS_2DFILTER_SHARPEN = None
''' :value: 3
'''

RAS_2DFILTER_SOBEL = None
''' :value: 7
'''

RM_POLYS = None
''' Draw only polygons.
'''

RM_TRIS = None
''' Draw triangle mesh.
'''

RM_WALLS = None
''' Draw only the walls.
'''

ROT_MODE_QUAT = None
''' Use quaternion in rotation attribute to update bone rotation. :value: 0
'''

ROT_MODE_XYZ = None
''' Use euler_rotation and apply angles on bone's Z, Y, X axis successively. :value: 1
'''

ROT_MODE_XZY = None
''' Use euler_rotation and apply angles on bone's Y, Z, X axis successively. :value: 2
'''

ROT_MODE_YXZ = None
''' Use euler_rotation and apply angles on bone's Z, X, Y axis successively. :value: 3
'''

ROT_MODE_YZX = None
''' Use euler_rotation and apply angles on bone's X, Z, Y axis successively. :value: 4
'''

ROT_MODE_ZXY = None
''' Use euler_rotation and apply angles on bone's Y, X, Z axis successively. :value: 5
'''

ROT_MODE_ZYX = None
''' Use euler_rotation and apply angles on bone's X, Y, Z axis successively. :value: 6
'''

SHD_TANGENT = None

VIEWMATRIX = None

VIEWMATRIX_INVERSE = None

VIEWMATRIX_INVERSETRANSPOSE = None

VIEWMATRIX_TRANSPOSE = None

globalDict = None
''' A dictionary that is saved between loading blend files so you can use it to store inventory and other variables you want to store between scenes and blend files. It can also be written to a file and loaded later on with the game load/save actuators.
'''

joysticks: list = None
''' A list of attached ~bge.types.SCA_PythonJoystick . The list size is the maximum number of supported joysticks. If no joystick is available for a given slot, the slot is set to None.
'''

keyboard = None
''' The current keyboard wrapped in an ~bge.types.SCA_PythonKeyboard object.
'''

mouse = None
''' The current mouse wrapped in an ~bge.types.SCA_PythonMouse object.
'''
