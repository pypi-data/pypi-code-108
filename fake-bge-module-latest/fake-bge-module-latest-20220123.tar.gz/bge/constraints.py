import sys
import typing


def createConstraint(physicsid_1: int,
                     physicsid_2: int,
                     constraint_type: int,
                     pivot_x: float = 0.0,
                     pivot_y: float = 0.0,
                     pivot_z: float = 0.0,
                     axis_x: float = 0.0,
                     axis_y: float = 0.0,
                     axis_z: float = 0.0,
                     flag: int = 0):
    ''' Creates a constraint.

    :param physicsid_1: The physics id of the first object in constraint.
    :type physicsid_1: int
    :param physicsid_2: The physics id of the second object in constraint.
    :type physicsid_2: int
    :param constraint_type: The type of the constraint, see Create Constraint Constants _.
    :type constraint_type: int
    :param pivot_x: Pivot X position. (optional)
    :type pivot_x: float
    :param pivot_y: Pivot Y position. (optional)
    :type pivot_y: float
    :param pivot_z: Pivot Z position. (optional)
    :type pivot_z: float
    :param axis_x: X axis angle in degrees. (optional)
    :type axis_x: float
    :param axis_y: Y axis angle in degrees. (optional)
    :type axis_y: float
    :param axis_z: Z axis angle in degrees. (optional)
    :type axis_z: float
    :param flag: 128 to disable collision between linked bodies. (optional)
    :type flag: int
    :return: A constraint wrapper.
    '''

    pass


def createVehicle(physicsid: int):
    ''' Creates a vehicle constraint.

    :param physicsid: The physics id of the chassis object in constraint.
    :type physicsid: int
    :return: A vehicle constraint wrapper.
    '''

    pass


def exportBulletFile(filename: str):
    ''' Exports a file representing the dynamics world (usually using .bullet extension). See Bullet binary serialization <http://bulletphysics.org/mediawiki-1.5.8/index.php/Bullet_binary_serialization> __.

    :param filename: File path.
    :type filename: str
    '''

    pass


def getAppliedImpulse(constraintId: int) -> float:
    ''' 

    :param constraintId: The id of the constraint.
    :type constraintId: int
    :rtype: float
    :return: The most recent applied impulse.
    '''

    pass


def getCharacter(gameobj):
    ''' 

    :param gameobj: The game object with the character physics.
    :return: Character wrapper.
    '''

    pass


def getVehicleConstraint(constraintId: int):
    ''' 

    :param constraintId: The id of the vehicle constraint.
    :type constraintId: int
    :return: A vehicle constraint object.
    '''

    pass


def removeConstraint(constraintId: int):
    ''' Removes a constraint.

    :param constraintId: The id of the constraint to be removed.
    :type constraintId: int
    '''

    pass


def setCFM(cfm: float):
    ''' Sets the Constraint Force Mixing (CFM) for soft constraints. If the Constraint Force Mixing (CFM) is set to zero, the constraint will be hard. If CFM is set to a positive value, it will be possible to violate the constraint by pushing on it (for example, for contact constraints by forcing the two contacting objects together). In other words the constraint will be soft, and the softness will increase as CFM increases.

    :param cfm: The CFM parameter for soft constraints.
    :type cfm: float
    '''

    pass


def setContactBreakingTreshold(breakingTreshold: float):
    ''' Sets tresholds to do with contact point management.

    :param breakingTreshold: The new contact breaking treshold.
    :type breakingTreshold: float
    '''

    pass


def setDeactivationAngularTreshold(angularTreshold: float):
    ''' Sets the angular velocity treshold.

    :param angularTreshold: New deactivation angular treshold.
    :type angularTreshold: float
    '''

    pass


def setDeactivationLinearTreshold(linearTreshold: float):
    ''' Sets the linear velocity treshold.

    :param linearTreshold: New deactivation linear treshold.
    :type linearTreshold: float
    '''

    pass


def setDeactivationTime(time: float):
    ''' Sets the time after which a resting rigidbody gets deactived.

    :param time: The deactivation time.
    :type time: float
    '''

    pass


def setDebugMode(mode: int):
    ''' Sets the debug mode.

    :param mode: The new debug mode, see Debug Mode Constants _.
    :type mode: int
    '''

    pass


