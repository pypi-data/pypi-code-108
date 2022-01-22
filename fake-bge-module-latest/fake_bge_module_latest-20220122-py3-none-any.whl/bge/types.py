import sys
import typing
import mathutils
import bpy.context
import bpy.types
import aud


class BL_ArmatureBone:
    ''' Proxy to Blender bone structure. All fields are read-only and comply to RNA names. All space attribute correspond to the rest pose.
    '''

    name: str = None
    ''' bone name.

    :type: str
    '''

    connected: bool = None
    ''' true when the bone head is struck to the parent's tail.

    :type: bool
    '''

    hinge: bool = None
    ''' true when bone doesn't inherit rotation or scale from parent bone.

    :type: bool
    '''

    inherit_scale: bool = None
    ''' true when bone inherits scaling from parent bone.

    :type: bool
    '''

    bbone_segments = None
    ''' number of B-bone segments.'''

    roll: float = None
    ''' bone rotation around head-tail axis.

    :type: float
    '''

    head = None
    ''' location of head end of the bone in parent bone space.'''

    tail = None
    ''' location of head end of the bone in parent bone space.'''

    length: float = None
    ''' bone length.

    :type: float
    '''

    arm_head = None
    ''' location of head end of the bone in armature space.'''

    arm_tail = None
    ''' location of tail end of the bone in armature space.'''

    arm_mat = None
    ''' matrix of the bone head in armature space.'''

    bone_mat = None
    ''' rotation matrix of the bone in parent bone space.'''

    parent = None
    ''' parent bone, or None for root bone.'''

    children: list = None
    ''' list of bone's children.

    :type: list
    '''


class BL_ArmatureChannel:
    ''' Proxy to armature pose channel. Allows to read and set armature pose. The attributes are identical to RNA attributes, but mostly in read-only mode.
    '''

    name: str = None
    ''' channel name (=bone name), read-only.

    :type: str
    '''

    bone = None
    ''' return the bone object corresponding to this pose channel, read-only.'''

    parent = None
    ''' return the parent channel object, None if root channel, read-only.'''

    has_ik: bool = None
    ''' true if the bone is part of an active IK chain, read-only. This flag is not set when an IK constraint is defined but not enabled (miss target information for example).

    :type: bool
    '''

    ik_dof_x: bool = None
    ''' true if the bone is free to rotation in the X axis, read-only.

    :type: bool
    '''

    ik_dof_y: bool = None
    ''' true if the bone is free to rotation in the Y axis, read-only.

    :type: bool
    '''

    ik_dof_z: bool = None
    ''' true if the bone is free to rotation in the Z axis, read-only.

    :type: bool
    '''

    ik_limit_x: bool = None
    ''' true if a limit is imposed on X rotation, read-only.

    :type: bool
    '''

    ik_limit_y: bool = None
    ''' true if a limit is imposed on Y rotation, read-only.

    :type: bool
    '''

    ik_limit_z: bool = None
    ''' true if a limit is imposed on Z rotation, read-only.

    :type: bool
    '''

    ik_rot_control: bool = None
    ''' true if channel rotation should applied as IK constraint, read-only.

    :type: bool
    '''

    ik_lin_control: bool = None
    ''' true if channel size should applied as IK constraint, read-only.

    :type: bool
    '''

    location = None
    ''' displacement of the bone head in armature local space, read-write.'''

    scale = None
    ''' scale of the bone relative to its parent, read-write.'''

    rotation_quaternion = None
    ''' rotation of the bone relative to its parent expressed as a quaternion, read-write.'''

    rotation_euler = None
    ''' rotation of the bone relative to its parent expressed as a set of euler angles, read-write.'''

    rotation_mode = None
    ''' Method of updating the bone rotation, read-write.'''

    channel_matrix = None
    ''' pose matrix in bone space (deformation of the bone due to action, constraint, etc), Read-only. This field is updated after the graphic render, it represents the current pose.'''

    pose_matrix = None
    ''' pose matrix in armature space, read-only, This field is updated after the graphic render, it represents the current pose.'''

    pose_head = None
    ''' position of bone head in armature space, read-only.'''

    pose_tail = None
    ''' position of bone tail in armature space, read-only.'''

    ik_min_x: float = None
    ''' minimum value of X rotation in degree (<= 0) when X rotation is limited (see ik_limit_x), read-only.

    :type: float
    '''

    ik_max_x: float = None
    ''' maximum value of X rotation in degree (>= 0) when X rotation is limited (see ik_limit_x), read-only.

    :type: float
    '''

    ik_min_y: float = None
    ''' minimum value of Y rotation in degree (<= 0) when Y rotation is limited (see ik_limit_y), read-only.

    :type: float
    '''

    ik_max_y: float = None
    ''' maximum value of Y rotation in degree (>= 0) when Y rotation is limited (see ik_limit_y), read-only.

    :type: float
    '''

    ik_min_z: float = None
    ''' minimum value of Z rotation in degree (<= 0) when Z rotation is limited (see ik_limit_z), read-only.

    :type: float
    '''

    ik_max_z: float = None
    ''' maximum value of Z rotation in degree (>= 0) when Z rotation is limited (see ik_limit_z), read-only.

    :type: float
    '''

    ik_stiffness_x: float = None
    ''' bone rotation stiffness in X axis, read-only.

    :type: float
    '''

    ik_stiffness_y: float = None
    ''' bone rotation stiffness in Y axis, read-only.

    :type: float
    '''

    ik_stiffness_z: float = None
    ''' bone rotation stiffness in Z axis, read-only.

    :type: float
    '''

    ik_stretch: float = None
    ''' ratio of scale change that is allowed, 0=bone can't change size, read-only.

    :type: float
    '''

    ik_rot_weight: float = None
    ''' weight of rotation constraint when ik_rot_control is set, read-write.

    :type: float
    '''

    ik_lin_weight: float = None
    ''' weight of size constraint when ik_lin_control is set, read-write.

    :type: float
    '''

    joint_rotation = None
    ''' Control bone rotation in term of joint angle (for robotic applications), read-write. When writing to this attribute, you pass a [x, y, z] vector and an appropriate set of euler angles or quaternion is calculated according to the rotation_mode. When you read this attribute, the current pose matrix is converted into a [x, y, z] vector representing the joint angles. The value and the meaning of the x, y, z depends on the ik_dof_x/ik_dof_y/ik_dof_z attributes: * 1DoF joint X, Y or Z: the corresponding x, y, or z value is used an a joint angle in radiant * 2DoF joint X+Y or Z+Y: treated as 2 successive 1DoF joints: first X or Z, then Y. The x or z value is used as a joint angle in radiant along the X or Z axis, followed by a rotation along the new Y axis of y radiants. * 2DoF joint X+Z: treated as a 2DoF joint with rotation axis on the X/Z plane. The x and z values are used as the coordinates of the rotation vector in the X/Z plane. * 3DoF joint X+Y+Z: treated as a revolute joint. The [x, y, z] vector represents the equivalent rotation vector to bring the joint from the rest pose to the new pose.'''


class BL_ArmatureConstraint:
    ''' Proxy to Armature Constraint. Allows to change constraint on the fly. Obtained through ~bge.types.BL_ArmatureObject .constraints.
    '''

    type = None
    ''' Type of constraint, (read-only). Use one of :ref: these constants<armatureconstraint-constants-type> .'''

    name: str = None
    ''' Name of constraint constructed as <bone_name>:<constraint_name>. constraints list. This name is also the key subscript on ~bge.types.BL_ArmatureObject .

    :type: str
    '''

    enforce: float = None
    ''' fraction of constraint effect that is enforced. Between 0 and 1.

    :type: float
    '''

    headtail = None
    ''' Position of target between head and tail of the target bone: 0=head, 1=tail.'''

    lin_error: float = None
    ''' runtime linear error (in Blender units) on constraint at the current frame. This is a runtime value updated on each frame by the IK solver. Only available on IK constraint and iTaSC solver.

    :type: float
    '''

    rot_error = None
    ''' Runtime rotation error (in radiant) on constraint at the current frame. This is a runtime value updated on each frame by the IK solver. Only available on IK constraint and iTaSC solver. It is only set if the constraint has a rotation part, for example, a CopyPose+Rotation IK constraint.'''

    target = None
    ''' Primary target object for the constraint. The position of this object in the GE will be used as target for the constraint.'''

    subtarget = None
    ''' Secondary target object for the constraint. The position of this object in the GE will be used as secondary target for the constraint. Currently this is only used for pole target on IK constraint.'''

    active: bool = None
    ''' True if the constraint is active.

    :type: bool
    '''

    ik_weight: float = None
    ''' Weight of the IK constraint between 0 and 1. Only defined for IK constraint.

    :type: float
    '''

    ik_type = None
    ''' Type of IK constraint, (read-only). Use one of :ref: these constants<armatureconstraint-constants-ik-type> .'''

    ik_flag = None
    ''' Combination of IK constraint option flags, read-only. Use one of :ref: these constants<armatureconstraint-constants-ik-flag> .'''

    ik_dist: float = None
    ''' Distance the constraint is trying to maintain with target, only used when ik_type=CONSTRAINT_IK_DISTANCE.

    :type: float
    '''

    ik_mode = None
    ''' Use one of :ref: these constants<armatureconstraint-constants-ik-mode> . Additional mode for IK constraint. Currently only used for Distance constraint:'''


class BL_ArmatureObject:
    ''' An armature object.
    '''

    constraints: list = None
    ''' The list of armature constraint defined on this armature. Elements of the list can be accessed by index or string. The key format for string access is '<bone_name>:<constraint_name>'.

    :type: list
    '''

    channels: list = None
    ''' The list of armature channels. Elements of the list can be accessed by index or name the bone.

    :type: list
    '''

    def update(self):
        ''' Ensures that the armature will be updated on next graphic frame. This action is unecessary if a KX_ArmatureActuator with mode run is active or if an action is playing. Use this function in other cases. It must be called on each frame to ensure that the armature is updated continously.

        '''
        pass

    def draw(self):
        ''' Draw lines that represent armature to view it in real time.

        '''
        pass


class BL_Shader:
    ''' BL_Shader is a class used to compile and use custom shaders scripts. This header set the #version directive, so the user must not define his own #version . Since 0.3.0, this class is only used with custom 2D filters.
    '''

    enabled: bool = None
    ''' Set shader enabled to use.

    :type: bool
    '''

    objectCallbacks = None
    ''' '''

    bindCallbacks = None
    ''' '''

    def setUniformfv(self, name: str, fList):
        ''' Set a uniform with a list of float values

        :param name: the uniform name
        :type name: str
        :param fList: a list (2, 3 or 4 elements) of float values
        :type fList: 
        '''
        pass

    def delSource(self):
        ''' 

        '''
        pass

    def getFragmentProg(self) -> str:
        ''' Returns the fragment program.

        :rtype: str
        :return: The fragment program.
        '''
        pass

    def getVertexProg(self) -> str:
        ''' Get the vertex program.

        :rtype: str
        :return: The vertex program.
        '''
        pass

    def isValid(self) -> bool:
        ''' Check if the shader is valid.

        :rtype: bool
        :return: True if the shader is valid
        '''
        pass

    def setAttrib(self, enum):
        ''' 

        '''
        pass

    def setSampler(self, name: str, index):
        ''' Set uniform texture sample index.

        :param name: Uniform name
        :type name: str
        :param index: Texture sample index.
        :type index: 
        '''
        pass

    def setSource(self, vertexProgram, fragmentProgram, apply):
        ''' 

        '''
        pass

    def setSourceList(self, sources, apply):
        ''' 

        '''
        pass

    def setUniform1f(self, name: str, fx: float):
        ''' Set a uniform with 1 float value.

        :param name: the uniform name
        :type name: str
        :param fx: Uniform value
        :type fx: float
        '''
        pass

    def setUniform1i(self, name: str, ix):
        ''' Set a uniform with an integer value.

        :param name: the uniform name
        :type name: str
        :param ix: the uniform value
        :type ix: 
        '''
        pass

    def setUniform2f(self, name: str, fx: float, fy: float):
        ''' Set a uniform with 2 float values

        :param name: the uniform name
        :type name: str
        :param fx: first float value
        :type fx: float
        :param fy: second float value
        :type fy: float
        '''
        pass

    def setUniform2i(self, name: str, ix, iy):
        ''' Set a uniform with 2 integer values

        :param name: the uniform name
        :type name: str
        :param ix: first integer value
        :type ix: 
        :param iy: second integer value
        :type iy: 
        '''
        pass

    def setUniform3f(self, name: str, fx: float, fy: float, fz: float):
        ''' Set a uniform with 3 float values.

        :param name: the uniform name
        :type name: str
        :param fx: first float value
        :type fx: float
        :param fy: second float value
        :type fy: float
        :param fz: third float value
        :type fz: float
        '''
        pass

    def setUniform3i(self, name: str, ix, iy, iz):
        ''' Set a uniform with 3 integer values

        :param name: the uniform name
        :type name: str
        :param ix: first integer value
        :type ix: 
        :param iy: second integer value
        :type iy: 
        :param iz: third integer value
        :type iz: 
        '''
        pass

    def setUniform4f(self, name: str, fx: float, fy: float, fz: float,
                     fw: float):
        ''' Set a uniform with 4 float values.

        :param name: the uniform name
        :type name: str
        :param fx: first float value
        :type fx: float
        :param fy: second float value
        :type fy: float
        :param fz: third float value
        :type fz: float
        :param fw: fourth float value
        :type fw: float
        '''
        pass

    def setUniform4i(self, name: str, ix, iy, iz, iw):
        ''' Set a uniform with 4 integer values

        :param name: the uniform name
        :type name: str
        :param ix: first integer value
        :type ix: 
        :param iy: second integer value
        :type iy: 
        :param iz: third integer value
        :type iz: 
        :param iw: fourth integer value
        :type iw: 
        '''
        pass

    def setUniformDef(self, name: str, type):
        ''' Define a new uniform

        :param name: the uniform name
        :type name: str
        :param type: these constants <shader-defined-uniform>
        :type type: 
        '''
        pass

    def setUniformMatrix3(self, name: str, mat, transpose: bool):
        ''' Set a uniform with a 3x3 matrix value

        :param name: the uniform name
        :type name: str
        :param mat: A 3x3 matrix [[f, f, f], [f, f, f], [f, f, f]]
        :type mat: 
        :param transpose: set to True to transpose the matrix
        :type transpose: bool
        '''
        pass

    def setUniformMatrix4(self, name: str, mat, transpose: bool):
        ''' Set a uniform with a 4x4 matrix value

        :param name: the uniform name
        :type name: str
        :param mat: A 4x4 matrix [[f, f, f, f], [f, f, f, f], [f, f, f, f], [f, f, f, f]]
        :type mat: 
        :param transpose: set to True to transpose the matrix
        :type transpose: bool
        '''
        pass

    def setUniformiv(self, name: str, iList):
        ''' Set a uniform with a list of integer values

        :param name: the uniform name
        :type name: str
        :param iList: a list (2, 3 or 4 elements) of integer values
        :type iList: 
        '''
        pass

    def setUniformEyef(self, name):
        ''' 

        '''
        pass

    def validate(self):
        ''' Validate the shader object.

        '''
        pass


class EXP_ListValue:
    ''' This is a list like object used in the game engine internally that behaves similar to a python list in most ways. As well as the normal index lookup ( val= clist[i] ), EXP_ListValue supports string lookups ( val= scene.objects["Cube"] ) Other operations such as len(clist) , list(clist) , clist[0:10] are also supported.
    '''

    def append(self, val):
        ''' Add an item to the list (like pythons append)

        '''
        pass

    def count(self, val):
        ''' Count the number of instances of a value in the list.

        :return: number of instances
        '''
        pass

    def index(self, val):
        ''' Return the index of a value in the list.

        :return: The index of the value in the list.
        '''
        pass

    def reverse(self):
        ''' Reverse the order of the list.

        '''
        pass

    def get(self, key, default=None):
        ''' Return the value matching key, or the default value if its not found.

        '''
        pass

    def filter(self, name, prop):
        ''' Return a list of items with name matching name regex and with a property matching prop regex. If name is empty every items are checked, if prop is empty no property check is proceeded.

        '''
        pass

    def from_id(self, id):
        ''' This is a funtion especially for the game engine to return a value with a spesific id. Since object names are not always unique, the id of an object can be used to get an object from the CValueList. Example: Where myObID is an int or long from the id function. This has the advantage that you can store the id in places you could not store a gameObject.

        '''
        pass


