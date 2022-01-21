from enum import Enum
import datetime


class DefFileConstants(object):
    """ """
    FUNC_CRITERIA = "criteria"
    FUNC_DATA_VISUALIZATION = "data_visualization"


class IsommeConstants(object):
    """ """
    CHANNELS = "Channels"
    CHANNEL = "Channel"
    INSTUMENTATION_STANDARD = "Not applicable"
    MODEL_6YO = "6yo"
    MODEL_AM50 = "AM50"

    TIME = "Time"
    CONTACT_FORCE = "Contact Force"
    TRAJECTORY = "Trajectory"
    TRAJECTORIES = "Trajectories"
    HEAD_COG = "HC"
    ENERGY = "Energy"
    ENERGIES = "Energies"
    ADDED_MASS = "Added Mass"
    TIMESTEP = "Timestep"
    GV = "GV"
    ENERGY_HBM = "Energy HBM"
    REL_ADDED_MASS = "Rel. Added Mass"
    ADDED_MASS_HBM = "Added Mass HBM"
    HIT = "HIT"
    WAD = "WAD"

    PEDESTRIAN_GV = "pedestrian-GV"
    HEAD_GV = "head-GV"
    ARM_GV = "arm-GV"
    RIGHT_LEG_BUMPER = "right_leg-bumper"
    TORSO_BUMPER = "torso-bumper"
    PEDESTRIAN_BONNET = "pedestrian-bonnet"
    PEDESTRIAN_BUMPER = "pedestrian-bumper"

    HC = "HC"
    C7 = "C7"
    T12 = "T12"
    AC = "AC"
    T8 = "T8"
    FER = "FER"
    ML = "ML"
    FEL = "FEL"
    MR = "MR"
    TOTAL_HOURGLASS_ENERGY_HBM = "total_hourglass_energy-HBM"
    HBM = "HBM"

    RESULTANT = "resultant"
    RESULTANT_CF = "resultant-CF"
    X_COORDINATE = "x-Coordinate"
    Z_COORDINATE = "z-Coordinate"
    Z_ACCELERATION = "z-acceleration"
    RESULTANT_ACCELERATION = "resultant-acceleration"
    RESULTANT_VELOCITY = "resultant-velocity"
    TOTAL_HOURGLASS_ENERGY = "total_hourglass_energy"
    TOTAL_INTERNAL_ENERGY = "total_internal_energy"
    TOTAL_ENERGY = "total_energy"
    CONTACT_ENERGY = "contact_energy"
    ADDED_MASS_WS = "added_mass-"
    # WS stands for whole setup, the definition in the templates is ambigous, maybe those need to be changed later
    # on because of the "-" at the end which is a mistake
    REL_ADDED_MASS_WS = "relative_added_mass-"
    WHOLE_SETUP = "whole_setup"

    NO_VALUE = "NOVALUE"


class TransducerConstants(object):
    """ """
    COORDINATE = "Coordinate"
    FORCE = "Force"
    TIME = "Time"
    ACCELERATION = "Acceleration"
    VELOCITY = "Velocity"
    ENERGY = "Energy"
    MASS = "Mass"


class UnitsConstants(object):
    """ """
    TIME = "time"
    LENGTH = "length"
    WEIGHT = "weight"
    SECOND = "s"
    MILLISECOND = "ms"
    METER = "m"
    MILLIMETER = "mm"
    KILOGRAM = "kg"
    KNEWTON = "kN"
    VELOCITY = "m/s"
    TON = "t"
    ONE = 1
    THOUSAND = 1000
    WEIGHT_DEFAULT = 0.001
    JOULE = "J"


class MadymoConstants:
    """ """
    CHANNEL_NAME = "channel_name"
    COMP = "COMP"
    Y_VALUES = "Y_VALUES"
    X_VALUES = "X_VALUES"
    IDS = "ids"
    SIGNALS = "signals"


class DefinitionConstants(object):
    """ """
    TITLE = "TITLE"
    UNIT = "UNIT"
    OBJECTS = "OBJECTS"
    DATA_VIS = "DATA VISUALIZATION"
    RISK_FUNCTION = "RISK FUNCTION"
    CRITERIA = "CRITERIA"
    OFFSET = "OFFSET"


class TestConstants:
    """ """
    ELOUT = "_element"
    DATA_VIS = "_data_vis"
    INJURY_CRIT = "_injury_crit"
    DEFORC = "_discrete"
    NODOUT = "_node"
    OBJECTS = "_objects"
    CONTACT = "_contact"
    RISK_FUN = "_riskfunction"
    SBTOUT = "_seatbelt"
    SECTION = "_section"
    TITLE = "_title"
    UNITS = "_units"