def setERPContact(erp2: float):
    ''' Sets the Error Reduction Parameter (ERP) for contact constraints. The Error Reduction Parameter (ERP) specifies what proportion of the joint error will be fixed during the next simulation step. If ERP = 0.0 then no correcting force is applied and the bodies will eventually drift apart as the simulation proceeds. If ERP = 1.0 then the simulation will attempt to fix all joint error during the next time step. However, setting ERP = 1.0 is not recommended, as the joint error will not be completely fixed due to various internal approximations. A value of ERP = 0.1 to 0.8 is recommended.

    :param erp2: The ERP parameter for contact constraints.
    :type erp2: float
    '''

    pass


def setERPNonContact(erp: float):
    ''' Sets the Error Reduction Parameter (ERP) for non-contact constraints. The Error Reduction Parameter (ERP) specifies what proportion of the joint error will be fixed during the next simulation step. If ERP = 0.0 then no correcting force is applied and the bodies will eventually drift apart as the simulation proceeds. If ERP = 1.0 then the simulation will attempt to fix all joint error during the next time step. However, setting ERP = 1.0 is not recommended, as the joint error will not be completely fixed due to various internal approximations. A value of ERP = 0.1 to 0.8 is recommended.

    :param erp: The ERP parameter for non-contact constraints.
    :type erp: float
    '''

    pass


def setGravity(x: float, y: float, z: float):
    ''' Sets the gravity force. Sets the linear air damping for rigidbodies.

    :param x: Gravity X force.
    :type x: float
    :param y: Gravity Y force.
    :type y: float
    :param z: Gravity Z force.
    :type z: float
    '''

    pass


def setNumIterations(numiter: int):
    ''' Sets the number of iterations for an iterative constraint solver.

    :param numiter: New number of iterations.
    :type numiter: int
    '''

    pass


def setNumTimeSubSteps(numsubstep: int):
    ''' Sets the number of substeps for each physics proceed. Tradeoff quality for performance.

    :param numsubstep: New number of substeps.
    :type numsubstep: int
    '''

    pass


def setSolverDamping(damping: float):
    ''' Sets the damper constant of a penalty based solver.

    :param damping: New damping for the solver.
    :type damping: float
    '''

    pass


def setSolverTau(tau: float):
    ''' Sets the spring constant of a penalty based solver.

    :param tau: New tau for the solver.
    :type tau: float
    '''

    pass


def setSolverType(solverType: int):
    ''' Sets the solver type.

    :param solverType: The new type of the solver.
    :type solverType: int
    '''

    pass


def setSorConstant(sor: float):
    ''' Sets the successive overrelaxation constant.

    :param sor: New sor value.
    :type sor: float
    '''

    pass


ANGULAR_CONSTRAINT = None

CONETWIST_CONSTRAINT = None

DBG_DISABLEBULLETLCP = None
''' Disable Bullet LCP.
'''

DBG_DRAWAABB = None
''' Draw Axis Aligned Bounding Box in debug.
'''

DBG_DRAWCONSTRAINTLIMITS = None
''' Draw constraint limits in debug.
'''

DBG_DRAWCONSTRAINTS = None
''' Draw constraints in debug.
'''

DBG_DRAWCONTACTPOINTS = None
''' Draw contact points in debug.
'''

DBG_DRAWFREATURESTEXT = None
''' Draw features text in debug.
'''

DBG_DRAWTEXT = None
''' Draw text in debug.
'''

DBG_DRAWWIREFRAME = None
''' Draw wireframe in debug.
'''

DBG_ENABLECCD = None
''' Enable Continous Collision Detection in debug.
'''

DBG_ENABLESATCOMPARISION = None
''' Enable sat comparision in debug.
'''

DBG_FASTWIREFRAME = None
''' Draw a fast wireframe in debug.
'''

DBG_NODEBUG = None
''' No debug.
'''

DBG_NOHELPTEXT = None
''' Debug without help text.
'''

DBG_PROFILETIMINGS = None
''' Draw profile timings in debug.
'''

GENERIC_6DOF_CONSTRAINT = None

LINEHINGE_CONSTRAINT = None

POINTTOPOINT_CONSTRAINT = None

VEHICLE_CONSTRAINT = None

error: str = None
''' Symbolic constant string that indicates error.
'''