class EXP_PropValue:
    ''' This class has no python functions
    '''

    pass


class EXP_PyObjectPlus:
    ''' EXP_PyObjectPlus base class of most other types in the Game Engine.
    '''

    invalid: bool = None
    ''' Test if the object has been freed by the game engine and is no longer valid. Normally this is not a problem but when storing game engine data in the GameLogic module, KX_Scenes or other KX_GameObjects its possible to hold a reference to invalid data. Calling an attribute or method on an invalid object will raise a SystemError. The invalid attribute allows testing for this case without exception handling.

    :type: bool
    '''


class EXP_Value:
    ''' This class is a basis for other classes.
    '''

    name: str = None
    ''' The name of this EXP_Value derived object (read-only).

    :type: str
    '''


class KX_2DFilter:
    ''' 2D filter shader object. Can be alterated with ~bge.types.BL_Shader 's functions.
    '''

    mipmap: bool = None
    ''' Request mipmap generation of the render bgl_RenderedTexture texture. Accessing mipmapping level is similar to:

    :type: bool
    '''

    offScreen = None
    ''' The custom off screen (framebuffer in 0.3.0) the filter render to (read-only).'''

    def setTexture(self, index, bindCode, samplerName: str = ""):
        ''' Set specified texture bind code :data: bindCode in specified slot :data: index . Any call to :data: setTexture should be followed by a call to :data: BL_Shader.setSampler <bge.types.BL_Shader.setSampler> with the same :data: index if :data: sampleName is not specified.

        :param index: The texture slot.
        :type index: 
        :param bindCode: The texture bind code/Id.
        :type bindCode: 
        :param samplerName: samplerName is passed in the function. (optional)
        :type samplerName: str
        '''
        pass

    def setCubeMap(self, index, bindCode, samplerName: str = ""):
        ''' Set specified cube map texture bind code :data: bindCode in specified slot :data: index . Any call to :data: setCubeMap should be followed by a call to :data: BL_Shader.setSampler <bge.types.BL_Shader.setSampler> with the same :data: index if :data: sampleName is not specified.

        :param index: The texture slot.
        :type index: 
        :param bindCode: The cube map texture bind code/Id.
        :type bindCode: 
        :param samplerName: samplerName is passed in the function. (optional)
        :type samplerName: str
        '''
        pass

    def addOffScreen(self,
                     slots,
                     width=None,
                     height=None,
                     mipmap: bool = False):
        ''' Register a custom off screen (framebuffer in 0.3.0) to render the filter to.

        :param slots: The number of color texture attached to the off screen, between 0 and 8 excluded.
        :type slots: 
        :param width: In 0.3.0, always canvas width (optional).
        :type width: 
        :param height: In 0.3.0, always canvas height (optional).
        :type height: 
        :param mipmap: True if the color texture generate mipmap at the end of the filter rendering (optional).
        :type mipmap: bool
        '''
        pass

    def removeOffScreen(self):
        ''' Unregister the custom off screen (framebuffer in 0.3.0) the filter render to.

        '''
        pass


class KX_2DFilterFrameBuffer:
    ''' 2D filter custom off screen (framebuffer in 0.3.0).
    '''

    width = None
    ''' The off screen width, always canvas width in 0.3.0 (read-only).'''

    height = None
    ''' The off screen height, always canvas height in 0.3.0 (read-only).'''

    colorBindCodes: list = None
    ''' The bind code of the color textures attached to the off screen (read-only).

    :type: list
    '''

    depthBindCode = None
    ''' The bind code of the depth texture attached to the off screen (read-only).'''


class KX_2DFilterManager:
    ''' 2D filter manager used to add, remove and find filters in a scene.
    '''

    def addFilter(self, index, type, fragmentProgram: str):
        ''' Add a filter to the pass index :data: index , type :data: type and fragment program if custom filter.

        :param index: The filter pass index.
        :type index: 
        :param type: * :data: bge.logic.RAS_2DFILTER_BLUR * :data: bge.logic.RAS_2DFILTER_DILATION * :data: bge.logic.RAS_2DFILTER_EROSION * :data: bge.logic.RAS_2DFILTER_SHARPEN * :data: bge.logic.RAS_2DFILTER_LAPLACIAN * :data: bge.logic.RAS_2DFILTER_PREWITT * :data: bge.logic.RAS_2DFILTER_SOBEL * :data: bge.logic.RAS_2DFILTER_GRAYSCALE * :data: bge.logic.RAS_2DFILTER_SEPIA * :data: bge.logic.RAS_2DFILTER_CUSTOMFILTER
        :type type: 
        :param fragmentProgram: The filter shader fragment program. Specified only if :data: type is :data: bge.logic.RAS_2DFILTER_CUSTOMFILTER . (optional)
        :type fragmentProgram: str
        :return: The 2D Filter.
        '''
        pass

    def removeFilter(self, index):
        ''' Remove filter to the pass index :data: index .

        :param index: The filter pass index.
        :type index: 
        '''
        pass

    def getFilter(self, index):
        ''' Return filter to the pass index :data: index . :warning: If the 2D Filter is added with a ~bge.types.SCA_2DFilterActuator , the filter will be available only after the 2D Filter program is linked. The python script to get the filter has to be executed one frame later. A delay sensor can be used.

        :param index: The filter pass index.
        :type index: 
        :return: The filter in the specified pass index or None.
        '''
        pass


class KX_BlenderMaterial:
    ''' This is kept for backward compatibility with some scripts.
    '''

    textures: list = None
    ''' List of all material's textures (read only).

    :type: list
    '''

    blenderMaterial = None
    ''' ~bpy.types.Material corresponding to this KX_BlenderMaterial (read only).'''


class KX_Camera:
    ''' A Camera object.
    '''

    INSIDE = None
    ''' See :data: sphereInsideFrustum and :data: boxInsideFrustum'''

    INTERSECT = None
    ''' See :data: sphereInsideFrustum and :data: boxInsideFrustum'''

    OUTSIDE = None
    ''' See :data: sphereInsideFrustum and :data: boxInsideFrustum'''

    lens: float = None
    ''' The camera's lens value.

    :type: float
    '''

    lodDistanceFactor: float = None
    ''' The factor to multiply distance to camera to adjust levels of detail. A float < 1.0f will make the distance to camera used to compute levels of detail decrease.

    :type: float
    '''

    fov: float = None
    ''' The camera's field of view value.

    :type: float
    '''

    ortho_scale: float = None
    ''' The camera's view scale when in orthographic mode.

    :type: float
    '''

    near: float = None
    ''' The camera's near clip distance.

    :type: float
    '''

    far: float = None
    ''' The camera's far clip distance.

    :type: float
    '''

    shift_x: float = None
    ''' The camera's horizontal shift.

    :type: float
    '''

    shift_y: float = None
    ''' The camera's vertical shift.

    :type: float
    '''

    perspective: bool = None
    ''' True if this camera has a perspective transform, False for an orthographic projection.

    :type: bool
    '''

    projection_matrix: 'mathutils.Matrix' = None
    ''' This camera's 4x4 projection matrix.

    :type: 'mathutils.Matrix'
    '''

    modelview_matrix: 'mathutils.Matrix' = None
    ''' This camera's 4x4 model view matrix. (read-only).

    :type: 'mathutils.Matrix'
    '''

    camera_to_world: 'mathutils.Matrix' = None
    ''' This camera's camera to world transform. (read-only).

    :type: 'mathutils.Matrix'
    '''

    world_to_camera: 'mathutils.Matrix' = None
    ''' This camera's world to camera transform. (read-only).

    :type: 'mathutils.Matrix'
    '''

    useViewport: bool = None
    ''' True when the camera is used as a viewport, set True to enable a viewport for this camera.

    :type: bool
    '''

    activityCulling: bool = None
    ''' True if this camera is used to compute object distance for object activity culling.

    :type: bool
    '''

    def sphereInsideFrustum(self, centre: list, radius: float):
        ''' Tests the given sphere against the view frustum.

        :param centre: The centre of the sphere (in world coordinates.)
        :type centre: list
        :param radius: the radius of the sphere
        :type radius: float
        :return: ~bge.types.KX_Camera.INTERSECT
        '''
        pass

    def boxInsideFrustum(self, box: list):
        ''' Tests the given box against the view frustum.

        :param box: Eight (8) corner points of the box (in world coordinates.)
        :type box: list
        '''
        pass

    def pointInsideFrustum(self, point: 'mathutils.Vector') -> bool:
        ''' Tests the given point against the view frustum.

        :param point: The point to test (in world coordinates.)
        :type point: 'mathutils.Vector'
        :rtype: bool
        :return: True if the given point is inside this camera's viewing frustum.
        '''
        pass

    def getCameraToWorld(self) -> list:
        ''' Returns the camera-to-world transform.

        :rtype: list
        :return: the camera-to-world transform matrix.
        '''
        pass

    def getWorldToCamera(self) -> list:
        ''' Returns the world-to-camera transform. This returns the inverse matrix of getCameraToWorld().

        :rtype: list
        :return: the world-to-camera transform matrix.
        '''
        pass

    def setOnTop(self):
        ''' Set this cameras viewport ontop of all other viewport.

        '''
        pass

    def setViewport(self, left, bottom, right, top):
        ''' Sets the region of this viewport on the screen in pixels. Use :data: bge.render.getWindowHeight and :data: bge.render.getWindowWidth to calculate values relative to the entire display.

        :param left: left pixel coordinate of this viewport
        :type left: 
        :param bottom: bottom pixel coordinate of this viewport
        :type bottom: 
        :param right: right pixel coordinate of this viewport
        :type right: 
        :param top: top pixel coordinate of this viewport
        :type top: 
        '''
        pass

    def getScreenPosition(self, object: 'mathutils.Vector') -> list:
        ''' Gets the position of an object projected on screen space.

        :param object: object name or list [x, y, z]
        :type object: 'mathutils.Vector'
        :rtype: list
        :return: the object's position in screen coordinates.
        '''
        pass

    def getScreenVect(self, x: float, y: float) -> 'mathutils.Vector':
        ''' Gets the vector from the camera position in the screen coordinate direction.

        :param x: X Axis
        :type x: float
        :param y: Y Axis
        :type y: float
        :rtype: 'mathutils.Vector'
        :return: The vector from screen coordinate.
        '''
        pass

    def getScreenRay(self,
                     x: float,
                     y: float,
                     dist: float = 'inf',
                     property: str = None):
        ''' Look towards a screen coordinate (x, y) and find first object hit within dist that matches prop. The ray is similar to KX_GameObject->rayCastTo.

        :param x: X Axis
        :type x: float
        :param y: Y Axis
        :type y: float
        :param dist: max distance to look (can be negative => look behind); 0 or omitted => detect up to other
        :type dist: float
        :param property: property name that object must have; can be omitted => detect any object
        :type property: str
        :return: the first object hit or None if no object or object does not match prop
        '''
        pass


class KX_CharacterWrapper:
    ''' A wrapper to expose character physics options.
    '''

    onGround: bool = None
    ''' Whether or not the character is on the ground. (read-only)

    :type: bool
    '''

    gravity = None
    ''' The gravity vector used for the character.'''

    fallSpeed: float = None
    ''' The character falling speed.

    :type: float
    '''

    maxJumps: int = None
    ''' The maximum number of jumps a character can perform before having to touch the ground. By default this is set to 1. 2 allows for a double jump, etc.

    :type: int
    '''

    jumpCount: int = None
    ''' The current jump count. This can be used to have different logic for a single jump versus a double jump. For example, a different animation for the second jump.

    :type: int
    '''

    jumpSpeed: float = None
    ''' The character jumping speed.

    :type: float
    '''

    maxSlope: float = None
    ''' The maximum slope which the character can climb.

    :type: float
    '''

    walkDirection = None
    ''' The speed and direction the character is traveling in using world coordinates. This should be used instead of applyMovement() to properly move the character.'''

    def jump(self):
        ''' The character jumps based on it's jump speed.

        '''
        pass

    def setVelocity(self,
                    velocity: 'mathutils.Vector',
                    time: float,
                    local: bool = False):
        ''' Sets the character's linear velocity for a given period. This method sets character's velocity through it's center of mass during a period.

        :param velocity: Linear velocity vector.
        :type velocity: 'mathutils.Vector'
        :param time: Period while applying linear velocity.
        :type time: float
        :param local: * False: you get the "global" velocity ie: relative to world orientation. * True: you get the "local" velocity ie: relative to object orientation.
        :type local: bool
        '''
        pass

    def reset(self):
        ''' Resets the character velocity and walk direction.

        '''
        pass


class KX_CollisionContactPoint:
    ''' A collision contact point passed to the collision callbacks.
    '''

    localPointA: 'mathutils.Vector' = None
    ''' The contact point in the owner object space.

    :type: 'mathutils.Vector'
    '''

    localPointB: 'mathutils.Vector' = None
    ''' The contact point in the collider object space.

    :type: 'mathutils.Vector'
    '''

    worldPoint: 'mathutils.Vector' = None
    ''' The contact point in world space.

    :type: 'mathutils.Vector'
    '''

    normal: 'mathutils.Vector' = None
    ''' The contact normal in owner object space.

    :type: 'mathutils.Vector'
    '''

    combinedFriction: float = None
    ''' The combined friction of the owner and collider object.

    :type: float
    '''

    combinedRollingFriction: float = None
    ''' The combined rolling friction of the owner and collider object.

    :type: float
    '''

    combinedRestitution: float = None
    ''' The combined restitution of the owner and collider object.

    :type: float
    '''

    appliedImpulse: float = None
    ''' The applied impulse to the owner object.

    :type: float
    '''


class KX_ConstraintWrapper:
    ''' KX_ConstraintWrapper
    '''

    constraint_id = None
    ''' Returns the contraint ID (read only)'''

    constraint_type = None
    ''' Returns the contraint type (read only) - ~bge.constraints.POINTTOPOINT_CONSTRAINT - ~bge.constraints.LINEHINGE_CONSTRAINT - ~bge.constraints.ANGULAR_CONSTRAINT - ~bge.constraints.CONETWIST_CONSTRAINT - ~bge.constraints.VEHICLE_CONSTRAINT - ~bge.constraints.GENERIC_6DOF_CONSTRAINT'''

    breakingThreshold: float = None
    ''' The impulse threshold breaking the constraint, if the constraint is broken :data: enabled is set to False .

    :type: float
    '''

    enabled: bool = None
    ''' The status of the constraint. Set to True to restore a constraint after breaking.

    :type: bool
    '''

    def getConstraintId(self, val):
        ''' Returns the contraint ID

        :return: the constraint ID
        '''
        pass

    def setParam(self, axis, value0: float, value1: float):
        ''' Set the contraint limits For PHY_LINEHINGE_CONSTRAINT = 2 or PHY_ANGULAR_CONSTRAINT = 3: axis = 3 is a constraint limit, with low/high limit value * 3: X axis angle For PHY_CONE_TWIST_CONSTRAINT = 4: axis = 3..5 are constraint limits, high limit values * 3: X axis angle * 4: Y axis angle * 5: Z axis angle For PHY_GENERIC_6DOF_CONSTRAINT = 12: axis = 0..2 are constraint limits, with low/high limit value * 0: X axis position * 1: Y axis position * 2: Z axis position axis = 3..5 are relative constraint (Euler) angles in radians * 3: X axis angle * 4: Y axis angle * 5: Z axis angle axis = 6..8 are translational motors, with value0=target velocity, value1 = max motor force * 6: X axis position * 7: Y axis position * 8: Z axis position axis = 9..11 are rotational motors, with value0=target velocity, value1 = max motor force * 9: X axis angle * 10: Y axis angle * 11: Z axis angle axis = 12..14 are for linear springs on each of the position of freedom * 12: X axis position * 13: Y axis position * 14: Z axis position axis = 15..17 are for angular springs on each of the angle of freedom in radians * 15: X axis angle * 16: Y axis angle * 17: Z axis angle

        :param axis: 
        :type axis: 
        :param value0: Set the minimum limit of the axis
        :type value0: float
        :param value1: Set the maximum limit of the axis
        :type value1: float
        :param value0: Set the minimum limit of the axis
        :type value0: float
        :param value1: Set the maximum limit of the axis
        :type value1: float
        :param value0: Set the minimum limit of the axis
        :type value0: float
        :param value1: Set the maximum limit of the axis
        :type value1: float
        :param value0: Set the linear velocity of the axis
        :type value0: float
        :param value1: Set the maximum force limit of the axis
        :type value1: float
        :param value0: Set the stiffness of the spring
        :type value0: float
        :param value1: Tendency of the spring to return to it's original position
        :type value1: float
        '''
        pass

    def getParam(self, axis) -> float:
        ''' Get the contraint position or euler angle of a generic 6DOF constraint axis = 0..2 are linear constraint values * 0: X axis position * 1: Y axis position * 2: Z axis position axis = 3..5 are relative constraint (Euler) angles in radians * 3: X axis angle * 4: Y axis angle * 5: Z axis angle

        :param axis: 
        :type axis: 
        :rtype: float
        :return: angle
        '''
        pass