class ObjectConstantsForData:
    """ """
    ELEMENT = "ELEMENT"
    AIRBAG = "AIRBAG"
    AIRBAG_CPM = "AIRBAG_CPM"
    ELEMENTOBJECT = "OBJECT"
    CROSS_SECTION = "CROSS_SECTION"
    DISCRETE = "DISCRETE"
    NODE = "NODE"
    JOINT = "JOINT"
    JOINT_TYPE = "JOINT_TYPE"
    SEAT_BELT = "SEAT_BELT"
    SLIP_RING = "SLIP_RING"
    CONTACT = "CONTACT"
    ENERGY_PART = "ENERGY_PART"
    ENERGY_GLOBAL = "ENERGY_GLOBAL"
    DISBOUT = "DISBOUT"
    DISBOUT_PART = "DISBOUT_PART"
    SLEOUT = "SLEOUT"
    RIGID_BODY = "RIGID_BODY"
    BOUNDARY_CONDITION = "BOUNDARY_CONDITION"


class JointTypeMapping:
    mapping = [('alpha_moment_stiffness', 'phi_moment_stiffnes'),
               ('d(gamma)_dt', 'd_theta_d_t'),
               ('joint_extra2', 'joint_energy'),
               ('alpha_degrees', 'phi_degrees'),
               ('alpha_moment_total', 'phi_moment_total'),
               ('gamma_degrees', 'theta_degrees'),
               ('d(alpha)_dt', 'phi_dt'),
               ('beta_degrees', 'psi_degrees'),
               ('alpha_moment_damping', 'phi_moment_damping'),
               ('beta_moment_total', 'psi_moment_total'),
               ('gamma_scale_factor', 'theta_scale_factor'),
               ('beta_moment_damping', 'psi_moment_damping'),
               ('d(beta)_dt', 'd_psi_d_t'),
               ('beta_moment_stiffness', 'psi_moment_stiffness')]

    @staticmethod
    def lspp_to_dynasaur_mapping(channel_type):
        """
        Searches for the identifier in JointTypeMapping.
        If channel_type is missing in the list, the original value is returned (i.e. time)

        Args:
          binary_data_type: return:

        Returns:

        """

        for tpl in JointTypeMapping.mapping:
            if tpl[1] == channel_type:
                return tpl[0]

        return channel_type


class DataTypeMapping:
    """ """
    mapping = [(ObjectConstantsForData.ELEMENT, "elout"),
               (ObjectConstantsForData.AIRBAG, "abstat"),
               (ObjectConstantsForData.AIRBAG_CPM, "abstat_cpm"),
               (ObjectConstantsForData.CROSS_SECTION, "secforc"),
               (ObjectConstantsForData.NODE, "nodout"),
               (ObjectConstantsForData.JOINT, "joints"),
               (ObjectConstantsForData.JOINT_TYPE, "type1"),
               (ObjectConstantsForData.SEAT_BELT, "sbtout"),
               (ObjectConstantsForData.SLIP_RING, "sbtout"),
               (ObjectConstantsForData.CONTACT, "rcforc"),
               (ObjectConstantsForData.DISCRETE, "deforc"),
               (ObjectConstantsForData.ENERGY_PART, "matsum"),
               (ObjectConstantsForData.ENERGY_GLOBAL, "glstat"),
               (ObjectConstantsForData.DISBOUT, "disbout"),
               (ObjectConstantsForData.DISBOUT_PART, "disbout_part"),
               (ObjectConstantsForData.SLEOUT, "sleout"),
               (ObjectConstantsForData.RIGID_BODY, "rbdout"),
               (ObjectConstantsForData.BOUNDARY_CONDITION, "bndout")]

    @staticmethod
    def binary_identifier_2_dynasaur_identifier(binary_data_type):
        """

        Args:
          binary_data_type: return:

        Returns:

        """

        possible_container = []
        for tpl in DataTypeMapping.mapping:
            if tpl[1] == binary_data_type:
                possible_container.append(tpl[0])

        return None if len(possible_container) == 0 else possible_container

    @staticmethod
    def dynasaur_identifier_2_binary_identifier(dynasaur_data_type):
        """

        Args:
          dynasaur_data_type: return:

        Returns:

        """
        for tpl in DataTypeMapping.mapping:
            if tpl[0] == dynasaur_data_type:
                return tpl[1]

        return None


class JsonConstants:
    """ """
    TYPE = "type"
    ID = "id"
    ID_UPPER_CASE = "ID"
    ID_RANGE = "id_range"
    PART_ID = "part_id"
    NAME = "name"
    VALUE = "value"
    FUNCTION = "function"
    PLUGIN = "plugin"
    DEFINITIONS = "definitions"
    DEFINITION = "definition"
    TYPE_OF_CRTITERIA = "type_of_criteria"
    PART_OF = "part_of"
    INFO = "info"
    CRITERIA_KINEMATIC = "kinematic"
    CRITERIA_LOAD = "load"
    CRITERIA_INJURY = "injury"
    CRITERIA_ENERGY = "energy"
    CRITERIA_METADATA = "metadata"
    CRITERIA_TIME = "time"
    CRITERIA_RISK = "risk"    
    PARAM = "param"
    ARRAY = "array"
    LIMITS = "limits"
    UNIT = "unit"