class KX_FontObject:
    ''' A Font game object. It is possible to use attributes from :type: ~bpy.types.TextCurve
    '''

    pass


class KX_GameObject:
    ''' All game objects are derived from this class. Properties assigned to game objects are accessible as attributes of this class. KX_GameObject can be subclassed to extend functionality. For example: When subclassing objects other than empties and meshes, the specific type should be used - e.g. inherit from ~bge.types.BL_ArmatureObject when the object to mutate is an armature.
    '''

    name: str = None
    ''' The object's name.

    :type: str
    '''

    mass: float = None
    ''' The object's mass

    :type: float
    '''

    friction: float = None
    ''' The object's friction

    :type: float
    '''

    isSuspendDynamics: bool = None
    ''' The object's dynamic state (read-only).

    :type: bool
    '''

    linearDamping: float = None
    ''' The object's linear damping, also known as translational damping. Can be set simultaneously with angular damping using the :py:meth: setDamping method.

    :type: float
    '''

    angularDamping: float = None
    ''' The object's angular damping, also known as rotationation damping. Can be set simultaneously with linear damping using the :py:meth: setDamping method.

    :type: float
    '''

    linVelocityMin: float = None
    ''' Enforces the object keeps moving at a minimum velocity.

    :type: float
    '''

    linVelocityMax: float = None
    ''' Clamp the maximum linear velocity to prevent objects moving beyond a set speed.

    :type: float
    '''

    angularVelocityMin: float = None
    ''' Enforces the object keeps rotating at a minimum velocity. A value of 0.0 disables this.

    :type: float
    '''

    angularVelocityMax: float = None
    ''' Clamp the maximum angular velocity to prevent objects rotating beyond a set speed. A value of 0.0 disables clamping; it does not stop rotation.

    :type: float
    '''

    localInertia = None
    ''' the object's inertia vector in local coordinates. Read only.'''

    parent = None
    ''' The object's parent object. (read-only).'''

    groupMembers = None
    ''' Returns the list of group members if the object is a group object (dupli group instance), otherwise None is returned.'''

    groupObject = None
    ''' Returns the group object (dupli group instance) that the object belongs to or None if the object is not part of a group.'''

    collisionGroup = None
    ''' The object's collision group.'''

    collisionMask = None
    ''' The object's collision mask.'''

    collisionCallbacks: list = None
    ''' A list of functions to be called when a collision occurs. Callbacks should either accept one argument (object) , or four arguments (object, point, normal, points) . For simplicity, per colliding object the first collision point is reported in second and third argument.

    :type: list
    '''

    scene = None
    ''' The object's scene. (read-only).'''

    visible: bool = None
    ''' visibility flag.

    :type: bool
    '''

    layer = None
    ''' '''

    cullingBox = None
    ''' '''

    culled = None
    ''' '''

    color: 'mathutils.Vector' = None
    ''' The object color of the object. [r, g, b, a]

    :type: 'mathutils.Vector'
    '''

    physicsCulling: bool = None
    ''' True if the object suspends its physics depending on its nearest distance to any camera.

    :type: bool
    '''

    logicCulling: bool = None
    ''' True if the object suspends its logic and animation depending on its nearest distance to any camera.

    :type: bool
    '''

    physicsCullingRadius: float = None
    ''' Suspend object's physics if this radius is smaller than its nearest distance to any camera and :data: physicsCulling set to True .

    :type: float
    '''

    logicCullingRadius: float = None
    ''' Suspend object's logic and animation if this radius is smaller than its nearest distance to any camera and :data: logicCulling set to True .

    :type: float
    '''

    occlusion = None
    ''' '''

    position: 'mathutils.Vector' = None
    ''' The object's position. [x, y, z] On write: local position, on read: world position

    :type: 'mathutils.Vector'
    '''

    orientation: 'mathutils.Matrix' = None
    ''' The object's orientation. 3x3 Matrix. You can also write a Quaternion or Euler vector. On write: local orientation, on read: world orientation

    :type: 'mathutils.Matrix'
    '''

    scaling: 'mathutils.Vector' = None
    ''' The object's scaling factor. [sx, sy, sz] On write: local scaling, on read: world scaling

    :type: 'mathutils.Vector'
    '''

    localOrientation: 'mathutils.Matrix' = None
    ''' The object's local orientation. 3x3 Matrix. You can also write a Quaternion or Euler vector.

    :type: 'mathutils.Matrix'
    '''

    worldOrientation: 'mathutils.Matrix' = None
    ''' The object's world orientation. 3x3 Matrix.

    :type: 'mathutils.Matrix'
    '''

    localScale: 'mathutils.Vector' = None
    ''' The object's local scaling factor. [sx, sy, sz]

    :type: 'mathutils.Vector'
    '''

    worldScale: 'mathutils.Vector' = None
    ''' The object's world scaling factor. [sx, sy, sz]

    :type: 'mathutils.Vector'
    '''

    localPosition: 'mathutils.Vector' = None
    ''' The object's local position. [x, y, z]

    :type: 'mathutils.Vector'
    '''

    worldPosition: 'mathutils.Vector' = None
    ''' The object's world position. [x, y, z]

    :type: 'mathutils.Vector'
    '''

    localTransform: 'mathutils.Matrix' = None
    ''' The object's local space transform matrix. 4x4 Matrix.

    :type: 'mathutils.Matrix'
    '''

    worldTransform: 'mathutils.Matrix' = None
    ''' The object's world space transform matrix. 4x4 Matrix.

    :type: 'mathutils.Matrix'
    '''

    localLinearVelocity: 'mathutils.Vector' = None
    ''' The object's local linear velocity. [x, y, z]

    :type: 'mathutils.Vector'
    '''

    worldLinearVelocity: 'mathutils.Vector' = None
    ''' The object's world linear velocity. [x, y, z]

    :type: 'mathutils.Vector'
    '''

    localAngularVelocity: 'mathutils.Vector' = None
    ''' The object's local angular velocity. [x, y, z]

    :type: 'mathutils.Vector'
    '''

    worldAngularVelocity: 'mathutils.Vector' = None
    ''' The object's world angular velocity. [x, y, z]

    :type: 'mathutils.Vector'
    '''

    gravity: 'mathutils.Vector' = None
    ''' The object's gravity. [x, y, z]

    :type: 'mathutils.Vector'
    '''

    timeOffset: float = None
    ''' adjust the slowparent delay at runtime.

    :type: float
    '''

    blenderObject = None
    ''' This KX_GameObject's Object.'''

    state: int = None
    ''' the game object's state bitmask, using the first 30 bits, one bit must always be set.

    :type: int
    '''

    meshes: list = None
    ''' a list meshes for this object.

    :type: list
    '''

    batchGroup = None
    ''' '''

    sensors: list = None
    ''' a sequence of ~bge.types.SCA_ISensor objects with string/index lookups and iterator support.

    :type: list
    '''

    controllers: list = None
    ''' a sequence of ~bge.types.SCA_IController objects with string/index lookups and iterator support.

    :type: list
    '''

    actuators: list = None
    ''' a list of ~bge.types.SCA_IActuator with string/index lookups and iterator support.

    :type: list
    '''

    attrDict: dict = None
    ''' get the objects internal python attribute dictionary for direct (faster) access.

    :type: dict
    '''

    components = None
    ''' All python components.'''

    children = None
    ''' direct children of this object, (read-only).'''

    childrenRecursive = None
    ''' all children of this object including children's children, (read-only).'''

    life: float = None
    ''' The number of frames until the object ends, assumes one frame is 1/60 second (read-only).

    :type: float
    '''

    debug: bool = None
    ''' If true, the object's debug properties will be displayed on screen.

    :type: bool
    '''

    debugRecursive: bool = None
    ''' If true, the object's and children's debug properties will be displayed on screen.

    :type: bool
    '''

    currentLodLevel: int = None
    ''' The index of the level of detail (LOD) currently used by this object (read-only).

    :type: int
    '''

    lodManager = None
    ''' Return the lod manager of this object. Needed to access to lod manager to set attributes of levels of detail of this object. The lod manager is shared between instance objects and can be changed to use the lod levels of an other object. If the lod manager is set to None the object's mesh backs to the mesh of the previous first lod level.'''

    onRemove: list = None
    ''' A list of callables to run when the KX_GameObject is destroyed. or

    :type: list
    '''

    logger = None
    ''' A logger instance that can be used to log messages related to this object (read-only).'''

    loggerName: str = None
    ''' A name used to create the logger instance. By default, it takes the form *Type[Name]* and can be optionally overridden as below:

    :type: str
    '''

    def endObject(self):
        ''' Delete this object, can be used in place of the EndObject Actuator. The actual removal of the object from the scene is delayed.

        '''
        pass

    def replaceMesh(self,
                    mesh: str,
                    useDisplayMesh: bool = True,
                    usePhysicsMesh: bool = False):
        ''' Replace the mesh of this object with a new mesh. This works the same was as the actuator.

        :param mesh: mesh to replace or the meshes name.
        :type mesh: str
        :param useDisplayMesh: when enabled the display mesh will be replaced (optional argument).
        :type useDisplayMesh: bool
        :param usePhysicsMesh: when enabled the physics mesh will be replaced (optional argument).
        :type usePhysicsMesh: bool
        '''
        pass

    def setVisible(self, visible: bool, recursive: bool):
        ''' Sets the game object's visible flag.

        :param visible: the visible state to set.
        :type visible: bool
        :param recursive: optional argument to set all childrens visibility flag too, defaults to False if no value passed.
        :type recursive: bool
        '''
        pass

    def setOcclusion(self, occlusion, recursive):
        ''' 

        '''
        pass

    def alignAxisToVect(self, vect, axis=2, factor: float = 1.0):
        ''' Aligns any of the game object's axis along the given vector.

        :param vect: a vector to align the axis.
        :type vect: 
        :param axis: The axis you want to align * 0: X axis * 1: Y axis * 2: Z axis
        :type axis: 
        :param factor: Only rotate a fraction of the distance to the target vector (0.0 - 1.0)
        :type factor: float
        '''
        pass

    def getAxisVect(self, vect: 'mathutils.Vector'):
        ''' Returns the axis vector rotates by the object's worldspace orientation. This is the equivalent of multiplying the vector by the orientation matrix.

        :param vect: a vector to align the axis.
        :type vect: 'mathutils.Vector'
        :return: The vector in relation to the objects rotation.
        '''
        pass

    def applyMovement(self, movement: 'mathutils.Vector', local):
        ''' Sets the game object's movement.

        :param movement: movement vector.
        :type movement: 'mathutils.Vector'
        :param local: 
        :type local: 
        :param local: 
        :type local: 
        '''
        pass

    def applyRotation(self, rotation: 'mathutils.Vector', local):
        ''' Sets the game object's rotation.

        :param rotation: rotation vector.
        :type rotation: 'mathutils.Vector'
        :param local: 
        :type local: 
        :param local: 
        :type local: 
        '''
        pass

    def applyForce(self, force: 'mathutils.Vector', local: bool):
        ''' Sets the game object's force. This requires a dynamic object.

        :param force: force vector.
        :type force: 'mathutils.Vector'
        :param local: * False: you get the "global" force ie: relative to world orientation. * True: you get the "local" force ie: relative to object orientation. * Default to False if not passed.
        :type local: bool
        '''
        pass

    def applyTorque(self, torque: 'mathutils.Vector', local: bool):
        ''' Sets the game object's torque. This requires a dynamic object.

        :param torque: torque vector.
        :type torque: 'mathutils.Vector'
        :param local: * False: you get the "global" torque ie: relative to world orientation. * True: you get the "local" torque ie: relative to object orientation. * Default to False if not passed.
        :type local: bool
        '''
        pass

    def getLinearVelocity(self, local: bool):
        ''' Gets the game object's linear velocity. This method returns the game object's velocity through it's center of mass, ie no angular velocity component.

        :param local: * False: you get the "global" velocity ie: relative to world orientation. * True: you get the "local" velocity ie: relative to object orientation. * Default to False if not passed.
        :type local: bool
        :return: the object's linear velocity.
        '''
        pass

    def setLinearVelocity(self, velocity: 'mathutils.Vector', local: bool):
        ''' Sets the game object's linear velocity. This method sets game object's velocity through it's center of mass, ie no angular velocity component. This requires a dynamic object.

        :param velocity: linear velocity vector.
        :type velocity: 'mathutils.Vector'
        :param local: * False: you get the "global" velocity ie: relative to world orientation. * True: you get the "local" velocity ie: relative to object orientation. * Default to False if not passed.
        :type local: bool
        '''
        pass

    def getAngularVelocity(self, local: bool):
        ''' Gets the game object's angular velocity.

        :param local: * False: you get the "global" velocity ie: relative to world orientation. * True: you get the "local" velocity ie: relative to object orientation. * Default to False if not passed.
        :type local: bool
        :return: the object's angular velocity.
        '''
        pass

    def setAngularVelocity(self, velocity: bool, local):
        ''' Sets the game object's angular velocity. This requires a dynamic object.

        :param velocity: angular velocity vector.
        :type velocity: bool
        :param local: 
        :type local: 
        '''
        pass

    def getVelocity(self, point: 'mathutils.Vector'):
        ''' Gets the game object's velocity at the specified point. Gets the game object's velocity at the specified point, including angular components.

        :param point: optional point to return the velocity for, in local coordinates, defaults to (0, 0, 0) if no value passed.
        :type point: 'mathutils.Vector'
        :return: the velocity at the specified point.
        '''
        pass

    def getReactionForce(self):
        ''' 

        '''
        pass

    def applyImpulse(self, point: 'bpy.context.world',
                     impulse: 'mathutils.Vector', local: bool):
        ''' Applies an impulse to the game object. This will apply the specified impulse to the game object at the specified point. If point != position, applyImpulse will also change the object's angular momentum. Otherwise, only linear momentum will change.

        :param point: the point to apply the impulse to (in world or local coordinates)
        :type point: 'bpy.context.world'
        :param impulse: impulse vector.
        :type impulse: 'mathutils.Vector'
        :param local: * False: you get the "global" impulse ie: relative to world coordinates with world orientation. * True: you get the "local" impulse ie: relative to local coordinates with object orientation. * Default to False if not passed.
        :type local: bool
        '''
        pass

    def setDamping(self, linear_damping: float, angular_damping: float):
        ''' Sets both the :py:attr: linearDamping and :py:attr: angularDamping simultaneously. This is more efficient than setting both properties individually.

        :param linear_damping: Linear ("translational") damping factor.
        :type linear_damping: float
        :param angular_damping: Angular ("rotational") damping factor.
        :type angular_damping: float
        '''
        pass

    def suspendPhysics(self, freeConstraints: bool):
        ''' Suspends physics for this object.

        :param freeConstraints: When set to True physics constraints used by the object are deleted. Else when False (the default) constraints are restored when restoring physics.
        :type freeConstraints: bool
        '''
        pass

    def restorePhysics(self):
        ''' Resumes physics for this object. Also reinstates collisions.

        '''
        pass

    def suspendDynamics(self, ghost: bool):
        ''' Suspends dynamics physics for this object.

        :param ghost: When set to True , collisions with the object will be ignored, similar to the "ghost" checkbox in Blender. When False (the default), the object becomes static but still collide with other objects.
        :type ghost: bool
        '''
        pass

    def restoreDynamics(self):
        ''' Resumes dynamics physics for this object. Also reinstates collisions; the object will no longer be a ghost.

        '''
        pass

    def enableRigidBody(self):
        ''' Enables rigid body physics for this object. Rigid body physics allows the object to roll on collisions.

        '''
        pass

    def disableRigidBody(self):
        ''' Disables rigid body physics for this object.

        '''
        pass

    def setCcdMotionThreshold(self, ccd_motion_threshold: float):
        ''' Sets :py:attr: ccdMotionThreshold that is the delta of movement that has to happen in one physics tick to trigger the continuous motion detection.

        :param ccd_motion_threshold: delta of movement.
        :type ccd_motion_threshold: float
        '''
        pass

    def setCcdSweptSphereRadius(self, ccd_swept_sphere_radius: float):
        ''' Sets :py:attr: ccdSweptSphereRadius that is the radius of the sphere that is used to check for possible collisions when ccd is actived.

        :param ccd_swept_sphere_radius: sphere radius.
        :type ccd_swept_sphere_radius: float
        '''
        pass

    def setParent(self, parent, compound: bool = True, ghost: bool = True):
        ''' Sets this object's parent. Control the shape status with the optional compound and ghost parameters: In that case you can control if it should be ghost or not:

        :param parent: new parent object.
        :type parent: 
        :param compound: whether the shape should be added to the parent compound shape. * True: the object shape should be added to the parent compound shape. * False: the object should keep its individual shape.
        :type compound: bool
        :param ghost: whether the object should be ghost while parented. * True: if the object should be made ghost while parented. * False: if the object should be solid while parented.
        :type ghost: bool
        '''
        pass

    def removeParent(self):
        ''' Removes this objects parent.

        '''
        pass

    def getPhysicsId(self):
        ''' Returns the user data object associated with this game object's physics controller.

        '''
        pass

    def getPropertyNames(self) -> list:
        ''' Gets a list of all property names.

        :rtype: list
        :return: All property names for this object.
        '''
        pass

    def getDistanceTo(self, other: list) -> float:
        ''' 

        :param other: ~bge.types.KX_GameObject to measure the distance to.
        :type other: list
        :rtype: float
        :return: distance to another object or point.
        '''
        pass

    def getVectTo(self, other: list) -> float:
        ''' Returns the vector and the distance to another object or point. The vector is normalized unless the distance is 0, in which a zero length vector is returned.

        :param other: ~bge.types.KX_GameObject to get the vector and distance to.
        :type other: list
        :rtype: float
        :return: (distance, globalVector(3), localVector(3))
        '''
        pass

    def rayCastTo(self, other, dist: float = 0, prop: str = ""):
        ''' Look towards another point/object and find first object hit within dist that matches prop. The ray is always casted from the center of the object, ignoring the object itself. The ray is casted towards the center of another object or an explicit [x, y, z] point. Use rayCast() if you need to retrieve the hit point

        :param other: [x, y, z] or object towards which the ray is casted
        :type other: 
        :param dist: max distance to look (can be negative => look behind); 0 or omitted => detect up to other
        :type dist: float
        :param prop: property name that object must have; can be omitted => detect any object
        :type prop: str
        :return: the first object hit or None if no object or object does not match prop
        '''
        pass

    def rayCast(self,
                objto,
                objfrom=None,
                dist: float = 0,
                prop: str = "",
                face=False,
                xray=False,
                poly=0,
                mask=0xFFFF):
        ''' Look from a point/object to another point/object and find first object hit within dist that matches prop. if poly is 0, returns a 3-tuple with object reference, hit point and hit normal or (None, None, None) if no hit. if poly is 1, returns a 4-tuple with in addition a ~bge.types.KX_PolyProxy as 4th element. if poly is 2, returns a 5-tuple with in addition a 2D vector with the UV mapping of the hit point as 5th element. The face parameter determines the orientation of the normal. * 0 => hit normal is always oriented towards the ray origin (as if you casted the ray from outside) * 1 => hit normal is the real face normal (only for mesh object, otherwise face has no effect) The ray has X-Ray capability if xray parameter is 1, otherwise the first object hit (other than self object) stops the ray. The prop and xray parameters interact as follow. * prop off, xray off: return closest hit or no hit if there is no object on the full extend of the ray. * prop off, xray on : idem. * prop on, xray off: return closest hit if it matches prop, no hit otherwise. * prop on, xray on : return closest hit matching prop or no hit if there is no object matching prop on the full extend of the ray. The ~bge.types.KX_PolyProxy 4th element of the return tuple when poly=1 allows to retrieve information on the polygon hit by the ray. If there is no hit or the hit object is not a static mesh, None is returned as 4th element. The ray ignores collision-free objects and faces that dont have the collision flag enabled, you can however use ghost objects.

        :param objto: [x, y, z] or object to which the ray is casted
        :type objto: 
        :param objfrom: [x, y, z] or object from which the ray is casted; None or omitted => use self object center
        :type objfrom: 
        :param dist: max distance to look (can be negative => look behind); 0 or omitted => detect up to to
        :type dist: float
        :param prop: property name that object must have; can be omitted or "" => detect any object
        :type prop: str
        :param face: 1=>return face normal; 0 or omitted => normal is oriented towards origin
        :type face: 
        :param xray: 1=>skip objects that don't match prop; 0 or omitted => stop on first object
        :type xray: 
        :param poly: 0, 1 or 2 to return a 3-, 4- or 5-tuple with information on the face hit. * 0 or omitted: return value is a 3-tuple (object, hitpoint, hitnormal) or (None, None, None) if no hit * 1: return value is a 4-tuple and the 4th element is a ~bge.types.KX_PolyProxy or None if no hit or the object doesn't use a mesh collision shape. * 2: return value is a 5-tuple and the 5th element is a 2-tuple (u, v) with the UV mapping of the hit point or None if no hit, or the object doesn't use a mesh collision shape, or doesn't have a UV mapping.
        :type poly: 
        :param mask: The collision mask (16 layers mapped to a 16-bit integer) is combined with each object's collision group, to hit only a subset of the objects in the scene. Only those objects for which collisionGroup & mask is true can be hit.
        :type mask: 
        :return: (object, hitpoint, hitnormal) or (object, hitpoint, hitnormal, polygon) or (object, hitpoint, hitnormal, polygon, hituv). * object, hitpoint and hitnormal are None if no hit. * polygon is valid only if the object is valid and is a static object, a dynamic object using mesh collision shape or a soft body object, otherwise it is None * hituv is valid only if polygon is valid and the object has a UV mapping, otherwise it is None
        '''
        pass

    def setCollisionMargin(self, margin: float):
        ''' Set the objects collision margin.

        :param margin: the collision margin distance in blender units.
        :type margin: float
        '''
        pass

    def sendMessage(self, subject: str, body: str = "", to: str = ""):
        ''' Sends a message.

        :param subject: The subject of the message
        :type subject: str
        :param body: The body of the message (optional)
        :type body: str
        :param to: The name of the object to send the message to (optional)
        :type to: str
        '''
        pass

    def reinstancePhysicsMesh(self, gameObject: str, meshObject: str,
                              dupli: bool, evaluated) -> bool:
        ''' Updates the physics system with the changed mesh. If no arguments are given the physics mesh will be re-created from the first mesh assigned to the game object.

        :param gameObject: optional argument, set the physics shape from this gameObjets mesh.
        :type gameObject: str
        :param meshObject: optional argument, set the physics shape from this mesh.
        :type meshObject: str
        :param dupli: optional argument, duplicate the physics shape.
        :type dupli: bool
        :param dupli: optional argument, duplicate the physics shape.
        :type dupli: bool
        :param evaluated: 
        :type evaluated: 
        :rtype: bool
        :return: True if reinstance succeeded, False if it failed.
        '''
        pass

    def replacePhysicsShape(self, gameObject: str) -> bool:
        ''' Replace the current physics shape.

        :param gameObject: set the physics shape from this gameObjets.
        :type gameObject: str
        :rtype: bool
        :return: True if replace succeeded, False if it failed.
        '''
        pass

    def get(self, key: str, default):
        ''' Return the value matching key, or the default value if its not found.

        :param key: the matching key
        :type key: str
        :param default: 
        :type default: 
        '''
        pass

    def playAction(self,
                   name: str,
                   start_frame,
                   end_frame,
                   layer=0,
                   priority=0,
                   blendin: float = 0,
                   play_mode='KX_ACTION_MODE_PLAY',
                   layer_weight: float = 0.0,
                   ipo_flags=0,
                   speed: float = 1.0,
                   blend_mode='KX_ACTION_BLEND_BLEND'):
        ''' Plays an action.

        :param name: the name of the action.
        :type name: str
        :param start: the start frame of the action.
        :type start: float
        :param end: the end frame of the action.
        :type end: float
        :param layer: the layer the action will play in (actions in different layers are added/blended together).
        :type layer: 
        :param priority: only play this action if there isn't an action currently playing in this layer with a higher (lower number) priority.
        :type priority: 
        :param blendin: the amount of blending between this animation and the previous one on this layer.
        :type blendin: float
        :param play_mode: these constants <gameobject-playaction-mode> .
        :type play_mode: 
        :param layer_weight: how much of the previous layer to use for blending.
        :type layer_weight: float
        :param ipo_flags: flags for the old IPO behaviors (force, etc).
        :type ipo_flags: 
        :param speed: the playback speed of the action as a factor (1.0 = normal speed, 2.0 = 2x speed, etc).
        :type speed: float
        :param blend_mode: these constants <gameobject-playaction-blend> .
        :type blend_mode: 
        '''
        pass

    def stopAction(self, layer):
        ''' Stop playing the action on the given layer.

        :param layer: The layer to stop playing, defaults to 0 if no value passed.
        :type layer: 
        '''
        pass

    def getActionFrame(self, layer) -> float:
        ''' Gets the current frame of the action playing in the supplied layer.

        :param layer: The layer that you want to get the frame from, defaults to 0 if no value passed.
        :type layer: 
        :rtype: float
        :return: The current frame of the action
        '''
        pass

    def getActionName(self, layer) -> str:
        ''' Gets the name of the current action playing in the supplied layer.

        :param layer: The layer that you want to get the action name from, defaults to 0 if no value passed.
        :type layer: 
        :rtype: str
        :return: The name of the current action
        '''
        pass

    def setActionFrame(self, frame: float, layer):
        ''' Set the current frame of the action playing in the supplied layer.

        :param layer: The layer where you want to set the frame, defaults to 0 if no value passed.
        :type layer: 
        :param frame: The frame to set the action to
        :type frame: float
        '''
        pass

    def isPlayingAction(self, layer) -> bool:
        ''' Checks to see if there is an action playing in the given layer.

        :param layer: The layer to check for a playing action, defaults to 0 if no value passed.
        :type layer: 
        :rtype: bool
        :return: Whether or not the action is playing
        '''
        pass

    def addDebugProperty(self, name: str, debug: bool):
        ''' Adds a single debug property to the debug list.

        :param name: name of the property that added to the debug list.
        :type name: str
        :param debug: the debug state, defaults to True if no value passed.
        :type debug: bool
        '''
        pass


class KX_LibLoadStatus:
    ''' Libload is deprecated since 0.3.0. An object providing information about a LibLoad() operation.
    '''

    onFinish = None
    ''' A callback that gets called when the lib load is done.'''

    finished: bool = None
    ''' The current status of the lib load.

    :type: bool
    '''

    progress: float = None
    ''' The current progress of the lib load as a normalized value from 0.0 to 1.0.

    :type: float
    '''

    libraryName: str = None
    ''' The name of the library being loaded (the first argument to LibLoad).

    :type: str
    '''

    timeTaken: float = None
    ''' The amount of time, in seconds, the lib load took (0 until the operation is complete).

    :type: float
    '''


class KX_LightObject:
    ''' A Light game object. It is possible to use attributes from :type: ~bpy.types.Light
    '''

    pass


class KX_LodLevel:
    ''' A single lod level for a game object lod manager.
    '''

    mesh = None
    ''' The mesh used for this lod level. (read only)'''

    level = None
    ''' The number of the lod level. (read only)'''

    distance: float = None
    ''' Distance to begin using this level of detail. (read only)

    :type: float
    '''

    hysteresis: float = None
    ''' Minimum distance factor change required to transition to the previous level of detail in percent. (read only)

    :type: float
    '''

    useMesh = None
    ''' '''

    useMaterial = None
    ''' '''

    useHysteresis: bool = None
    ''' Return true if the lod level uses hysteresis override. (read only)

    :type: bool
    '''


class KX_LodManager:
    ''' This class contains a list of all levels of detail used by a game object.
    '''

    levels: list = None
    ''' Return the list of all levels of detail of the lod manager.

    :type: list
    '''

    distanceFactor: float = None
    ''' Method to multiply the distance to the camera.

    :type: float
    '''


class KX_MeshProxy:
    ''' A mesh object. You can only change the vertex properties of a mesh object, not the mesh topology. To use mesh objects effectively, you should know a bit about how the game engine handles them. #. Mesh Objects are converted from Blender at scene load. #. The Converter groups polygons by Material. This means they can be sent to the renderer efficiently. A material holds: #. The texture. #. The Blender material. #. The Tile properties #. The face properties - (From the "Texture Face" panel) #. Transparency & z sorting #. Light layer #. Polygon shape (triangle/quad) #. Game Object #. Vertices will be split by face if necessary. Vertices can only be shared between faces if: #. They are at the same position #. UV coordinates are the same #. Their normals are the same (both polygons are "Set Smooth") #. They are the same color, for example: a cube has 24 vertices: 6 faces with 4 vertices per face. The correct method of iterating over every ~bge.types.KX_VertexProxy in a game object
    '''

    materials: list = None
    ''' 

    :type: list
    '''

    numPolygons = None
    ''' '''

    numMaterials = None
    ''' '''

    polygons: list = None
    ''' Returns the list of polygons of this mesh.

    :type: list
    '''

    def getMaterialName(self, matid) -> str:
        ''' Gets the name of the specified material.

        :param matid: the specified material.
        :type matid: 
        :rtype: str
        :return: the attached material name.
        '''
        pass

    def getTextureName(self, matid) -> str:
        ''' Gets the name of the specified material's texture.

        :param matid: the specified material
        :type matid: 
        :rtype: str
        :return: the attached material's texture name.
        '''
        pass

    def getVertexArrayLength(self, matid):
        ''' Gets the length of the vertex array associated with the specified material. There is one vertex array for each material.

        :param matid: the specified material
        :type matid: 
        :return: the number of verticies in the vertex array.
        '''
        pass

    def getVertex(self, matid, index):
        ''' Gets the specified vertex from the mesh object.

        :param matid: the specified material
        :type matid: 
        :param index: the index into the vertex array.
        :type index: 
        :return: a vertex object.
        '''
        pass

    def getPolygon(self, index):
        ''' Gets the specified polygon from the mesh.

        :param index: polygon number
        :type index: 
        :return: a polygon object.
        '''
        pass

    def transform(self, matid, matrix):
        ''' Transforms the vertices of a mesh.

        :param matid: material index, -1 transforms all.
        :type matid: 
        :param matrix: transformation matrix.
        :type matrix: 
        '''
        pass

    def transformUV(self, matid, matrix, uv_index=-1, uv_index_from=-1):
        ''' Transforms the vertices UV's of a mesh.

        :param matid: material index, -1 transforms all.
        :type matid: 
        :param matrix: transformation matrix.
        :type matrix: 
        :param uv_index: optional uv index, -1 for all, otherwise 0 or 1.
        :type uv_index: 
        :param uv_index_from: optional uv index to copy from, -1 to transform the current uv.
        :type uv_index_from: 
        '''
        pass

    def replaceMaterial(self, matid, material):
        ''' Replace the material in slot :data: matid by the material :data: material .

        :param matid: The material index.
        :type matid: 
        :param material: The material replacement.
        :type material: 
        '''
        pass


class KX_NavMeshObject:
    ''' Python interface for using and controlling navigation meshes.
    '''

    def findPath(self, start, goal) -> list:
        ''' Finds the path from start to goal points.

        :param start: 
        :type start: 
        :param start: 
        :type start: 
        :param goal: 
        :type goal: 
        :param start: 
        :type start: 
        :rtype: list
        :return: a path as a list of points
        '''
        pass

    def raycast(self, start, goal) -> float:
        ''' Raycast from start to goal points.

        :param start: 
        :type start: 
        :param start: 
        :type start: 
        :param goal: 
        :type goal: 
        :param start: 
        :type start: 
        :rtype: float
        :return: the hit factor
        '''
        pass

    def draw(self, mode):
        ''' Draws a debug mesh for the navigation mesh.

        :param mode: 
        :type mode: 
        :param mode: 
        :type mode: 
        '''
        pass

    def rebuild(self):
        ''' Rebuild the navigation mesh.

        '''
        pass