class PluginsParamDictDef:
    """ """
    DYNASAUR_JSON = "dynasaur_json"
    START_TIME = "t_start"
    END_TIME = "t_end"
    LIMIT = 'limit'
    NR_LARGESR_EL = 'nr_largest_elements'
    AGE = 'age'
    X_LABEL = "x_label"
    Y_LABEL = "y_label"
    X_UNIT = "x_unit"
    Y_UNIT = "y_unit"
    SELECTION_TENSION_COMPRESSION = "selection_tension_compression"
    INTEGRATION_POINT = "integration_point"
    PERCENTILE = "percentile"


class OutputStringForPlugins:
    """ """
    VALUE = 'Value'
    LIMITS = "Limits"
    UNIT = "unit"


class DataPluginConstants:
    """ """
    TIME = 'time'
    VISUALIZATION = "visualization"
    X = "x"
    Y = "y"


class StandardFunctionsDefinition:
    """ """
    HIC15 = "HIC_15"
    HIC36 = "HIC_36"
    ERROR_NOT_STANDARD_FUNCTION = " is not a standard or user function"
    FUNCTION_NAME = "function_name"


class LOGConstants(object):
    """ """
    ERROR = ("[ERROR]", "red")
    WARNING = ("[WARNING]", "magenta")
    READ_BINOUT = ("[READ BINOUT]", "blue")
    READ_MADYMO = ("[READ MADYMO]", "yellow")
    READ_VOLUME = ("[READ VOLUME]", "grey")
    READ_DYNASAUR_DEF = ("[READ DYNASAUR DEF]", "green")
    DATA_PLUGIN = ("[DATA]", "white")
    SCRIPT = ("[CALCULATION]", "cyan")
    INPUT = ("[USER INPUT]", "blue")


class LoggerDefinitionFileValidator:
    """ """
    ID_MUST_BE_DEFINITED = "ID has to be defied!"
    ID_IS_INTEGER_LIST = "ID has to be a list of integers!"
    DEFINITION_MISSING = "Definition is missing!"
    TITLE_MISSING = "Title value is missing!"
    STRING_TYPE = "Value type has to be a string!"
    TIME_MISSING = "Time has to be defined!"
    LENGTH_MISSING = "Length has to be defined!"
    WEIGHT_MISSING = "Weight has to be defined!"
    RISK_FUN_DEF = "Risk function has to be defined!"
    LIST_TYPE = "Value has to be defined as list!"
    PLUGIN_MISSING = "Plugin has to be defined!"
    LOWER_CASE = "Definition has to be be lowercase!"
    NAME_MISSING = "Name has to be defined!"
    OBJECT_MISSING = "Objects have to be defined in object!"
    TYPE_MISSING = "object type is missing!"
    PART_OF_MISSING = "\"part_of\" is missing! Definition name: "
    CRITERIA_MISSING = "Criteria has to be defined!"
    CRITERIA_DEFINITION_MISSING = "Criteria has to be a definitions{}"
    CRITERIA_TYPE_OF_MISSING = "Type of criteria has to be defined! Definition name: "
    CRITERIA_FUNCTION_MISSING = "function has to be defined! Definition name: "
    CRITERIA_TYPE_INCORRECT = "Type of criteria can be: load, kinematic or injury. Incorrect:"
    NOT_VALID_DEFINITION = "Invalid DEFINITION: "
    GITLAB_REFERENCE = " check out : https://gitlab.com/VSI-TUGraz/Dynasaur/wikis/definition-file"


class LoggerERROR:
    """ """
    print_statements = {
        1: " is not supported as data type. Use ",
        3: " No file to select",
        4: " JSON object issue: %s",
        5: " Definition does not contain key ",
        6: " In CRITERIA plugin: Definition does not contain key ",
        7: " In DATA VISUALIZATION plugin: Definition does not contain key ",
        8: " Double define of "
    }


class LoggerWARNING:
    """ """
    print_statements = {
        1: " is not a valid DYNASAUR type! Available types are: ",
        2: " DATA VISUALIZATION plugin: Definition does not contain header information for the generating ISO-MME files."
           " The information is preset to [" + "NOVALUE , " + datetime.date.today().strftime("%d/%m/%Y") + ", 1, 6yo]",
        3: " used in your calculation procedure file, but not available in your binout"

    }


class LoggerSCRIPT:
    """ """
    print_statements = {
        1: " writing csv to ",
        2: " writing pdf to ",
        3: " writing channel files to ",
        4: " writing channel summary to ",
        5: " writing isomme to ",
        6: " done writing csv to "
    }