class KX_PolyProxy:
    ''' A polygon holds the index of the vertex forming the poylgon. Note: The polygon attributes are read-only, you need to retrieve the vertex proxy if you want to change the vertex settings.
    '''

    material_name: str = None
    ''' The name of polygon material, empty if no material.

    :type: str
    '''

    material = None
    ''' The material of the polygon.'''

    texture_name: str = None
    ''' The texture name of the polygon.

    :type: str
    '''

    material_id = None
    ''' The material index of the polygon, use this to retrieve vertex proxy from mesh proxy.'''

    v1 = None
    ''' vertex index of the first vertex of the polygon, use this to retrieve vertex proxy from mesh proxy.'''

    v2 = None
    ''' vertex index of the second vertex of the polygon, use this to retrieve vertex proxy from mesh proxy.'''

    v3 = None
    ''' vertex index of the third vertex of the polygon, use this to retrieve vertex proxy from mesh proxy.'''

    v4 = None
    ''' Vertex index of the fourth vertex of the polygon, 0 if polygon has only 3 vertex Use this to retrieve vertex proxy from mesh proxy.'''

    visible = None
    ''' visible state of the polygon: 1=visible, 0=invisible.'''

    collide = None
    ''' collide state of the polygon: 1=receives collision, 0=collision free.'''

    vertices: list = None
    ''' Returns the list of vertices of this polygon.

    :type: list
    '''

    def getMaterialName(self) -> str:
        ''' Returns the polygon material name with MA prefix

        :rtype: str
        :return: material name
        '''
        pass

    def getMaterial(self):
        ''' 

        :return: The polygon material
        '''
        pass

    def getTextureName(self) -> str:
        ''' 

        :rtype: str
        :return: The texture name
        '''
        pass

    def getMaterialIndex(self):
        ''' Returns the material bucket index of the polygon. This index and the ones returned by getVertexIndex() are needed to retrieve the vertex proxy from ~bge.types.KX_MeshProxy .

        :return: the material index in the mesh
        '''
        pass

    def getNumVertex(self):
        ''' Returns the number of vertex of the polygon.

        :return: number of vertex, 3 or 4.
        '''
        pass

    def isVisible(self) -> bool:
        ''' Returns whether the polygon is visible or not

        :rtype: bool
        :return: 0=invisible, 1=visible
        '''
        pass

    def isCollider(self):
        ''' Returns whether the polygon is receives collision or not

        :return: 0=collision free, 1=receives collision
        '''
        pass

    def getVertexIndex(self, vertex):
        ''' Returns the mesh vertex index of a polygon vertex This index and the one returned by getMaterialIndex() are needed to retrieve the vertex proxy from ~bge.types.KX_MeshProxy .

        :param vertex: 
        :type vertex: 
        :param vertex: 
        :type vertex: 
        :return: mesh vertex index
        '''
        pass

    def getMesh(self):
        ''' Returns a mesh proxy

        :return: mesh proxy
        '''
        pass


class KX_PythonComponent:
    ''' Python component can be compared to python logic bricks with parameters. The python component is a script loaded in the UI, this script defined a component class by inheriting from ~bge.types.KX_PythonComponent . This class must contain a dictionary of properties: :attr: args and two default functions: :meth: start and :meth: update . The script must have .py extension. The component properties are loaded from the :attr: args attribute from the UI at loading time. When the game start the function :meth: start is called with as arguments a dictionary of the properties' name and value. The :meth: update function is called every frames during the logic stage before running logics bricks, the goal of this function is to handle and process everything. The following component example moves and rotates the object when pressing the keys W, A, S and D. Since the components are loaded for the first time outside the bge, then :attr: bge is a fake module that contains only the class ~bge.types.KX_PythonComponent to avoid importing all the bge modules. This behavior is safer but creates some issues at loading when the user want to use functions or attributes from the bge modules other than the ~bge.types.KX_PythonComponent class. The way is to not call these functions at loading outside the bge. To detect it, the bge module contains the attribute :attr: __component__ when it's imported outside the bge. The following component example add a "Cube" object at initialization and move it along x for each update. It shows that the user can use functions from scene and load the component outside the bge by setting global attributes in a condition at the beginning of the script. The property types supported are float, integer, boolean, string, set (for enumeration) and Vector 2D, 3D and 4D. The following example show all of these property types.
    '''

    object = None
    ''' The object owner of the component.'''

    args: dict = None
    ''' Dictionary of the component properties, the keys are string and the value can be: float, integer, Vector(2D/3D/4D), set, string.

    :type: dict
    '''

    logger = None
    ''' A logger instance that can be used to log messages related to this object (read-only).'''

    loggerName: str = None
    ''' A name used to create the logger instance. By default, it takes the form *Type[Name]* and can be optionally overridden as below:

    :type: str
    '''

    def start(self, args: dict):
        ''' Initialize the component.

        :param args: The dictionary of the properties' name and value.
        :type args: dict
        '''
        pass

    def update(self):
        ''' Process the logic of the component.

        '''
        pass

    def dispose(self):
        ''' Function called when the component is destroyed.

        '''
        pass


class KX_Scene:
    ''' An active scene that gives access to objects, cameras, lights and scene attributes. The activity culling stuff is supposed to disable logic bricks when their owner gets too far from the active camera. It was taken from some code lurking at the back of KX_Scene - who knows what it does! @bug: All attributes are read only at the moment.
    '''

    name: str = None
    ''' The scene's name, (read-only).

    :type: str
    '''

    objects = None
    ''' A list of objects in the scene, (read-only).'''

    objectsInactive = None
    ''' A list of objects on background layers (used for the addObject actuator), (read-only).'''

    lights = None
    ''' A list of lights in the scene, (read-only).'''

    cameras = None
    ''' A list of cameras in the scene, (read-only).'''

    texts = None
    ''' A list of texts in the scene, (read-only).'''

    active_camera = None
    ''' The current active camera.'''

    overrideCullingCamera = None
    ''' '''

    world = None
    ''' '''

    filterManager = None
    ''' The scene's 2D filter manager, (read-only).'''

    suspended = None
    ''' '''

    activityCulling: bool = None
    ''' True if the scene allow object activity culling.

    :type: bool
    '''

    dbvt_culling = None
    ''' '''

    pre_draw: list = None
    ''' A list of callables to be run before the render step. The callbacks can take as argument the rendered camera.

    :type: list
    '''

    post_draw: list = None
    ''' A list of callables to be run after the render step.

    :type: list
    '''

    pre_draw_setup: list = None
    ''' A list of callables to be run before the drawing setup (i.e., before the model view and projection matrices are computed). The callbacks can take as argument the rendered camera, the camera could be temporary in case of stereo rendering.

    :type: list
    '''

    onRemove: list = None
    ''' A list of callables to run when the scene is destroyed.

    :type: list
    '''

    gravity = None
    ''' The scene gravity using the world x, y and z axis.'''

    logger = None
    ''' A logger instance that can be used to log messages related to this object (read-only).'''

    loggerName: str = None
    ''' A name used to create the logger instance. By default, it takes the form *KX_Scene[Name]*.

    :type: str
    '''

    def addObject(self,
                  object: str,
                  reference: str,
                  time: float = 0.0,
                  dupli: bool = False):
        ''' Adds an object to the scene like the Add Object Actuator would.

        :param object: The (name of the) object to add.
        :type object: str
        :param reference: The (name of the) object which position, orientation, and scale to copy (optional), if the object to add is a light and there is not reference the light's layer will be the same that the active layer in the blender scene.
        :type reference: str
        :param time: The lifetime of the added object, in frames (assumes one frame is 1/60 second). A time of 0.0 means the object will last forever (optional).
        :type time: float
        :param dupli: Full duplication of object data (mesh, materials...).
        :type dupli: bool
        :return: The newly added object.
        '''
        pass

    def end(self):
        ''' Removes the scene from the game.

        '''
        pass

    def restart(self):
        ''' Restarts the scene.

        '''
        pass

    def replace(self, scene: str) -> bool:
        ''' Replaces this scene with another one.

        :param scene: The name of the scene to replace this scene with.
        :type scene: str
        :rtype: bool
        :return: True if the scene exists and was scheduled for addition, False otherwise.
        '''
        pass

    def suspend(self):
        ''' 

        '''
        pass

    def resume(self):
        ''' 

        '''
        pass

    def get(self, key, default=None):
        ''' Return the value matching key, or the default value if its not found.

        '''
        pass

    def drawObstacleSimulation(self):
        ''' Draw debug visualization of obstacle simulation.

        '''
        pass

    def convertBlenderObject(self, blenderObject):
        ''' Converts a ~bpy.types.Object into a ~bge.types.KX_GameObject during runtime. For example, you can append an Object from another .blend file during bge runtime using: bpy.ops.wm.append(...) then convert this Object into a KX_GameObject to have logic bricks, physics... converted. This is meant to replace libload.

        :param blenderObject: The Object to be converted.
        :type blenderObject: 
        :return: Returns the newly converted gameobject.
        '''
        pass

    def convertBlenderObjectsList(self, blenderObjectsList: list,
                                  asynchronous: bool):
        ''' Converts all bpy.types.Object inside a python List into its correspondent ~bge.types.KX_GameObject during runtime. For example, you can append an Object List during bge runtime using: ob = object_data_add(...) and ML.append(ob) then convert the Objects inside the List into several KX_GameObject to have logic bricks, physics... converted. This is meant to replace libload. The conversion can be asynchronous or synchronous.

        :param blenderObjectsList: The Object list to be converted.
        :type blenderObjectsList: list
        :param asynchronous: The Object list conversion can be asynchronous or not.
        :type asynchronous: bool
        '''
        pass

    def convertBlenderCollection(self, blenderCollection, asynchronous: bool):
        ''' Converts all bpy.types.Object inside a Collection into its correspondent ~bge.types.KX_GameObject during runtime. For example, you can append a Collection from another .blend file during bge runtime using: bpy.ops.wm.append(...) then convert the Objects inside the Collection into several KX_GameObject to have logic bricks, physics... converted. This is meant to replace libload. The conversion can be asynchronous or synchronous.

        :param blenderCollection: The collection to be converted.
        :type blenderCollection: 
        :param asynchronous: The collection conversion can be asynchronous or not.
        :type asynchronous: bool
        '''
        pass

    def convertBlenderAction(self, Action):
        ''' Registers a bpy.types.Action into the bge logic manager to be abled to play it during runtime. For example, you can append an Action from another .blend file during bge runtime using: bpy.ops.wm.append(...) then register this Action to be abled to play it.

        :param Action: The Action to be converted.
        :type Action: 
        '''
        pass

    def unregisterBlenderAction(self, Action):
        ''' Unregisters a bpy.types.Action from the bge logic manager. The unregistered action will still be in the .blend file but can't be played anymore with bge. If you want to completely remove the action you need to call bpy.data.actions.remove(Action, do_unlink=True) after you unregistered it from bge logic manager.

        :param Action: The Action to be unregistered.
        :type Action: 
        '''
        pass

    def addOverlayCollection(self, kxCamera, blenderCollection):
        ''' Adds an overlay collection (as with collection actuator) to render this collection objects during a second render pass in overlay using the KX_Camera passed as argument.

        :param kxCamera: The camera used to render the overlay collection.
        :type kxCamera: 
        :param blenderCollection: The overlay collection to add.
        :type blenderCollection: 
        '''
        pass

    def removeOverlayCollection(self, blenderCollection):
        ''' Removes an overlay collection (as with collection actuator).

        :param blenderCollection: The overlay collection to remove.
        :type blenderCollection: 
        '''
        pass

    def getGameObjectFromObject(self, blenderObject: 'bpy.types.Object'):
        ''' Get the KX_GameObject corresponding to the blenderObject.

        :param blenderObject: the Object from which we want to get the KX_GameObject.
        :type blenderObject: 'bpy.types.Object'
        '''
        pass


class KX_VehicleWrapper:
    ''' KX_VehicleWrapper TODO - description
    '''

    rayMask = None
    ''' Set ray cast mask.'''

    def addWheel(self, wheel, attachPos, downDir, axleDir,
                 suspensionRestLength: float, wheelRadius: float,
                 hasSteering: bool):
        ''' Add a wheel to the vehicle

        :param wheel: The object to use as a wheel.
        :type wheel: 
        :param attachPos: The position to attach the wheel, relative to the chassis object center.
        :type attachPos: 
        :param downDir: The direction vector pointing down to where the vehicle should collide with the floor.
        :type downDir: 
        :param axleDir: The axis the wheel rotates around, relative to the chassis.
        :type axleDir: 
        :param suspensionRestLength: The length of the suspension when no forces are being applied.
        :type suspensionRestLength: float
        :param wheelRadius: The radius of the wheel (half the diameter).
        :type wheelRadius: float
        :param hasSteering: True if the wheel should turn with steering, typically used in front wheels.
        :type hasSteering: bool
        '''
        pass

    def applyBraking(self, force: float, wheelIndex):
        ''' Apply a braking force to the specified wheel

        :param force: the brake force
        :type force: float
        :param wheelIndex: index of the wheel where the force needs to be applied
        :type wheelIndex: 
        '''
        pass

    def applyEngineForce(self, force: float, wheelIndex):
        ''' Apply an engine force to the specified wheel

        :param force: the engine force
        :type force: float
        :param wheelIndex: index of the wheel where the force needs to be applied
        :type wheelIndex: 
        '''
        pass

    def getConstraintId(self):
        ''' Get the constraint ID

        :return: the constraint id
        '''
        pass

    def getConstraintType(self):
        ''' Returns the constraint type.

        :return: constraint type
        '''
        pass

    def getNumWheels(self):
        ''' Returns the number of wheels.

        :return: the number of wheels for this vehicle
        '''
        pass

    def getWheelOrientationQuaternion(self, wheelIndex):
        ''' Returns the wheel orientation as a quaternion.

        :param wheelIndex: the wheel index
        :type wheelIndex: 
        :return: TODO Description
        '''
        pass

    def getWheelPosition(self, wheelIndex):
        ''' Returns the position of the specified wheel

        :param wheelIndex: the wheel index
        :type wheelIndex: 
        :return: position vector
        '''
        pass

    def getWheelRotation(self, wheelIndex) -> float:
        ''' Returns the rotation of the specified wheel

        :param wheelIndex: the wheel index
        :type wheelIndex: 
        :rtype: float
        :return: the wheel rotation
        '''
        pass

    def setRollInfluence(self, rollInfluece: float, wheelIndex):
        ''' Set the specified wheel's roll influence. The higher the roll influence the more the vehicle will tend to roll over in corners.

        :param rollInfluece: the wheel roll influence
        :type rollInfluece: float
        :param wheelIndex: the wheel index
        :type wheelIndex: 
        '''
        pass

    def setSteeringValue(self, steering: float, wheelIndex):
        ''' Set the specified wheel's steering

        :param steering: the wheel steering
        :type steering: float
        :param wheelIndex: the wheel index
        :type wheelIndex: 
        '''
        pass

    def setSuspensionCompression(self, compression: float, wheelIndex):
        ''' Set the specified wheel's compression

        :param compression: the wheel compression
        :type compression: float
        :param wheelIndex: the wheel index
        :type wheelIndex: 
        '''
        pass

    def setSuspensionDamping(self, damping: float, wheelIndex):
        ''' Set the specified wheel's damping

        :param damping: the wheel damping
        :type damping: float
        :param wheelIndex: the wheel index
        :type wheelIndex: 
        '''
        pass

    def setSuspensionStiffness(self, stiffness: float, wheelIndex):
        ''' Set the specified wheel's stiffness

        :param stiffness: the wheel stiffness
        :type stiffness: float
        :param wheelIndex: the wheel index
        :type wheelIndex: 
        '''
        pass

    def setTyreFriction(self, friction: float, wheelIndex):
        ''' Set the specified wheel's tyre friction

        :param friction: the tyre friction
        :type friction: float
        :param wheelIndex: the wheel index
        :type wheelIndex: 
        '''
        pass