class LoggerReadDynasaurDefinitionFile:
    """ """
    READ = "read %s"
    DONE = "done"


class VPSDataConstant:
    """ """
    NODOUT = "nodout"
    NODE = "NODE"
    SECFORC = "secforc"
    SECTION = "SECTION"
    JOINT = "JOINT"
    RIGID_BODY = "rbdout"

    RCFORC = "rcforc"
    CONTACT = "CONTACT"
    GLSTAT = "glstat"
    ENERGY_GLOBAL = "MODEL"
    MATSUM = "matsum"
    ENERGY_PART = "PART"

    SBTOUT = "sbtout"
    SLIPRING = "SLIPRING" #"BAR"


    #nodout
    COORDINATE = "COORDINATE"
    TRANSLATION_DISPLACEMENT = "Translational_Displacement"
    VELOCITY = "Velocity"
    ACCELERATION = "Acceleration"
    ROTATION_ANGLE = "Rotational_Angle"
    ROTATION_VELOCITY = "Rotational_Velocity"
    ROTATION_ACCELERATION = "Rotational_Acceleration"

    #secforc
    SECTION_CENTRE_POSITION = "Section_Centre_Position"
    SECTION_FORCE = "Section_Force"
    SECTION_MOMENT = "Section_Moment"

    #rcforc
    CONTACT_FORCE = "Contact_Force"

    #joint
    JOINT_FORCE = "Force"
    JOINT_MOMENT_R = "Moment_R"
    JOINT_MOMENT_S_I = "Moment_S_i"
    JOINT_MOMENT_T_II = "Moment_T_ii"
    JOINT_RELATIVE_DISPLACEMENT = "Relative_Displacement"
    JOINT_RELATIVE_ROTATION_R = "Relative_Rotation_R"
    JOINT_RELATIVE_ROTATION_S_I = "Relative_Rotation_S_i"
    JOINT_RELATIVE_ROTATION_T_II = "Relative_Rotation_T_ii"

    #sbtout
    SLIPRING_VARIABLES = "Slipring_Variables" # "Axial_Elongation"

    #glstat
    ENERGY_GLOBAL_EXTERNAL = "TEXT"
    ENERGY_GLOBAL_ENKIT = "ENKIT"

class DataChannelTypesNodout:
    """ """
    X_COORDINATE = "x_coordinate"
    Y_COORDINATE = "y_coordinate"
    Z_COORDINATE = "z_coordinate"

    X_DISPLACEMENT = "x_displacement"
    Y_DISPLACEMENT = "y_displacement"
    Z_DISPLACEMENT = "z_displacement"

    X_VELOCITY = "x_velocity"
    Y_VELOCITY = "y_velocity"
    Z_VELOCITY = "z_velocity"

    X_ACCELERATION = "x_acceleration"
    Y_ACCELERATION = "y_acceleration"
    Z_ACCELERATION = "z_acceleration"

    RX_DISPLACEMENT = "rx_displacement"
    RY_DISPLACEMENT = "ry_displacement"
    RZ_DISPLACEMENT = "rz_displacement"

    RX_VELOCITY = "rx_velocity"
    RY_VELOCITY = "ry_velocity"
    RZ_VELOCITY = "rz_velocity"

    RX_ACCELERATION = "rx_acceleration"
    RY_ACCELERATION = "ry_acceleration"
    RZ_ACCELERATION = "rz_acceleration"


class DataChannelTypesContact:
    """ """
    X_FORCE = "x_force"
    Y_FORCE = "y_force"
    Z_FORCE = "z_force"
    TIE_AREA = "tie_area"

class DataChannelTypesGlobalEnergy:
    """ """
    EXTERNAL_WORK = "external_work"
    INTERNAL_ENERGY = "internal_energy"
    KINETIC_ENERGY = "kinetic_energy"
    TOTAL_ENERGY = "total_energy"


class DataChannelTypesSecforc:
    """ """
    X_CENTROID = "x_centroid"
    Y_CENTROID = "y_centroid"
    Z_CENTROID = "z_centroid"

    X_FORCE = "x_force"
    Y_FORCE = "y_force"
    Z_FORCE = "z_force"
    TOTAL_FORCE = "total_force"

    X_MOMENT = "x_moment"
    Y_MOMENT = "y_moment"
    Z_MOMENT = "z_moment"
    TOTAL_MOMENT = "total_moment"


class DataChannelTypesRbdout:
    """ """
    LOCAL_RDX ='local_rdx'
    LOCAL_RDY = 'local_rdy'
    LOCAL_RDZ = 'local_rdz'

class DataChannelTypesSbtout:
    """ """
    BELT_FORCE = "belt_force"
    BELT_LENGTH = "belt_length"
    RING_SLIP = "ring_slip"