class KX_VertexProxy:
    ''' A vertex holds position, UV, color and normal information. Note: The physics simulation is NOT currently updated - physics will not respond to changes in the vertex position.
    '''

    XYZ = None
    ''' The position of the vertex.'''

    UV = None
    ''' The texture coordinates of the vertex.'''

    uvs: list = None
    ''' The texture coordinates list of the vertex.

    :type: list
    '''

    normal = None
    ''' The normal of the vertex.'''

    color = None
    ''' The color of the vertex. Black = [0.0, 0.0, 0.0, 1.0], White = [1.0, 1.0, 1.0, 1.0]'''

    colors: list = None
    ''' The color list of the vertex.

    :type: list
    '''

    x: float = None
    ''' The x coordinate of the vertex.

    :type: float
    '''

    y: float = None
    ''' The y coordinate of the vertex.

    :type: float
    '''

    z: float = None
    ''' The z coordinate of the vertex.

    :type: float
    '''

    u: float = None
    ''' The u texture coordinate of the vertex.

    :type: float
    '''

    v: float = None
    ''' The v texture coordinate of the vertex.

    :type: float
    '''

    u2: float = None
    ''' The second u texture coordinate of the vertex.

    :type: float
    '''

    v2: float = None
    ''' The second v texture coordinate of the vertex.

    :type: float
    '''

    r: float = None
    ''' The red component of the vertex color. 0.0 <= r <= 1.0.

    :type: float
    '''

    g: float = None
    ''' The green component of the vertex color. 0.0 <= g <= 1.0.

    :type: float
    '''

    b: float = None
    ''' The blue component of the vertex color. 0.0 <= b <= 1.0.

    :type: float
    '''

    a: float = None
    ''' The alpha component of the vertex color. 0.0 <= a <= 1.0.

    :type: float
    '''

    def getXYZ(self):
        ''' Gets the position of this vertex.

        :return: this vertexes position in local coordinates.
        '''
        pass

    def setXYZ(self, pos):
        ''' Sets the position of this vertex.

        :param pos: 
        :type pos: 
        '''
        pass

    def getUV(self):
        ''' Gets the UV (texture) coordinates of this vertex.

        :return: this vertexes UV (texture) coordinates.
        '''
        pass

    def setUV(self, uv):
        ''' Sets the UV (texture) coordinates of this vertex.

        '''
        pass

    def getUV2(self):
        ''' Gets the 2nd UV (texture) coordinates of this vertex.

        :return: this vertexes UV (texture) coordinates.
        '''
        pass

    def setUV2(self, uv, unit):
        ''' Sets the 2nd UV (texture) coordinates of this vertex.

        :param unit: 
        :type unit: 
        :param unit: 
        :type unit: 
        '''
        pass

    def getRGBA(self):
        ''' Gets the color of this vertex. The color is represented as four bytes packed into an integer value. The color is packed as RGBA. Since Python offers no way to get each byte without shifting, you must use the struct module to access color in an machine independent way. Because of this, it is suggested you use the r, g, b and a attributes or the color attribute instead.

        :return: packed color. 4 byte integer with one byte per color channel in RGBA format.
        '''
        pass

    def setRGBA(self, col: list):
        ''' Sets the color of this vertex. See getRGBA() for the format of col, and its relevant problems. Use the r, g, b and a attributes or the color attribute instead. setRGBA() also accepts a four component list as argument col. The list represents the color as [r, g, b, a] with black = [0.0, 0.0, 0.0, 1.0] and white = [1.0, 1.0, 1.0, 1.0]

        :param col: the new color of this vertex in packed RGBA format.
        :type col: list
        '''
        pass

    def getNormal(self):
        ''' Gets the normal vector of this vertex.

        :return: normalized normal vector.
        '''
        pass

    def setNormal(self, normal):
        ''' Sets the normal vector of this vertex.

        :param normal: 
        :type normal: 
        '''
        pass


class SCA_2DFilterActuator:
    ''' Create, enable and disable 2D filters. The following properties don't have an immediate effect. You must active the actuator to get the result. The actuator is not persistent: it automatically stops itself after setting up the filter but the filter remains active. To stop a filter you must activate the actuator with 'type' set to :data: ~bge.logic.RAS_2DFILTER_DISABLED or :data: ~bge.logic.RAS_2DFILTER_NOFILTER .
    '''

    shaderText: str = None
    ''' shader source code for custom shader.

    :type: str
    '''

    disableMotionBlur = None
    ''' '''

    mode = None
    ''' Type of 2D filter, use one of :ref: these constants <Two-D-FilterActuator-mode> .'''

    passNumber = None
    ''' order number of filter in the stack of 2D filters. Filters are executed in increasing order of passNb. Only be one filter can be defined per passNb.'''

    value = None
    ''' '''


class SCA_ANDController:
    ''' An AND controller activates only when all linked sensors are activated. There are no special python methods for this controller.
    '''

    pass


class SCA_ActionActuator:
    ''' Action Actuators apply an action to an actor.
    '''

    action: str = None
    ''' The name of the action to set as the current action.

    :type: str
    '''

    frameStart: float = None
    ''' Specifies the starting frame of the animation.

    :type: float
    '''

    frameEnd: float = None
    ''' Specifies the ending frame of the animation.

    :type: float
    '''

    blendIn: float = None
    ''' Specifies the number of frames of animation to generate when making transitions between actions.

    :type: float
    '''

    priority = None
    ''' Sets the priority of this actuator. Actuators will lower priority numbers will override actuators with higher numbers.'''

    frame: float = None
    ''' Sets the current frame for the animation.

    :type: float
    '''

    propName: str = None
    ''' Sets the property to be used in FromProp playback mode.

    :type: str
    '''

    mode = None
    ''' The operation mode of the actuator. Can be one of :ref: these constants<action-actuator> .'''

    useContinue: bool = None
    ''' The actions continue option, True or False. When True, the action will always play from where last left off, otherwise negative events to this actuator will reset it to its start frame.

    :type: bool
    '''

    framePropName: str = None
    ''' The name of the property that is set to the current frame number.

    :type: str
    '''


class SCA_ActuatorSensor:
    ''' Actuator sensor detect change in actuator state of the parent object. It generates a positive pulse if the corresponding actuator is activated and a negative pulse if the actuator is deactivated.
    '''

    actuator: str = None
    ''' the name of the actuator that the sensor is monitoring.

    :type: str
    '''


class SCA_AddObjectActuator:
    ''' Edit Object Actuator (in Add Object Mode)
    '''

    object = None
    ''' the object this actuator adds.'''

    objectLastCreated = None
    ''' the last added object from this actuator (read-only).'''

    time: float = None
    ''' the lifetime of added objects, in frames. Set to 0 to disable automatic deletion.

    :type: float
    '''

    linearVelocity: list = None
    ''' the initial linear velocity of added objects.

    :type: list
    '''

    angularVelocity: list = None
    ''' the initial angular velocity of added objects.

    :type: list
    '''

    def instantAddObject(self):
        ''' adds the object without needing to calling SCA_PythonController.activate()

        '''
        pass


class SCA_AlwaysSensor:
    ''' This sensor is always activated.
    '''

    pass


class SCA_ArmatureActuator:
    ''' Armature Actuators change constraint condition on armatures.
    '''

    type = None
    ''' The type of action that the actuator executes when it is active. Can be one of :ref: these constants <armatureactuator-constants-type>'''

    constraint = None
    ''' The constraint object this actuator is controlling.'''

    target = None
    ''' The object that this actuator will set as primary target to the constraint it controls.'''

    subtarget = None
    ''' The object that this actuator will set as secondary target to the constraint it controls.'''

    weight = None
    ''' The weight this actuator will set on the constraint it controls.'''

    influence = None
    ''' The influence this actuator will set on the constraint it controls.'''


class SCA_ArmatureSensor:
    ''' Armature sensor detect conditions on armatures.
    '''

    type = None
    ''' The type of measurement that the sensor make when it is active. Can be one of :ref: these constants <armaturesensor-type>'''

    constraint = None
    ''' The constraint object this sensor is watching.'''

    value: float = None
    ''' The threshold used in the comparison with the constraint error The linear error is only updated on CopyPose/Distance IK constraint with iTaSC solver The rotation error is only updated on CopyPose+rotation IK constraint with iTaSC solver The linear error on CopyPose is always >= 0: it is the norm of the distance between the target and the bone The rotation error on CopyPose is always >= 0: it is the norm of the equivalent rotation vector between the bone and the target orientations The linear error on Distance can be positive if the distance between the bone and the target is greater than the desired distance, and negative if the distance is smaller.

    :type: float
    '''


class SCA_CameraActuator:
    ''' Applies changes to a camera.
    '''

    damping: float = None
    ''' strength of of the camera following movement.

    :type: float
    '''

    axis: int = None
    ''' The camera axis (0, 1, 2) for positive XYZ , (3, 4, 5) for negative XYZ .

    :type: int
    '''

    min: float = None
    ''' minimum distance to the target object maintained by the actuator.

    :type: float
    '''

    max: float = None
    ''' maximum distance to stay from the target object.

    :type: float
    '''

    height: float = None
    ''' height to stay above the target object.

    :type: float
    '''

    object = None
    ''' the object this actuator tracks.'''


class SCA_CollisionSensor:
    ''' Collision sensor detects collisions between objects.
    '''

    propName: str = None
    ''' The property or material to collide with.

    :type: str
    '''

    useMaterial: bool = None
    ''' Determines if the sensor is looking for a property or material. KX_True = Find material; KX_False = Find property.

    :type: bool
    '''

    usePulseCollision: bool = None
    ''' When enabled, changes to the set of colliding objects generate a pulse.

    :type: bool
    '''

    hitObject = None
    ''' The last collided object. (read-only).'''

    hitObjectList = None
    ''' A list of colliding objects. (read-only).'''

    hitMaterial: str = None
    ''' The material of the object in the face hit by the ray. (read-only).

    :type: str
    '''


class SCA_ConstraintActuator:
    ''' A constraint actuator limits the position, rotation, distance or orientation of an object.
    '''

    damp = None
    ''' Time constant of the constraint expressed in frame (not use by Force field constraint).'''

    rotDamp = None
    ''' Time constant for the rotation expressed in frame (only for the distance constraint), 0 = use damp for rotation as well.'''

    direction = None
    ''' The reference direction in world coordinate for the orientation constraint.'''

    option = None
    ''' Binary combination of :ref: these constants <constraint-actuator-option>'''

    time = None
    ''' activation time of the actuator. The actuator disables itself after this many frame. If set to 0, the actuator is not limited in time.'''

    propName: str = None
    ''' the name of the property or material for the ray detection of the distance constraint.

    :type: str
    '''

    min: float = None
    ''' The lower bound of the constraint. For the rotation and orientation constraint, it represents radiant.

    :type: float
    '''

    distance: float = None
    ''' the target distance of the distance constraint.

    :type: float
    '''

    max: float = None
    ''' the upper bound of the constraint. For rotation and orientation constraints, it represents radiant.

    :type: float
    '''

    rayLength: float = None
    ''' the length of the ray of the distance constraint.

    :type: float
    '''

    limit = None
    ''' type of constraint. Use one of the :ref: these constants <constraint-actuator-limit>'''


class SCA_DelaySensor:
    ''' The Delay sensor generates positive and negative triggers at precise time, expressed in number of frames. The delay parameter defines the length of the initial OFF period. A positive trigger is generated at the end of this period. The duration parameter defines the length of the ON period following the OFF period. There is a negative trigger at the end of the ON period. If duration is 0, the sensor stays ON and there is no negative trigger. The sensor runs the OFF-ON cycle once unless the repeat option is set: the OFF-ON cycle repeats indefinately (or the OFF cycle if duration is 0). Use :meth: SCA_ISensor.reset <bge.types.SCA_ISensor.reset> at any time to restart sensor.
    '''

    delay = None
    ''' length of the initial OFF period as number of frame, 0 for immediate trigger.'''

    duration = None
    ''' length of the ON period in number of frame after the initial OFF period. If duration is greater than 0, a negative trigger is sent at the end of the ON pulse.'''

    repeat = None
    ''' 1 if the OFF-ON cycle should be repeated indefinately, 0 if it should run once.'''


class SCA_DynamicActuator:
    ''' Dynamic Actuator.
    '''

    mode = None
    ''' the type of operation of the actuator, 0-4 * KX_DYN_RESTORE_DYNAMICS(0) * KX_DYN_DISABLE_DYNAMICS(1) * KX_DYN_ENABLE_RIGID_BODY(2) * KX_DYN_DISABLE_RIGID_BODY(3) * KX_DYN_SET_MASS(4)'''

    mass: float = None
    ''' the mass value for the KX_DYN_SET_MASS operation.

    :type: float
    '''


class SCA_EndObjectActuator:
    ''' Edit Object Actuator (in End Object mode) This actuator has no python methods.
    '''

    pass


class SCA_GameActuator:
    ''' The game actuator loads a new .blend file, restarts the current .blend file or quits the game.
    '''

    fileName: str = None
    ''' the new .blend file to load.

    :type: str
    '''

    mode = None
    ''' The mode of this actuator. Can be on of :ref: these constants <game-actuator>'''


class SCA_IActuator:
    ''' Base class for all actuator logic bricks.
    '''

    pass


class SCA_IController:
    ''' Base class for all controller logic bricks.
    '''

    state: int = None
    ''' The controllers state bitmask. This can be used with the GameObject's state to test if the controller is active.

    :type: int
    '''

    sensors: list = None
    ''' A list of sensors linked to this controller.

    :type: list
    '''

    actuators: list = None
    ''' A list of actuators linked to this controller.

    :type: list
    '''

    useHighPriority: bool = None
    ''' When set the controller executes always before all other controllers that dont have this set.

    :type: bool
    '''


class SCA_ILogicBrick:
    ''' Base class for all logic bricks.
    '''

    executePriority = None
    ''' This determines the order controllers are evaluated, and actuators are activated (lower priority is executed first).'''

    owner = None
    ''' The game object this logic brick is attached to (read-only).'''

    name: str = None
    ''' The name of this logic brick (read-only).

    :type: str
    '''


class SCA_IObject:
    ''' This class has no python functions
    '''

    pass


class SCA_ISensor:
    ''' Base class for all sensor logic bricks.
    '''

    usePosPulseMode: bool = None
    ''' Flag to turn positive pulse mode on and off.

    :type: bool
    '''

    useNegPulseMode: bool = None
    ''' Flag to turn negative pulse mode on and off.

    :type: bool
    '''

    frequency = None
    ''' The frequency for pulse mode sensors.'''

    skippedTicks = None
    ''' Number of logic ticks skipped between 2 active pulses'''

    level: bool = None
    ''' level Option whether to detect level or edge transition when entering a state. It makes a difference only in case of logic state transition (state actuator). A level detector will immediately generate a pulse, negative or positive depending on the sensor condition, as soon as the state is activated. A edge detector will wait for a state change before generating a pulse. note: mutually exclusive with :attr: tap , enabling will disable :attr: tap .

    :type: bool
    '''

    tap: bool = None
    ''' When enabled only sensors that are just activated will send a positive event, after this they will be detected as negative by the controllers. This will make a key thats held act as if its only tapped for an instant. note: mutually exclusive with :attr: level , enabling will disable :attr: level .

    :type: bool
    '''

    invert: bool = None
    ''' Flag to set if this sensor activates on positive or negative events.

    :type: bool
    '''

    triggered: bool = None
    ''' True if this sensor brick is in a positive state. (read-only).

    :type: bool
    '''

    positive: bool = None
    ''' True if this sensor brick is in a positive state. (read-only).

    :type: bool
    '''

    pos_ticks: int = None
    ''' The number of ticks since the last positive pulse (read-only).

    :type: int
    '''

    neg_ticks: int = None
    ''' The number of ticks since the last negative pulse (read-only).

    :type: int
    '''

    status: int = None
    ''' The status of the sensor (read-only): can be one of :ref: these constants<sensor-status> .

    :type: int
    '''

    def reset(self):
        ''' Reset sensor internal state, effect depends on the type of sensor and settings. The sensor is put in its initial state as if it was just activated.

        '''
        pass


class SCA_InputEvent:
    ''' Events for a keyboard or mouse input.
    '''

    status: list = None
    ''' A list of existing status of the input from the last frame. Can contain :data: bge.logic.KX_INPUT_NONE and :data: bge.logic.KX_INPUT_ACTIVE . The list always contains one value. The first value of the list is the last value of the list in the last frame. (read-only)

    :type: list
    '''

    queue: list = None
    ''' A list of existing events of the input from the last frame. Can contain :data: bge.logic.KX_INPUT_JUST_ACTIVATED and :data: bge.logic.KX_INPUT_JUST_RELEASED . The list can be empty. (read-only)

    :type: list
    '''

    values: list = None
    ''' A list of existing value of the input from the last frame. For keyboard it contains 1 or 0 and for mouse the coordinate of the mouse or the movement of the wheel mouse. The list contains always one value, the size of the list is the same than :data: queue + 1 only for keyboard inputs. The first value of the list is the last value of the list in the last frame. (read-only) Example to get the non-normalized mouse coordinates:

    :type: list
    '''

    inactive: bool = None
    ''' True if the input was inactive from the last frame.

    :type: bool
    '''

    active: bool = None
    ''' True if the input was active from the last frame.

    :type: bool
    '''

    activated: bool = None
    ''' True if the input was activated from the last frame.

    :type: bool
    '''

    released: bool = None
    ''' True if the input was released from the last frame. Example to execute some action when I click or release mouse left button:

    :type: bool
    '''

    type = None
    ''' The type of the input. One of :ref: these constants<keyboard-keys>'''


class SCA_JoystickSensor:
    ''' This sensor detects player joystick events.
    '''

    axisValues: list = None
    ''' The state of the joysticks axis as a list of values :attr: numAxis long. (read-only). Each specifying the value of an axis between -32767 and 32767 depending on how far the axis is pushed, 0 for nothing. The first 2 values are used by most joysticks and gamepads for directional control. 3rd and 4th values are only on some joysticks and can be used for arbitary controls. * left:[-32767, 0, ...] * right:[32767, 0, ...] * up:[0, -32767, ...] * down:[0, 32767, ...]

    :type: list
    '''

    axisSingle = None
    ''' like :attr: axisValues but returns a single axis value that is set by the sensor. (read-only).'''

    hatValues: list = None
    ''' The state of the joysticks hats as a list of values :attr: numHats long. (read-only). Each specifying the direction of the hat from 1 to 12, 0 when inactive. Hat directions are as follows... * 0:None * 1:Up * 2:Right * 4:Down * 8:Left * 3:Up - Right * 6:Down - Right * 12:Down - Left * 9:Up - Left

    :type: list
    '''

    hatSingle = None
    ''' Like :attr: hatValues but returns a single hat direction value that is set by the sensor. (read-only).'''

    numAxis = None
    ''' The number of axes for the joystick at this index. (read-only).'''

    numButtons = None
    ''' The number of buttons for the joystick at this index. (read-only).'''

    numHats = None
    ''' The number of hats for the joystick at this index. (read-only).'''

    connected: bool = None
    ''' True if a joystick is connected at this joysticks index. (read-only).

    :type: bool
    '''

    index = None
    ''' The joystick index to use (from 0 to 7). The first joystick is always 0.'''

    threshold = None
    ''' Axis threshold. Joystick axis motion below this threshold wont trigger an event. Use values between (0 and 32767), lower values are more sensitive.'''

    button = None
    ''' The button index the sensor reacts to (first button = 0). When the "All Events" toggle is set, this option has no effect.'''

    axis = None
    ''' The axis this sensor reacts to, as a list of two values [axisIndex, axisDirection] * axisIndex: the axis index to use when detecting axis movement, 1=primary directional control, 2=secondary directional control. * axisDirection: 0=right, 1=up, 2=left, 3=down.'''

    hat = None
    ''' The hat the sensor reacts to, as a list of two values: [hatIndex, hatDirection] * hatIndex: the hat index to use when detecting hat movement, 1=primary hat, 2=secondary hat (4 max). * hatDirection: 1-12.'''

    def getButtonActiveList(self) -> list:
        ''' 

        :rtype: list
        :return: A list containing the indicies of the currently pressed buttons.
        '''
        pass

    def getButtonStatus(self, buttonIndex) -> bool:
        ''' 

        :param buttonIndex: the button index, 0=first button
        :type buttonIndex: 
        :rtype: bool
        :return: The current pressed state of the specified button.
        '''
        pass


class SCA_KeyboardSensor:
    ''' A keyboard sensor detects player key presses. See module :mod: bge.events for keycode values.
    '''

    key = None
    ''' The key code this sensor is looking for. Expects a keycode from :mod: bge.events module.'''

    hold1 = None
    ''' The key code for the first modifier this sensor is looking for. Expects a keycode from :mod: bge.events module.'''

    hold2 = None
    ''' The key code for the second modifier this sensor is looking for. Expects a keycode from :mod: bge.events module.'''

    toggleProperty: str = None
    ''' The name of the property that indicates whether or not to log keystrokes as a string.

    :type: str
    '''

    targetProperty: str = None
    ''' The name of the property that receives keystrokes in case in case a string is logged.

    :type: str
    '''

    useAllKeys: bool = None
    ''' Flag to determine whether or not to accept all keys.

    :type: bool
    '''

    inputs = None
    ''' A list of pressed input keys that have either been pressed, or just released, or are active this frame. (read-only).'''

    events: list = None
    ''' a list of pressed keys that have either been pressed, or just released, or are active this frame. (read-only).

    :type: list
    '''

    def getKeyStatus(self, keycode) -> int:
        ''' Get the status of a key.

        :param keycode: these constants<keyboard-keys>
        :type keycode: 
        :rtype: int
        :return: these constants<input-status>
        '''
        pass


class SCA_MouseActuator:
    ''' The mouse actuator gives control over the visibility of the mouse cursor and rotates the parent object according to mouse movement.
    '''

    visible: bool = None
    ''' The visibility of the mouse cursor.

    :type: bool
    '''

    use_axis_x: bool = None
    ''' Mouse movement along the x axis effects object rotation.

    :type: bool
    '''

    use_axis_y: bool = None
    ''' Mouse movement along the y axis effects object rotation.

    :type: bool
    '''

    threshold: list = None
    ''' Amount of movement from the mouse required before rotation is triggered. The values in the list should be between 0.0 and 0.5.

    :type: list
    '''

    reset_x: bool = None
    ''' Mouse is locked to the center of the screen on the x axis.

    :type: bool
    '''

    reset_y: bool = None
    ''' Mouse is locked to the center of the screen on the y axis.

    :type: bool
    '''

    object_axis: list = None
    ''' The object's 3D axis to rotate with the mouse movement. ([x, y]) * KX_ACT_MOUSE_OBJECT_AXIS_X * KX_ACT_MOUSE_OBJECT_AXIS_Y * KX_ACT_MOUSE_OBJECT_AXIS_Z

    :type: list
    '''

    local_x: bool = None
    ''' Rotation caused by mouse movement along the x axis is local.

    :type: bool
    '''

    local_y: bool = None
    ''' Rotation caused by mouse movement along the y axis is local.

    :type: bool
    '''

    sensitivity: list = None
    ''' The amount of rotation caused by mouse movement along the x and y axis. Negative values invert the rotation.

    :type: list
    '''

    limit_x: list = None
    ''' The minimum and maximum angle of rotation caused by mouse movement along the x axis in degrees. limit_x[0] is minimum, limit_x[1] is maximum.

    :type: list
    '''

    limit_y: list = None
    ''' The minimum and maximum angle of rotation caused by mouse movement along the y axis in degrees. limit_y[0] is minimum, limit_y[1] is maximum.

    :type: list
    '''

    angle: list = None
    ''' The current rotational offset caused by the mouse actuator in degrees.

    :type: list
    '''

    def reset(self):
        ''' Undoes the rotation caused by the mouse actuator.

        '''
        pass


class SCA_MouseFocusSensor:
    ''' The mouse focus sensor detects when the mouse is over the current game object. The mouse focus sensor works by transforming the mouse coordinates from 2d device space to 3d space then raycasting away from the camera.
    '''

    raySource: list = None
    ''' The worldspace source of the ray (the view position).

    :type: list
    '''

    rayTarget: list = None
    ''' The worldspace target of the ray.

    :type: list
    '''

    rayDirection: list = None
    ''' The :attr: rayTarget - :attr: raySource normalized.

    :type: list
    '''

    hitObject = None
    ''' the last object the mouse was over.'''

    hitPosition: list = None
    ''' The worldspace position of the ray intersecton.

    :type: list
    '''

    hitNormal: list = None
    ''' the worldspace normal from the face at point of intersection.

    :type: list
    '''

    hitUV: list = None
    ''' the UV coordinates at the point of intersection. If the object has no UV mapping, it returns [0, 0]. The UV coordinates are not normalized, they can be < 0 or > 1 depending on the UV mapping.

    :type: list
    '''

    usePulseFocus: bool = None
    ''' When enabled, moving the mouse over a different object generates a pulse. (only used when the 'Mouse Over Any' sensor option is set).

    :type: bool
    '''

    useXRay: bool = None
    ''' If enabled it allows the sensor to see through game objects that don't have the selected property or material.

    :type: bool
    '''

    mask = None
    ''' The collision mask (16 layers mapped to a 16-bit integer) combined with each object's collision group, to hit only a subset of the objects in the scene. Only those objects for which collisionGroup & mask is true can be hit.'''

    propName: str = None
    ''' The property or material the sensor is looking for.

    :type: str
    '''

    useMaterial: bool = None
    ''' Determines if the sensor is looking for a property or material. KX_True = Find material; KX_False = Find property.

    :type: bool
    '''


class SCA_MouseSensor:
    ''' Mouse Sensor logic brick.
    '''

    position = None
    ''' current [x, y] coordinates of the mouse, in frame coordinates (pixels).'''

    mode = None
    ''' sensor mode. one of the following constants: * KX_MOUSESENSORMODE_LEFTBUTTON(1) * KX_MOUSESENSORMODE_MIDDLEBUTTON(2) * KX_MOUSESENSORMODE_RIGHTBUTTON(3) * KX_MOUSESENSORMODE_BUTTON4(4) * KX_MOUSESENSORMODE_BUTTON5(5) * KX_MOUSESENSORMODE_BUTTON6(6) * KX_MOUSESENSORMODE_BUTTON7(7) * KX_MOUSESENSORMODE_WHEELUP(8) * KX_MOUSESENSORMODE_WHEELDOWN(9) * KX_MOUSESENSORMODE_MOVEMENT(10)'''

    def getButtonStatus(self, button: int) -> int:
        ''' Get the mouse button status.

        :param button: these constants<mouse-keys>
        :type button: int
        :rtype: int
        :return: these constants<input-status>
        '''
        pass


class SCA_NANDController:
    ''' An NAND controller activates when all linked sensors are not active. There are no special python methods for this controller.
    '''

    pass


class SCA_NORController:
    ''' An NOR controller activates only when all linked sensors are de-activated. There are no special python methods for this controller.
    '''

    pass


class SCA_NearSensor:
    ''' A near sensor is a specialised form of touch sensor.
    '''

    distance: float = None
    ''' The near sensor activates when an object is within this distance.

    :type: float
    '''

    resetDistance: float = None
    ''' The near sensor deactivates when the object exceeds this distance.

    :type: float
    '''


class SCA_NetworkMessageActuator:
    ''' Message Actuator
    '''

    propName: str = None
    ''' Messages will only be sent to objects with the given property name.

    :type: str
    '''

    subject: str = None
    ''' The subject field of the message.

    :type: str
    '''

    body: str = None
    ''' The body of the message.

    :type: str
    '''

    usePropBody: bool = None
    ''' Send a property instead of a regular body message.

    :type: bool
    '''


class SCA_NetworkMessageSensor:
    ''' The Message Sensor logic brick. Currently only loopback (local) networks are supported.
    '''

    subject: str = None
    ''' The subject the sensor is looking for.

    :type: str
    '''

    frameMessageCount = None
    ''' The number of messages received since the last frame. (read-only).'''

    subjects: list = None
    ''' The list of message subjects received. (read-only).

    :type: list
    '''

    bodies: list = None
    ''' The list of message bodies received. (read-only).

    :type: list
    '''


class SCA_ORController:
    ''' An OR controller activates when any connected sensor activates. There are no special python methods for this controller.
    '''

    pass


class SCA_ObjectActuator:
    ''' The object actuator ("Motion Actuator") applies force, torque, displacement, angular displacement, velocity, or angular velocity to an object. Servo control allows to regulate force to achieve a certain speed target.
    '''

    force = None
    ''' The force applied by the actuator.'''

    useLocalForce: bool = None
    ''' A flag specifying if the force is local.

    :type: bool
    '''

    torque = None
    ''' The torque applied by the actuator.'''

    useLocalTorque: bool = None
    ''' A flag specifying if the torque is local.

    :type: bool
    '''

    dLoc = None
    ''' The displacement vector applied by the actuator.'''

    useLocalDLoc: bool = None
    ''' A flag specifying if the dLoc is local.

    :type: bool
    '''

    dRot = None
    ''' The angular displacement vector applied by the actuator'''

    useLocalDRot: bool = None
    ''' A flag specifying if the dRot is local.

    :type: bool
    '''

    linV = None
    ''' The linear velocity applied by the actuator.'''

    useLocalLinV: bool = None
    ''' A flag specifying if the linear velocity is local.

    :type: bool
    '''

    angV = None
    ''' The angular velocity applied by the actuator.'''

    useLocalAngV: bool = None
    ''' A flag specifying if the angular velocity is local.

    :type: bool
    '''

    damping = None
    ''' The damping parameter of the servo controller.'''

    forceLimitX: typing.List[float] = None
    ''' The min/max force limit along the X axis and activates or deactivates the limits in the servo controller.

    :type: typing.List[float]
    '''

    forceLimitY: typing.List[float] = None
    ''' The min/max force limit along the Y axis and activates or deactivates the limits in the servo controller.

    :type: typing.List[float]
    '''

    forceLimitZ: typing.List[float] = None
    ''' The min/max force limit along the Z axis and activates or deactivates the limits in the servo controller.

    :type: typing.List[float]
    '''

    pid: list = None
    ''' The PID coefficients of the servo controller.

    :type: list
    '''

    reference = None
    ''' The object that is used as reference to compute the velocity for the servo controller.'''


class SCA_ParentActuator:
    ''' The parent actuator can set or remove an objects parent object.
    '''

    object = None
    ''' the object this actuator sets the parent too.'''

    mode = None
    ''' The mode of this actuator.'''

    compound: bool = None
    ''' Whether the object shape should be added to the parent compound shape when parenting. Effective only if the parent is already a compound shape.

    :type: bool
    '''

    ghost: bool = None
    ''' Whether the object should be made ghost when parenting Effective only if the shape is not added to the parent compound shape.

    :type: bool
    '''


class SCA_PropertyActuator:
    ''' Property Actuator
    '''

    propName: str = None
    ''' the property on which to operate.

    :type: str
    '''

    value: str = None
    ''' the value with which the actuator operates.

    :type: str
    '''

    mode = None
    ''' TODO - add constants to game logic dict!.'''


class SCA_PropertySensor:
    ''' Activates when the game object property matches.
    '''

    mode = None
    ''' Type of check on the property. Can be one of :ref: these constants <logic-property-sensor>'''

    propName: str = None
    ''' the property the sensor operates.

    :type: str
    '''

    value: str = None
    ''' the value with which the sensor compares to the value of the property.

    :type: str
    '''

    min: str = None
    ''' the minimum value of the range used to evaluate the property when in interval mode.

    :type: str
    '''

    max: str = None
    ''' the maximum value of the range used to evaluate the property when in interval mode.

    :type: str
    '''


class SCA_PythonController:
    ''' A Python controller uses a Python script to activate it's actuators, based on it's sensors.
    '''

    owner = None
    ''' The object the controller is attached to.'''

    script: str = None
    ''' The value of this variable depends on the execution methid. * When 'Script' execution mode is set this value contains the entire python script as a single string (not the script name as you might expect) which can be modified to run different scripts. * When 'Module' execution mode is set this value will contain a single line string - module name and function "module.func" or "package.modile.func" where the module names are python textblocks or external scripts.

    :type: str
    '''

    mode = None
    ''' the execution mode for this controller (read-only). * Script: 0, Execite the :attr: script as a python code. * Module: 1, Execite the :attr: script as a module and function.'''

    def activate(self, actuator: str):
        ''' Activates an actuator attached to this controller.

        :param actuator: The actuator to operate on. Expects either an actuator instance or its name.
        :type actuator: str
        '''
        pass

    def deactivate(self, actuator: str):
        ''' Deactivates an actuator attached to this controller.

        :param actuator: The actuator to operate on. Expects either an actuator instance or its name.
        :type actuator: str
        '''
        pass


class SCA_PythonJoystick:
    ''' A Python interface to a joystick.
    '''

    name: str = None
    ''' The name assigned to the joystick by the operating system. (read-only)

    :type: str
    '''

    activeButtons: list = None
    ''' A list of active button values. (read-only)

    :type: list
    '''

    axisValues: list = None
    ''' The state of the joysticks axis as a list of values :attr: numAxis long. (read-only). Each specifying the value of an axis between -1.0 and 1.0 depending on how far the axis is pushed, 0 for nothing. The first 2 values are used by most joysticks and gamepads for directional control. 3rd and 4th values are only on some joysticks and can be used for arbitary controls. * left:[-1.0, 0.0, ...] * right:[1.0, 0.0, ...] * up:[0.0, -1.0, ...] * down:[0.0, 1.0, ...]

    :type: list
    '''

    hatValues = None
    ''' '''

    numAxis = None
    ''' The number of axes for the joystick at this index. (read-only).'''

    numButtons = None
    ''' The number of buttons for the joystick at this index. (read-only).'''

    numHats = None
    ''' '''

    strengthLeft: float = None
    ''' Strength of the Low frequency joystick's motor (placed at left position usually).

    :type: float
    '''

    strengthRight: float = None
    ''' Strength of the High frequency joystick's motor (placed at right position usually).

    :type: float
    '''

    duration = None
    ''' Duration of the vibration in milliseconds.'''

    isVibrating: bool = None
    ''' Check status of joystick vibration

    :type: bool
    '''

    hasVibration: bool = None
    ''' Check if the joystick supports vibration

    :type: bool
    '''

    def startVibration(self):
        ''' Starts the vibration.

        '''
        pass

    def stopVibration(self):
        ''' Stops the vibration.

        '''
        pass


class SCA_PythonKeyboard:
    ''' The current keyboard.
    '''

    inputs = None
    ''' A dictionary containing the input of each keyboard key. (read-only).'''

    events = None
    ''' A dictionary containing the status of each keyboard event or key. (read-only).'''

    activeInputs = None
    ''' A dictionary containing the input of only the active keyboard keys. (read-only).'''

    active_events = None
    ''' A dictionary containing the status of only the active keyboard events or keys. (read-only).'''

    text: str = None
    ''' The typed unicode text from the last frame.

    :type: str
    '''

    def getClipboard(self):
        ''' Gets the clipboard text.

        '''
        pass

    def setClipboard(self, text: str):
        ''' Sets the clipboard text.

        :param text: New clipboard text
        :type text: str
        '''
        pass


class SCA_PythonMouse:
    ''' The current mouse.
    '''

    inputs = None
    ''' A dictionary containing the input of each mouse event. (read-only).'''

    events = None
    ''' a dictionary containing the status of each mouse event. (read-only).'''

    activeInputs = None
    ''' A dictionary containing the input of only the active mouse events. (read-only).'''

    active_events = None
    ''' a dictionary containing the status of only the active mouse events. (read-only).'''

    position: tuple = None
    ''' The normalized x and y position of the mouse cursor.

    :type: tuple
    '''

    visible: bool = None
    ''' The visibility of the mouse cursor.

    :type: bool
    '''


class SCA_RadarSensor:
    ''' Radar sensor is a near sensor with a conical sensor object.
    '''

    coneOrigin: list = None
    ''' The origin of the cone with which to test. The origin is in the middle of the cone. (read-only).

    :type: list
    '''

    coneTarget: list = None
    ''' The center of the bottom face of the cone with which to test. (read-only).

    :type: list
    '''

    distance: float = None
    ''' The height of the cone with which to test (read-only).

    :type: float
    '''

    angle: float = None
    ''' The angle of the cone (in degrees) with which to test (read-only).

    :type: float
    '''

    axis = None
    ''' The axis on which the radar cone is cast. KX_RADAR_AXIS_POS_X, KX_RADAR_AXIS_POS_Y, KX_RADAR_AXIS_POS_Z, KX_RADAR_AXIS_NEG_X, KX_RADAR_AXIS_NEG_Y, KX_RADAR_AXIS_NEG_Z'''


class SCA_RandomActuator:
    ''' Random Actuator
    '''

    seed = None
    ''' Seed of the random number generator. Equal seeds produce equal series. If the seed is 0, the generator will produce the same value on every call.'''

    para1: float = None
    ''' the first parameter of the active distribution. Refer to the documentation of the generator types for the meaning of this value.

    :type: float
    '''

    para2: float = None
    ''' the second parameter of the active distribution. Refer to the documentation of the generator types for the meaning of this value.

    :type: float
    '''

    distribution = None
    ''' Distribution type. (read-only). Can be one of :ref: these constants <logic-random-distributions>'''

    propName: str = None
    ''' the name of the property to set with the random value. If the generator and property types do not match, the assignment is ignored.

    :type: str
    '''

    def setBoolConst(self, value: bool):
        ''' Sets this generator to produce a constant boolean value.

        :param value: The value to return.
        :type value: bool
        '''
        pass

    def setBoolUniform(self):
        ''' Sets this generator to produce a uniform boolean distribution. The generator will generate True or False with 50% chance.

        '''
        pass

    def setBoolBernouilli(self, value: float):
        ''' Sets this generator to produce a Bernouilli distribution.

        :param value: Specifies the proportion of False values to produce. * 0.0: Always generate True * 1.0: Always generate False
        :type value: float
        '''
        pass

    def setIntConst(self, value):
        ''' Sets this generator to always produce the given value.

        :param value: the value this generator produces.
        :type value: 
        '''
        pass

    def setIntUniform(self, lower_bound, upper_bound):
        ''' Sets this generator to produce a random value between the given lower and upper bounds (inclusive).

        :param lower_bound: 
        :type lower_bound: 
        :param upper_bound: 
        :type upper_bound: 
        '''
        pass

    def setIntPoisson(self, value: float):
        ''' Generate a Poisson-distributed number. This performs a series of Bernouilli tests with parameter value. It returns the number of tries needed to achieve succes.

        :param value: 
        :type value: float
        '''
        pass

    def setFloatConst(self, value: float):
        ''' Always generate the given value.

        :param value: 
        :type value: float
        '''
        pass

    def setFloatUniform(self, lower_bound: float, upper_bound: float):
        ''' Generates a random float between lower_bound and upper_bound with a uniform distribution.

        :param lower_bound: 
        :type lower_bound: float
        :param upper_bound: 
        :type upper_bound: float
        '''
        pass

    def setFloatNormal(self, mean: float, standard_deviation: float):
        ''' Generates a random float from the given normal distribution.

        :param mean: The mean (average) value of the generated numbers
        :type mean: float
        :param standard_deviation: The standard deviation of the generated numbers.
        :type standard_deviation: float
        '''
        pass

    def setFloatNegativeExponential(self, half_life: float):
        ''' Generate negative-exponentially distributed numbers. The half-life 'time' is characterized by half_life.

        :param half_life: 
        :type half_life: float
        '''
        pass


class SCA_RandomSensor:
    ''' This sensor activates randomly.
    '''

    lastDraw = None
    ''' The seed of the random number generator.'''

    seed = None
    ''' The seed of the random number generator.'''


class SCA_RaySensor:
    ''' A ray sensor detects the first object in a given direction.
    '''

    propName: str = None
    ''' The property the ray is looking for.

    :type: str
    '''

    range: float = None
    ''' The distance of the ray.

    :type: float
    '''

    useMaterial: bool = None
    ''' Whether or not to look for a material (false = property).

    :type: bool
    '''

    useXRay: bool = None
    ''' Whether or not to use XRay.

    :type: bool
    '''

    mask = None
    ''' The collision mask (16 layers mapped to a 16-bit integer) combined with each object's collision group, to hit only a subset of the objects in the scene. Only those objects for which collisionGroup & mask is true can be hit.'''

    hitObject = None
    ''' The game object that was hit by the ray. (read-only).'''

    hitPosition: list = None
    ''' The position (in worldcoordinates) where the object was hit by the ray. (read-only).

    :type: list
    '''

    hitNormal: list = None
    ''' The normal (in worldcoordinates) of the object at the location where the object was hit by the ray. (read-only).

    :type: list
    '''

    hitMaterial: str = None
    ''' The material of the object in the face hit by the ray. (read-only).

    :type: str
    '''

    rayDirection: list = None
    ''' The direction from the ray (in worldcoordinates). (read-only).

    :type: list
    '''

    axis = None
    ''' The axis the ray is pointing on. * KX_RAY_AXIS_POS_X * KX_RAY_AXIS_POS_Y * KX_RAY_AXIS_POS_Z * KX_RAY_AXIS_NEG_X * KX_RAY_AXIS_NEG_Y * KX_RAY_AXIS_NEG_Z'''


class SCA_ReplaceMeshActuator:
    ''' Edit Object actuator, in Replace Mesh mode.
    '''

    mesh: typing.Set['bpy.context.mesh'] = None
    ''' ~bge.types.KX_MeshProxy or the name of the mesh that will replace the current one. Set to None to disable actuator.

    :type: typing.Set['bpy.context.mesh']
    '''

    useDisplayMesh: bool = None
    ''' when true the displayed mesh is replaced.

    :type: bool
    '''

    usePhysicsMesh: bool = None
    ''' when true the physics mesh is replaced.

    :type: bool
    '''

    def instantReplaceMesh(self):
        ''' Immediately replace mesh without delay.

        '''
        pass


class SCA_SceneActuator:
    ''' Scene Actuator logic brick.
    '''

    scene: str = None
    ''' the name of the scene to change to/overlay/underlay/remove/suspend/resume.

    :type: str
    '''

    camera: str = None
    ''' the camera to change to.

    :type: str
    '''

    useRestart: bool = None
    ''' Set flag to True to restart the sene.

    :type: bool
    '''

    mode = None
    ''' The mode of the actuator.'''


class SCA_SoundActuator:
    ''' Sound Actuator. The :meth: startSound , :meth: pauseSound and :meth: stopSound do not require the actuator to be activated - they act instantly provided that the actuator has been activated once at least.
    '''

    volume: float = None
    ''' The volume (gain) of the sound.

    :type: float
    '''

    time: float = None
    ''' The current position in the audio stream (in seconds).

    :type: float
    '''

    pitch: float = None
    ''' The pitch of the sound.

    :type: float
    '''

    mode = None
    ''' The operation mode of the actuator. Can be one of :ref: these constants<logic-sound-actuator>'''

    sound: 'aud.Sound' = None
    ''' The sound the actuator should play.

    :type: 'aud.Sound'
    '''

    is3D: bool = None
    ''' Whether or not the actuator should be using 3D sound. (read-only)

    :type: bool
    '''

    volume_maximum: float = None
    ''' The maximum gain of the sound, no matter how near it is.

    :type: float
    '''

    volume_minimum: float = None
    ''' The minimum gain of the sound, no matter how far it is away.

    :type: float
    '''

    distance_reference: float = None
    ''' The distance where the sound has a gain of 1.0.

    :type: float
    '''

    distance_maximum: float = None
    ''' The maximum distance at which you can hear the sound.

    :type: float
    '''

    attenuation: float = None
    ''' The influence factor on volume depending on distance.

    :type: float
    '''

    cone_angle_inner: float = None
    ''' The angle of the inner cone.

    :type: float
    '''

    cone_angle_outer: float = None
    ''' The angle of the outer cone.

    :type: float
    '''

    cone_volume_outer: float = None
    ''' The gain outside the outer cone (the gain in the outer cone will be interpolated between this value and the normal gain in the inner cone).

    :type: float
    '''

    def startSound(self):
        ''' Starts the sound.

        '''
        pass

    def pauseSound(self):
        ''' Pauses the sound.

        '''
        pass

    def stopSound(self):
        ''' Stops the sound.

        '''
        pass


class SCA_StateActuator:
    ''' State actuator changes the state mask of parent object.
    '''

    operation = None
    ''' Type of bit operation to be applied on object state mask. You can use one of :ref: these constants <state-actuator-operation>'''

    mask = None
    ''' Value that defines the bits that will be modified by the operation. The bits that are 1 in the mask will be updated in the object state. The bits that are 0 are will be left unmodified expect for the Copy operation which copies the mask to the object state.'''


class SCA_SteeringActuator:
    ''' Steering Actuator for navigation.
    '''

    behavior = None
    ''' The steering behavior to use. One of :ref: these constants <logic-steering-actuator> .'''

    velocity: float = None
    ''' Velocity magnitude

    :type: float
    '''

    acceleration: float = None
    ''' Max acceleration

    :type: float
    '''

    turnspeed: float = None
    ''' Max turn speed

    :type: float
    '''

    distance: float = None
    ''' Relax distance

    :type: float
    '''

    target = None
    ''' Target object'''

    navmesh = None
    ''' Navigation mesh'''

    selfterminated: bool = None
    ''' Terminate when target is reached

    :type: bool
    '''

    enableVisualization: bool = None
    ''' Enable debug visualization

    :type: bool
    '''

    pathUpdatePeriod: int = None
    ''' Path update period

    :type: int
    '''

    path: typing.List['mathutils.Vector'] = None
    ''' Path point list.

    :type: typing.List['mathutils.Vector']
    '''


class SCA_TrackToActuator:
    ''' Edit Object actuator in Track To mode.
    '''

    object = None
    ''' the object this actuator tracks.'''

    time = None
    ''' the time in frames with which to delay the tracking motion.'''

    use3D: bool = None
    ''' the tracking motion to use 3D.

    :type: bool
    '''

    upAxis = None
    ''' The axis that points upward. * KX_TRACK_UPAXIS_POS_X * KX_TRACK_UPAXIS_POS_Y * KX_TRACK_UPAXIS_POS_Z'''

    trackAxis = None
    ''' The axis that points to the target object. * KX_TRACK_TRAXIS_POS_X * KX_TRACK_TRAXIS_POS_Y * KX_TRACK_TRAXIS_POS_Z * KX_TRACK_TRAXIS_NEG_X * KX_TRACK_TRAXIS_NEG_Y * KX_TRACK_TRAXIS_NEG_Z'''


class SCA_VibrationActuator:
    ''' Vibration Actuator.
    '''

    joyindex = None
    ''' Joystick index.'''

    strengthLeft: float = None
    ''' Strength of the Low frequency joystick's motor (placed at left position usually).

    :type: float
    '''

    strengthRight: float = None
    ''' Strength of the High frequency joystick's motor (placed at right position usually).

    :type: float
    '''

    duration = None
    ''' Duration of the vibration in milliseconds.'''

    isVibrating: bool = None
    ''' Check status of joystick vibration

    :type: bool
    '''

    hasVibration: bool = None
    ''' Check if the joystick supports vibration

    :type: bool
    '''

    def startVibration(self):
        ''' Starts the vibration.

        '''
        pass

    def stopVibration(self):
        ''' Stops the vibration.

        '''
        pass


class SCA_VisibilityActuator:
    ''' Visibility Actuator.
    '''

    visibility: bool = None
    ''' whether the actuator makes its parent object visible or invisible.

    :type: bool
    '''

    useOcclusion: bool = None
    ''' whether the actuator makes its parent object an occluder or not.

    :type: bool
    '''

    useRecursion: bool = None
    ''' whether the visibility/occlusion should be propagated to all children of the object.

    :type: bool
    '''


class SCA_XNORController:
    ''' An XNOR controller activates when all linked sensors are the same (activated or inative). There are no special python methods for this controller.
    '''

    pass


class SCA_XORController:
    ''' An XOR controller activates when there is the input is mixed, but not when all are on or off. There are no special python methods for this controller.
    '''

    pass


class BL_Texture(EXP_Value):
    ''' This is kept for backward compatibility with some scripts (bindCode mainly).
    '''

    bindCode = None
    ''' Texture bind code/Id/number.'''
