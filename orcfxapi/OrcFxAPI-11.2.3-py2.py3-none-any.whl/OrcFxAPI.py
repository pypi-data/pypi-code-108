# Interface module for OrcFxAPI.dll, version 9.5a and later

from __future__ import division
import sys
import os.path
from datetime import datetime
import locale
try:
    from collections.abc import MutableMapping
except:
    from collections import MutableMapping
import functools
import contextlib
import ctypes
import ctypes.wintypes
import numpy
import numpy.ctypeslib
import OrcFxAPIConfig

_interfaceCapabilities = 1
_isPy3k = sys.version_info[0] >= 3
_lib = OrcFxAPIConfig.lib()

_Encoding = locale.getdefaultlocale()[1]
_char = ctypes.c_wchar
_pchar = ctypes.c_wchar_p
Handle = ctypes.c_void_p

_BeginEndDataChangeAvailable = hasattr(_lib, 'C_BeginDataChange')
_GetObjectTypeFromHandleAvailable = hasattr(_lib, 'C_GetObjectTypeFromHandle')
_ReportActionProgressAvailable = hasattr(_lib, 'C_ReportActionProgressW')
_GetFrequencyDomainProcessComponents2Available = hasattr(_lib, 'C_GetFrequencyDomainProcessComponents2')
_CalculateRratioAvailable = hasattr(_lib, 'C_CalculateRratio')


def _redirectOutputToOrcaFlex():
    class outputStream(object):

        def write(self, str):
            status = ctypes.c_int()
            str = _PrepareString(str)
            _ExternalFunctionPrint(str, status)
            _CheckStatus(status)
    sys.stderr = sys.stdout = outputStream()


def _redirectOutputToNull():
    class outputStream(object):

        def write(self, str):
            pass
    sys.stderr = sys.stdout = outputStream()


if _isPy3k:
    def _PrepareString(value):
        if value is None:
            return None
        return str(value)  # str is ASCII in Python 2, and Unicode in Python 3
else:
    def _PrepareString(value):
        if value is None:
            return None
        if isinstance(value, str):
            return unicode(value, _Encoding, 'strict')
        return unicode(value)


def _DecodeString(value):
    if _isPy3k and isinstance(value, bytes):
        return value.decode(_Encoding)  # byte data to string
    else:
        return value


class FunctionNotFound(object):

    def __init__(self, name):
        self.name = name

    def __call__(self, *args, **kwargs):
        raise MissingRequirementError(
            'Function \'' + self.name + '\' is not exported by the linked OrcFxAPI DLL'
        )


def ImportedFunctionAvailable(func):
    return not isinstance(func, FunctionNotFound)


def _bind(lib, name, restype, *argtypes):
    func = getattr(lib, name, None)
    if func is not None:
        func.restype = restype
        func.argtypes = argtypes
        return func
    else:
        return FunctionNotFound(name)


_bindToOrcFxAPI = functools.partial(_bind, _lib)

# declare functions that we import from system libraries
_DeleteObject = _bind(
    ctypes.windll.gdi32,
    'DeleteObject',
    ctypes.wintypes.BOOL,
    Handle
)

_GetModuleFileName = _bind(
    ctypes.windll.kernel32,
    'GetModuleFileNameW',
    ctypes.wintypes.DWORD,
    Handle,
    _pchar,
    ctypes.wintypes.DWORD
)

_mmioStringToFOURCCA = _bind(
    ctypes.windll.winmm,
    'mmioStringToFOURCCA',
    ctypes.c_uint32,
    ctypes.c_char_p,
    ctypes.c_uint32
)

_SysFreeString = _bind(
    ctypes.windll.OleAut32,
    'SysFreeString',
    None,
    ctypes.c_void_p
)

# declare these functions first so that they can be used by structure definitions
_GetDLLVersion = _bindToOrcFxAPI(
    'C_GetDLLVersionW',
    None,
    ctypes.POINTER(_char * 16),
    ctypes.POINTER(_char * 16),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
)

_OrcinaDefaultReal = _bindToOrcFxAPI(
    'OrcinaDefaultReal',
    ctypes.c_double
)

_OrcinaInfinity = _bindToOrcFxAPI(
    'OrcinaInfinity',
    ctypes.c_double
)

_OrcinaUndefinedReal = _bindToOrcFxAPI(
    'OrcinaUndefinedReal',
    ctypes.c_double
)

_OrcinaNullReal = _bindToOrcFxAPI(
    'OrcinaNullReal',
    ctypes.c_double
)


def _checkVersion(requiredVersion):
    s = (_char * 16)()
    s.value = _PrepareString(requiredVersion)
    OK = ctypes.c_int()
    status = ctypes.c_int()
    _GetDLLVersion(s, (_char * 16)(), OK, status)
    _CheckStatus(status)
    return OK.value == 1


def _supportsVesselDisturbance():
    return _checkVersion('9.7a')


def _supportsModeTypeClassification():
    return _checkVersion('9.7a')


def _supportsShadedFillMode():
    return _checkVersion('9.8a')


def _supportsGetModelProperty():
    return _checkVersion('10.0a')


def _supportsDrawNameLabels():
    return _checkVersion('10.2a')


def _supportsLineFeeding():
    return _checkVersion('10.2a')


def _supportsDrawOrigins():
    return _checkVersion('11.0a')


def _supportsJpegCompressionQuality():
    return _checkVersion('11.1a')


def _supportsModalMassStiffness():
    return _checkVersion('11.1a')


def _supportsTimeSeriesStatisticsRMS():
    return _checkVersion('11.2a')


# http://stackoverflow.com/questions/43867646/
class PByte(ctypes.POINTER(ctypes.c_char)):
    _type_ = ctypes.c_char

    @classmethod
    def from_param(cls, param, array_t=ctypes.c_char * 0):
        if isinstance(param, bytearray):
            param = array_t.from_buffer(param)
        return super(PByte, cls).from_param(param)


def _allocateArray(length):
    return numpy.empty(length, dtype=numpy.float64)


def prepareArray(array):
    if array is not numpy.ndarray or array.dtype != numpy.float64:
        return numpy.array(array, dtype=numpy.float64)
    else:
        return array


_prepareArray = prepareArray
del(prepareArray)


def _finaliseArray(array):
    return array


def _allocateIntArray(length):
    return numpy.empty(length, dtype=numpy.int32)


_finaliseIntArray = _finaliseArray


def _getArrayData(array):
    return array.ctypes.data_as(ctypes.POINTER(ctypes.c_double))


_array = numpy.array

# http://stackoverflow.com/q/32120178/


def wrapped_ndpointer(*args, **kwargs):
    base = numpy.ctypeslib.ndpointer(*args, **kwargs)

    def from_param(cls, obj):
        if obj is None:
            return obj
        return base.from_param(obj)
    return type(base.__name__, (base,), {'from_param': classmethod(from_param)})


ByteArrayType = wrapped_ndpointer(dtype=numpy.uint8, ndim=1, flags='C_CONTIGUOUS')
IntArrayType = wrapped_ndpointer(dtype=numpy.int32, ndim=1, flags='C_CONTIGUOUS')
DoubleArrayType = wrapped_ndpointer(dtype=numpy.float64, ndim=1, flags='C_CONTIGUOUS')
ComplexArrayType = wrapped_ndpointer(dtype=numpy.complex128, ndim=1, flags='C_CONTIGUOUS')


# Status constants returned by API functions
stOK = 0
stDLLsVersionError = 1
stCreateModelError = 2
stModelHandleError = 3
stObjectHandleError = 4
stInvalidObjectType = 5
stFileNotFound = 6
stFileReadError = 7
stTimeHistoryError = 8
stNoSuchNodeNum = 9
stInvalidPropertyNum = 10
stInvalidPeriod = 12
stInvalidVarNum = 13
stRangeGraphError = 14
stInvalidObjectExtra = 15
stNotEnoughVars = 16
stInvalidVars = 17
stUnrecognisedVarNum = 18
stInvalidHandle = 19
stUnexpectedError = 20
stInvalidIndex = 21
stNoSuchObject = 23
stNotAVariantArray = 24
stLicensingError = 25
stUnrecognisedVarName = 26
stStaticsFailed = 27
stFileWriteError = 28
stOperationCancelled = 29
stSolveEquationFailed = 30
stInvalidDataName = 31
stInvalidDataType = 32
stInvalidDataAccess = 33
stInvalidVersion = 34
stInvalidStructureSize = 35
stRequiredModulesNotEnabled = 36
stPeriodNotYetStarted = 37
stCouldNotDestroyObject = 38
stInvalidModelState = 39
stSimulationError = 40
stInvalidModule = 41
stInvalidResultType = 42
stInvalidViewParameters = 43
stCannotExtendSimulation = 44
stUnrecognisedObjectTypeName = 45
stUnknownModelState = 46
stFunctionNotAvailable = 47
stStructureSizeTooSmall = 48
stInvalidParameter = 49
stResponseGraphError = 50
stResultsNotAvailableWhenNotIncludedInStatics = 51
stInvalidFileType = 52
stBatchScriptFailed = 53
stInvalidTimeHistoryValues = 54
stResultsNotLogged = 55
stWizardFailed = 56
stDLLInitFailed = 57
stInvalidArclengthRange = 58
stValueNotAvailable = 59
stInvalidValue = 60
stModalAnalysisFailed = 61
stVesselTypeDataImportFailed = 62
stOperationNotAvailable = 63
stFatigueAnalysisFailed = 64
stExtremeStatisticsFailed = 65
stTagNotFound = 66
stInvalidFileFormat = 67
stThreadAffinityError = 68

# Object type constants
otGeneral = 1
otEnvironment = 3
otVessel = 5
otLine = 6
ot6DBuoy = 7
ot3DBuoy = 8
otWinch = 9
otLink = 10
otShape = 11
otConstraint = 12
otTurbine = 13
otDragChain = 14
otLineType = 15
otClumpType = 16
otWingType = 17
otVesselType = 18
otDragChainType = 19
otFlexJointType = 20
otStiffenerType = 21
otFlexJoint = 41
otAttachedBuoy = 43
otFrictionCoefficients = 47
otSolidFrictionCoefficients = otFrictionCoefficients  # back-compat
otRayleighDampingCoefficients = 48
otWakeModel = 49
otPyModel = 50
otLineContact = 51
otCodeChecks = 52
otShear7Data = 53
otVIVAData = 54
otSupportType = 55
otMorisonElementType = 57
otBrowserGroup = 61
otMultibodyGroup = 62

# Object type constants (variable data sources)
otDragCoefficient = 1000
otAxialStiffness = 1001
otBendingStiffness = 1002
otBendingConnectionStiffness = 1003
otWingOrientation = 1004
otKinematicViscosity = 1005
otFluidTemperature = 1006
otCurrentSpeed = 1007
otCurrentDirection = 1008
otExternalFunction = 1009
otHorizontalVariationFactor = 1010
otLoadForce = 1011
otLoadMoment = 1012
otExpansionFactor = 1013
otPayoutRate = 1014
otWinchPayoutRate = otPayoutRate  # backwards compatibility
otWinchTension = 1015
otVerticalVariationFactor = 1016
otTorsionalStiffness = 1017
otMinimumBendRadius = 1018
otLiftCoefficient = 1019
otLiftCloseToSeabed = 1020
otDragCloseToSeabed = 1021
otDragAmplificationFactor = 1022
otLineTypeDiameter = 1023
otStressStrainRelationship = 1024
otCoatingOrLining = 1025
otContentsFlowVelocity = 1026
otAddedMassRateOfChangeCloseToSurface = 1027
otAddedMassCloseToSurface = 1028
otContactStiffness = 1029
otSupportsStiffness = 1030
otConstraintTranslationalStiffness = 1031
otConstraintRotationalStiffness = 1032
otConstraintTranslationalDamping = 1033
otConstraintRotationalDamping = 1034
otAddedMassCloseToSeabed = 1035
otSeabedTangentialResistance = 1036

# Variable Data Names
vdnWingAzimuth = 'WingAzimuth'
vdnWingDeclination = 'WingDeclination'
vdnWingGamma = 'WingGamma'
vdnGlobalAppliedForceX = 'GlobalAppliedForceX'
vdnGlobalAppliedForceY = 'GlobalAppliedForceY'
vdnGlobalAppliedForceZ = 'GlobalAppliedForceZ'
vdnGlobalAppliedMomentX = 'GlobalAppliedMomentX'
vdnGlobalAppliedMomentY = 'GlobalAppliedMomentY'
vdnGlobalAppliedMomentZ = 'GlobalAppliedMomentZ'
vdnLocalAppliedForceX = 'LocalAppliedForceX'
vdnLocalAppliedForceY = 'LocalAppliedForceY'
vdnLocalAppliedForceZ = 'LocalAppliedForceZ'
vdnLocalAppliedMomentX = 'LocalAppliedMomentX'
vdnLocalAppliedMomentY = 'LocalAppliedMomentY'
vdnLocalAppliedMomentZ = 'LocalAppliedMomentZ'
vdnRefCurrentSpeed = 'RefCurrentSpeed'
vdnRefCurrentDirection = 'RefCurrentDirection'
vdnWholeSimulationTension = 'WholeSimulationTension'
vdnWholeSimulationPayoutRate = 'WholeSimulationPayoutRate'
vdnXBendStiffness = 'xBendStiffness'
vdnXBendMomentIn = 'xBendMomentIn'
vdnYBendMomentIn = 'yBendMomentIn'
vdnXBendMomentOut = 'xBendMomentOut'
vdnYBendMomentOut = 'yBendMomentOut'
vdnAxialStiffness = 'AxialStiffness'
vdnTorsionalStiffness = 'TorsionalStiffness'
vdnPayoutRate = 'PayoutRate'
vdnExternallyCalculatedPrimaryMotion = 'ExternallyCalculatedPrimaryMotion'
vdnExternallyCalculatedImposedMotion = 'ExternallyCalculatedImposedMotion'
vdnPitchController = 'PitchController'
vdnGeneratorTorqueController = 'GeneratorTorqueController'
vdnGeneratorMotionController = 'GeneratorMotionController'

# Period constants
pnBuildUp = 0
# Stage n has Period number n
pnSpecifiedPeriod = 32001
pnLatestWave = 32002
pnWholeSimulation = 32003
pnStaticState = 32004
pnInstantaneousValue = 32005

# For ObjectExtra.LinePoint
ptEndA = 0
ptEndB = 1
ptTouchdown = 2
ptNodeNum = 3
ptArcLength = 4

# For ObjectExtra.RadialPos
rpInner = 0
rpOuter = 1
rpMid = 2

# Special integer value equivalent to '~' in OrcaFlex UI
OrcinaDefaultWord = 65500

# DataType constants
dtDouble = 0
dtInteger = 1
dtString = 2
dtVariable = 3
dtIntegerIndex = 4
dtBoolean = 5

# Data action constants
daIsDefault = 0
daHasChanged = 1
daIsMarkedAsChanged = 2
daSetToDefault = 3
daSetToOriginalValue = 4
daMarkAsChanged = 5

# For EnumerateVars
rtTimeHistory = 0
rtRangeGraph = 1
rtLinkedStatistics = 2
rtFrequencyDomain = 3

# For range graph arclength range modes
armEntireRange = 0
armEntireLine = armEntireRange  # legacy name
armSpecifiedArclengths = 1
armSpecifiedSections = 2

# For move objects
sbDisplacement = 0
sbPolarDisplacement = 1
sbNewPosition = 2
sbRotation = 3

# For module disable/enabled
moduleDynamics = 0
moduleVIV = 1

# Modify model actions
modifyModelActionDeleteUnusedTypes = 0
modifyModelActionDeleteUnusedVariableDataSources = 1

# For licence reconnection
lrBegin = 0
lrContinue = 1
lrEnd = 2

# For time history summary
thstSpectralDensity = 0
thstEmpiricalDistribution = 1
thstRainflowHalfCycles = 2
thstRainflowAssociatedMean = 3

# For view parameter graphics mode
gmWireFrame = 0
gmShaded = 1

# For view parameter shaded fill mode
fmSolid = 0
fmMesh = 1

# For saving external program files
eftShear7dat = 0
eftShear7mds = 1
eftShear7out = 2
eftShear7plt = 3
eftShear7anm = 4
eftShear7dmg = 5
eftShear7fat = 6
eftShear7out1 = 7
eftShear7out2 = 8
eftShear7allOutput = 9
eftShear7str = 10
eftVIVAInput = 11
eftVIVAOutput = 12
eftVIVAModes = 13
eftShear7cat = 14
eftShear7inhyst = 15
eftShear7curv = 16
eftShear7zetahyst = 17
eftShear7sth = 18

# For saving spreadsheets
sptSummaryResults = 0
sptFullResults = 1
sptWaveSearch = 2
sptVesselDisplacementRAOs = 3
sptVesselSpectralResponse = 4
sptLineClashingReport = 5
sptDetailedProperties = 6
sptLineTypesPropertiesReport = 7
sptCodeChecksProperties = 8
sptSupportGeometryTable = 9
sptAirGapReport = 10
sptDiffractionResults = 11
sptDiffractionMeshDetails = 12
sptDiffractionWaveComponents = 13

# For view parameter file format
bffWindowsBitmap = 0
bffPNG = 1
bffGIF = 2
bffJPEG = 3
bffPDF = 4
bffRGB = 5

# For frequency domain process type
iptWave = 0
iptWind = 1
iptWaveDrift = 2

# For extreme statistics
evdRayleigh = 0
evdWeibull = 1
evdGPD = 2

exUpperTail = 0
exLowerTail = 1

# For panel mesh import
mfWamitGdf = 0
mfWamitFdf = 1
mfWamitCsf = 2
mfNemohDat = 3
mfHydrostarHst = 4
mfAqwaDat = 5
mfSesamFem = 6
mfGmshMsh = 7
mfWavefrontObj = 8

msNone = 0
msXZ = 1
msYZ = 2
msXZYZ = 3

wftEdges = 0
wftPanels = 1

# For post calculation actions
atInProcPython = 0
atCmdScript = 1

# Object extra fields, also used by user defined results
oefEnvironmentPos = 0
oefLinePoint = 1
oefRadialPos = 2
oefTheta = 3
oefWingName = 4
oefClearanceLineName = 5
oefWinchConnectionPoint = 6
oefRigidBodyPos = 7
oefExternalResultText = 8
oefDisturbanceVesselName = 9
oefSupportIndex = 10
oefSupportedLineName = 11
oefBladeIndex = 12
oefElementIndex = 13
oefSeaSurfaceScalingFactor = 14

# For user defined results, values for LineResultPoints
lrpNone = 0
lrpWholeLine = 1
lrpNodes = 2
lrpMidSegments = 3
lrpMidSegmentsAndEnds = 4
lrpEnds = 5

# For modal analysis
mtNotAvailable = -1
mtTransverse = 0
mtMostlyTransverse = 1
mtInline = 2
mtMostlyInline = 3
mtAxial = 4
mtMostlyAxial = 5
mtMixed = 6
mtRotational = 7
mtMostlyRotational = 8

# For fatigue output
fotOutputPointCount = 0
fotHomogeneousPipeOutputPointDetails = 1
fotComponentOutputPointDetails = 2
fotMooringOutputPointDetails = 3
fotShear7OutputPointDetails = 4
fotHistogramOutputPointDetails = 5
fotTheta = 6
fotDeterministicLoadCaseDamage = 7
fotSpectralLoadCaseDamage = 8
fotShear7LoadCaseDamage = 9
fotOverallDamage = 10
fotHistogramBins = 11
fotHistogramLoadCaseCycleRate = 12
fotHistogramCombinedCycleRate = 13

# For diffraction output
dotHeadings = 0
dotFrequencies = 1
dotAngularFrequencies = 2
dotPeriods = 3
dotPeriodsOrFrequencies = 4
dotHydrostaticResults = 5
dotAddedMass = 6
dotInfiniteFrequencyAddedMass = 7
dotDamping = 8
dotLoadRAOsHaskind = 9
dotLoadRAOsDiffraction = 10
dotDisplacementRAOs = 11
dotMeanDriftHeadingPairs = 12
dotQTFHeadingPairs = 13
dotQTFFrequencies = 14
dotQTFAngularFrequencies = 15
dotQTFPeriods = 16
dotQTFPeriodsOrFrequencies = 17
dotMeanDriftLoadPressureIntegration = 18
dotMeanDriftLoadControlSurface = 19
dotFieldPointPressure = 20
dotFieldPointRAO = 21
dotFieldPointVelocity = 22
dotFieldPointRAOGradient = 23
dotPanelCount = 24
dotPanelGeometry = 25
dotPanelPressure = 26
dotPanelVelocity = 27
dotQuadraticLoadFromPressureIntegration = 28
dotQuadraticLoadFromControlSurface = 29
dotDirectPotentialLoad = 30
dotIndirectPotentialLoad = 31
dotExtraRollDamping = 32
dotRollDampingPercentCritical = 33
dotPanelPressureDiffraction = 34
dotPanelPressureRadiation = 35
dotPanelVelocityDiffraction = 36
dotPanelVelocityRadiation = 37

# Model property IDs
propIsTimeDomainDynamics = 0
propIsFrequencyDomainDynamics = 1
propIsDeterministicFrequencyDomainDynamics = 2
propGeneralHandle = 3
propEnvironmentHandle = 4
propFrictionCoefficientsHandle = 5
propSolidFrictionCoefficientsHandle = propFrictionCoefficientsHandle  # back-compat
propLineContactHandle = 6
propCodeChecksHandle = 7
propShear7DataHandle = 8
propVIVADataHandle = 9
propIsPayoutRateNonZero = 10
propCanResumeSimulation = 11
propStageZeroIsBuildUp = 12

# For vessel type data import
vdtDisplacementRAOs = 0
vdtLoadRAOs = 1
vdtNewmanQTFs = 2
vdtFullQTFs = 3
vdtStiffnessAddedMassDamping = 4
vdtStructure = 5
vdtOtherDamping = 6
vdtSeaStateRAOs = 7
vdtSymmetry = 8
vdtDrawing = 9

iftGeneric = 0
iftAQWA = 1
iftWAMIT = 2
iftOrcaWave = 3

# Default autosave interval
DefaultAutoSaveIntervalMinutes = 60  # same as OrcaFlex default


def _CheckStatus(status):
    if status.value != stOK:
        raise DLLError(status.value)


class _DictLookup(object):

    def __init__(self, dict):
        for (k, v) in dict.items():
            setattr(self, k, v)

    def __repr__(self):
        result = ''
        for name, value in vars(self).items():
            result += u'{0!r}: {1!r}, '.format(name, value)
        return '<' + result[0:len(result) - 2] + '>'

    def __str__(self):
        result = ''
        for name, value in vars(self).items():
            result += u'{0!s}: {1!s}, '.format(name, value)
        return '<' + result[0:len(result) - 2] + '>'


def objectFromDict(dict):
    return _DictLookup(dict)


class DLLError(Exception):

    def __init__(self, status, errorString=None):
        if errorString is None:
            length = _GetLastErrorString(None)
            str = (_char * length)()
            _GetLastErrorString(str)
            errorString = str.value
        self.status = status
        self.errorString = errorString
        self.msg = u'\nError code: {0}\n{1}'.format(status, errorString)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.msg


class MissingRequirementError(Exception):
    pass


def Enum(*names):

    class EnumClass(object):
        __slots__ = names

        def __iter__(self):
            return iter(constants)

        def __len__(self):
            return len(constants)

        def __getitem__(self, i):
            return constants[i]

        def __repr__(self):
            return 'Enum' + str(names)

        def __str__(self):
            return 'enum ' + str(constants)

        def __contains__(self, item):
            return item in names

    enumType = EnumClass()

    class EnumValue(object):
        __slots__ = ('__value')

        def __init__(self, value):
            self.__value = value
        Value = property(
            lambda self: self.__value
        )
        EnumType = property(
            lambda self: enumType
        )

        def __hash__(self):
            return hash(self.__value)

        def __eq__(self, other):
            if not isinstance(other, EnumValue):
                return NotImplemented
            return self.__value == other.__value

        def __lt__(self, other):
            if not isinstance(other, EnumValue):
                return NotImplemented
            return self.__value < other.__value

        def __gt__(self, other):
            if not isinstance(other, EnumValue):
                return NotImplemented
            return self.__value > other.__value

        def __le__(self, other):
            if not isinstance(other, EnumValue):
                return NotImplemented
            return self.__value <= other.__value

        def __ge__(self, other):
            if not isinstance(other, EnumValue):
                return NotImplemented
            return self.__value >= other.__value

        def __repr__(self):
            return str(names[self.__value])

    maximum = len(names) - 1
    constants = [None] * len(names)
    for i, each in enumerate(names):
        val = EnumValue(i)
        setattr(EnumClass, each, val)
        constants[i] = val
    constants = tuple(constants)
    return enumType


ModelType = Enum(
    'Standard',
    'Variation',
    'Restart'
)

ModelState = Enum(
    'Reset',
    'CalculatingStatics',
    'InStaticState',
    'RunningSimulation',
    'SimulationStopped',
    'SimulationStoppedUnstable'
)

DiffractionState = Enum(
    'Reset',
    'Calculating',
    'CalculationComplete'
)

FileType = Enum(
    'DataFile',
    'StaticStateSimulationFile',
    'DynamicSimulationFile'
)

DataFileType = Enum(
    'Binary',
    'Text'
)

SpreadsheetFileType = Enum(
    'Csv',
    'Tab',
    'Xlsx'
)


class IndexedDataItem(object):

    __slots__ = 'dataName', 'obj'

    def __init__(self, dataName, obj):
        self.dataName = dataName
        self.obj = obj

    def Assign(self, value):
        with self.obj.dataChange():
            count = len(value)
            if len(self) != count:
                self.obj.SetDataRowCount(self.dataName, count)
            for i in range(count):
                self[i] = value[i]

    def wrappedIndex(self, index):
        length = len(self)
        if index < 0:
            index += length
        if index < 0 or index >= length:
            raise IndexError(index)
        return index

    def sliceCount(self, slice):
        start, stop, stride = slice.indices(len(self))
        # (a > b) - (a < b) is equivalent to cmp(a, b), see https://docs.python.org/3.0/whatsnew/3.0.html#ordering-comparisons
        return (stop - start + stride + (0 > stride) - (0 < stride)) // stride

    def sliceIndices(self, slice):
        start, stop, stride = slice.indices(len(self))
        if stride > 0:
            def moreItems(index, stop): return index < stop
        else:
            def moreItems(index, stop): return index > stop
        index = start
        while moreItems(index, stop):
            yield index
            index += stride

    def __getitem__(self, index):
        if isinstance(index, slice):
            return [self.obj.GetData(self.dataName, i) for i in self.sliceIndices(index)]
        else:
            return self.obj.GetData(self.dataName, self.wrappedIndex(index))

    def __setitem__(self, index, value):
        if isinstance(index, slice):
            if self.sliceCount(index) != len(value):
                raise ValueError(
                    'attempt to assign sequence of size {0} to slice of size {1}'.format(
                        len(value), self.sliceCount(index)))
            for i, item in zip(self.sliceIndices(index), value):
                self.obj.SetData(self.dataName, i, item)
        else:
            self.obj.SetData(self.dataName, self.wrappedIndex(index), value)

    def __len__(self):
        return self.obj.GetDataRowCount(self.dataName)

    def __repr__(self):
        return repr(tuple(self))

    def DeleteRow(self, index):
        self.obj.DeleteDataRow(self.dataName, index)

    def InsertRow(self, index):
        self.obj.InsertDataRow(self.dataName, index)

    @property
    def rowCount(self):
        return self.obj.GetDataRowCount(self.dataName)

    @rowCount.setter
    def rowCount(self, value):
        self.obj.SetDataRowCount(self.dataName, value)


class Tags(MutableMapping):

    def __init__(self, handle):
        object.__setattr__(self, '__handle__', handle)

    def __getattr__(self, name):
        result = self.get(name)
        if result is None:
            raise AttributeError(name)
        return result

    def __setattr__(self, name, value):
        self.set(name, value)

    def __delattr__(self, name):
        if not self.delete(name):
            raise AttributeError(name)

    def __getitem__(self, name):
        result = self.get(name)
        if result is None:
            raise KeyError(name)
        return result

    def __setitem__(self, name, value):
        self.set(name, value)

    def __delitem__(self, name):
        if not self.delete(name):
            raise KeyError(name)

    def __contains__(self, name):
        handle = self.__handle__
        name = _PrepareString(name)
        status = ctypes.c_int()
        length = _GetTag(handle, name, None, status)
        if status.value == stTagNotFound:
            return False
        _CheckStatus(status)
        return True

    def __len__(self):
        handle = self.__handle__
        status = ctypes.c_int()
        result = _GetTagCount(handle, status)
        _CheckStatus(status)
        return result

    def __iter__(self):
        handle = self.__handle__
        tags = ObjectTags()
        status = ctypes.c_int()
        _GetTags(handle, tags, status)
        _CheckStatus(status)
        try:
            for index in range(tags.Count):
                name = tags.Names[index]
                value = tags.Values[index]
                yield name
        finally:
            _DestroyTags(tags, status)
            _CheckStatus(status)

    def __str__(self):
        return u'tags({})'.format(str(dict(self)))

    def get(self, name, default=None):
        handle = self.__handle__
        name = _PrepareString(name)
        status = ctypes.c_int()
        length = _GetTag(handle, name, None, status)
        if status.value == stTagNotFound:
            return default
        _CheckStatus(status)
        result = (_char * length)()
        _GetTag(handle, name, result, status)
        _CheckStatus(status)
        return _DecodeString(result.value)

    def set(self, name, value):
        handle = self.__handle__
        name = _PrepareString(name)
        value = _PrepareString(value)
        status = ctypes.c_int()
        _SetTag(handle, name, value, status)
        _CheckStatus(status)

    def delete(self, name):
        handle = self.__handle__
        name = _PrepareString(name)
        status = ctypes.c_int()
        _DeleteTag(handle, name, status)
        if status.value == stTagNotFound:
            return False
        _CheckStatus(status)
        return True

    def clear(self):
        handle = self.__handle__
        status = ctypes.c_int()
        _ClearTags(handle, status)
        _CheckStatus(status)


class PackedStructure(ctypes.Structure):

    _pack_ = 1

    def __init__(self, **kwargs):
        ctypes.Structure.__init__(self, **kwargs)
        if hasattr(self, 'Size'):
            self.Size = ctypes.sizeof(self)

    def asObject(self):
        dict = {}
        for field, _type in self._fields_:  # _type to avoid name clash with type function
            if field != 'Size':
                dict[field] = getattr(self, field)
        return objectFromDict(dict)

    # __eq__ for the benefit of internal unit testing
    def __eq__(self, other):
        if not isinstance(other, PackedStructure):
            return NotImplemented
        for field, _type in self._fields_:  # _type to avoid name clash with type function
            value1 = getattr(self, field)
            value2 = getattr(other, field)
            if isinstance(value1, ctypes.Array):
                if value1[:] != value2[:]:
                    return False
            elif value1 != value2:
                return False
        return True


class PackedStructureWithObjectHandles(PackedStructure):

    @staticmethod
    def _objectFromHandle(handle):
        if not handle:
            return None
        modelHandle = HelperMethods.GetModelHandle(handle)
        return HelperMethods.CreateOrcaFlexObject(modelHandle, handle)

    @staticmethod
    def _handleFromObject(value):
        if value is None:
            return None
        else:
            return value.handle


class CreateModelParams(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('ThreadCount', ctypes.c_int)
    ]


class NewModelParams(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('ModelType', ctypes.c_int),
        ('ParentFileName', _pchar)
    ]

    def __init__(self, modelType, parentFileName):
        PackedStructure.__init__(self)
        self.ModelType = modelType.Value
        self.ParentFileName = _PrepareString(parentFileName)


class ObjectInfo(PackedStructure):

    _fields_ = [
        ('ObjectHandle', Handle),
        ('ObjectType', ctypes.c_int),
        ('ObjectName', _char * 50)
    ]


class Period(PackedStructure):

    _fields_ = [
        ('PeriodNum', ctypes.c_int),
        ('Unused', ctypes.c_int),
        ('FromTime', ctypes.c_double),
        ('ToTime', ctypes.c_double)
    ]

    def __init__(self, PeriodNum, FromTime=0.0, ToTime=0.0):
        PackedStructure.__init__(self)
        self.PeriodNum = PeriodNum
        self.FromTime = FromTime
        self.ToTime = ToTime


def SpecifiedPeriod(FromTime=0.0, ToTime=0.0):
    return Period(pnSpecifiedPeriod, FromTime, ToTime)


class ObjectExtra(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('EnvironmentPos', ctypes.c_double * 3),
        ('LinePoint', ctypes.c_int),
        ('NodeNum', ctypes.c_int),
        ('ArcLength', ctypes.c_double),
        ('RadialPos', ctypes.c_int),
        ('Theta', ctypes.c_double),
        ('WingName', _pchar),
        ('ClearanceLineName', _pchar),
        ('WinchConnectionPoint', ctypes.c_int),
        ('RigidBodyPos', ctypes.c_double * 3),
        ('ExternalResultText', _pchar),
        ('DisturbanceVesselName', _pchar),
        ('SupportIndex', ctypes.c_int),
        ('SupportedLineName', _pchar),
        ('BladeIndex', ctypes.c_int),
        ('ElementIndex', ctypes.c_int),
        ('SeaSurfaceScalingFactor', ctypes.c_double)
    ]


def OrcinaDefaultReal():
    return _OrcinaDefaultReal()


def OrcinaInfinity():
    return _OrcinaInfinity()


def OrcinaUndefinedReal():
    return _OrcinaUndefinedReal()


def OrcinaNullReal():
    return _OrcinaNullReal()


def Vector(*args):
    if len(args) == 1:
        args = args[0]  # assume parameter is iterable
    if len(args) != 3:
        raise TypeError('Vector must have length of 3')
    return list(args)


def Vector2(*args):
    if len(args) == 1:
        args = args[0]  # assume parameter is iterable
    if len(args) != 2:
        raise TypeError('Vector2 must have length of 2')
    return list(args)


def oeEnvironment(*args):
    result = ObjectExtra()
    result.EnvironmentPos[:] = Vector(*args)
    return result


def oeRigidBody(*args):
    result = ObjectExtra()
    result.RigidBodyPos[:] = Vector(*args)
    return result


oeVessel = oeRigidBody


def oeAirGap(RigidBodyPos, SeaSurfaceScalingFactor):
    result = ObjectExtra()
    if len(RigidBodyPos) != 3:
        raise TypeError('RigidBodyPos must have length of 3')
    result.RigidBodyPos[:] = RigidBodyPos
    result.SeaSurfaceScalingFactor = SeaSurfaceScalingFactor
    return result


oeBuoy = oeRigidBody

oeConstraint = oeRigidBody


def oeWing(WingName):
    result = ObjectExtra()
    result.WingName = WingName
    return result


def oeSupport(SupportIndex, SupportedLineName=None):
    result = ObjectExtra()
    result.SupportIndex = SupportIndex
    result.SupportedLineName = SupportedLineName
    return result


def oeWinch(WinchConnectionPoint):
    result = ObjectExtra()
    result.WinchConnectionPoint = WinchConnectionPoint
    return result


def oeLine(
        LinePoint=ptArcLength,
        NodeNum=0,
        ArcLength=0.0,
        RadialPos=rpInner,
        Theta=0.0,
        ClearanceLineName=None,
        ExternalResultText=None):
    result = ObjectExtra()
    result.LinePoint = LinePoint
    result.NodeNum = NodeNum
    result.ArcLength = ArcLength
    result.RadialPos = RadialPos
    result.Theta = Theta
    result.ClearanceLineName = ClearanceLineName
    result.ExternalResultText = ExternalResultText
    return result


def oeNodeNum(NodeNum):
    return oeLine(LinePoint=ptNodeNum, NodeNum=NodeNum)


def oeArcLength(ArcLength):
    return oeLine(LinePoint=ptArcLength, ArcLength=ArcLength)


oeEndA = oeLine(LinePoint=ptEndA)
oeEndB = oeLine(LinePoint=ptEndB)
oeTouchdown = oeLine(LinePoint=ptTouchdown)


def oeTurbine(BladeIndex, ArcLength=0.0, ClearanceLineName=None):
    result = oeLine(LinePoint=ptArcLength, ArcLength=ArcLength, ClearanceLineName=ClearanceLineName)
    result.BladeIndex = BladeIndex
    return result


def oeTurbineEndA(BladeIndex, ClearanceLineName=None):
    result = oeLine(LinePoint=ptEndA, ClearanceLineName=ClearanceLineName)
    result.BladeIndex = BladeIndex
    return result


def oeTurbineEndB(BladeIndex, ClearanceLineName=None):
    result = oeLine(LinePoint=ptEndB, ClearanceLineName=ClearanceLineName)
    result.BladeIndex = BladeIndex
    return result


def oeMorisonElement(ElementIndex, ArcLength=0.0):
    result = oeLine(LinePoint=ptArcLength, ArcLength=ArcLength)
    result.ElementIndex = ElementIndex
    return result


class RangeGraphCurveNames(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('Min', _char * 30),
        ('Max', _char * 30),
        ('Mean', _char * 30),
        ('StdDev', _char * 30),
        ('Upper', _char * 30),
        ('Lower', _char * 30)
    ]


class ArclengthRange(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('Mode', ctypes.c_int),
        ('FromArclength', ctypes.c_double),
        ('ToArclength', ctypes.c_double),
        ('FromSection', ctypes.c_int),
        ('ToSection', ctypes.c_int)
    ]


def arEntireRange():
    result = ArclengthRange()
    result.Mode = armEntireRange
    return result


arEntireLine = arEntireRange


def arSpecifiedArclengths(FromArclength, ToArclength):
    result = ArclengthRange()
    result.Mode = armSpecifiedArclengths
    result.FromArclength = FromArclength
    result.ToArclength = ToArclength
    return result


def arSpecifiedSections(FromSection, ToSection):
    result = ArclengthRange()
    result.Mode = armSpecifiedSections
    result.FromSection = FromSection
    result.ToSection = ToSection
    return result


class MoveObjectPoint(PackedStructureWithObjectHandles):

    _fields_ = [
        ('ObjectHandle', Handle),
        ('PointIndex', ctypes.c_int)
    ]

    def __init__(self, object, pointIndex):
        PackedStructureWithObjectHandles.__init__(self)
        self.ObjectHandle = object.handle
        self.PointIndex = pointIndex

    @property
    def Object(self):
        return self._objectFromHandle(self.ObjectHandle)

    @Object.setter
    def Object(self, value):
        self.ObjectHandle = self._handleFromObject(value)


class MoveObjectSpecification(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('MoveSpecifiedBy', ctypes.c_int),
        ('Displacement', ctypes.c_double * 3),
        ('PolarDisplacementDirection', ctypes.c_double),
        ('PolarDisplacementDistance', ctypes.c_double),
        ('NewPositionReferencePoint', MoveObjectPoint),
        ('NewPosition', ctypes.c_double * 3),
        ('RotationAngle', ctypes.c_double),
        ('RotationCentre', ctypes.c_double * 2)
    ]


class _TimeHistorySpecification(PackedStructure):

    _fields_ = [
        ('ObjectHandle', Handle),
        ('ObjectExtra', ctypes.POINTER(ObjectExtra)),
        ('VarID', ctypes.c_int)
    ]


class _CompoundProperties(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('Mass', ctypes.c_double),
        ('CentreOfMass', ctypes.c_double * 3),
        ('MassMomentOfInertia', ctypes.c_double * 9),
        ('Volume', ctypes.c_double),
        ('CentreOfVolume', ctypes.c_double * 3)
    ]


class ModesFilesParameters(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('FirstMode', ctypes.c_int),
        ('LastMode', ctypes.c_int),
        ('IncludeCoupledObjects', ctypes.wintypes.BOOL)
    ]

    def __init__(self, firstMode=-1, lastMode=-1, includeCoupledObjects=False):
        PackedStructure.__init__(self)
        self.FirstMode = firstMode
        self.LastMode = lastMode
        self.IncludeCoupledObjects = includeCoupledObjects


Shear7MdsFileParameters = ModesFilesParameters
VIVAModesFilesParameters = ModesFilesParameters


class TimeSeriesStats(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('Mean', ctypes.c_double),
        ('StdDev', ctypes.c_double),
        ('m0', ctypes.c_double),
        ('m2', ctypes.c_double),
        ('m4', ctypes.c_double),
        ('Tz', ctypes.c_double),
        ('Tc', ctypes.c_double),
        ('Bandwidth', ctypes.c_double)
    ]
    if _supportsTimeSeriesStatisticsRMS():
        _fields_.extend([
            ('RMS', ctypes.c_double)
        ])


class FrequencyDomainResults(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('StaticValue', ctypes.c_double),
        ('StdDev', ctypes.c_double),
        ('Amplitude', ctypes.c_double),
        ('PhaseLag', ctypes.c_double),
        ('m0', ctypes.c_double),
        ('m1', ctypes.c_double),
        ('m2', ctypes.c_double),
        ('m3', ctypes.c_double),
        ('m4', ctypes.c_double),
        ('Tz', ctypes.c_double),
        ('Tc', ctypes.c_double),
        ('Bandwidth', ctypes.c_double)
    ]


class UseCalculatedPositionsForStaticsParameters(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('SetLinesToUserSpecifiedStartingShape', ctypes.wintypes.BOOL)
    ]


class ViewParameters(PackedStructureWithObjectHandles):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('ViewSize', ctypes.c_double),
        ('ViewAzimuth', ctypes.c_double),
        ('ViewElevation', ctypes.c_double),
        ('ViewCentre', ctypes.c_double * 3),
        ('Height', ctypes.c_int),
        ('Width', ctypes.c_int),
        ('BackgroundColour', ctypes.c_int),
        ('DrawViewAxes', ctypes.wintypes.BOOL),
        ('DrawScaleBar', ctypes.wintypes.BOOL),
        ('DrawGlobalAxes', ctypes.wintypes.BOOL),
        ('DrawEnvironmentAxes', ctypes.wintypes.BOOL),
        ('DrawLocalAxes', ctypes.wintypes.BOOL),
        ('DrawOutOfBalanceForces', ctypes.wintypes.BOOL),
        ('DrawNodeAxes', ctypes.wintypes.BOOL),
        ('GraphicsMode', ctypes.c_int),
        ('FileFormat', ctypes.c_int),
        ('ViewGamma', ctypes.c_double),
        ('RelativeToObjectHandle', Handle)
    ]
    if _supportsVesselDisturbance():
        _fields_.extend([
            ('DisturbanceVesselHandle', Handle),
            ('DisturbancePosition', ctypes.c_double * 2)
        ])
    if _supportsShadedFillMode():
        _fields_.extend([
            ('ShadedFillMode', ctypes.c_int)
        ])
    if _supportsDrawNameLabels():
        _fields_.extend([
            ('DrawNameLabels', ctypes.wintypes.BOOL),
            ('DrawConnections', ctypes.wintypes.BOOL),
            ('LabelScale', ctypes.c_int)
        ])
    if _supportsDrawOrigins():
        _fields_.extend([
            ('DrawOrigins', ctypes.wintypes.BOOL)
        ])
    if _supportsJpegCompressionQuality():
        _fields_.extend([
            ('MonochromeOutput', ctypes.wintypes.BOOL),
            ('AddDetailsToOutput', ctypes.wintypes.BOOL),
            ('JpegCompressionQuality', ctypes.c_int)
        ])

    @property
    def RelativeToObject(self):
        return self._objectFromHandle(self.RelativeToObjectHandle)

    @RelativeToObject.setter
    def RelativeToObject(self, value):
        self.RelativeToObjectHandle = self._handleFromObject(value)

    @property
    def DisturbanceVessel(self):
        return self._objectFromHandle(self.DisturbanceVesselHandle)

    @DisturbanceVessel.setter
    def DisturbanceVessel(self, value):
        self.DisturbanceVesselHandle = self._handleFromObject(value)


class AVIFileParameters(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('Codec', ctypes.c_uint32),
        ('Interval', ctypes.c_double)
    ]

    def __init__(self, codec, interval):
        PackedStructure.__init__(self)
        self.Codec = _mmioStringToFOURCCA(
            str(codec).encode(_Encoding),
            0x0010  # MMIO_TOUPPER = 0x0010
        )
        self.Interval = float(interval)


class VarInfo(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('VarID', ctypes.c_int),
        ('VarName', _pchar),
        ('VarUnits', _pchar),
        ('FullName', _pchar),
        ('ObjectHandle', Handle)
    ]


class SimulationTimeStatus(PackedStructure):

    _fields_ = [
        ('StartTime', ctypes.c_double),
        ('StopTime', ctypes.c_double),
        ('CurrentTime', ctypes.c_double)
    ]


class TimeSteps(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('InnerTimeStep', ctypes.c_double),
        ('OuterTimeStep', ctypes.c_double)
    ]


class TimeHistorySummarySpecification(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('SpectralDensityFundamentalFrequency', ctypes.c_double)
    ]


class ObjectTags(PackedStructure):

    _fields_ = [
        ('Count', ctypes.c_int),
        ('Names', ctypes.POINTER(_pchar)),
        ('Values', ctypes.POINTER(_pchar))
    ]


class RunSimulationParameters(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('EnableAutoSave', ctypes.wintypes.BOOL),
        ('AutoSaveIntervalMinutes', ctypes.c_int),
        ('AutoSaveFileName', _pchar)
    ]

    def __init__(self, enableAutoSave, autoSaveIntervalMinutes, autoSaveFileName):
        PackedStructure.__init__(self)
        self.EnableAutoSave = enableAutoSave
        self.AutoSaveIntervalMinutes = autoSaveIntervalMinutes
        self.AutoSaveFileName = _PrepareString(autoSaveFileName)


class StatisticsQuery(PackedStructure):

    _fields_ = [
        ('StdDev', ctypes.c_double),
        ('Mean', ctypes.c_double),
        ('TimeOfMax', ctypes.c_double),
        ('ValueAtMax', ctypes.c_double),
        ('LinkedValueAtMax', ctypes.c_double),
        ('TimeOfMin', ctypes.c_double),
        ('ValueAtMin', ctypes.c_double),
        ('LinkedValueAtMin', ctypes.c_double)
    ]


class WaveComponent(PackedStructure):

    _fields_ = [
        ('WaveTrainIndex', ctypes.c_int),
        ('Frequency', ctypes.c_double),
        ('FrequencyLowerBound', ctypes.c_double),
        ('FrequencyUpperBound', ctypes.c_double),
        ('Amplitude', ctypes.c_double),
        ('PhaseLagWrtWaveTrainTime', ctypes.c_double),
        ('PhaseLagWrtSimulationTime', ctypes.c_double),
        ('WaveNumber', ctypes.c_double),
        ('Direction', ctypes.c_double)
    ]


class DiffractionWaveComponent(PackedStructure):

    _fields_ = [
        ('Frequency', ctypes.c_double),
        ('FrequencyLowerBound', ctypes.c_double),
        ('FrequencyUpperBound', ctypes.c_double),
        ('Amplitude', ctypes.c_double),
        ('WaveNumber', ctypes.c_double),
        ('Direction', ctypes.c_double)
    ]


class WindComponent(PackedStructure):

    _fields_ = [
        ('Frequency', ctypes.c_double),
        ('FrequencyLowerBound', ctypes.c_double),
        ('FrequencyUpperBound', ctypes.c_double),
        ('Amplitude', ctypes.c_double),
        ('PhaseLagWrtWindTime', ctypes.c_double),
        ('PhaseLagWrtSimulationTime', ctypes.c_double)
    ]


class FrequencyDomainProcessComponent(PackedStructure):

    _fields_ = [
        ('ProcessType', ctypes.c_int),
        ('ProcessIndex', ctypes.c_int),
        ('Frequency', ctypes.c_double),
        ('FrequencyLowerBound', ctypes.c_double),
        ('FrequencyUpperBound', ctypes.c_double)
    ]
    if _GetFrequencyDomainProcessComponents2Available:
        _fields_.extend([
            ('PhaseLagWrtSimulationTime', ctypes.c_double)
        ])


class _GraphCurve(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('_X', ctypes.POINTER(ctypes.c_double)),
        ('_Y', ctypes.POINTER(ctypes.c_double))
    ]

    def __init__(self, count):
        PackedStructure.__init__(self)
        self.X = _allocateArray(count)
        self.Y = _allocateArray(count)
        self._X = _getArrayData(self.X)
        self._Y = _getArrayData(self.Y)

    @property
    def data(self):
        return _finaliseArray(self.X), _finaliseArray(self.Y)


class PanelMeshImportOptions(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('Format', ctypes.c_int),
        ('Scale', ctypes.c_double),
        ('BodyNumber', ctypes.c_int),
        ('ImportDryPanels', ctypes.wintypes.BOOL)
    ]

    def __init__(self, format, scale, bodyNumber, importDryPanels):
        PackedStructure.__init__(self)
        self.Format = format
        self.Scale = scale
        self.BodyNumber = bodyNumber
        self.ImportDryPanels = importDryPanels


class LineClashingReportParameters(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('Period', Period)
    ]


class AirGapReportParameters(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('Period', Period)
    ]


class VesselTypeDataImportSpecification(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('ImportFileType', ctypes.c_int),
        ('BodyCount', ctypes.c_int),
        ('MultibodyGroupName', _pchar),
        ('ImportDisplacementRAOs', ctypes.wintypes.BOOL),
        ('ImportLoadRAOs', ctypes.wintypes.BOOL),
        ('ImportNewmanQTFs', ctypes.wintypes.BOOL),
        ('ImportFullQTFs', ctypes.wintypes.BOOL),
        ('ImportStiffnessAddedMassDamping', ctypes.wintypes.BOOL),
        ('ImportStructure', ctypes.wintypes.BOOL),
        ('ImportSeaStateRAOs', ctypes.wintypes.BOOL),
        ('ImportOtherDamping', ctypes.wintypes.BOOL),
        ('ImportSymmetry', ctypes.wintypes.BOOL),
        ('ImportDrawing', ctypes.wintypes.BOOL),
        ('LoadRAOMethod', ctypes.c_int),
        ('DiagonalQTFMethod', ctypes.c_int),
        ('FullQTFMethod', ctypes.c_int),
        ('ClearExistingData', ctypes.wintypes.BOOL)
    ]

    def __init__(self, fileType, bodyCount, multibodyGroup, requestedData, calculationMethods, clearExistingData):

        loadRAOMethods = Enum(
            'lmDefault',
            'lmHaskind',
            'lmDiffraction'
        )
        diagonalQTFMethods = Enum(
            'qmDefault',
            'qmPressureIntegration',
            'qmControlSurface',
            'qmMomentumConservation'
        )
        fullQTFMethods = Enum(
            'fmDefault',
            'fmDirect',
            'fmIndirect'
        )

        PackedStructure.__init__(self)
        self.ImportFileType = fileType
        self.BodyCount = bodyCount
        self.MultibodyGroupName = multibodyGroup
        self.ImportDisplacementRAOs = vdtDisplacementRAOs in requestedData
        self.ImportLoadRAOs = vdtLoadRAOs in requestedData
        self.ImportNewmanQTFs = vdtNewmanQTFs in requestedData
        self.ImportFullQTFs = vdtFullQTFs in requestedData
        self.ImportStiffnessAddedMassDamping = vdtStiffnessAddedMassDamping in requestedData
        self.ImportStructure = vdtStructure in requestedData
        self.ImportSeaStateRAOs = vdtSeaStateRAOs in requestedData
        self.ImportOtherDamping = vdtOtherDamping in requestedData
        self.ImportSymmetry = vdtSymmetry in requestedData
        self.ImportDrawing = vdtDrawing in requestedData
        self.LoadRAOMethod = loadRAOMethods.lmDefault.Value
        self.DiagonalQTFMethod = diagonalQTFMethods.qmDefault.Value
        self.FullQTFMethod = fullQTFMethods.fmDefault.Value
        self.ClearExistingData = clearExistingData
        if calculationMethods:
            for method in calculationMethods:
                if method in loadRAOMethods:
                    self.LoadRAOMethod = getattr(loadRAOMethods, method).Value
                if method in diagonalQTFMethods:
                    self.DiagonalQTFMethod = getattr(diagonalQTFMethods, method).Value
                if method in fullQTFMethods:
                    self.FullQTFMethod = getattr(fullQTFMethods, method).Value


class VesselTypeDataGenericImportBodyMap(PackedStructure):

    _fields_ = [
        ('DraughtName', _pchar),
        ('RefOrigin', ctypes.c_double * 3),
        ('RefPhaseOrigin', ctypes.c_double * 3)
    ]

    def __init__(
        self,
        DraughtName,
        refOrigin=(
            0.0,
            0.0,
            0.0),
        refPhaseOrigin=(
            OrcinaDefaultReal(),
            OrcinaDefaultReal(),
            OrcinaDefaultReal())):
        PackedStructure.__init__(self)
        self.DraughtName = _PrepareString(DraughtName)
        self.RefOrigin[:] = Vector(refOrigin)
        self.RefPhaseOrigin[:] = Vector(refPhaseOrigin)


class VesselTypeDataGenericImportBodyMapSpecification(PackedStructure):

    _fields_ = [
        ('DestinationVesselType', _pchar),
        ('BodyMapList', ctypes.POINTER(VesselTypeDataGenericImportBodyMap))
    ]

    def __init__(self, DestinationVesselType, bodyCount):
        PackedStructure.__init__(self)
        self.DestinationVesselType = DestinationVesselType
        self.BodyMapList = (VesselTypeDataGenericImportBodyMap * bodyCount)()


class VesselTypeDataDiffractionImportBodyMap(PackedStructure):

    _fields_ = [
        ('Source', _pchar),
        ('DestinationVesselType', _pchar),
        ('DestinationDraught', _pchar)
    ]

    def __init__(self, DestinationVesselType, DestinationDraught):
        PackedStructure.__init__(self)
        self.DestinationVesselType = _PrepareString(DestinationVesselType)
        self.DestinationDraught = _PrepareString(DestinationDraught)


class Interval(PackedStructure):

    _fields_ = [
        ('Lower', ctypes.c_double),
        ('Upper', ctypes.c_double)
    ]


class CycleBin(PackedStructure):

    _fields_ = [
        ('Value', ctypes.c_double),
        ('Count', ctypes.c_double)
    ]


class WaveScatterBin(PackedStructure):

    _fields_ = [
        ('Value', ctypes.c_double),
        ('LowerBound', ctypes.c_double),
        ('UpperBound', ctypes.c_double)
    ]


class WaveScatterAutomationSpecification(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('BatchScriptFileName', _pchar),
        ('TextDataFilePath', _pchar),
        ('FatigueAnalysisFileName', _pchar),
        ('FatigueLoadCaseSimulationPath', _pchar),
    ]


class ExtremeStatisticsSpecification(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('Distribution', ctypes.c_int),
        ('ExtremesToAnalyse', ctypes.c_int),
        ('Threshold', ctypes.c_double),
        ('DeclusterPeriod', ctypes.c_double)
    ]


def RayleighStatisticsSpecification(ExtremesToAnalyse=exUpperTail):
    result = ExtremeStatisticsSpecification()
    result.Distribution = evdRayleigh
    result.ExtremesToAnalyse = ExtremesToAnalyse
    return result


def LikelihoodStatisticsSpecification(Distribution, Threshold, DeclusterPeriod, ExtremesToAnalyse=exUpperTail):
    result = ExtremeStatisticsSpecification()
    result.Distribution = Distribution
    result.Threshold = Threshold
    result.DeclusterPeriod = DeclusterPeriod
    result.ExtremesToAnalyse = ExtremesToAnalyse
    return result


class ExtremeStatisticsQuery(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('StormDurationHours', ctypes.c_double),
        ('RiskFactor', ctypes.c_double),
        ('ConfidenceLevel', ctypes.c_double)
    ]


def RayleighStatisticsQuery(StormDurationHours, RiskFactor):
    result = ExtremeStatisticsQuery()
    result.StormDurationHours = StormDurationHours
    result.RiskFactor = RiskFactor
    return result


def LikelihoodStatisticsQuery(StormDurationHours, ConfidenceLevel):
    result = ExtremeStatisticsQuery()
    result.StormDurationHours = StormDurationHours
    result.ConfidenceLevel = ConfidenceLevel
    return result


class ExtremeStatisticsOutput(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('MostProbableExtremeValue', ctypes.c_double),
        ('ExtremeValueWithRiskFactor', ctypes.c_double),
        ('ReturnLevel', ctypes.c_double),
        ('ConfidenceInterval', Interval),
        ('Sigma', ctypes.c_double),
        ('SigmaStdError', ctypes.c_double),
        ('Xi', ctypes.c_double),
        ('XiStdError', ctypes.c_double)
    ]


class ModalAnalysisSpecification(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('CalculateShapes', ctypes.wintypes.BOOL),
        ('FirstMode', ctypes.c_int),
        ('LastMode', ctypes.c_int),
        ('IncludeCoupledObjects', ctypes.wintypes.BOOL),
        ('AnglesReportedInRadians', ctypes.wintypes.BOOL)
    ]

    def __init__(
            self,
            calculateShapes=True,
            firstMode=-1,
            lastMode=-1,
            includeCoupledObjects=False,
            anglesReportedInRadians=False):
        PackedStructure.__init__(self)
        self.CalculateShapes = calculateShapes
        self.FirstMode = firstMode
        self.LastMode = lastMode
        self.IncludeCoupledObjects = includeCoupledObjects
        self.AnglesReportedInRadians = anglesReportedInRadians


class ModeDetails(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('ModeNumber', ctypes.c_int),
        ('Period', ctypes.c_double),
        ('_ShapeWrtGlobal', ctypes.POINTER(ctypes.c_double)),
        ('_ShapeWrtLocal', ctypes.POINTER(ctypes.c_double))
    ]
    if _supportsModeTypeClassification():
        _fields_.extend([
            ('ModeType', ctypes.c_int),
            ('PercentageInInlineDirection', ctypes.c_double),
            ('PercentageInAxialDirection', ctypes.c_double),
            ('PercentageInTransverseDirection', ctypes.c_double),
            ('PercentageInRotationalDirection', ctypes.c_double)
        ])
    if _supportsModalMassStiffness():
        _fields_.extend([
            ('Mass', ctypes.c_double),
            ('Stiffness', ctypes.c_double)
        ])

    def __init__(self, dofCount=None):
        PackedStructure.__init__(self)
        if dofCount is None:
            self._ShapeWrtGlobal = None
            self._ShapeWrtLocal = None
        else:
            self.ShapeWrtGlobal = _allocateArray(dofCount)
            self.ShapeWrtLocal = _allocateArray(dofCount)
            self._ShapeWrtGlobal = _getArrayData(self.ShapeWrtGlobal)
            self._ShapeWrtLocal = _getArrayData(self.ShapeWrtLocal)


class ModeLoadOutputPoint(PackedStructure):

    _fields_ = [
        ('Owner', Handle),
        ('Arclength', ctypes.c_double)
    ]


class SolveEquationParameters(PackedStructure):

    _fields_ = [
        ('Size', ctypes.c_int),
        ('MaxNumberOfIterations', ctypes.c_int),
        ('Tolerance', ctypes.c_double),
        ('MaxStep', ctypes.c_double),
        ('Delta', ctypes.c_double)
    ]

    def __init__(self):
        PackedStructure.__init__(self)
        status = ctypes.c_int()
        _GetDefaultSolveEquationParameters(self, status)
        _CheckStatus(status)


class GraphCurve(object):

    __slots__ = 'X', 'Y'

    def __init__(self, X, Y):
        self.X = X
        self.Y = Y

    def __len__(self):
        return 2

    def __getitem__(self, index):
        if index == 0:
            return self.X
        if index == 1:
            return self.Y
        raise IndexError(index)


def _CallbackType(restype, *argtypes):

    def from_param(cls, obj):
        if obj is None:
            return obj
        return ctypes._CFuncPtr.from_param(obj)

    result = ctypes.WINFUNCTYPE(restype, *argtypes)
    result.from_param = classmethod(from_param)
    return result


# callback types
_CorrectExternalFileReferencesProc = _CallbackType(
    None,
    Handle
)
_DynamicsProgressHandlerProc = _CallbackType(
    None,
    Handle,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.POINTER(ctypes.wintypes.BOOL)
)
_EnumerateObjectsProc = _CallbackType(
    None,
    Handle,
    ctypes.POINTER(ObjectInfo)
)
_EnumerateVarsProc = _CallbackType(
    None,
    ctypes.POINTER(VarInfo)
)
_LicenceNotFoundHandlerProc = ctypes.WINFUNCTYPE(
    None,
    ctypes.c_int,
    ctypes.POINTER(ctypes.wintypes.BOOL),
    ctypes.POINTER(ctypes.c_void_p)
)
_ProgressHandlerProc = _CallbackType(
    None,
    Handle,
    ctypes.c_int,
    ctypes.POINTER(ctypes.wintypes.BOOL)
)
_SolveEquationCalcYProc = _CallbackType(
    ctypes.c_double,
    ctypes.c_int,
    ctypes.c_double,
    ctypes.POINTER(ctypes.c_int)
)
_StringProgressHandlerProc = _CallbackType(
    None,
    Handle,
    _pchar,
    ctypes.POINTER(ctypes.wintypes.BOOL)
)

# declare the other functions, after the structure definitions
_AnalyseExtrema = _bindToOrcFxAPI(
    'C_AnalyseExtrema',
    None,
    DoubleArrayType,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
)

_AssignWireFrameFromPanelMesh = _bindToOrcFxAPI(
    'C_AssignWireFrameFromPanelMesh',
    None,
    Handle,
    Handle,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_double * 3),
    ctypes.POINTER(ctypes.c_int)
)

_AttachToThread = _bindToOrcFxAPI(
    'C_AttachToThread',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_AVIFileAddBitmap = _bindToOrcFxAPI(
    'C_AVIFileAddBitmap',
    None,
    Handle,
    ctypes.wintypes.HBITMAP,
    ctypes.POINTER(ctypes.c_int)
)

_AVIFileFinalise = _bindToOrcFxAPI(
    'C_AVIFileFinalise',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_AVIFileInitialise = _bindToOrcFxAPI(
    'C_AVIFileInitialiseW',
    None,
    ctypes.POINTER(Handle),
    _pchar,
    ctypes.POINTER(AVIFileParameters),
    ctypes.POINTER(ctypes.c_int)
)

_BeginDataChange = _bindToOrcFxAPI(
    'C_BeginDataChange',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_CalculateDiffraction = _bindToOrcFxAPI(
    'C_CalculateDiffractionW',
    None,
    Handle,
    _StringProgressHandlerProc,
    ctypes.POINTER(ctypes.c_int)
)

_CalculateExtremeStatisticsExcessesOverThreshold = _bindToOrcFxAPI(
    'C_CalculateExtremeStatisticsExcessesOverThreshold',
    ctypes.c_int,
    Handle,
    ctypes.POINTER(ExtremeStatisticsSpecification),
    DoubleArrayType,
    ctypes.POINTER(ctypes.c_int)
)

_CalculateFatigue = _bindToOrcFxAPI(
    'C_CalculateFatigueW',
    None,
    Handle,
    _pchar,
    _StringProgressHandlerProc,
    ctypes.POINTER(ctypes.c_int)
)

_CalculateLinkedStatisticsTimeSeriesStatistics = _bindToOrcFxAPI(
    'C_CalculateLinkedStatisticsTimeSeriesStatistics',
    None,
    Handle,
    ctypes.c_int,
    ctypes.POINTER(TimeSeriesStats),
    ctypes.POINTER(ctypes.c_int)
)

_CalculateMooringStiffness = _bindToOrcFxAPI(
    'C_CalculateMooringStiffness',
    None,
    ctypes.c_int,
    ctypes.POINTER(Handle),
    DoubleArrayType,
    ctypes.POINTER(ctypes.c_int)
)

_CalculateRratio = _bindToOrcFxAPI(
    'C_CalculateRratio',
    None,
    ctypes.c_int,
    DoubleArrayType,
    DoubleArrayType,
    DoubleArrayType,
    ctypes.POINTER(ctypes.c_int)
)

_CalculateStatics = _bindToOrcFxAPI(
    'C_CalculateStaticsW',
    None,
    Handle,
    _StringProgressHandlerProc,
    ctypes.POINTER(ctypes.c_int)
)

_CalculateTimeSeriesStatistics = _bindToOrcFxAPI(
    'C_CalculateTimeSeriesStatistics',
    None,
    DoubleArrayType,
    ctypes.c_int,
    ctypes.c_double,
    ctypes.POINTER(TimeSeriesStats),
    ctypes.POINTER(ctypes.c_int)
)

_ClearDiffraction = _bindToOrcFxAPI(
    'C_ClearDiffraction',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_ClearModel = _bindToOrcFxAPI(
    'C_ClearModel',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_ClearTags = _bindToOrcFxAPI(
    'C_ClearTags',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_CloseExtremeStatistics = _bindToOrcFxAPI(
    'C_CloseExtremeStatistics',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_CloseLinkedStatistics = _bindToOrcFxAPI(
    'C_CloseLinkedStatistics',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_CopyBuffer = _bindToOrcFxAPI(
    'C_CopyBuffer',
    None,
    Handle,
    PByte,
    ctypes.c_int64,
    ctypes.POINTER(ctypes.c_int)
)

_CreateClone = _bindToOrcFxAPI(
    'C_CreateClone',
    None,
    Handle,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int)
)

_CreateClone2 = _bindToOrcFxAPI(
    'C_CreateClone2',
    None,
    Handle,
    Handle,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int)
)

_CreateDiffraction = _bindToOrcFxAPI(
    'C_CreateDiffraction',
    None,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int)
)

_CreateFatigue = _bindToOrcFxAPI(
    'C_CreateFatigue',
    None,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int)
)

_CreateCycleHistogramBins = _bindToOrcFxAPI(
    'C_CreateCycleHistogramBins',
    None,
    ctypes.c_int,
    DoubleArrayType,
    ctypes.c_double,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.POINTER(CycleBin)),
    ctypes.POINTER(ctypes.c_int)
)

_CreateModel2 = _bindToOrcFxAPI(
    'C_CreateModel2',
    None,
    ctypes.POINTER(Handle),
    ctypes.POINTER(CreateModelParams),
    ctypes.POINTER(ctypes.c_int)
)

_CreateModel3DViewBitmap = _bindToOrcFxAPI(
    'C_CreateModel3DViewBitmap',
    None,
    Handle,
    ctypes.POINTER(ViewParameters),
    ctypes.POINTER(ctypes.wintypes.HBITMAP),
    ctypes.POINTER(ctypes.c_int)
)

_CreateModes = _bindToOrcFxAPI(
    'C_CreateModes',
    None,
    Handle,
    ctypes.POINTER(ModalAnalysisSpecification),
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
)

_CreateObject = _bindToOrcFxAPI(
    'C_CreateObject',
    None,
    Handle,
    ctypes.c_int,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int)
)

_CreatePanelMesh = _bindToOrcFxAPI(
    'C_CreatePanelMeshW',
    None,
    _pchar,
    ctypes.c_int,
    ctypes.c_double,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
)

_CreatePanelMesh2 = _bindToOrcFxAPI(
    'C_CreatePanelMesh2W',
    None,
    _pchar,
    ctypes.POINTER(PanelMeshImportOptions),
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
)

_CreateTimeHistorySummary = _bindToOrcFxAPI(
    'C_CreateTimeHistorySummary',
    None,
    ctypes.c_int,
    ctypes.c_int,
    DoubleArrayType,
    DoubleArrayType,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
)

_CreateTimeHistorySummary2 = _bindToOrcFxAPI(
    'C_CreateTimeHistorySummary2',
    None,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.POINTER(TimeHistorySummarySpecification),
    DoubleArrayType,
    DoubleArrayType,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
)

_CreateWaveScatter = _bindToOrcFxAPI(
    'C_CreateWaveScatter',
    None,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int)
)

_DefaultInMemoryLogging = _bindToOrcFxAPI(
    'C_DefaultInMemoryLogging',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_DeleteDataRow = _bindToOrcFxAPI(
    'C_DeleteDataRowW',
    None,
    Handle,
    _pchar,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int)
)

_DeleteTag = _bindToOrcFxAPI(
    'C_DeleteTagW',
    None,
    Handle,
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_DestroyDiffraction = _bindToOrcFxAPI(
    'C_DestroyDiffraction',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_DestroyFatigue = _bindToOrcFxAPI(
    'C_DestroyFatigue',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_DestroyModel = _bindToOrcFxAPI(
    'C_DestroyModel',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_DestroyModes = _bindToOrcFxAPI(
    'C_DestroyModes',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_DestroyCycleHistogramBins = _bindToOrcFxAPI(
    'C_DestroyCycleHistogramBins',
    None,
    ctypes.POINTER(CycleBin),
    ctypes.POINTER(ctypes.c_int)
)

_DestroyObject = _bindToOrcFxAPI(
    'C_DestroyObject',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_DestroyPanelMesh = _bindToOrcFxAPI(
    'C_DestroyPanelMesh',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_DestroyTags = _bindToOrcFxAPI(
    'C_DestroyTagsW',
    None,
    ctypes.POINTER(ObjectTags),
    ctypes.POINTER(ctypes.c_int)
)

_DestroyTimeHistorySummary = _bindToOrcFxAPI(
    'C_DestroyTimeHistorySummary',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_DestroyWaveScatter = _bindToOrcFxAPI(
    'C_DestroyWaveScatter',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_DetachFromThread = _bindToOrcFxAPI(
    'C_DetachFromThread',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_DisableInMemoryLogging = _bindToOrcFxAPI(
    'C_DisableInMemoryLogging',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_DisableModule = _bindToOrcFxAPI(
    'C_DisableModule',
    None,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int)
)

_EndDataChange = _bindToOrcFxAPI(
    'C_EndDataChange',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_EnumerateObjects = _bindToOrcFxAPI(
    'C_EnumerateObjectsW',
    None,
    Handle,
    _EnumerateObjectsProc,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
)

_EnumerateVars2 = _bindToOrcFxAPI(
    'C_EnumerateVars2W',
    None,
    Handle,
    ctypes.POINTER(ObjectExtra),
    ctypes.c_int,
    _EnumerateVarsProc,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
)

_EvaluateWaveFrequencySpectrum = _bindToOrcFxAPI(
    'C_EvaluateWaveFrequencySpectrum',
    None,
    Handle,
    ctypes.c_int,
    DoubleArrayType,
    DoubleArrayType,
    ctypes.POINTER(ctypes.c_int)
)

_ExchangeObjects = _bindToOrcFxAPI(
    'C_ExchangeObjects',
    None,
    Handle,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_ExecutePostCalculationActions = _bindToOrcFxAPI(
    'C_ExecutePostCalculationActionsW',
    None,
    Handle,
    _pchar,
    _StringProgressHandlerProc,
    ctypes.c_int,
    ctypes.wintypes.BOOL,
    ctypes.POINTER(ctypes.c_int)
)

_ExtendSimulation = _bindToOrcFxAPI(
    'C_ExtendSimulation',
    None,
    Handle,
    ctypes.c_double,
    ctypes.POINTER(ctypes.c_int)
)

_ExternalFunctionPrint = _bindToOrcFxAPI(
    'C_ExternalFunctionPrintW',
    None,
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_FitExtremeStatistics = _bindToOrcFxAPI(
    'C_FitExtremeStatistics',
    None,
    Handle,
    ctypes.POINTER(ExtremeStatisticsSpecification),
    ctypes.POINTER(ctypes.c_int)
)

_ForceInMemoryLogging = _bindToOrcFxAPI(
    'C_ForceInMemoryLogging',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_FreeBuffer = _bindToOrcFxAPI(
    'C_FreeBuffer',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_GetBinaryFileType = _bindToOrcFxAPI(
    'C_GetBinaryFileTypeW',
    None,
    _pchar,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
)

_GetCompoundProperties = _bindToOrcFxAPI(
    'C_GetCompoundPropertiesW',
    None,
    ctypes.c_int,
    ctypes.POINTER(Handle),
    Handle,
    _pchar,
    ctypes.POINTER(_CompoundProperties),
    ctypes.POINTER(ctypes.c_int)
)

_GetDataDouble = _bindToOrcFxAPI(
    'C_GetDataDoubleW',
    None,
    Handle,
    _pchar,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_int)
)

_GetDataInteger = _bindToOrcFxAPI(
    'C_GetDataIntegerW',
    None,
    Handle,
    _pchar,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
)

_GetDataRowCount = _bindToOrcFxAPI(
    'C_GetDataRowCountW',
    None,
    Handle,
    _pchar,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
)

_GetDataString = _bindToOrcFxAPI(
    'C_GetDataStringW',
    ctypes.c_int,
    Handle,
    _pchar,
    ctypes.c_int,
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_GetDataType = _bindToOrcFxAPI(
    'C_GetDataTypeW',
    None,
    Handle,
    _pchar,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
)

_GetDefaultSolveEquationParameters = _bindToOrcFxAPI(
    'C_GetDefaultSolveEquationParameters',
    None,
    ctypes.POINTER(SolveEquationParameters),
    ctypes.POINTER(ctypes.c_int)
)

_GetDefaultViewParameters = _bindToOrcFxAPI(
    'C_GetDefaultViewParameters',
    None,
    Handle,
    ctypes.POINTER(ViewParameters),
    ctypes.POINTER(ctypes.c_int)
)

_GetDiffractionOutput = _bindToOrcFxAPI(
    'C_GetDiffractionOutput',
    None,
    Handle,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int),
    ByteArrayType,
    ctypes.POINTER(ctypes.c_int)
)

_GetDiffractionState = _bindToOrcFxAPI(
    'C_GetDiffractionState',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
)

_GetDLLBuildDate = _bindToOrcFxAPI(
    'C_GetDLLBuildDate',
    ctypes.wintypes.DWORD
)

_GetFatigueOutput = _bindToOrcFxAPI(
    'C_GetFatigueOutput',
    None,
    Handle,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int),
    ByteArrayType,
    ctypes.POINTER(ctypes.c_int)
)

_GetFileCreatorVersion = _bindToOrcFxAPI(
    'C_GetFileCreatorVersionW',
    ctypes.c_int,
    _pchar,
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_GetFrequencyDomainMPM = _bindToOrcFxAPI(
    'C_GetFrequencyDomainMPM',
    None,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_int)
)

_GetFrequencyDomainProcessComponents = _bindToOrcFxAPI(
    'C_GetFrequencyDomainProcessComponents',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(FrequencyDomainProcessComponent),
    ctypes.POINTER(ctypes.c_int)
)

_GetFrequencyDomainProcessComponents2 = _bindToOrcFxAPI(
    'C_GetFrequencyDomainProcessComponents2',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(FrequencyDomainProcessComponent),
    ctypes.POINTER(ctypes.c_int)
)

_GetFrequencyDomainResults = _bindToOrcFxAPI(
    'C_GetFrequencyDomainResultsW',
    None,
    Handle,
    ctypes.POINTER(ObjectExtra),
    ctypes.c_int,
    ctypes.POINTER(FrequencyDomainResults),
    ctypes.POINTER(ctypes.c_int)
)

_GetFrequencyDomainResultsFromProcess = _bindToOrcFxAPI(
    'C_GetFrequencyDomainResultsFromProcess',
    None,
    Handle,
    ctypes.c_int,
    ComplexArrayType,
    ctypes.POINTER(FrequencyDomainResults),
    ctypes.POINTER(ctypes.c_int)
)

_GetFrequencyDomainResultsProcess = _bindToOrcFxAPI(
    'C_GetFrequencyDomainResultsProcessW',
    None,
    Handle,
    ctypes.POINTER(ObjectExtra),
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int),
    ComplexArrayType,
    ctypes.POINTER(ctypes.c_int)
)

_GetFrequencyDomainSpectralDensityGraph = _bindToOrcFxAPI(
    'C_GetFrequencyDomainSpectralDensityGraphW',
    None,
    Handle,
    ctypes.POINTER(ObjectExtra),
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(_GraphCurve),
    ctypes.POINTER(ctypes.c_int)
)

_GetFrequencyDomainSpectralDensityGraphFromProcess = _bindToOrcFxAPI(
    'C_GetFrequencyDomainSpectralDensityGraphFromProcess',
    None,
    Handle,
    ctypes.c_int,
    ComplexArrayType,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(_GraphCurve),
    ctypes.POINTER(ctypes.c_int)
)

_GetFrequencyDomainSpectralResponseGraphFromProcess = _bindToOrcFxAPI(
    'C_GetFrequencyDomainSpectralResponseGraphFromProcess',
    None,
    Handle,
    ctypes.c_int,
    ComplexArrayType,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(_GraphCurve),
    ctypes.POINTER(ctypes.c_int)
)

_GetFrequencyDomainTimeHistoryFromProcess = _bindToOrcFxAPI(
    'C_GetFrequencyDomainTimeHistoryFromProcess',
    None,
    Handle,
    ctypes.c_int,
    ComplexArrayType,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_int,
    DoubleArrayType,
    ctypes.POINTER(ctypes.c_int)
)

_GetFrequencyDomainTimeHistorySampleCount = _bindToOrcFxAPI(
    'C_GetFrequencyDomainTimeHistorySampleCount',
    None,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
)

_GetFrequencyDomainTimeHistorySampleTimes = _bindToOrcFxAPI(
    'C_GetFrequencyDomainTimeHistorySampleTimes',
    None,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_int,
    DoubleArrayType,
    ctypes.POINTER(ctypes.c_int)
)

_GetLastErrorString = _bindToOrcFxAPI(
    'C_GetLastErrorStringW',
    ctypes.c_int,
    _pchar,
)

_GetLineResultPoints = _bindToOrcFxAPI(
    'C_GetLineResultPoints',
    None,
    Handle,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
)

_GetModeDegreeOfFreedomDetails = _bindToOrcFxAPI(
    'C_GetModeDegreeOfFreedomDetails',
    None,
    Handle,
    IntArrayType,
    IntArrayType,
    ctypes.POINTER(ctypes.c_int)
)

_GetModeDegreeOfFreedomOwners = _bindToOrcFxAPI(
    'C_GetModeDegreeOfFreedomOwners',
    None,
    Handle,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int)
)

_GetModeDetails = _bindToOrcFxAPI(
    'C_GetModeDetails',
    None,
    Handle,
    ctypes.c_int,
    ctypes.POINTER(ModeDetails),
    ctypes.POINTER(ctypes.c_int)
)

_GetModeLoad = _bindToOrcFxAPI(
    'C_GetModeLoad',
    None,
    Handle,
    ctypes.c_int,
    DoubleArrayType,
    ctypes.POINTER(ctypes.c_int)
)

_GetModeLoadOutputPoints = _bindToOrcFxAPI(
    'C_GetModeLoadOutputPoints',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ModeLoadOutputPoint),
    ctypes.POINTER(ctypes.c_int)
)

_GetModeSummary = _bindToOrcFxAPI(
    'C_GetModeSummary',
    None,
    Handle,
    IntArrayType,
    DoubleArrayType,
    ctypes.POINTER(ctypes.c_int)
)

_GetModelHandle = _bindToOrcFxAPI(
    'C_GetModelHandle',
    None,
    Handle,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int)
)

_GetModelProperty = _bindToOrcFxAPI(
    'C_GetModelProperty',
    None,
    Handle,
    ctypes.c_int,
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_int)
)

_GetModelState = _bindToOrcFxAPI(
    'C_GetModelState',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
)

_GetModelThreadCount = _bindToOrcFxAPI(
    'C_GetModelThreadCount',
    ctypes.c_int,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_GetMultipleTimeHistories = _bindToOrcFxAPI(
    'C_GetMultipleTimeHistoriesW',
    None,
    ctypes.c_int,
    ctypes.POINTER(_TimeHistorySpecification),
    ctypes.POINTER(Period),
    DoubleArrayType,
    ctypes.POINTER(ctypes.c_int)
)

_GetNodeArclengths = _bindToOrcFxAPI(
    'C_GetNodeArclengths',
    None,
    Handle,
    DoubleArrayType,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
)

_GetNumOfSamples = _bindToOrcFxAPI(
    'C_GetNumOfSamples',
    ctypes.c_int,
    Handle,
    ctypes.POINTER(Period),
    ctypes.POINTER(ctypes.c_int)
)

_GetNumOfWarnings = _bindToOrcFxAPI(
    'C_GetNumOfWarnings',
    ctypes.c_int,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_GetObjectExtraFieldRequired = _bindToOrcFxAPI(
    'C_GetObjectExtraFieldRequired',
    None,
    Handle,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.POINTER(ctypes.wintypes.BOOL),
    ctypes.POINTER(ctypes.c_int)
)

_GetObjectTypeFromHandle = _bindToOrcFxAPI(
    'C_GetObjectTypeFromHandle',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
)

_GetObjectTypeName = _bindToOrcFxAPI(
    'C_GetObjectTypeNameW',
    ctypes.c_int,
    Handle,
    ctypes.c_int,
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_GetPanels = _bindToOrcFxAPI(
    'C_GetPanels',
    None,
    Handle,
    DoubleArrayType,
    ctypes.POINTER(ctypes.c_int)
)

_GetRangeGraph3 = _bindToOrcFxAPI(
    'C_GetRangeGraph3W',
    None,
    Handle,
    ctypes.POINTER(ObjectExtra),
    ctypes.POINTER(Period),
    ctypes.c_int,
    DoubleArrayType,
    DoubleArrayType,
    DoubleArrayType,
    DoubleArrayType,
    DoubleArrayType,
    DoubleArrayType,
    DoubleArrayType,
    ctypes.POINTER(ctypes.c_int)
)

_GetRangeGraph4 = _bindToOrcFxAPI(
    'C_GetRangeGraph4W',
    None,
    Handle,
    ctypes.POINTER(ObjectExtra),
    ctypes.POINTER(Period),
    ctypes.POINTER(ArclengthRange),
    ctypes.c_int,
    DoubleArrayType,
    DoubleArrayType,
    DoubleArrayType,
    DoubleArrayType,
    DoubleArrayType,
    DoubleArrayType,
    DoubleArrayType,
    ctypes.POINTER(ctypes.c_int)
)

_GetRangeGraphCurveNames = _bindToOrcFxAPI(
    'C_GetRangeGraphCurveNamesW',
    None,
    Handle,
    ctypes.POINTER(ObjectExtra),
    ctypes.POINTER(Period),
    ctypes.c_int,
    ctypes.POINTER(RangeGraphCurveNames),
    ctypes.POINTER(ctypes.c_int)
)

_GetRangeGraphNumOfPoints = _bindToOrcFxAPI(
    'C_GetRangeGraphNumOfPoints',
    ctypes.c_int,
    Handle,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int)
)

_GetRangeGraphNumOfPoints2 = _bindToOrcFxAPI(
    'C_GetRangeGraphNumOfPoints2',
    ctypes.c_int,
    Handle,
    ctypes.POINTER(ArclengthRange),
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int)
)

_GetRangeGraphNumOfPoints3 = _bindToOrcFxAPI(
    'C_GetRangeGraphNumOfPoints3',
    ctypes.c_int,
    Handle,
    ctypes.POINTER(Period),
    ctypes.POINTER(ArclengthRange),
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int)
)

_GetRecommendedTimeSteps = _bindToOrcFxAPI(
    'C_GetRecommendedTimeSteps',
    None,
    Handle,
    ctypes.POINTER(TimeSteps),
    ctypes.POINTER(ctypes.c_int)
)

_GetRequiredObjectExtraFields = _bindToOrcFxAPI(
    'C_GetRequiredObjectExtraFields',
    None,
    Handle,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
)

_GetRestartParentFileName = _bindToOrcFxAPI(
    'C_GetRestartParentFileNameW',
    None,
    _pchar,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int64),
    ctypes.POINTER(ctypes.c_int)
)

_GetRestartParentFileNames = _bindToOrcFxAPI(
    'C_GetRestartParentFileNamesW',
    None,
    Handle,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int64),
    ctypes.POINTER(ctypes.c_int)
)

_GetSampleTimes = _bindToOrcFxAPI(
    'C_GetSampleTimes',
    None,
    Handle,
    ctypes.POINTER(Period),
    DoubleArrayType,
    ctypes.POINTER(ctypes.c_int)
)

_GetTag = _bindToOrcFxAPI(
    'C_GetTagW',
    ctypes.c_int,
    Handle,
    _pchar,
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_GetTagCount = _bindToOrcFxAPI(
    'C_GetTagCount',
    ctypes.c_int,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_GetTags = _bindToOrcFxAPI(
    'C_GetTagsW',
    None,
    Handle,
    ctypes.POINTER(ObjectTags),
    ctypes.POINTER(ctypes.c_int)
)

_GetWaveScatterTable = _bindToOrcFxAPI(
    'C_GetWaveScatterTable',
    None,
    Handle,
    ctypes.POINTER(WaveScatterBin),
    ctypes.POINTER(WaveScatterBin),
    DoubleArrayType,
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_int)
)

_GetSimulationComplete = _bindToOrcFxAPI(
    'C_GetSimulationComplete',
    None,
    Handle,
    ctypes.POINTER(ctypes.wintypes.BOOL),
    ctypes.POINTER(ctypes.c_int)
)

_GetSimulationDrawTime = _bindToOrcFxAPI(
    'C_GetSimulationDrawTime',
    ctypes.c_double,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_GetSimulationTimeStatus = _bindToOrcFxAPI(
    'C_GetSimulationTimeStatus',
    None,
    Handle,
    ctypes.POINTER(SimulationTimeStatus),
    ctypes.POINTER(ctypes.c_int)
)

_GetSimulationTimeToGo = _bindToOrcFxAPI(
    'C_GetSimulationTimeToGo',
    ctypes.c_double,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_GetSpectralResponseGraph = _bindToOrcFxAPI(
    'C_GetSpectralResponseGraphW',
    None,
    Handle,
    ctypes.POINTER(ObjectExtra),
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(_GraphCurve),
    ctypes.POINTER(ctypes.c_int)
)

_GetTimeHistory2 = _bindToOrcFxAPI(
    'C_GetTimeHistory2W',
    None,
    Handle,
    ctypes.POINTER(ObjectExtra),
    ctypes.POINTER(Period),
    ctypes.c_int,
    DoubleArrayType,
    ctypes.POINTER(ctypes.c_int)
)

_GetTimeHistorySummaryValues = _bindToOrcFxAPI(
    'C_GetTimeHistorySummaryValues',
    None,
    Handle,
    DoubleArrayType,
    DoubleArrayType,
    ctypes.POINTER(ctypes.c_int)
)

_GetUnitsConversionFactor = _bindToOrcFxAPI(
    'C_GetUnitsConversionFactorW',
    None,
    Handle,
    _pchar,
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_int)
)

_GetVariableDataType = _bindToOrcFxAPI(
    'C_GetVariableDataTypeW',
    None,
    Handle,
    _pchar,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
)

_GetVarID = _bindToOrcFxAPI(
    'C_GetVarIDW',
    None,
    Handle,
    _pchar,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
)

_GetWarningText = _bindToOrcFxAPI(
    'C_GetWarningTextW',
    ctypes.c_int,
    Handle,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int),
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_GetWaveComponents2 = _bindToOrcFxAPI(
    'C_GetWaveComponents2',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(WaveComponent),
    ctypes.POINTER(ctypes.c_int)
)

_GetDiffractionWaveComponents = _bindToOrcFxAPI(
    'C_GetDiffractionWaveComponents',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(DiffractionWaveComponent),
    ctypes.POINTER(ctypes.c_int)
)

_GetWindComponents = _bindToOrcFxAPI(
    'C_GetWindComponents',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(WindComponent),
    ctypes.POINTER(ctypes.c_int)
)

_GroupGetFirstChild = _bindToOrcFxAPI(
    'C_GroupGetFirstChild',
    None,
    Handle,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int)
)

_GroupGetNextSibling = _bindToOrcFxAPI(
    'C_GroupGetNextSibling',
    None,
    Handle,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int)
)

_GroupGetParent = _bindToOrcFxAPI(
    'C_GroupGetParent',
    None,
    Handle,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int)
)

_GroupGetPrevSibling = _bindToOrcFxAPI(
    'C_GroupGetPrevSibling',
    None,
    Handle,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int)
)

_GroupMoveAfter = _bindToOrcFxAPI(
    'C_GroupMoveAfter',
    None,
    Handle,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_GroupMoveBefore = _bindToOrcFxAPI(
    'C_GroupMoveBefore',
    None,
    Handle,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_GroupSetParent = _bindToOrcFxAPI(
    'C_GroupSetParent',
    None,
    Handle,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_ImportVesselTypeDataW = _bindToOrcFxAPI(
    'C_ImportVesselTypeDataW',
    None,
    Handle,
    ctypes.c_wchar_p,
    ctypes.POINTER(VesselTypeDataImportSpecification),
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_void_p),
    ctypes.POINTER(ctypes.c_int)
)

_InsertDataRow = _bindToOrcFxAPI(
    'C_InsertDataRowW',
    None,
    Handle,
    _pchar,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int)
)

_InvokeLineSetupWizard = _bindToOrcFxAPI(
    'C_InvokeLineSetupWizardW',
    None,
    Handle,
    _StringProgressHandlerProc,
    ctypes.POINTER(ctypes.c_int)
)

_InvokeWizard = _bindToOrcFxAPI(
    'C_InvokeWizard',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_LoadData = _bindToOrcFxAPI(
    'C_LoadDataW',
    None,
    Handle,
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_LoadDataMem = _bindToOrcFxAPI(
    'C_LoadDataMem',
    None,
    Handle,
    ctypes.c_int,
    PByte,
    ctypes.c_int64,
    ctypes.POINTER(ctypes.c_int)
)

_LoadDiffractionData = _bindToOrcFxAPI(
    'C_LoadDiffractionDataW',
    None,
    Handle,
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_LoadDiffractionDataMem = _bindToOrcFxAPI(
    'C_LoadDiffractionDataMem',
    None,
    Handle,
    ctypes.c_int,
    PByte,
    ctypes.c_int64,
    ctypes.POINTER(ctypes.c_int)
)

_LoadDiffractionResults = _bindToOrcFxAPI(
    'C_LoadDiffractionResultsW',
    None,
    Handle,
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_LoadDiffractionResultsMem = _bindToOrcFxAPI(
    'C_LoadDiffractionResultsMem',
    None,
    Handle,
    PByte,
    ctypes.c_int64,
    ctypes.POINTER(ctypes.c_int)
)

_LoadFatigue = _bindToOrcFxAPI(
    'C_LoadFatigueW',
    None,
    Handle,
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_LoadFatigueMem = _bindToOrcFxAPI(
    'C_LoadFatigueMem',
    None,
    Handle,
    ctypes.c_int,
    PByte,
    ctypes.c_int64,
    ctypes.POINTER(ctypes.c_int)
)

_LoadSimulation = _bindToOrcFxAPI(
    'C_LoadSimulationW',
    None,
    Handle,
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_LoadSimulationMem = _bindToOrcFxAPI(
    'C_LoadSimulationMem',
    None,
    Handle,
    PByte,
    ctypes.c_int64,
    ctypes.POINTER(ctypes.c_int)
)

_LoadWaveScatter = _bindToOrcFxAPI(
    'C_LoadWaveScatterW',
    None,
    Handle,
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_LoadWaveScatterMem = _bindToOrcFxAPI(
    'C_LoadWaveScatterMem',
    None,
    Handle,
    ctypes.c_int,
    PByte,
    ctypes.c_int64,
    ctypes.POINTER(ctypes.c_int)
)

_ModifyModel = _bindToOrcFxAPI(
    'C_ModifyModel',
    None,
    Handle,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int)
)

_ModuleEnabled = _bindToOrcFxAPI(
    'C_ModuleEnabled',
    ctypes.wintypes.BOOL,
    Handle,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int)
)

_MoveObjects = _bindToOrcFxAPI(
    'C_MoveObjects',
    None,
    ctypes.POINTER(MoveObjectSpecification),
    ctypes.c_int,
    ctypes.POINTER(MoveObjectPoint),
    ctypes.POINTER(ctypes.c_int)
)

_NewDiffraction = _bindToOrcFxAPI(
    'C_NewDiffractionW',
    None,
    Handle,
    ctypes.POINTER(NewModelParams),
    ctypes.POINTER(ctypes.c_int)
)

_NewModel = _bindToOrcFxAPI(
    'C_NewModelW',
    None,
    Handle,
    ctypes.POINTER(NewModelParams),
    ctypes.POINTER(ctypes.c_int)
)

_ObjectCalled = _bindToOrcFxAPI(
    'C_ObjectCalledW',
    None,
    Handle,
    _pchar,
    ctypes.POINTER(ObjectInfo),
    ctypes.POINTER(ctypes.c_int)
)

_OpenExtremeStatistics = _bindToOrcFxAPI(
    'C_OpenExtremeStatistics',
    None,
    ctypes.c_int,
    DoubleArrayType,
    ctypes.c_double,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int)
)

_OpenLinkedStatistics2 = _bindToOrcFxAPI(
    'C_OpenLinkedStatistics2W',
    None,
    Handle,
    ctypes.POINTER(ObjectExtra),
    ctypes.POINTER(Period),
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int)
)

_PauseSimulation = _bindToOrcFxAPI(
    'C_PauseSimulation',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_PerformDataAction = _bindToOrcFxAPI(
    'C_PerformDataActionW',
    None,
    Handle,
    _pchar,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_int)
)

_ProcessBatchScript = _bindToOrcFxAPI(
    'C_ProcessBatchScriptW',
    None,
    Handle,
    _pchar,
    _StringProgressHandlerProc,
    _StringProgressHandlerProc,
    _DynamicsProgressHandlerProc,
    ctypes.POINTER(RunSimulationParameters),
    ctypes.POINTER(ctypes.c_int)
)

_QueryExtremeStatistics = _bindToOrcFxAPI(
    'C_QueryExtremeStatistics',
    None,
    Handle,
    ctypes.POINTER(ExtremeStatisticsQuery),
    ctypes.POINTER(ExtremeStatisticsOutput),
    ctypes.POINTER(ctypes.c_int)
)

_QueryLinkedStatistics = _bindToOrcFxAPI(
    'C_QueryLinkedStatistics',
    None,
    Handle,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.POINTER(StatisticsQuery),
    ctypes.POINTER(ctypes.c_int)
)

_RegisterLicenceNotFoundHandler = _bindToOrcFxAPI(
    'C_RegisterLicenceNotFoundHandler',
    None,
    _LicenceNotFoundHandlerProc,
    ctypes.POINTER(ctypes.c_int)
)

_ReportActionProgressW = _bindToOrcFxAPI(
    'C_ReportActionProgressW',
    None,
    Handle,
    ctypes.c_wchar_p,
    ctypes.POINTER(ctypes.c_int)
)

_ResetDiffraction = _bindToOrcFxAPI(
    'C_ResetDiffraction',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_ResetModel = _bindToOrcFxAPI(
    'C_ResetModel',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_RunSimulation2 = _bindToOrcFxAPI(
    'C_RunSimulation2W',
    None,
    Handle,
    _DynamicsProgressHandlerProc,
    ctypes.POINTER(RunSimulationParameters),
    ctypes.POINTER(ctypes.c_int)
)

_SaveData = _bindToOrcFxAPI(
    'C_SaveDataW',
    None,
    Handle,
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_SaveDataMem = _bindToOrcFxAPI(
    'C_SaveDataMem',
    None,
    Handle,
    ctypes.c_int,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int64),
    ctypes.POINTER(ctypes.c_int)
)

_SaveDiffractionData = _bindToOrcFxAPI(
    'C_SaveDiffractionDataW',
    None,
    Handle,
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_SaveDiffractionDataMem = _bindToOrcFxAPI(
    'C_SaveDiffractionDataMem',
    None,
    Handle,
    ctypes.c_int,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int64),
    ctypes.POINTER(ctypes.c_int)
)

_SaveDiffractionResults = _bindToOrcFxAPI(
    'C_SaveDiffractionResultsW',
    None,
    Handle,
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_SaveDiffractionResultsMem = _bindToOrcFxAPI(
    'C_SaveDiffractionResultsMem',
    None,
    Handle,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int64),
    ctypes.POINTER(ctypes.c_int)
)

_SaveExternalProgramFile = _bindToOrcFxAPI(
    'C_SaveExternalProgramFileW',
    None,
    Handle,
    ctypes.c_int,
    ctypes.c_void_p,
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_SaveFatigue = _bindToOrcFxAPI(
    'C_SaveFatigueW',
    None,
    Handle,
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_SaveFatigueMem = _bindToOrcFxAPI(
    'C_SaveFatigueMem',
    None,
    Handle,
    ctypes.c_int,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int64),
    ctypes.POINTER(ctypes.c_int)
)

_SaveModel3DViewBitmapMem = _bindToOrcFxAPI(
    'C_SaveModel3DViewBitmapMem',
    None,
    Handle,
    ctypes.POINTER(ViewParameters),
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int64),
    ctypes.POINTER(ctypes.c_int)
)

_SaveModel3DViewBitmapToFile = _bindToOrcFxAPI(
    'C_SaveModel3DViewBitmapToFileW',
    None,
    Handle,
    ctypes.POINTER(ViewParameters),
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_SaveWaveScatterAutomationFiles = _bindToOrcFxAPI(
    'C_SaveWaveScatterAutomationFilesW',
    None,
    Handle,
    ctypes.POINTER(WaveScatterAutomationSpecification),
    ctypes.POINTER(ctypes.c_int)
)

_SaveSimulation = _bindToOrcFxAPI(
    'C_SaveSimulationW',
    None,
    Handle,
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_SaveSimulationMem = _bindToOrcFxAPI(
    'C_SaveSimulationMem',
    None,
    Handle,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int64),
    ctypes.POINTER(ctypes.c_int)
)

_SaveSpreadsheet = _bindToOrcFxAPI(
    'C_SaveSpreadsheetW',
    None,
    Handle,
    ctypes.c_int,
    ctypes.c_void_p,
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_SaveSpreadsheetMem = _bindToOrcFxAPI(
    'C_SaveSpreadsheetMem',
    None,
    Handle,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_void_p,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int64),
    ctypes.POINTER(ctypes.c_int)
)

_SaveWaveScatter = _bindToOrcFxAPI(
    'C_SaveWaveScatterW',
    None,
    Handle,
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_SaveWaveScatterMem = _bindToOrcFxAPI(
    'C_SaveWaveScatterMem',
    None,
    Handle,
    ctypes.c_int,
    ctypes.POINTER(Handle),
    ctypes.POINTER(ctypes.c_int64),
    ctypes.POINTER(ctypes.c_int)
)

_SetCorrectExternalFileReferencesHandler = _bindToOrcFxAPI(
    'C_SetCorrectExternalFileReferencesHandler',
    None,
    Handle,
    _CorrectExternalFileReferencesProc,
    ctypes.POINTER(ctypes.c_int)
)

_SetDataDouble = _bindToOrcFxAPI(
    'C_SetDataDoubleW',
    None,
    Handle,
    _pchar,
    ctypes.c_int,
    ctypes.c_double,
    ctypes.POINTER(ctypes.c_int)
)

_SetDataInteger = _bindToOrcFxAPI(
    'C_SetDataIntegerW',
    None,
    Handle,
    _pchar,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int)
)

_SetDataRowCount = _bindToOrcFxAPI(
    'C_SetDataRowCountW',
    None,
    Handle,
    _pchar,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int)
)

_SetDataString = _bindToOrcFxAPI(
    'C_SetDataStringW',
    None,
    Handle,
    _pchar,
    ctypes.c_int,
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_SetDiffractionProgressHandler = _bindToOrcFxAPI(
    'C_SetDiffractionProgressHandler',
    None,
    Handle,
    _ProgressHandlerProc,
    ctypes.POINTER(ctypes.c_int)
)

_SetLibraryPolicy = _bindToOrcFxAPI(
    'C_SetLibraryPolicyW',
    None,
    _pchar,
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_SetModelThreadCount = _bindToOrcFxAPI(
    'C_SetModelThreadCount',
    None,
    Handle,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int)
)

_SetProgressHandler = _bindToOrcFxAPI(
    'C_SetProgressHandler',
    None,
    Handle,
    _ProgressHandlerProc,
    ctypes.POINTER(ctypes.c_int)
)

_SetSimulationDrawTime = _bindToOrcFxAPI(
    'C_SetSimulationDrawTime',
    None,
    Handle,
    ctypes.c_double,
    ctypes.POINTER(ctypes.c_int)
)

_SetTag = _bindToOrcFxAPI(
    'C_SetTagW',
    None,
    Handle,
    _pchar,
    _pchar,
    ctypes.POINTER(ctypes.c_int)
)

_SimulateToleranceIntervals = _bindToOrcFxAPI(
    'C_SimulateToleranceIntervals',
    None,
    Handle,
    ctypes.c_int,
    ctypes.POINTER(Interval),
    ctypes.POINTER(ctypes.c_int)
)

_SolveEquation = _bindToOrcFxAPI(
    'C_SolveEquation',
    None,
    ctypes.c_void_p,
    _SolveEquationCalcYProc,
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_double,
    ctypes.POINTER(SolveEquationParameters),
    ctypes.POINTER(ctypes.c_int)
)

_TranslateDiffractionOutput = _bindToOrcFxAPI(
    'C_TranslateDiffractionOutput',
    None,
    Handle,
    ctypes.c_int,
    ctypes.c_int,
    ByteArrayType,
    DoubleArrayType,
    ctypes.POINTER(ctypes.c_int)
)

_UseCalculatedPositionsForStatics = _bindToOrcFxAPI(
    'C_UseCalculatedPositionsForStatics',
    None,
    Handle,
    ctypes.POINTER(UseCalculatedPositionsForStaticsParameters),
    ctypes.POINTER(ctypes.c_int)
)

_UseStaticLineEndOrientations = _bindToOrcFxAPI(
    'C_UseStaticLineEndOrientations',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)

_UseVirtualLogging = _bindToOrcFxAPI(
    'C_UseVirtualLogging',
    None,
    Handle,
    ctypes.POINTER(ctypes.c_int)
)


def DisableModule(module):
    status = ctypes.c_int()
    _DisableModule(module, status)
    _CheckStatus(status)


class HelperMethods(object):

    # data access indices are 1-based in this class, because OrcFxAPI is 1-based

    @staticmethod
    def ActualLogSampleInterval(modelHandle):
        generalHandle = HelperMethods.GetGeneralHandle(modelHandle)
        return HelperMethods.GetDataDouble(generalHandle, 'ActualLogSampleInterval', 0)

    @staticmethod
    def CreateOrcaFlexObject(modelHandle, objectHandle, _type=None):
        if not isinstance(objectHandle, Handle):
            objectHandle = Handle(objectHandle)
        if _type is None:
            _type = HelperMethods.GetObjectTypeFromHandle(modelHandle, objectHandle)
        return Model.orcaFlexObjectClass(_type)(modelHandle, objectHandle, _type)

    @staticmethod
    def DataNameValid(handle, dataName):
        dataName = _PrepareString(dataName)
        dataType = ctypes.c_int()
        status = ctypes.c_int()
        _GetDataType(handle, dataName, dataType, status)
        return status.value == stOK

    @staticmethod
    def FileOperation(handle, func, filename):
        filename = _PrepareString(filename)
        status = ctypes.c_int()
        func(handle, filename, status)
        _CheckStatus(status)

    @staticmethod
    def CopyAndFreeBuffer(buffer, bufferLen):
        status = ctypes.c_int()
        result = bytearray(bufferLen)
        _CopyBuffer(buffer, result, bufferLen, status)
        _CheckStatus(status)
        _FreeBuffer(buffer, status)
        _CheckStatus(status)
        return result

    @staticmethod
    def CopyToStringAndFreeBuffer(buffer, bufferLen):
        status = ctypes.c_int()
        bytes = bytearray(bufferLen)
        _CopyBuffer(buffer, bytes, bufferLen, status)
        _CheckStatus(status)
        _FreeBuffer(buffer, status)
        _CheckStatus(status)
        return bytes[:-2].decode('utf_16')

    @staticmethod
    def CopyToStringsAndFreeBuffer(buffer, bufferLen):
        status = ctypes.c_int()
        bytes = bytearray(bufferLen)
        _CopyBuffer(buffer, bytes, bufferLen, status)
        _CheckStatus(status)
        _FreeBuffer(buffer, status)
        _CheckStatus(status)
        return bytes[:-4].decode('utf_16').split('\x00')

    @staticmethod
    def GetBooleanModelProperty(handle, propertyId, defaultValue=None):
        result = ctypes.wintypes.BOOL()
        status = ctypes.c_int()
        _GetModelProperty(handle, propertyId, ctypes.byref(result), status)
        if status == stInvalidParameter and defaultValue is not None:
            return defaultValue
        _CheckStatus(status)
        return bool(result)

    @staticmethod
    def PerformDataAction(handle, dataName, index, action):
        index = int(index) + 1  # Python is 0-based, OrcFxAPI is 1-based
        dataName = _PrepareString(dataName)
        status = ctypes.c_int()
        _PerformDataAction(handle, dataName, index, action, None, status)
        _CheckStatus(status)

    @staticmethod
    def PerformDataActionGetBool(handle, dataName, index, action):
        index = int(index) + 1  # Python is 0-based, OrcFxAPI is 1-based
        dataName = _PrepareString(dataName)
        status = ctypes.c_int()
        result = ctypes.wintypes.BOOL()
        _PerformDataAction(handle, dataName, index, action, ctypes.byref(result), status)
        _CheckStatus(status)
        return bool(result)

    @staticmethod
    def PerformDataActionSetBool(handle, dataName, index, action, value):
        index = int(index) + 1  # Python is 0-based, OrcFxAPI is 1-based
        dataName = _PrepareString(dataName)
        status = ctypes.c_int()
        value = ctypes.wintypes.BOOL(value)
        _PerformDataAction(handle, dataName, index, action, ctypes.byref(value), status)
        _CheckStatus(status)

    @staticmethod
    def GetDataDouble(handle, dataName, index):
        result = ctypes.c_double()
        status = ctypes.c_int()
        _GetDataDouble(handle, dataName, index, result, status)
        if status.value == stValueNotAvailable:
            return None
        _CheckStatus(status)
        return result.value

    @staticmethod
    def GetDataInteger(handle, dataName, index):
        result = ctypes.c_int()
        status = ctypes.c_int()
        _GetDataInteger(handle, dataName, index, result, status)
        if status.value == stValueNotAvailable:
            return None
        _CheckStatus(status)
        return result.value

    @staticmethod
    def GetDataString(handle, dataName, index):
        dataName = _PrepareString(dataName)
        status = ctypes.c_int()
        length = _GetDataString(handle, dataName, index, None, status)
        if status.value == stValueNotAvailable:
            return None
        _CheckStatus(status)
        result = (_char * length)()
        _GetDataString(handle, dataName, index, result, status)
        _CheckStatus(status)
        return _DecodeString(result.value)

    @staticmethod
    def GetDataBoolean(handle, dataName, index):
        dataName = _PrepareString(dataName)
        dataType = ctypes.c_int()
        status = ctypes.c_int()
        _GetDataType(handle, dataName, dataType, status)
        _CheckStatus(status)
        if dataType.value == dtString:
            length = _GetDataString(handle, dataName, index, None, status)
            if status.value == stValueNotAvailable:
                return None
            _CheckStatus(status)
            result = (_char * length)()
            _GetDataString(handle, dataName, index, result, status)
            _CheckStatus(status)
            value = _DecodeString(result.value)
            result = value == 'Yes'
            if not result and value != 'No':
                raise DLLError(stInvalidDataType, dataName + ' is not a boolean data item')
            return result
        elif dataType.value == dtBoolean:
            result = ctypes.c_int()
            _GetDataInteger(handle, dataName, index, result, status)
            if status.value == stValueNotAvailable:
                return None
            _CheckStatus(status)
            return result.value != 0
        else:
            raise DLLError(stInvalidDataType, dataName + ' is not a boolean data item')

    @staticmethod
    def SetDataString(handle, dataName, index, value):
        status = ctypes.c_int()
        _SetDataString(handle, _PrepareString(dataName), index, _PrepareString(value), status)
        _CheckStatus(status)

    @staticmethod
    def SetDataBoolean(handle, dataName, index, value):
        dataName = _PrepareString(dataName)
        dataType = ctypes.c_int()
        status = ctypes.c_int()
        _GetDataType(handle, dataName, dataType, status)
        _CheckStatus(status)
        if dataType.value == dtString:
            _SetDataString(handle, dataName, index, _PrepareString('Yes' if value else 'No'), status)
            _CheckStatus(status)
        elif dataType.value == dtBoolean:
            _SetDataInteger(handle, dataName, index, ctypes.c_int(value), status)
            _CheckStatus(status)
        else:
            raise DLLError(stInvalidDataType, dataName + ' is not a boolean data item')

    @staticmethod
    def GetGeneralHandle(modelHandle):
        if _supportsGetModelProperty():
            status = ctypes.c_int()
            result = Handle()
            _GetModelProperty(modelHandle, propGeneralHandle, ctypes.byref(result), status)
            if status.value == stOK:
                return result

        return HelperMethods.ObjectCalled(modelHandle, 'General').ObjectHandle

    @staticmethod
    def GetEnvironmentHandle(modelHandle):
        if _supportsGetModelProperty():
            status = ctypes.c_int()
            result = Handle()
            _GetModelProperty(modelHandle, propEnvironmentHandle, ctypes.byref(result), status)
            if status.value == stOK:
                return result

        return HelperMethods.ObjectCalled(modelHandle, 'Environment').ObjectHandle

    @staticmethod
    def GetModelHandle(objectHandle):
        modelHandle = Handle()
        status = ctypes.c_int()
        _GetModelHandle(objectHandle, modelHandle, status)
        _CheckStatus(status)
        return modelHandle

    @staticmethod
    def GetModelState(modelHandle):
        state = ctypes.c_int()
        status = ctypes.c_int()
        _GetModelState(modelHandle, state, status)
        _CheckStatus(status)
        return state.value

    @staticmethod
    def GetModelThreadCount(handle):
        status = ctypes.c_int()
        result = _GetModelThreadCount(handle, status)
        _CheckStatus(status)
        return result

    @staticmethod
    def GetObjectTypeFromHandle(modelHandle, handle):
        if _GetObjectTypeFromHandleAvailable:
            status = ctypes.c_int()
            result = ctypes.c_int()
            _GetObjectTypeFromHandle(handle, result, status)
            _CheckStatus(status)
            return result.value
        else:
            objectInfo = HelperMethods.FindObjectFromHandle(modelHandle, handle)
            return objectInfo.ObjectType

    @staticmethod
    def GetSimulationTimeStatus(modelHandle):
        result = SimulationTimeStatus()
        status = ctypes.c_int()
        _GetSimulationTimeStatus(modelHandle, result, status)
        _CheckStatus(status)
        return result

    @staticmethod
    def GetSimulationStartTime(modelHandle):
        return HelperMethods.GetSimulationTimeStatus(modelHandle).StartTime

    @staticmethod
    def GetSpectralDensityFundamentalFrequency(modelHandle):
        generalHandle = HelperMethods.GetGeneralHandle(modelHandle)
        if HelperMethods.DataNameValid(generalHandle, 'SpectralDensityFundamentalFrequency'):
            return HelperMethods.GetDataDouble(generalHandle, 'SpectralDensityFundamentalFrequency', 0)
        return None

    @staticmethod
    def IsTimeDomainDynamics(modelHandle):
        return not _supportsGetModelProperty() \
            or HelperMethods.GetBooleanModelProperty(modelHandle, propIsTimeDomainDynamics)

    @staticmethod
    def IsFrequencyDomainDynamics(modelHandle):
        return _supportsGetModelProperty() \
            and HelperMethods.GetBooleanModelProperty(modelHandle, propIsFrequencyDomainDynamics)

    @staticmethod
    def IsDeterministicFrequencyDomainDynamics(modelHandle):
        return _supportsGetModelProperty() \
            and HelperMethods.GetBooleanModelProperty(modelHandle, propIsDeterministicFrequencyDomainDynamics)

    @staticmethod
    def IsFrequencyDomainResult(modelHandle, period):
        return HelperMethods.IsFrequencyDomainDynamics(modelHandle) and period.PeriodNum != pnStaticState

    @staticmethod
    def IsLinePayoutNonZero(lineHandle):
        return _supportsLineFeeding() \
            and HelperMethods.GetBooleanModelProperty(lineHandle, propIsPayoutRateNonZero)

    @staticmethod
    def CanResumeSimulation(objectHandle):
        return not _supportsGetModelProperty() \
            or HelperMethods.GetBooleanModelProperty(objectHandle, propCanResumeSimulation, True)

    @staticmethod
    def StageZeroIsBuildUp(objectHandle):
        return not _supportsGetModelProperty() \
            or HelperMethods.GetBooleanModelProperty(objectHandle, propStageZeroIsBuildUp, True)

    @staticmethod
    def ModeLoadOutputPointCount(handle):
        result = ctypes.c_int()
        status = ctypes.c_int()
        _GetModeLoadOutputPoints(handle, result, None, status)
        _CheckStatus(status)
        return result.value

    @staticmethod
    def FindObjectFromHandle(modelHandle, handle):
        result = ObjectInfo()

        def callback(modelHandle, objectInfo):
            if objectInfo[0].ObjectHandle == handle.value:
                # clone objectInfo, see http://stackoverflow.com/q/1470343/
                ctypes.pointer(result)[0] = objectInfo[0]
        status = ctypes.c_int()
        _EnumerateObjects(modelHandle, _EnumerateObjectsProc(callback), ctypes.c_int(), status)
        _CheckStatus(status)
        return result

    @staticmethod
    def FrequencyDomainResults(handle, varID, objectExtra):
        result = FrequencyDomainResults()
        status = ctypes.c_int()
        _GetFrequencyDomainResults(handle, objectExtra, varID, result, status)
        _CheckStatus(status)
        return result.asObject()

    @staticmethod
    def FrequencyDomainResultsProcess(handle, varID, objectExtra):
        componentCount = ctypes.c_int()
        status = ctypes.c_int()
        _GetFrequencyDomainResultsProcess(
            handle, objectExtra, varID, componentCount, None, status)
        _CheckStatus(status)
        process = numpy.empty(componentCount.value, dtype=numpy.complex128)
        _GetFrequencyDomainResultsProcess(
            handle, objectExtra, varID, componentCount, process, status)
        _CheckStatus(status)
        return process

    @staticmethod
    def FrequencyDomainTimeHistorySampleInterval(modelHandle):
        generalHandle = HelperMethods.GetGeneralHandle(modelHandle)
        return HelperMethods.GetDataDouble(generalHandle, 'FrequencyDomainSampleInterval', 0)

    @staticmethod
    def FrequencyDomainSampleCount(modelHandle, period, sampleInterval):
        fromTime, toTime = HelperMethods.PrepareFrequencyDomainPeriod(modelHandle, period)
        if sampleInterval is None:
            sampleInterval = HelperMethods.FrequencyDomainTimeHistorySampleInterval(modelHandle)
        sampleCount = ctypes.c_int()
        status = ctypes.c_int()
        _GetFrequencyDomainTimeHistorySampleCount(
            fromTime, toTime, sampleInterval, sampleCount, status)
        _CheckStatus(status)
        return sampleCount.value

    @staticmethod
    def FrequencyDomainSampleTimes(modelHandle, period, sampleInterval):
        fromTime, toTime = HelperMethods.PrepareFrequencyDomainPeriod(modelHandle, period)
        if sampleInterval is None:
            sampleInterval = HelperMethods.FrequencyDomainTimeHistorySampleInterval(modelHandle)
        sampleCount = ctypes.c_int()
        status = ctypes.c_int()
        _GetFrequencyDomainTimeHistorySampleCount(
            fromTime, toTime, sampleInterval, sampleCount, status)
        _CheckStatus(status)
        values = _allocateArray(sampleCount.value)
        _GetFrequencyDomainTimeHistorySampleTimes(
            fromTime, sampleInterval, sampleCount, values, status)
        _CheckStatus(status)
        return _finaliseArray(values)

    @staticmethod
    def TimeDomainSampleCount(modelHandle, period):
        period = HelperMethods.PreparePeriod(modelHandle, period)
        status = ctypes.c_int()
        sampleCount = _GetNumOfSamples(modelHandle, period, status)
        _CheckStatus(status)
        return sampleCount

    @staticmethod
    def TimeDomainSampleTimes(modelHandle, period):
        period = HelperMethods.PreparePeriod(modelHandle, period)
        status = ctypes.c_int()
        sampleCount = _GetNumOfSamples(modelHandle, period, status)
        _CheckStatus(status)
        samples = _allocateArray(sampleCount)
        _GetSampleTimes(modelHandle, period, samples, status)
        _CheckStatus(status)
        return _finaliseArray(samples)

    @staticmethod
    def SampleCount(modelHandle, period):
        period = HelperMethods.PreparePeriod(modelHandle, period)
        if HelperMethods.IsFrequencyDomainResult(modelHandle, period):
            return HelperMethods.FrequencyDomainSampleCount(modelHandle, period, None)
        else:
            return HelperMethods.TimeDomainSampleCount(modelHandle, period)

    @staticmethod
    def SampleTimes(modelHandle, period):
        period = HelperMethods.PreparePeriod(modelHandle, period)
        if HelperMethods.IsFrequencyDomainResult(modelHandle, period):
            return HelperMethods.FrequencyDomainSampleTimes(modelHandle, period, None)
        else:
            return HelperMethods.TimeDomainSampleTimes(modelHandle, period)

    @staticmethod
    def RangeGraphPointCount(handle, type, varID, arclengthRange, period):
        status = ctypes.c_int()
        if ImportedFunctionAvailable(_GetRangeGraphNumOfPoints3):
            pointCount = _GetRangeGraphNumOfPoints3(handle, period, arclengthRange, varID, status)
        elif type == otLine and HelperMethods.IsLinePayoutNonZero(handle) and arclengthRange is not None and arclengthRange.Mode != armEntireRange:
            raise ValueError(
                'Range graphs cannot be obtained for a given arclength range when the payout rate is non-zero in this version of OrcFxAPI.dll')
        elif ImportedFunctionAvailable(_GetRangeGraphNumOfPoints2):
            pointCount = _GetRangeGraphNumOfPoints2(handle, arclengthRange, varID, status)  # support 10.2 and earlier
        else:
            pointCount = _GetRangeGraphNumOfPoints(handle, varID, status)  # support 9.1 and earlier
        _CheckStatus(status)
        return pointCount

    @staticmethod
    def FrequencyDomainTimeHistoryFromProcess(modelHandle, process, period, sampleInterval):
        fromTime, toTime = HelperMethods.PrepareFrequencyDomainPeriod(modelHandle, period)
        if sampleInterval is None:
            sampleInterval = HelperMethods.FrequencyDomainTimeHistorySampleInterval(modelHandle)
        sampleCount = ctypes.c_int()
        status = ctypes.c_int()
        _GetFrequencyDomainTimeHistorySampleCount(
            fromTime, toTime, sampleInterval, sampleCount, status)
        _CheckStatus(status)
        values = _allocateArray(sampleCount.value)
        process, length = HelperMethods.PrepareProcess(process)
        _GetFrequencyDomainTimeHistoryFromProcess(
            modelHandle, length, process, fromTime, sampleInterval, sampleCount, values, status)
        _CheckStatus(status)
        return _finaliseArray(values)

    @staticmethod
    def FrequencyDomainTimeHistory(modelHandle, handle, varID, period, objectExtra, sampleInterval):
        process = HelperMethods.FrequencyDomainResultsProcess(handle, varID, objectExtra)
        values = HelperMethods.FrequencyDomainTimeHistoryFromProcess(modelHandle, process, period, sampleInterval)
        staticValue = HelperMethods.TimeDomainTimeHistory(modelHandle, handle, varID, pnStaticState, objectExtra)
        return values + staticValue

    @staticmethod
    def TimeDomainTimeHistory(modelHandle, handle, varID, period, objectExtra):
        period = HelperMethods.PreparePeriod(modelHandle, period)
        status = ctypes.c_int()
        sampleCount = _GetNumOfSamples(modelHandle, period, status)
        _CheckStatus(status)
        values = _allocateArray(sampleCount)
        _GetTimeHistory2(handle, objectExtra, period, varID, values, status)
        _CheckStatus(status)
        return _finaliseArray(values)

    @staticmethod
    def PrepareFrequencyDomainPeriod(modelHandle, period):
        period = HelperMethods.PreparePeriod(modelHandle, period)
        if period.PeriodNum != pnSpecifiedPeriod:
            raise ValueError('must use specified period for frequency domain time history synthesis')
        return period.FromTime, period.ToTime

    @staticmethod
    def PreparePeriod(modelHandle, period):
        if isinstance(period, Period):
            return period
        elif period is None:
            if HelperMethods.GetModelState(modelHandle) == ModelState.InStaticState.Value:
                return Period(pnStaticState)
            else:
                return Period(pnWholeSimulation)
        elif isinstance(period, int):
            return Period(period)
        else:
            return SpecifiedPeriod(period[0], period[1])

    @staticmethod
    def PrepareProcess(process):
        if not process.flags.c_contiguous:
            process = numpy.ascontiguousarray(process, dtype=numpy.complex128)
        return process, len(process)

    @staticmethod
    def ObjectCalled(modelHandle, name):
        objectInfo = ObjectInfo()
        name = _PrepareString(name)
        status = ctypes.c_int()
        _ObjectCalled(modelHandle, name, objectInfo, status)
        _CheckStatus(status)
        return objectInfo

    @staticmethod
    def ProgressCallbackCancel(progressHandlerReturnValue):
        if progressHandlerReturnValue is None:
            progressHandlerReturnValue = False
        return ctypes.wintypes.BOOL(progressHandlerReturnValue)

    @staticmethod
    def SaveExternalFile(handle, filename, filetype, params=None):
        filename = _PrepareString(filename)
        if params is not None:
            params = ctypes.byref(params)
        status = ctypes.c_int()
        _SaveExternalProgramFile(handle, filetype, params, filename, status)
        _CheckStatus(status)

    @staticmethod
    def SaveSpreadsheet(handle, spreadsheetType, filename, parameters):
        filename = _PrepareString(filename)
        if parameters is not None:
            parameters = ctypes.byref(parameters)
        status = ctypes.c_int()
        _SaveSpreadsheet(handle, spreadsheetType, parameters, filename, status)
        _CheckStatus(status)

    @staticmethod
    def SaveSpreadsheetMem(handle, spreadsheetType, spreadsheetFileType, parameters):
        if parameters is not None:
            parameters = ctypes.byref(parameters)
        status = ctypes.c_int()
        buffer = Handle()
        bufferLen = ctypes.c_int64()
        _SaveSpreadsheetMem(handle, spreadsheetType, spreadsheetFileType.Value, parameters, buffer, bufferLen, status)
        _CheckStatus(status)
        return HelperMethods.CopyAndFreeBuffer(buffer, bufferLen.value)

    @staticmethod
    def SetModelThreadCount(handle, value):
        status = ctypes.c_int()
        _SetModelThreadCount(handle, value, status)
        _CheckStatus(status)

    @staticmethod
    def TimeHistorySummary(timeHistorySummaryType, times, values, spectralDensityFundamentalFrequency=None):
        if timeHistorySummaryType == thstSpectralDensity:
            if len(times) != len(values):
                raise ValueError('times and values must have the same length')
            times = _prepareArray(times)
        else:
            times = None
        values = _prepareArray(values)
        handle = Handle()
        summaryValueCount = ctypes.c_int()
        status = ctypes.c_int()
        if spectralDensityFundamentalFrequency is None:
            _CreateTimeHistorySummary(
                timeHistorySummaryType,
                len(values),
                times,
                values,
                handle,
                summaryValueCount,
                status
            )
        else:
            specification = TimeHistorySummarySpecification()
            specification.SpectralDensityFundamentalFrequency = spectralDensityFundamentalFrequency
            _CreateTimeHistorySummary2(
                timeHistorySummaryType,
                len(values),
                specification,
                times,
                values,
                handle,
                summaryValueCount,
                status
            )
        _CheckStatus(status)
        try:
            x = _allocateArray(summaryValueCount.value)
            y = _allocateArray(summaryValueCount.value)
            _GetTimeHistorySummaryValues(handle, x, y, status)
            _CheckStatus(status)
        finally:
            _DestroyTimeHistorySummary(handle, status)
            _CheckStatus(status)
        return GraphCurve(_finaliseArray(x), _finaliseArray(y))

    @staticmethod
    @contextlib.contextmanager
    def PanelMeshImporter(filename, format, scale, bodyNumber, importDryPanels):
        status = ctypes.c_int()
        filename = _PrepareString(filename)
        panelMesh = Handle()
        panelCount = ctypes.c_int()
        symmetry = ctypes.c_int()
        if bodyNumber == 1 and importDryPanels:
            _CreatePanelMesh(filename, format, scale, panelMesh, panelCount, symmetry, status)
        else:
            options = PanelMeshImportOptions(format, scale, bodyNumber, importDryPanels)
            _CreatePanelMesh2(filename, options, panelMesh, panelCount, symmetry, status)
        _CheckStatus(status)
        try:
            yield objectFromDict({
                'handle': panelMesh,
                'panelCount': panelCount.value,
                'symmetry': symmetry.value,
            })
        finally:
            # no point checking status here since we can't really do anything about a failure
            _DestroyPanelMesh(panelMesh, status)

    @staticmethod
    def Reinterpreted(array, dtype, shape=None):
        result = array.view(dtype=dtype)
        if shape is not None:
            result.shape = shape
        return result

    @staticmethod
    def FlattenReportingOrigins(handle, reportingOrigins):
        bodyCount = HelperMethods.DiffractionIncludedBodyCount(handle)
        if type(reportingOrigins) is numpy.ndarray:
            if reportingOrigins.ndim == 2:
                if reportingOrigins.shape[0] != bodyCount:
                    raise ValueError('the number of rows of reportingOrigins must match the number of bodies included in the analysis')
                if reportingOrigins.shape[1] != 3:
                    raise ValueError('reportingOrigins must have three columns')
                return numpy.array(reportingOrigins.flatten(), dtype=numpy.float64)
            elif reportingOrigins.ndim == 1:
                if reportingOrigins.size != bodyCount * 3:
                    raise ValueError('invalid size for reportingOrigins')
                return numpy.array(reportingOrigins.flatten(), dtype=numpy.float64)
            else:
                raise ValueError('invalid dimensions for reportingOrigins')
        else:
            if len(reportingOrigins) != bodyCount:
                raise ValueError('the length of reportingOrigins must match the number of bodies included in the analysis')
            return numpy.array([Vector(origin) for origin in reportingOrigins], dtype=numpy.float64).flatten()

    @staticmethod
    def TranslatedDiffractionOutput(handle, outputType, reportingOrigins, output, dtype):
        if output is None:
            return
        reportingOrigins = HelperMethods.FlattenReportingOrigins(handle, reportingOrigins)
        shape = output.shape
        outputSize = output.size * dtype().itemsize
        output = HelperMethods.Reinterpreted(output, numpy.uint8, (outputSize,))
        status = ctypes.c_int()
        _TranslateDiffractionOutput(handle, outputType, outputSize, output, reportingOrigins, status)
        _CheckStatus(status)
        return HelperMethods.Reinterpreted(output, dtype, shape)

    @staticmethod
    def DiffractionDoubleArray(handle, outputType):
        outputSize = ctypes.c_int(0)
        status = ctypes.c_int()
        _GetDiffractionOutput(handle, outputType, outputSize, None, status)
        _CheckStatus(status)
        if outputSize.value == 0:
            return

        output = numpy.empty(outputSize.value, dtype=numpy.uint8)
        _GetDiffractionOutput(handle, outputType, outputSize, output, status)
        _CheckStatus(status)
        return HelperMethods.Reinterpreted(output, numpy.float64)

    @staticmethod
    def DiffractionIncludedBodyCount(handle):
        return HelperMethods.GetDataInteger(handle, 'NumberOfIncludedBodies', 0)

    @staticmethod
    def DiffractionFieldPointCount(handle):
        return HelperMethods.GetDataInteger(handle, 'NumberOfFieldPoints', 0)

    @staticmethod
    def DiffractionDoubleArrayLength(handle, outputType):
        outputSize = ctypes.c_int(0)
        status = ctypes.c_int()
        _GetDiffractionOutput(handle, outputType, outputSize, None, status)
        _CheckStatus(status)
        return outputSize.value // 8

    @staticmethod
    def HydrostaticResults(handle):
        outputSize = ctypes.c_int(0)
        status = ctypes.c_int()
        _GetDiffractionOutput(handle, dotHydrostaticResults, outputSize, None, status)
        _CheckStatus(status)
        if outputSize.value == 0:
            return

        itemFields = [
            ('volume', numpy.float64),
            ('centreOfBuoyancy', numpy.float64, (3,)),
            ('mass', numpy.float64),
            ('centreOfMass', numpy.float64, (3,)),
            ('restoringMatrix', numpy.float64, (6,6)),
            ('inertiaMatrix', numpy.float64, (6,6)),
            ('Awp', numpy.float64),
            ('Lxx', numpy.float64),
            ('Lyy', numpy.float64),
            ('Lxy', numpy.float64),
            ('centreOfFloatation', numpy.float64, (2,)),
        ]

        itemSizeFromFields = numpy.array([], dtype=numpy.dtype(itemFields)).itemsize
        bodyCount = HelperMethods.DiffractionIncludedBodyCount(handle)
        itemSize = outputSize.value // bodyCount
        if outputSize.value % bodyCount != 0 or itemSize < itemSizeFromFields:
            raise NotImplementedError('Unrecognised body hydrostatic result type')
        output = numpy.empty(outputSize.value, dtype=numpy.uint8)
        _GetDiffractionOutput(handle, dotHydrostaticResults, outputSize, output, status)
        _CheckStatus(status)

        if itemSize > itemSizeFromFields:
            itemFields.append(('Unknown', numpy.uint8, itemSize - itemSizeFromFields))
        itemType = numpy.dtype(itemFields)

        output = output.view(dtype=itemType)
        output.shape = [bodyCount]
        return output

    @staticmethod
    def AddedMassDamping(handle, outputType):
        outputSize = ctypes.c_int(0)
        status = ctypes.c_int()
        _GetDiffractionOutput(handle, outputType, outputSize, None, status)
        _CheckStatus(status)
        if outputSize.value == 0:
            return

        periodOrFreqCount = HelperMethods.DiffractionDoubleArrayLength(handle, dotPeriodsOrFrequencies)
        bodyCount = HelperMethods.DiffractionIncludedBodyCount(handle)
        dofCount = 6 * bodyCount
        output = numpy.empty(outputSize.value, dtype=numpy.uint8)
        _GetDiffractionOutput(handle, outputType, outputSize, output, status)
        _CheckStatus(status)
        return HelperMethods.Reinterpreted(output, numpy.float64, (periodOrFreqCount, dofCount, dofCount))

    @staticmethod
    def AddedMassDampingRelativeTo(handle, outputType, reportingOrigins):
        output = HelperMethods.AddedMassDamping(handle, outputType)
        return HelperMethods.TranslatedDiffractionOutput(handle, outputType, reportingOrigins, output, numpy.float64)

    @staticmethod
    def InfiniteFrequencyAddedMass(handle):
        outputSize = ctypes.c_int(0)
        status = ctypes.c_int()
        _GetDiffractionOutput(handle, dotInfiniteFrequencyAddedMass, outputSize, None, status)
        _CheckStatus(status)
        if outputSize.value == 0:
            return

        bodyCount = HelperMethods.DiffractionIncludedBodyCount(handle)
        dofCount = 6 * bodyCount
        output = numpy.empty(outputSize.value, dtype=numpy.uint8)
        _GetDiffractionOutput(handle, dotInfiniteFrequencyAddedMass, outputSize, output, status)
        _CheckStatus(status)
        return HelperMethods.Reinterpreted(output, numpy.float64, (dofCount, dofCount))

    @staticmethod
    def InfiniteFrequencyAddedMassRelativeTo(handle, reportingOrigins):
        output = HelperMethods.InfiniteFrequencyAddedMass(handle)
        return HelperMethods.TranslatedDiffractionOutput(handle, dotInfiniteFrequencyAddedMass, reportingOrigins, output, numpy.float64)

    @staticmethod
    def ExtraRollDamping(handle):
        outputSize = ctypes.c_int(0)
        status = ctypes.c_int()
        _GetDiffractionOutput(handle, dotExtraRollDamping, outputSize, None, status)
        _CheckStatus(status)
        if outputSize.value == 0:
            return

        bodyCount = HelperMethods.DiffractionIncludedBodyCount(handle)
        output = numpy.empty(outputSize.value, dtype=numpy.uint8)
        _GetDiffractionOutput(handle, dotExtraRollDamping, outputSize, output, status)
        _CheckStatus(status)
        return HelperMethods.Reinterpreted(output, numpy.float64, (bodyCount))

    @staticmethod
    def RollDampingPercentCritical(handle):
        outputSize = ctypes.c_int(0)
        status = ctypes.c_int()
        _GetDiffractionOutput(handle, dotRollDampingPercentCritical, outputSize, None, status)
        _CheckStatus(status)
        if outputSize.value == 0:
            return

        periodOrFreqCount = HelperMethods.DiffractionDoubleArrayLength(handle, dotPeriodsOrFrequencies)
        bodyCount = HelperMethods.DiffractionIncludedBodyCount(handle)
        output = numpy.empty(outputSize.value, dtype=numpy.uint8)
        _GetDiffractionOutput(handle, dotRollDampingPercentCritical, outputSize, output, status)
        _CheckStatus(status)
        return HelperMethods.Reinterpreted(output, numpy.float64, (periodOrFreqCount, bodyCount))

    @staticmethod
    def DiffractionRAOs(handle, outputType):
        outputSize = ctypes.c_int(0)
        status = ctypes.c_int()
        _GetDiffractionOutput(handle, outputType, outputSize, None, status)
        _CheckStatus(status)
        if outputSize.value == 0:
            return

        headingCount = HelperMethods.DiffractionDoubleArrayLength(handle, dotHeadings)
        periodOrFreqCount = HelperMethods.DiffractionDoubleArrayLength(handle, dotPeriodsOrFrequencies)
        bodyCount = HelperMethods.DiffractionIncludedBodyCount(handle)
        dofCount = 6 * bodyCount
        output = numpy.empty(outputSize.value, dtype=numpy.uint8)
        _GetDiffractionOutput(handle, outputType, outputSize, output, status)
        _CheckStatus(status)
        return HelperMethods.Reinterpreted(output, numpy.complex128, (headingCount, periodOrFreqCount, dofCount))

    @staticmethod
    def DiffractionRAOsRelativeTo(handle, outputType, reportingOrigins):
        output = HelperMethods.DiffractionRAOs(handle, outputType)
        return HelperMethods.TranslatedDiffractionOutput(handle, outputType, reportingOrigins, output, numpy.complex128)

    @staticmethod
    def QTFHeadingsOrPeriodsOrFrequencies(handle, outputType, itemValueCount):
        outputSize = ctypes.c_int(0)
        status = ctypes.c_int()
        _GetDiffractionOutput(handle, outputType, outputSize, None, status)
        _CheckStatus(status)
        if outputSize.value == 0:
            return

        itemCount = outputSize.value // 8 // itemValueCount
        output = numpy.empty(outputSize.value, dtype=numpy.uint8)
        _GetDiffractionOutput(handle, outputType, outputSize, output, status)
        _CheckStatus(status)
        return HelperMethods.Reinterpreted(output, numpy.float64, (itemCount, itemValueCount))

    @staticmethod
    def MeanDriftLoad(handle, outputType):
        outputSize = ctypes.c_int(0)
        status = ctypes.c_int()
        _GetDiffractionOutput(handle, outputType, outputSize, None, status)
        _CheckStatus(status)
        if outputSize.value == 0:
            return

        output = numpy.empty(outputSize.value, dtype=numpy.uint8)
        _GetDiffractionOutput(handle, outputType, outputSize, output, status)
        _CheckStatus(status)
        outputSize.value = 0
        _GetDiffractionOutput(handle, dotMeanDriftHeadingPairs, outputSize, None, status)
        _CheckStatus(status)
        headingPairCount = outputSize.value // 16
        periodOrFreqCount = HelperMethods.DiffractionDoubleArrayLength(handle, dotPeriodsOrFrequencies)
        bodyCount = HelperMethods.DiffractionIncludedBodyCount(handle)
        dofCount = 6 * bodyCount
        return HelperMethods.Reinterpreted(output, numpy.complex128, (headingPairCount, periodOrFreqCount, dofCount))

    @staticmethod
    def FieldPointOutput(handle, outputType, dofCount):
        outputSize = ctypes.c_int(0)
        status = ctypes.c_int()
        _GetDiffractionOutput(handle, outputType, outputSize, None, status)
        _CheckStatus(status)
        if outputSize.value == 0:
            return

        headingCount = HelperMethods.DiffractionDoubleArrayLength(handle, dotHeadings)
        periodOrFreqCount = HelperMethods.DiffractionDoubleArrayLength(handle, dotPeriodsOrFrequencies)
        fieldPointCount = HelperMethods.DiffractionFieldPointCount(handle)
        output = numpy.empty(outputSize.value, dtype=numpy.uint8)
        _GetDiffractionOutput(handle, outputType, outputSize, output, status)
        _CheckStatus(status)
        if dofCount > 1:
            shape = headingCount, periodOrFreqCount, fieldPointCount, dofCount
        elif dofCount == 1:
            shape = headingCount, periodOrFreqCount, fieldPointCount
        else:
            raise ValueError('invalid dofCount')
        return HelperMethods.Reinterpreted(output, numpy.complex128, shape)

    @staticmethod
    def DiffractionPanelCount(handle):
        outputSize = ctypes.c_int(4)
        output = numpy.empty(4, dtype=numpy.uint8)
        status = ctypes.c_int()
        _GetDiffractionOutput(handle, dotPanelCount, outputSize, output, status)
        _CheckStatus(status)
        if outputSize.value == 0:
            return 0
        return output.view(dtype=numpy.int32)[0]

    @staticmethod
    def PanelGeometry(handle):
        outputSize = ctypes.c_int(0)
        status = ctypes.c_int()
        _GetDiffractionOutput(handle, dotPanelGeometry, outputSize, None, status)
        _CheckStatus(status)
        if outputSize.value == 0:
            return

        itemFields = [
            ('objectId', numpy.int32),
            ('vertices', numpy.float64, (4,3)),
            ('centroid', numpy.float64, (3,)),
            ('normal', numpy.float64, (3,)),
            ('area', numpy.float64),
        ]

        itemSizeFromFields = numpy.array([], dtype=numpy.dtype(itemFields)).itemsize
        panelCount = HelperMethods.DiffractionPanelCount(handle)
        itemSize = outputSize.value // panelCount
        if outputSize.value % panelCount != 0 or itemSize < itemSizeFromFields:
            raise NotImplementedError('Panel geometry type not recognised')
        output = numpy.empty(outputSize.value, dtype=numpy.uint8)
        _GetDiffractionOutput(handle, dotPanelGeometry, outputSize, output, status)
        _CheckStatus(status)

        if itemSize > itemSizeFromFields:
            itemFields.append(('Unknown', numpy.uint8, itemSize - itemSizeFromFields))
        itemType = numpy.dtype(itemFields)

        output = output.view(dtype=itemType)
        output.shape = [panelCount]

        def objectName(objectId):
            if objectId == -1:
                return 'Damping lid'
            bodyIndex = HelperMethods.GetDataInteger(
                handle, 'BodyIndex', objectId + 1)  # convert to 1-based index
            return HelperMethods.GetDataString(handle, 'BodyName', bodyIndex)

        requiredObjectNameLength = max([len(objectName(objectId)) for objectId in output['objectId']])
        itemFields.insert(1, ('objectName', numpy.dtype('<U{}'.format(requiredObjectNameLength))))
        itemType = numpy.dtype(itemFields)
        result = numpy.empty([panelCount], dtype=itemType)
        for field in itemFields:
            if field[0] == 'objectName':
                value = [objectName(objectId) for objectId in output['objectId']]
            else:
                value = output[field[0]]
            result[field[0]] = value
        return result

    @staticmethod
    def PanelPressureVelocity(handle, outputType, outerCount, dofCount):
        outputSize = ctypes.c_int(0)
        status = ctypes.c_int()
        _GetDiffractionOutput(handle, outputType, outputSize, None, status)
        _CheckStatus(status)
        if outputSize.value == 0:
            return

        panelCount = HelperMethods.DiffractionPanelCount(handle)
        periodOrFreqCount = HelperMethods.DiffractionDoubleArrayLength(handle, dotPeriodsOrFrequencies)
        output = numpy.empty(outputSize.value, dtype=numpy.uint8)
        _GetDiffractionOutput(handle, outputType, outputSize, output, status)
        _CheckStatus(status)
        if dofCount > 1:
            shape = (outerCount, periodOrFreqCount, panelCount, dofCount)
        else:
            shape = (outerCount, periodOrFreqCount, panelCount)
        return HelperMethods.Reinterpreted(output, numpy.complex128, shape)

    @staticmethod
    def SecondOrderLoad(handle, outputType):
        outputSize = ctypes.c_int(0)
        status = ctypes.c_int()
        _GetDiffractionOutput(handle, outputType, outputSize, None, status)
        _CheckStatus(status)
        if outputSize.value == 0:
            return

        outputLength = outputSize.value // 8
        output = numpy.empty(outputSize.value, dtype=numpy.uint8)
        _GetDiffractionOutput(handle, outputType, outputSize, output, status)
        _CheckStatus(status)
        outputSize.value = 0
        _GetDiffractionOutput(handle, dotQTFHeadingPairs, outputSize, None, status)
        _CheckStatus(status)
        headingCount = outputSize.value // 16
        outputSize.value = 0
        _GetDiffractionOutput(handle, dotQTFPeriodsOrFrequencies, outputSize, None, status)
        _CheckStatus(status)
        periodCount = outputSize.value // 24
        bodyCount = HelperMethods.DiffractionIncludedBodyCount(handle)
        dofCount = 6 * bodyCount
        return HelperMethods.Reinterpreted(output, numpy.complex128, (headingCount, periodCount, dofCount))

    @staticmethod
    def FatigueIntegerScalar(handle, outputType):
        outputSize = ctypes.c_int(4)
        output = numpy.empty(4, dtype=numpy.uint8)
        status = ctypes.c_int()
        _GetFatigueOutput(handle, outputType, outputSize, output, status)
        _CheckStatus(status)
        if outputSize.value == 0:
            return 0
        return output.view(dtype=numpy.int32)[0]

    @staticmethod
    def FatigueDoubleArray(handle, outputType):
        outputSize = ctypes.c_int(0)
        status = ctypes.c_int()
        _GetFatigueOutput(handle, outputType, outputSize, None, status)
        _CheckStatus(status)
        if outputSize.value == 0:
            return

        output = numpy.empty(outputSize.value, dtype=numpy.uint8)
        _GetFatigueOutput(handle, outputType, outputSize, output, status)
        _CheckStatus(status)
        return HelperMethods.Reinterpreted(output, numpy.float64)

    @staticmethod
    def FatigueDoubleArrayLength(handle, outputType):
        outputSize = ctypes.c_int(0)
        status = ctypes.c_int()
        _GetFatigueOutput(handle, outputType, outputSize, None, status)
        _CheckStatus(status)
        return outputSize.value // 8

    @staticmethod
    def FatigueUsingComponents(handle):
        return HelperMethods.GetDataInteger(handle, 'ComponentCount', 0) is not None

    @staticmethod
    def FatigueUsingTheta(handle):
        return HelperMethods.GetDataInteger(handle, 'ThetaCount', 0) is not None

    @staticmethod
    def FatigueLoadCaseCount(handle):
        return HelperMethods.GetDataInteger(handle, 'LoadCaseCount', 0)

    @staticmethod
    def FatigueOutputPointCount(handle):
        return HelperMethods.GetDataInteger(handle, 'OutputPointCount', 0)

    @staticmethod
    def FatigueComponentCount(handle):
        result = HelperMethods.GetDataInteger(handle, 'ComponentCount', 0)
        if result is None:
            return 1
        return result

    @staticmethod
    def FatigueThetaCount(handle):
        result = HelperMethods.GetDataInteger(handle, 'ThetaCount', 0)
        if result is None:
            return 1
        return result

    @staticmethod
    def FatigueOutputPointDetails(handle, outputType, itemFields):
        outputSize = ctypes.c_int(0)
        status = ctypes.c_int()
        _GetFatigueOutput(handle, outputType, outputSize, None, status)
        _CheckStatus(status)
        if outputSize.value == 0:
            return

        itemSizeFromFields = numpy.array([], dtype=numpy.dtype(itemFields)).itemsize
        pointCount = HelperMethods.FatigueIntegerScalar(handle, fotOutputPointCount)
        itemSize = outputSize.value // pointCount
        if outputSize.value % pointCount != 0 or itemSize < itemSizeFromFields:
            raise NotImplementedError('Output point details type not recognised')
        output = numpy.empty(outputSize.value, dtype=numpy.uint8)
        _GetFatigueOutput(handle, outputType, outputSize, output, status)
        _CheckStatus(status)

        if itemSize > itemSizeFromFields:
            itemFields.append(('Unknown', numpy.uint8, itemSize - itemSizeFromFields))
        itemType = numpy.dtype(itemFields)

        output = output.view(dtype=itemType)
        output.shape = [pointCount]
        return output

    @staticmethod
    def FatigueHomogeneousPipeOutputPointDetails(handle):
        itemFields = [
            ('arclength', numpy.float64),
            ('SNcurveIndex', numpy.int32),
            ('radialPos', numpy.int32),
            ('SCF', numpy.float64),
            ('thicknessCorrectionFactor', numpy.float64),
        ]
        output = HelperMethods.FatigueOutputPointDetails(handle, fotHomogeneousPipeOutputPointDetails, itemFields)
        output['SNcurveIndex'] -= 1 # convert to 0-based indices
        return output

    @staticmethod
    def FatigueComponentOutputPointDetails(handle):
        itemFields = [
            ('arclength', numpy.float64),
        ]
        output = HelperMethods.FatigueOutputPointDetails(handle, fotComponentOutputPointDetails, itemFields)
        return output

    @staticmethod
    def FatigueMooringOutputPointDetails(handle):
        itemFields = [
            ('arclength', numpy.float64),
            ('TNcurveIndex', numpy.int32),
        ]
        output = HelperMethods.FatigueOutputPointDetails(handle, fotMooringOutputPointDetails, itemFields)
        output['TNcurveIndex'] -= 1 # convert to 0-based indices
        return output

    @staticmethod
    def FatigueShear7OutputPointDetails(handle):
        itemFields = [
            ('arclength', numpy.float64),
            ('xOverL', numpy.float64),
        ]
        output = HelperMethods.FatigueOutputPointDetails(handle, fotShear7OutputPointDetails, itemFields)
        return output

    @staticmethod
    def FatigueHistogramOutputPointDetails(handle):
        itemFields = [
            ('arclength', numpy.float64),
            ('radialPos', numpy.int32),
        ]
        output = HelperMethods.FatigueOutputPointDetails(handle, fotHistogramOutputPointDetails, itemFields)
        return output

    @staticmethod
    def FatigueDamage(handle, outputType, loadCaseCount, itemFields):
        outputSize = ctypes.c_int(0)
        status = ctypes.c_int()
        _GetFatigueOutput(handle, outputType, outputSize, None, status)
        _CheckStatus(status)
        if outputSize.value == 0:
            return

        arclengthCount = HelperMethods.FatigueOutputPointCount(handle)
        componentCount = HelperMethods.FatigueComponentCount(handle) if HelperMethods.FatigueUsingComponents(handle) else None
        thetaCount = HelperMethods.FatigueThetaCount(handle) if HelperMethods.FatigueUsingTheta(handle) else None

        shape = []
        if loadCaseCount is None:
            loadCaseCount = 1
        else:
            shape.append(loadCaseCount)
        shape.append(arclengthCount)
        if componentCount is None:
            componentCount = 1
        else:
            shape.append(componentCount)
        if thetaCount is None:
            thetaCount = 1
        else:
            shape.append(thetaCount)

        itemSizeFromFields = numpy.array([], dtype=numpy.dtype(itemFields)).itemsize
        itemCount = loadCaseCount * arclengthCount * componentCount * thetaCount
        itemSize = outputSize.value // itemCount
        if outputSize.value % itemCount != 0 or itemSize < itemSizeFromFields:
            raise NotImplementedError('Damage item type not recognised')
        output = numpy.empty(outputSize.value, dtype=numpy.uint8)
        _GetFatigueOutput(handle, outputType, outputSize, output, status)
        _CheckStatus(status)

        if itemSize > itemSizeFromFields:
            itemFields.append(('Unknown', numpy.uint8, itemSize - itemSizeFromFields))
        itemType = numpy.dtype(itemFields)

        output = output.view(dtype=itemType)
        output.shape = shape
        return output

    @staticmethod
    def FatigueDeterministicLoadCaseDamage(handle):
        itemFields = [
            ('MinResponse', numpy.float64),
            ('MaxResponse', numpy.float64),
            ('MeanResponse', numpy.float64),
            ('Damage', numpy.float64),
            ('DamageRate', numpy.float64),
        ]
        output = HelperMethods.FatigueDamage(
            handle,
            fotDeterministicLoadCaseDamage,
            HelperMethods.FatigueLoadCaseCount(handle),
            itemFields
        )
        return output

    @staticmethod
    def FatigueSpectralLoadCaseDamage(handle):
        itemFields = [
            ('MeanResponse', numpy.float64),
            ('Damage', numpy.float64),
            ('DamageRate', numpy.float64),
        ]
        output = HelperMethods.FatigueDamage(
            handle,
            fotSpectralLoadCaseDamage,
            HelperMethods.FatigueLoadCaseCount(handle),
            itemFields
        )
        return output

    @staticmethod
    def FatigueShear7LoadCaseDamage(handle):
        itemFields = [
            ('Damage', numpy.float64),
            ('DamageRate', numpy.float64),
        ]
        output = HelperMethods.FatigueDamage(
            handle,
            fotShear7LoadCaseDamage,
            HelperMethods.FatigueLoadCaseCount(handle),
            itemFields
        )
        return output

    @staticmethod
    def FatigueOverallDamage(handle):
        itemFields = [
            ('Damage', numpy.float64),
            ('Life', numpy.float64),
        ]
        output = HelperMethods.FatigueDamage(
            handle,
            fotOverallDamage,
            None,
            itemFields
        )
        return output

    @staticmethod
    def FatigueCycleRate(handle, outputType, loadCaseCount):
        outputSize = ctypes.c_int(0)
        status = ctypes.c_int()
        _GetFatigueOutput(handle, outputType, outputSize, None, status)
        _CheckStatus(status)
        if outputSize.value == 0:
            return

        arclengthCount = HelperMethods.FatigueOutputPointCount(handle)
        thetaCount = HelperMethods.FatigueThetaCount(handle) if HelperMethods.FatigueUsingTheta(handle) else None
        binCount = HelperMethods.FatigueDoubleArrayLength(handle, fotHistogramBins)

        shape = []
        if loadCaseCount is not None:
            shape.append(loadCaseCount)
        shape.append(arclengthCount)
        if thetaCount is not None:
            shape.append(thetaCount)
        shape.append(binCount)

        output = numpy.empty(outputSize.value, dtype=numpy.uint8)
        _GetFatigueOutput(handle, outputType, outputSize, output, status)
        _CheckStatus(status)
        return HelperMethods.Reinterpreted(output, numpy.float64, shape)


class Model(object):

    __slots__ = 'handle', 'ownsModelHandle', 'general', 'environment', 'progressHandler', \
        'progressHandlerCallback', 'correctExternalFileReferencesHandler', \
        'correctExternalFileReferencesHandlerCallback', 'batchProgressHandler', \
        'staticsProgressHandler', 'dynamicsProgressHandler', 'postCalculationActionProgressHandler'

    _hookOrcaFlexObjectClass = []

    @classmethod
    def addOrcaFlexObjectClassHook(cls, hook):
        cls._hookOrcaFlexObjectClass.append(hook)

    @classmethod
    def removeOrcaFlexObjectClassHook(cls, hook):
        cls._hookOrcaFlexObjectClass.remove(hook)

    def __init__(self, filename=None, threadCount=None, handle=None):
        status = ctypes.c_int()
        self.ownsModelHandle = not handle
        if self.ownsModelHandle:
            handle = Handle()
            if threadCount is None:
                threadCount = -1
            params = CreateModelParams()
            params.ThreadCount = threadCount
            _CreateModel2(handle, params, status)
            _CheckStatus(status)
            self.handle = handle
        else:
            self.handle = handle
        self.general = HelperMethods.CreateOrcaFlexObject(
            self.handle, HelperMethods.GetGeneralHandle(self.handle), otGeneral)
        self.environment = HelperMethods.CreateOrcaFlexObject(
            self.handle, HelperMethods.GetEnvironmentHandle(
                self.handle), otEnvironment)
        self.progressHandler = None
        self.batchProgressHandler = None
        self.staticsProgressHandler = None
        self.dynamicsProgressHandler = None
        self.postCalculationActionProgressHandler = None
        # avoid calling C_SetCorrectExternalFileReferencesHandler which fails on
        # older versions of the DLL
        object.__setattr__(self, 'correctExternalFileReferencesHandler', None)
        if filename:
            ft = ctypes.c_int()
            filename = _PrepareString(filename)
            status = ctypes.c_int()
            _GetBinaryFileType(filename, ft, status)
            if status.value != stOK or FileType[ft.value] == FileType.DataFile:
                _LoadData(handle, filename, status)
            else:
                _LoadSimulation(handle, filename, status)
            _CheckStatus(status)

    def __del__(self):
        if self.ownsModelHandle:
            try:
                _DestroyModel(self.handle, ctypes.c_int())
                # no point checking status here since we can't really do anything about a failure
            except BaseException:                # swallow this since we get exceptions when Python terminates unexpectedly
                # (e.g. CTRL+Z)
                pass

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name == 'progressHandler':
            status = ctypes.c_int()
            if self.progressHandler:
                def callback(handle, progress, cancel):
                    cancel[0] = HelperMethods.ProgressCallbackCancel(
                        self.progressHandler(self, progress))
                self.progressHandlerCallback = _ProgressHandlerProc(callback)
            else:
                self.progressHandlerCallback = None
            _SetProgressHandler(self.handle, self.progressHandlerCallback, status)
            _CheckStatus(status)
        elif name == 'correctExternalFileReferencesHandler':
            status = ctypes.c_int()
            if self.correctExternalFileReferencesHandler:
                def callback(handle):
                    self.correctExternalFileReferencesHandler(self)
                self.correctExternalFileReferencesHandlerCallback = _CorrectExternalFileReferencesProc(
                    callback
                )
            else:
                self.correctExternalFileReferencesHandlerCallback = None
            _SetCorrectExternalFileReferencesHandler(
                self.handle,
                self.correctExternalFileReferencesHandlerCallback,
                status
            )
            _CheckStatus(status)

    def __getitem__(self, name):
        objectInfo = HelperMethods.ObjectCalled(self.handle, name)
        return HelperMethods.CreateOrcaFlexObject(self.handle, objectInfo.ObjectHandle, objectInfo.ObjectType)

    def _stringProgressHandler(self, handler):
        if handler:
            def callback(handle, progress, cancel):
                cancel[0] = HelperMethods.ProgressCallbackCancel(handler(self, progress))
            return _StringProgressHandlerProc(callback)
        else:
            return None

    def _batchProgressHandler(self):
        return self._stringProgressHandler(self.batchProgressHandler)

    def _staticsProgressHandler(self):
        return self._stringProgressHandler(self.staticsProgressHandler)

    def _dynamicsProgressHandler(self):
        if self.dynamicsProgressHandler:
            def callback(handle, time, start, stop, cancel):
                cancel[0] = HelperMethods.ProgressCallbackCancel(
                    self.dynamicsProgressHandler(self, time, start, stop))
            return _DynamicsProgressHandlerProc(callback)
        else:
            return None

    def _postCalculationActionProgressHandler(self):
        return self._stringProgressHandler(self.postCalculationActionProgressHandler)

    @staticmethod
    def orcaFlexObjectClass(type):
        if type == otLine:
            objectClass = OrcaFlexLineObject
        elif type == otLineType or type == otBendingStiffness:
            objectClass = OrcaFlexWizardObject
        elif type == otVessel:
            objectClass = OrcaFlexVesselObject
        elif type == ot6DBuoy:
            objectClass = OrcaFlex6DBuoyObject
        elif type == otTurbine:
            objectClass = OrcaFlexTurbineObject
        else:
            objectClass = OrcaFlexObject
        for hook in Model._hookOrcaFlexObjectClass:
            objectClass = hook(type, objectClass)
        return objectClass

    def createOrcaFlexObject(self, objectHandle, _type=None):
        # do not remove this method since it is called by the external function code in OrcaFlex
        return HelperMethods.CreateOrcaFlexObject(self.handle, objectHandle, _type)

    def ModuleEnabled(self, module):
        status = ctypes.c_int()
        result = _ModuleEnabled(self.handle, module, status)
        _CheckStatus(status)
        return bool(result)

    @property
    def groupFirstChild(self):
        handle = Handle()
        status = ctypes.c_int()
        _GroupGetFirstChild(self.handle, handle, status)
        _CheckStatus(status)
        if handle:
            return HelperMethods.CreateOrcaFlexObject(self.handle, handle)
        else:
            return None

    @property
    def threadCount(self):
        return HelperMethods.GetModelThreadCount(self.handle)

    @threadCount.setter
    def threadCount(self, value):
        HelperMethods.SetModelThreadCount(self.handle, value)

    @property
    def recommendedTimeSteps(self):
        result = TimeSteps()
        status = ctypes.c_int()
        _GetRecommendedTimeSteps(self.handle, result, status)
        _CheckStatus(status)
        return result

    @property
    def simulationStartTime(self):
        return self.simulationTimeStatus.StartTime

    @property
    def simulationStopTime(self):
        return self.simulationTimeStatus.StopTime

    @property
    def simulationTimeToGo(self):
        status = ctypes.c_int()
        result = _GetSimulationTimeToGo(self.handle, status)
        _CheckStatus(status)
        return result

    @property
    def state(self):
        return ModelState[HelperMethods.GetModelState(self.handle)]

    @property
    def dongleName(self):
        return HelperMethods.GetDataString(self.handle, 'DongleName', 0)

    @property
    def dongleAccessMode(self):
        return HelperMethods.GetDataString(self.handle, 'DongleAccessMode', 0)

    @property
    def donglePort(self):
        return HelperMethods.GetDataString(self.handle, 'DonglePort', 0)

    @property
    def dongleServer(self):
        return HelperMethods.GetDataString(self.handle, 'DongleServer', 0)

    @property
    def licenceFileLocation(self):
        return HelperMethods.GetDataString(self.handle, 'LicenceFileLocation', 0)

    @property
    def licenceStatus(self):
        return HelperMethods.GetDataString(self.handle, 'LicenceStatus', 0)

    @property
    def latestFileName(self):
        return HelperMethods.GetDataString(self.handle, 'LatestFileName', 0)

    @latestFileName.setter
    def latestFileName(self, value):
        HelperMethods.SetDataString(self.handle, 'LatestFileName', 0, value)

    @property
    def type(self):
        return ModelType[self.general.ModelType]

    @type.setter
    def type(self, value):
        self.general.ModelType = value.Value

    @property
    def outputBrowserGroupStructureWhenTrackingChanges(self):
        return HelperMethods.GetDataBoolean(self.handle, 'OutputBrowserGroupStructureWhenTrackingChanges', 0)

    @outputBrowserGroupStructureWhenTrackingChanges.setter
    def outputBrowserGroupStructureWhenTrackingChanges(self, value):
        HelperMethods.SetDataBoolean(self.handle, 'OutputBrowserGroupStructureWhenTrackingChanges', 0, value)

    @property
    def restartParentFileNames(self):
        status = ctypes.c_int()
        buffer = Handle()
        bufferLen = ctypes.c_int64()
        length = _GetRestartParentFileNames(self.handle, buffer, bufferLen, status)
        _CheckStatus(status)
        return HelperMethods.CopyToStringsAndFreeBuffer(buffer, bufferLen.value)

    @property
    def simulationComplete(self):
        simulationComplete = ctypes.wintypes.BOOL()
        status = ctypes.c_int()
        _GetSimulationComplete(self.handle, simulationComplete, status)
        _CheckStatus(status)
        return bool(simulationComplete)

    @property
    def simulationTimeStatus(self):
        return HelperMethods.GetSimulationTimeStatus(self.handle)

    @property
    def canResumeSimulation(self):
        return HelperMethods.CanResumeSimulation(self.handle)

    @property
    def isTimeDomainDynamics(self):
        return HelperMethods.IsTimeDomainDynamics(self.handle)

    @property
    def isFrequencyDomainDynamics(self):
        return HelperMethods.IsFrequencyDomainDynamics(self.handle)

    @property
    def isDeterministicFrequencyDomainDynamics(self):
        return HelperMethods.IsDeterministicFrequencyDomainDynamics(self.handle)

    @property
    def objects(self):
        result = []

        def callback(handle, objectInfo):
            result.append(HelperMethods.CreateOrcaFlexObject(
                self.handle, objectInfo[0].ObjectHandle, objectInfo[0].ObjectType))
        status = ctypes.c_int()
        _EnumerateObjects(self.handle, _EnumerateObjectsProc(callback), ctypes.c_int(), status)
        _CheckStatus(status)
        return tuple(result)

    def AttachToThread(self):
        status = ctypes.c_int()
        _AttachToThread(self.handle, status)
        _CheckStatus(status)

    def DetachFromThread(self):
        status = ctypes.c_int()
        _DetachFromThread(self.handle, status)
        _CheckStatus(status)

    def CreateObject(self, type, name=None):
        handle = Handle()
        type = int(type)
        status = ctypes.c_int()
        _CreateObject(self.handle, type, handle, status)
        _CheckStatus(status)
        obj = HelperMethods.CreateOrcaFlexObject(self.handle, handle, type)
        if name:
            obj.name = name
        return obj

    def DestroyObject(self, obj):
        if not hasattr(obj, 'handle'):
            obj = self[obj]  # assume that obj is a name
        status = ctypes.c_int()
        _DestroyObject(obj.handle, status)
        _CheckStatus(status)

    def DeleteUnusedTypes(self):
        status = ctypes.c_int()
        _ModifyModel(self.handle, modifyModelActionDeleteUnusedTypes, status)
        _CheckStatus(status)

    def DeleteUnusedVariableDataSources(self):
        status = ctypes.c_int()
        _ModifyModel(self.handle, modifyModelActionDeleteUnusedVariableDataSources, status)
        _CheckStatus(status)

    def Reset(self):
        status = ctypes.c_int()
        _ResetModel(self.handle, status)
        _CheckStatus(status)

    def Clear(self):
        status = ctypes.c_int()
        _ClearModel(self.handle, status)
        _CheckStatus(status)

    def NewVariationModel(self, parentFileName):
        status = ctypes.c_int()
        _NewModel(self.handle, NewModelParams(ModelType.Variation, parentFileName), status)
        _CheckStatus(status)

    def NewRestartAnalysis(self, parentFileName):
        status = ctypes.c_int()
        _NewModel(self.handle, NewModelParams(ModelType.Restart, parentFileName), status)
        _CheckStatus(status)

    def LoadData(self, filename):
        HelperMethods.FileOperation(self.handle, _LoadData, filename)

    def LoadDataMem(self, buffer, dataFileType=DataFileType.Binary):
        status = ctypes.c_int()
        _LoadDataMem(self.handle, dataFileType.Value, buffer, len(buffer), status)
        _CheckStatus(status)

    def SaveData(self, filename):
        HelperMethods.FileOperation(self.handle, _SaveData, filename)

    def SaveDataMem(self, dataFileType=DataFileType.Binary):
        status = ctypes.c_int()
        buffer = Handle()
        bufferLen = ctypes.c_int64()
        _SaveDataMem(self.handle, dataFileType.Value, buffer, bufferLen, status)
        _CheckStatus(status)
        return HelperMethods.CopyAndFreeBuffer(buffer, bufferLen.value)

    def LoadSimulation(self, filename):
        HelperMethods.FileOperation(self.handle, _LoadSimulation, filename)

    def LoadSimulationMem(self, buffer):
        status = ctypes.c_int()
        _LoadSimulationMem(self.handle, buffer, len(buffer), status)
        _CheckStatus(status)

    def SaveSimulation(self, filename):
        HelperMethods.FileOperation(self.handle, _SaveSimulation, filename)

    def SaveSimulationMem(self):
        status = ctypes.c_int()
        buffer = Handle()
        bufferLen = ctypes.c_int64()
        _SaveSimulationMem(self.handle, buffer, bufferLen, status)
        _CheckStatus(status)
        return HelperMethods.CopyAndFreeBuffer(buffer, bufferLen.value)

    @property
    def warnings(self):

        def generator():
            status = ctypes.c_int()
            count = _GetNumOfWarnings(self.handle, status)
            _CheckStatus(status)
            for index in range(count):
                length = _GetWarningText(self.handle, index, None, None, status)
                _CheckStatus(status)
                warningText = (_char * length)()
                _GetWarningText(self.handle, index, None, warningText, status)
                _CheckStatus(status)
                yield warningText.value

        return tuple(generator())

    def EvaluateWaveFrequencySpectrum(self, f):
        f = _prepareArray(f)
        N = len(f)
        S = _allocateArray(N)
        status = ctypes.c_int()
        _EvaluateWaveFrequencySpectrum(self.handle, N, f, S, status)
        _CheckStatus(status)
        return _finaliseArray(S)

    @property
    def waveComponents(self):

        def generator():
            count = ctypes.c_int()
            status = ctypes.c_int()

            _GetWaveComponents2(self.handle, count, None, status)
            _CheckStatus(status)

            components = (WaveComponent * count.value)()
            _GetWaveComponents2(self.handle, count, components, status)
            _CheckStatus(status)

            for component in components:
                obj = component.asObject()
                obj.Period = 1 / obj.Frequency
                obj.WaveLength = 2 * numpy.pi / obj.WaveNumber
                yield obj

        return tuple(generator())

    @property
    def windComponents(self):

        def generator():
            count = ctypes.c_int()
            status = ctypes.c_int()

            _GetWindComponents(self.handle, count, None, status)
            _CheckStatus(status)

            components = (WindComponent * count.value)()
            _GetWindComponents(self.handle, count, components, status)
            _CheckStatus(status)

            for index in range(count.value):
                yield components[index].asObject()

        return tuple(generator())

    @property
    def frequencyDomainProcessComponents(self):

        def generator():
            count = ctypes.c_int()
            status = ctypes.c_int()

            if _GetFrequencyDomainProcessComponents2Available:
                GetFrequencyDomainProcessComponents = _GetFrequencyDomainProcessComponents2
            else:
                GetFrequencyDomainProcessComponents = _GetFrequencyDomainProcessComponents

            GetFrequencyDomainProcessComponents(self.handle, count, None, status)
            _CheckStatus(status)
            components = (FrequencyDomainProcessComponent * count.value)()
            GetFrequencyDomainProcessComponents(self.handle, count, components, status)
            _CheckStatus(status)

            for index in range(count.value):
                yield components[index].asObject()

        return tuple(generator())

    def DefaultInMemoryLogging(self):
        status = ctypes.c_int()
        _DefaultInMemoryLogging(self.handle, status)
        _CheckStatus(status)

    def DisableInMemoryLogging(self):
        status = ctypes.c_int()
        _DisableInMemoryLogging(self.handle, status)
        _CheckStatus(status)

    def ForceInMemoryLogging(self):
        status = ctypes.c_int()
        _ForceInMemoryLogging(self.handle, status)
        _CheckStatus(status)

    def UseVirtualLogging(self):
        status = ctypes.c_int()
        _UseVirtualLogging(self.handle, status)
        _CheckStatus(status)

    def CalculateStatics(self):
        status = ctypes.c_int()
        _CalculateStatics(self.handle, self._staticsProgressHandler(), status)
        _CheckStatus(status)

    def RunSimulation(
            self,
            enableAutoSave=False,
            autoSaveIntervalMinutes=DefaultAutoSaveIntervalMinutes,
            autoSaveFileName=None):
        params = RunSimulationParameters(enableAutoSave, autoSaveIntervalMinutes, autoSaveFileName)
        status = ctypes.c_int()
        if self.state <= ModelState.Reset:
            if not self.general.DataNameValid('StaticsEnabled') \
                or HelperMethods.GetDataBoolean(self.general.handle, 'StaticsEnabled', 0):
                self.CalculateStatics()
        _RunSimulation2(self.handle, self._dynamicsProgressHandler(), params, status)
        _CheckStatus(status)

    def ProcessBatchScript(
            self,
            filename,
            enableAutoSave=False,
            autoSaveIntervalMinutes=DefaultAutoSaveIntervalMinutes,
            autoSaveFileName=None):
        filename = _PrepareString(filename)
        params = RunSimulationParameters(enableAutoSave, autoSaveIntervalMinutes, autoSaveFileName)
        status = ctypes.c_int()
        _ProcessBatchScript(
            self.handle,
            filename,
            self._batchProgressHandler(),
            self._staticsProgressHandler(),
            self._dynamicsProgressHandler(),
            params,
            status
        )
        _CheckStatus(status)

    def ExtendSimulation(self, time):
        status = ctypes.c_int()
        _ExtendSimulation(self.handle, time, status)
        _CheckStatus(status)

    def PauseSimulation(self):
        if self.state == ModelState.RunningSimulation:
            status = ctypes.c_int()
            _PauseSimulation(self.handle, status)
            _CheckStatus(status)

    def InvokeLineSetupWizard(self):
        status = ctypes.c_int()
        _InvokeLineSetupWizard(self.handle, self._staticsProgressHandler(), status)
        _CheckStatus(status)

    def UseCalculatedPositions(self, SetLinesToUserSpecifiedStartingShape=False):
        params = UseCalculatedPositionsForStaticsParameters()
        params.SetLinesToUserSpecifiedStartingShape = SetLinesToUserSpecifiedStartingShape
        status = ctypes.c_int()
        _UseCalculatedPositionsForStatics(self.handle, params, status)
        _CheckStatus(status)

    def UseStaticLineEndOrientations(self):
        status = ctypes.c_int()
        _UseStaticLineEndOrientations(self.handle, status)
        _CheckStatus(status)

    @property
    def defaultViewParameters(self):
        result = ViewParameters()
        status = ctypes.c_int()
        _GetDefaultViewParameters(self.handle, result, status)
        _CheckStatus(status)
        return result

    def SaveModelView(self, filename, viewParameters=None):
        filename = _PrepareString(filename)
        status = ctypes.c_int()
        _SaveModel3DViewBitmapToFile(self.handle, viewParameters, filename, status)
        _CheckStatus(status)

    def SaveModelViewMem(self, viewParameters=None):
        status = ctypes.c_int()
        buffer = Handle()
        bufferLen = ctypes.c_int64()
        _SaveModel3DViewBitmapMem(self.handle, viewParameters, buffer, bufferLen, status)
        _CheckStatus(status)
        return HelperMethods.CopyAndFreeBuffer(buffer, bufferLen.value)

    @property
    def simulationDrawTime(self):
        status = ctypes.c_int()
        result = _GetSimulationDrawTime(self.handle, status)
        _CheckStatus(status)
        return result

    @simulationDrawTime.setter
    def simulationDrawTime(self, value):
        status = ctypes.c_int()
        _SetSimulationDrawTime(self.handle, value, status)
        _CheckStatus(status)

    def SaveWaveSearchSpreadsheet(self, filename):
        HelperMethods.SaveSpreadsheet(self.handle, sptWaveSearch, filename, None)

    def SaveWaveSearchSpreadsheetMem(self, spreadsheetFileType=SpreadsheetFileType.Xlsx):
        return HelperMethods.SaveSpreadsheetMem(self.handle, sptWaveSearch, spreadsheetFileType, None)

    def SaveLineTypesPropertiesSpreadsheet(self, filename):
        HelperMethods.SaveSpreadsheet(self.handle, sptLineTypesPropertiesReport, filename, None)

    def SaveLineTypesPropertiesSpreadsheetMem(self, spreadsheetFileType=SpreadsheetFileType.Xlsx):
        return HelperMethods.SaveSpreadsheetMem(self.handle, sptLineTypesPropertiesReport, spreadsheetFileType, None)

    def SaveCodeChecksProperties(self, filename):
        HelperMethods.SaveSpreadsheet(self.handle, sptCodeChecksProperties, filename, None)

    def SaveCodeChecksPropertiesMem(self, spreadsheetFileType=SpreadsheetFileType.Xlsx):
        return HelperMethods.SaveSpreadsheetMem(self.handle, sptCodeChecksProperties, spreadsheetFileType, None)

    def SampleCount(self, period=None):
        return HelperMethods.SampleCount(self.handle, period)

    def SampleTimes(self, period=None):
        return HelperMethods.SampleTimes(self.handle, period)

    def ExecutePostCalculationActions(self, filename, actionType, treatExecutionErrorsAsWarnings=False):
        filename = _PrepareString(filename)
        status = ctypes.c_int()
        _ExecutePostCalculationActions(
            self.handle,
            filename,
            self._postCalculationActionProgressHandler(),
            actionType,
            treatExecutionErrorsAsWarnings,
            status
        )
        _CheckStatus(status)

    def ReportActionProgress(self, progress):
        if _ReportActionProgressAvailable:
            progress = _PrepareString(progress)
            status = ctypes.c_int()
            _ReportActionProgressW(self.handle, progress, status)
            _CheckStatus(status)

    def SaveSummaryResults(self, filename, abbreviated=True):
        spreadsheetType = sptSummaryResults if abbreviated else sptFullResults
        HelperMethods.SaveSpreadsheet(self.handle, spreadsheetType, filename, None)

    def SaveSummaryResultsMem(self, spreadsheetFileType=SpreadsheetFileType.Xlsx, abbreviated=True):
        spreadsheetType = sptSummaryResults if abbreviated else sptFullResults
        return HelperMethods.SaveSpreadsheetMem(self.handle, spreadsheetType, spreadsheetFileType, None)

    # deprecated, use SaveSummaryResults(filename, False) instead
    def SaveFullResults(self, filename):
        HelperMethods.SaveSpreadsheet(self.handle, sptFullResults, filename, None)

    def FrequencyDomainResultsFromProcess(self, process):
        status = ctypes.c_int()
        result = FrequencyDomainResults()
        process, length = HelperMethods.PrepareProcess(process)
        _GetFrequencyDomainResultsFromProcess(self.handle, length, process, result, status)
        _CheckStatus(status)
        return result.asObject()

    def FrequencyDomainSpectralDensityFromProcess(self, process):
        status = ctypes.c_int()
        pointCount = ctypes.c_int()
        process, length = HelperMethods.PrepareProcess(process)
        _GetFrequencyDomainSpectralDensityGraphFromProcess(
            self.handle, length, None, pointCount, None, status)
        _CheckStatus(status)
        curve = _GraphCurve(pointCount.value)
        _GetFrequencyDomainSpectralDensityGraphFromProcess(
            self.handle, length, process, pointCount, curve, status)
        _CheckStatus(status)
        return GraphCurve(*curve.data)

    def FrequencyDomainSpectralResponseRAOFromProcess(self, process):
        status = ctypes.c_int()
        pointCount = ctypes.c_int()
        process, length = HelperMethods.PrepareProcess(process)
        _GetFrequencyDomainSpectralResponseGraphFromProcess(
            self.handle, length, None, pointCount, None, status)
        _CheckStatus(status)
        curve = _GraphCurve(pointCount.value)
        _GetFrequencyDomainSpectralResponseGraphFromProcess(
            self.handle, length, process, pointCount, curve, status)
        _CheckStatus(status)
        return GraphCurve(*curve.data)

    def FrequencyDomainTimeHistorySampleCount(self, period, sampleInterval=None):
        return HelperMethods.FrequencyDomainSampleCount(self.handle, period, sampleInterval)

    def FrequencyDomainTimeHistorySampleTimes(self, period, sampleInterval=None):
        return HelperMethods.FrequencyDomainSampleTimes(self.handle, period, sampleInterval)

    def FrequencyDomainTimeHistoryFromProcess(self, process, period, sampleInterval=None):
        return HelperMethods.FrequencyDomainTimeHistoryFromProcess(self.handle, process, period, sampleInterval)

    # Unsupported, undocumented, internal function, do not call it
    def ImportVesselTypeData(
        self,
        filename,
        fileType,
        mappings,
        calculationMethods=None,
        destVesselType='',
        multibodyGroup='',
        requestedData=(),
        clearExistingData=False
    ):
        try:
            bodyCount = len(mappings)
        except TypeError:
            bodyCount = 1
            mappings = [mappings]
        multibodyGroup = _PrepareString(multibodyGroup)
        specification = VesselTypeDataImportSpecification(
            fileType, bodyCount, multibodyGroup, requestedData, calculationMethods, clearExistingData)

        def prepareGenericBodyMap(destVesselType, count, mappings):
            bodyMap = VesselTypeDataGenericImportBodyMapSpecification(destVesselType, count)
            for i, map in enumerate(mappings):
                bodyMap.BodyMapList[i] = map
            return bodyMap

        def prepareDiffractionBodyMap(fileType, count, mappings):
            bodyMap = (VesselTypeDataDiffractionImportBodyMap * count)()

            def OrcaWaveBodyName(OrcaWave):
                for i in range(OrcaWave.NumberOfBodies):
                    if HelperMethods.GetDataBoolean(OrcaWave.handle, 'BodyIncludedInAnalysis', i + 1): # convert to 1-based index
                        yield OrcaWave.BodyName[i]

            if fileType == iftOrcaWave:
                OrcaWave = Diffraction()
                OrcaWave.LoadData(filename)
                getBodyName = OrcaWaveBodyName(OrcaWave)

            for i, map in enumerate(mappings):
                bodyMap[i] = map
                if fileType == iftAQWA:
                    bodyMap[i].Source = 'Structure {0}'.format(i + 1)
                elif fileType == iftWAMIT:
                    bodyMap[i].Source = 'Body number {0}'.format(i + 1)
                elif fileType == iftOrcaWave:
                    bodyMap[i].Source = next(getBodyName)
            return bodyMap

        if fileType == iftGeneric:
            bodyMap = prepareGenericBodyMap(destVesselType, bodyCount, mappings)
        elif fileType in [iftAQWA, iftWAMIT, iftOrcaWave]:
            bodyMap = prepareDiffractionBodyMap(fileType, bodyCount, mappings)
        else:
            raise TypeError('invalid dataType: ', fileType)
        messages = ctypes.c_void_p()
        filename = _PrepareString(filename)
        status = ctypes.c_int()
        _ImportVesselTypeDataW(
            self.handle,
            filename,
            specification,
            ctypes.byref(bodyMap),
            messages,
            status
        )

        def decode(messages):
            # have to perform manual marshalling because memory is allocated in DLL
            # and not by ctypes
            bufferLength = ctypes.cdll.msvcrt.wcslen(messages) + 1
            buffer = (_char * bufferLength)()
            ctypes.cdll.msvcrt.wcsncpy(ctypes.byref(buffer), messages, bufferLength)
            return _DecodeString(buffer.value)
        if status.value == stVesselTypeDataImportFailed:
            result = False, decode(messages)
        else:
            _CheckStatus(status)
            result = True, decode(messages)
        _SysFreeString(messages.value)
        return result


class DataObject(object):

    def __init__(self, handle):
        self.handle = handle

    def __hash__(self):
        return hash(self.handle.value)

    def __eq__(self, other):
        if not isinstance(other, DataObject):
            return NotImplemented
        return self.handle.value == other.handle.value

    def isBuiltInAttribute(self, name):
        return name in ('handle', 'status', '_tags')

    def __getattr__(self, name):
        if self.isBuiltInAttribute(name):
            return object.__getattr__(self, name)
        elif self.DataNameValid(name):
            if self.DataNameRequiresIndex(name):
                return IndexedDataItem(name, self)
            else:
                return self.GetData(name, -1)
        else:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if self.isBuiltInAttribute(name):
            object.__setattr__(self, name, value)
        elif self.DataNameValid(name):
            if self.DataNameRequiresIndex(name):
                IndexedDataItem(name, self).Assign(value)
            else:
                self.SetData(name, -1, value)
        else:
            raise AttributeError(name)

    def DataType(self, dataName):
        dataName = _PrepareString(dataName)
        status = ctypes.c_int()
        result = ctypes.c_int()
        _GetDataType(self.handle, dataName, result, status)
        _CheckStatus(status)
        return result.value

    def VariableDataType(self, dataName, index):
        index = int(index) + 1  # Python is 0-based, OrcFxAPI is 1-based
        dataName = _PrepareString(dataName)
        status = ctypes.c_int()
        result = ctypes.c_int()
        _GetVariableDataType(self.handle, dataName, index, result, status)
        _CheckStatus(status)
        return result.value

    def DataNameValid(self, dataName):
        return HelperMethods.DataNameValid(self.handle, dataName)

    def DataNameRequiresIndex(self, dataName):
        return self.GetDataRowCount(dataName) != -1

    def IsDefault(self, dataName, index):
        return HelperMethods.PerformDataActionGetBool(self.handle, dataName, index, daIsDefault)

    def HasChanged(self, dataName, index):
        return HelperMethods.PerformDataActionGetBool(self.handle, dataName, index, daHasChanged)

    def IsMarkedAsChanged(self, dataName, index):
        return HelperMethods.PerformDataActionGetBool(self.handle, dataName, index, daIsMarkedAsChanged)

    def SetToDefault(self, dataName, index):
        HelperMethods.PerformDataAction(self.handle, dataName, index, daSetToDefault)

    def SetToOriginalValue(self, dataName, index):
        HelperMethods.PerformDataAction(self.handle, dataName, index, daSetToOriginalValue)

    def MarkAsChanged(self, dataName, index, value):
        HelperMethods.PerformDataActionSetBool(self.handle, dataName, index, daMarkAsChanged, value)

    def GetDataRowCount(self, indexedDataName):
        rowCount = ctypes.c_int()
        indexedDataName = _PrepareString(indexedDataName)
        status = ctypes.c_int()
        _GetDataRowCount(self.handle, indexedDataName, rowCount, status)
        _CheckStatus(status)
        return rowCount.value

    def SetDataRowCount(self, indexedDataName, rowCount):
        indexedDataName = _PrepareString(indexedDataName)
        status = ctypes.c_int()
        _SetDataRowCount(self.handle, indexedDataName, rowCount, status)
        _CheckStatus(status)

    def InsertDataRow(self, indexedDataName, index):
        index = int(index) + 1  # Python is 0-based, OrcFxAPI is 1-based
        indexedDataName = _PrepareString(indexedDataName)
        status = ctypes.c_int()
        _InsertDataRow(self.handle, indexedDataName, index, status)
        _CheckStatus(status)

    def DeleteDataRow(self, indexedDataName, index):
        index = int(index) + 1  # Python is 0-based, OrcFxAPI is 1-based
        indexedDataName = _PrepareString(indexedDataName)
        status = ctypes.c_int()
        _DeleteDataRow(self.handle, indexedDataName, index, status)
        _CheckStatus(status)

    def dataChange(self):

        class dataChangeContext(object):

            def __init__(self, obj):
                self.obj = obj

            def __enter__(self):
                if _BeginEndDataChangeAvailable:
                    status = ctypes.c_int()
                    _BeginDataChange(self.obj.handle, status)
                    _CheckStatus(status)

            def __exit__(self, type, value, traceback):
                if _BeginEndDataChangeAvailable:
                    status = ctypes.c_int()
                    _EndDataChange(self.obj.handle, status)
                    _CheckStatus(status)

        return dataChangeContext(self)

    def GetData(self, dataNames, index):

        def GetSingleDataItem(dataName, index):
            index = int(index) + 1  # Python is 0-based, OrcFxAPI is 1-based
            dataType = ctypes.c_int()
            dataName = _PrepareString(dataName)
            status = ctypes.c_int()
            _GetDataType(self.handle, dataName, dataType, status)
            _CheckStatus(status)
            if dataType.value == dtVariable:
                _GetVariableDataType(self.handle, dataName, index, dataType, status)
                if status.value == stValueNotAvailable:
                    return None
                _CheckStatus(status)
            if dataType.value == dtDouble:
                return HelperMethods.GetDataDouble(self.handle, dataName, index)
            elif dataType.value == dtInteger:
                return HelperMethods.GetDataInteger(self.handle, dataName, index)
            elif dataType.value == dtIntegerIndex:
                result = HelperMethods.GetDataInteger(self.handle, dataName, index)
                if result is None:
                    return None
                return result - 1  # Python is 0-based, OrcFxAPI is 1-based
            elif dataType.value == dtString:
                return HelperMethods.GetDataString(self.handle, dataName, index)
            elif dataType.value == dtBoolean:
                result = HelperMethods.GetDataInteger(self.handle, dataName, index)
                if result is None:
                    return None
                return result != 0
            else:
                raise DLLError(stUnexpectedError, 'Unrecognised data type')

        if isinstance(dataNames, str if _isPy3k else basestring):
            return GetSingleDataItem(dataNames, index)
        else:
            return [GetSingleDataItem(dataName, index) for dataName in dataNames]

    def SetData(self, dataNames, index, values):

        def SetSingleDataItem(dataName, index, value):
            dataName = _PrepareString(dataName)
            index = int(index) + 1  # Python is 0-based, OrcFxAPI is 1-based
            dataType = ctypes.c_int()
            status = ctypes.c_int()
            _GetDataType(self.handle, dataName, dataType, status)
            _CheckStatus(status)
            if dataType.value == dtVariable:
                try:
                    float(value)
                    dataType.value = dtDouble
                except BaseException:
                    dataType.value = dtString
            if dataType.value == dtDouble:
                _SetDataDouble(self.handle, dataName, index, ctypes.c_double(value), status)
                _CheckStatus(status)
            elif dataType.value == dtInteger:
                _SetDataInteger(self.handle, dataName, index, ctypes.c_int(value), status)
                _CheckStatus(status)
            elif dataType.value == dtIntegerIndex:
                # Python is 0-based, OrcFxAPI is 1-based:
                _SetDataInteger(self.handle, dataName, index, ctypes.c_int(value + 1), status)
                _CheckStatus(status)
            elif dataType.value == dtString:
                value = _PrepareString(value)
                _SetDataString(self.handle, dataName, index, value, status)
                _CheckStatus(status)
            elif dataType.value == dtBoolean:
                _SetDataInteger(self.handle, dataName, index, ctypes.c_int(value), status)
                _CheckStatus(status)
            else:
                raise DLLError(stUnexpectedError, 'Unrecognised data type')

        if isinstance(dataNames, str if _isPy3k else basestring):
            SetSingleDataItem(dataNames, index, values)
        else:
            [SetSingleDataItem(dataName, index, value)
             for dataName, value in zip(dataNames, values)]

    def UnitsConversionFactor(self, units):
        status = ctypes.c_int()
        result = ctypes.c_double()
        _GetUnitsConversionFactor(self.handle, units, result, status)
        _CheckStatus(status)
        return result.value

    @property
    def tags(self):
        result = getattr(self, '_tags', None)
        if result is None:
            # deal with scenarios where tags are not available without throwing exceptions at the consumer
            if not ImportedFunctionAvailable(_GetTagCount):
                return None
            status = ctypes.c_int()
            _GetTagCount(self.handle, status)
            if status.value == stInvalidObjectType:
                return None
            _CheckStatus(status)

            result = Tags(self.handle)
            self._tags = result
        return result


class OrcaFlexObject(DataObject):

    def __init__(self, modelHandle, handle, type):
        DataObject.__init__(self, handle)
        self.modelHandle = modelHandle
        self.type = type

    def isBuiltInAttribute(self, name):
        return name in ('modelHandle', 'type', 'groupParent') \
            or DataObject.isBuiltInAttribute(self, name)

    def __str__(self):
        return u"<{0!s}: '{1!s}'>".format(self.typeName, self.name)

    def CreateClone(self, name=None, model=None):
        handle = Handle()
        status = ctypes.c_int()
        if model is None:
            modelHandle = self.modelHandle
            _CreateClone(self.handle, handle, status)
            _CheckStatus(status)
            clone = HelperMethods.CreateOrcaFlexObject(self.modelHandle, handle, self.type)
        else:
            modelHandle = model.handle
            _CreateClone2(self.handle, modelHandle, handle, status)
            _CheckStatus(status)
        clone = HelperMethods.CreateOrcaFlexObject(modelHandle, handle, self.type)
        if name is not None:
            clone.name = name
        return clone

    @property
    def typeName(self):
        status = ctypes.c_int()
        length = _GetObjectTypeName(self.modelHandle, self.type, None, status)
        _CheckStatus(status)
        name = (_char * length)()
        _GetObjectTypeName(self.modelHandle, self.type, name, status)
        _CheckStatus(status)
        return _DecodeString(name.value)

    @property
    def groupFirstChild(self):
        handle = Handle()
        status = ctypes.c_int()
        _GroupGetFirstChild(self.handle, handle, status)
        _CheckStatus(status)
        if handle:
            return HelperMethods.CreateOrcaFlexObject(self.modelHandle, handle)
        else:
            return None

    @property
    def groupParent(self):
        handle = Handle()
        status = ctypes.c_int()
        _GroupGetParent(self.handle, handle, status)
        _CheckStatus(status)
        if handle:
            return HelperMethods.CreateOrcaFlexObject(self.modelHandle, handle)
        else:
            return None

    @groupParent.setter
    def groupParent(self, value):
        status = ctypes.c_int()
        if value is None:
            parentHandle = None
        else:
            parentHandle = value.handle
        _GroupSetParent(self.handle, parentHandle, status)
        _CheckStatus(status)

    @property
    def groupNextSibling(self):
        handle = Handle()
        status = ctypes.c_int()
        _GroupGetNextSibling(self.handle, handle, status)
        _CheckStatus(status)
        if handle:
            return HelperMethods.CreateOrcaFlexObject(self.modelHandle, handle)
        else:
            return None

    @property
    def groupPrevSibling(self):
        handle = Handle()
        status = ctypes.c_int()
        _GroupGetPrevSibling(self.handle, handle, status)
        _CheckStatus(status)
        if handle:
            return HelperMethods.CreateOrcaFlexObject(self.modelHandle, handle)
        else:
            return None

    def GroupChildren(self, recurse=True):
        child = self.groupFirstChild
        while child is not None:
            yield child
            if recurse:
                for obj in child.GroupChildren(True):
                    yield obj
            child = child.groupNextSibling

    def GroupMoveAfter(self, target):
        status = ctypes.c_int()
        _GroupMoveAfter(self.handle, target.handle, status)
        _CheckStatus(status)

    def GroupMoveBefore(self, target):
        status = ctypes.c_int()
        _GroupMoveBefore(self.handle, target.handle, status)
        _CheckStatus(status)

    def AssignWireFrameFromPanelMesh(
            self,
            filename,
            format,
            symmetry,
            importOrigin=None,
            wireFrameType=wftPanels,
            scale=1,
            bodyNumber=1,
            importDryPanels=True):
        with HelperMethods.PanelMeshImporter(filename, format, scale, bodyNumber, importDryPanels) as importer:
            status = ctypes.c_int()
            if importOrigin is None:
                importOrigin = (0,) * 3
            importOrigin = (ctypes.c_double * 3)(*importOrigin)
            _AssignWireFrameFromPanelMesh(self.handle, importer.handle, symmetry | (wireFrameType << 3), importOrigin, status)
            _CheckStatus(status)

    def SampleCount(self, period=None):
        return HelperMethods.SampleCount(self.modelHandle, period)

    def SampleTimes(self, period=None):
        return HelperMethods.SampleTimes(self.modelHandle, period)

    def varID(self, varName):
        varName = _PrepareString(varName)
        varID = ctypes.c_int()
        status = ctypes.c_int()
        _GetVarID(self.handle, varName, varID, status)
        _CheckStatus(status)
        return varID.value

    def varDetails(self, resultType=rtTimeHistory, objectExtra=None):
        result = []

        def callback(varInfo):
            result.append(
                objectFromDict({
                    'VarName': varInfo[0].VarName,
                    'VarUnits': varInfo[0].VarUnits,
                    'FullName': varInfo[0].FullName
                })
            )
        varCount = ctypes.c_int()
        status = ctypes.c_int()
        _EnumerateVars2(
            self.handle,
            objectExtra,
            resultType,
            _EnumerateVarsProc(callback),
            varCount,
            status
        )
        _CheckStatus(status)
        return tuple(result)

    def vars(self, resultType=rtTimeHistory, objectExtra=None):
        result = []

        def callback(varInfo):
            result.append(varInfo[0].VarName)
        varCount = ctypes.c_int()
        status = ctypes.c_int()
        _EnumerateVars2(
            self.handle,
            objectExtra,
            resultType,
            _EnumerateVarsProc(callback),
            varCount,
            status
        )
        _CheckStatus(status)
        return tuple(result)

    def ObjectExtraFieldRequired(self, varName, field):
        varID = self.varID(varName)
        required = ctypes.wintypes.BOOL()
        status = ctypes.c_int()
        _GetObjectExtraFieldRequired(self.handle, varID, field, required, status)
        _CheckStatus(status)
        return bool(required)

    def RequiredObjectExtraFields(self, varName):
        varID = self.varID(varName)
        fields = ctypes.c_int()
        status = ctypes.c_int()
        _GetRequiredObjectExtraFields(self.handle, varID, fields, status)
        _CheckStatus(status)
        return [i for i in range(32) if fields.value & 1 << i]

    def LineResultPoints(self, varName):
        varID = self.varID(varName)
        result = ctypes.c_int()
        status = ctypes.c_int()
        _GetLineResultPoints(self.handle, varID, result, status)
        _CheckStatus(status)
        return result.value

    def TimeHistory(self, varNames, period=None, objectExtra=None):

        def getTimeHistory(varName, period, objectExtra):
            if isFrequencyDomainResult:
                return HelperMethods.FrequencyDomainTimeHistory(
                    self.modelHandle, self.handle, self.varID(varName), period, objectExtra, None)
            else:
                return HelperMethods.TimeDomainTimeHistory(
                    self.modelHandle, self.handle, self.varID(varName), period, objectExtra)

        period = HelperMethods.PreparePeriod(self.modelHandle, period)
        isFrequencyDomainResult = HelperMethods.IsFrequencyDomainResult(self.modelHandle, period)
        if isinstance(varNames, str if _isPy3k else basestring):
            return getTimeHistory(varNames, period, objectExtra)
        elif isFrequencyDomainResult or not ImportedFunctionAvailable(_GetMultipleTimeHistories):
            hist = []
            for varName in varNames:
                hist.append(getTimeHistory(varName, period, objectExtra))
            return numpy.column_stack(hist)
        else:
            spec = [TimeHistorySpecification(self, varName, objectExtra) for varName in varNames]
            return GetMultipleTimeHistories(spec, period)

    def StaticResult(self, varNames, objectExtra=None):
        return self.TimeHistory(varNames, Period(pnStaticState), objectExtra)[0]

    def LinkedStatistics(self, varNames, period=None, objectExtra=None):
        return LinkedStatistics(self, varNames, period, objectExtra)

    def TimeSeriesStatistics(self, varName, period=None, objectExtra=None):
        return TimeSeriesStatistics(
            self.TimeHistory(varName, period, objectExtra),
            HelperMethods.ActualLogSampleInterval(self.modelHandle)
        )

    def ExtremeStatistics(self, varName, period=None, objectExtra=None):
        values = self.TimeHistory(varName, period, objectExtra)
        sampleInterval = HelperMethods.ActualLogSampleInterval(self.modelHandle)
        return ExtremeStatistics(values, sampleInterval)

    def FrequencyDomainResults(self, varName, objectExtra=None):
        return HelperMethods.FrequencyDomainResults(self.handle, self.varID(varName), objectExtra)

    def FrequencyDomainResultsProcess(self, varName, objectExtra=None):
        return HelperMethods.FrequencyDomainResultsProcess(self.handle, self.varID(varName), objectExtra)

    def FrequencyDomainMPM(self, varName, stormDurationHours, objectExtra=None):
        fdr = self.FrequencyDomainResults(varName, objectExtra)
        return FrequencyDomainMPM(stormDurationHours * 3600.0, fdr.StdDev, fdr.Tz)

    def AnalyseExtrema(self, varName, period=None, objectExtra=None):
        return AnalyseExtrema(
            self.TimeHistory(varName, period, objectExtra)
        )

    def SpectralResponseRAO(self, varName, objectExtra=None):
        varID = self.varID(varName)
        NumOfGraphPoints = ctypes.c_int()
        status = ctypes.c_int()
        _GetSpectralResponseGraph(self.handle, objectExtra, varID, NumOfGraphPoints, None, status)
        _CheckStatus(status)
        curve = _GraphCurve(NumOfGraphPoints.value)
        _GetSpectralResponseGraph(self.handle, objectExtra, varID, NumOfGraphPoints, curve, status)
        _CheckStatus(status)
        return GraphCurve(*curve.data)

    def SpectralDensity(self, varName, period=None, objectExtra=None, fundamentalFrequency=None):
        if HelperMethods.IsFrequencyDomainDynamics(self.modelHandle):
            varID = self.varID(varName)
            NumOfGraphPoints = ctypes.c_int()
            status = ctypes.c_int()
            _GetFrequencyDomainSpectralDensityGraph(
                self.handle,
                objectExtra,
                varID,
                NumOfGraphPoints,
                None,
                status
            )
            _CheckStatus(status)

            curve = _GraphCurve(NumOfGraphPoints.value)
            _GetFrequencyDomainSpectralDensityGraph(
                self.handle,
                objectExtra,
                varID,
                NumOfGraphPoints,
                curve,
                status
            )
            _CheckStatus(status)
            return GraphCurve(*curve.data)
        else:
            if fundamentalFrequency is None:
                fundamentalFrequency = HelperMethods.GetSpectralDensityFundamentalFrequency(
                    self.modelHandle)
            return SpectralDensity(
                self.SampleTimes(period),
                self.TimeHistory(varName, period, objectExtra),
                fundamentalFrequency
            )

    def EmpiricalDistribution(self, varName, period=None, objectExtra=None):
        return EmpiricalDistribution(
            self.TimeHistory(varName, period, objectExtra)
        )

    def RainflowHalfCycles(self, varName, period=None, objectExtra=None):
        return RainflowHalfCycles(
            self.TimeHistory(varName, period, objectExtra)
        )

    def UnorderedRainflowHalfCycles(self, varName, period=None, objectExtra=None):
        return UnorderedRainflowHalfCycles(
            self.TimeHistory(varName, period, objectExtra)
        )

    def RainflowAssociatedMean(self, varName, period=None, objectExtra=None):
        return RainflowAssociatedMean(
            self.TimeHistory(varName, period, objectExtra)
        )

    def CycleHistogramBins(self, varName, period=None, objectExtra=None, binSize=None):
        halfCycles = self.UnorderedRainflowHalfCycles(varName, period, objectExtra)
        return CycleHistogramBins(halfCycles, binSize)

    def SaveSummaryResults(self, filename, abbreviated=True):
        spreadsheetType = sptSummaryResults if abbreviated else sptFullResults
        HelperMethods.SaveSpreadsheet(self.handle, spreadsheetType, filename, None)

    def SaveSummaryResultsMem(self, spreadsheetFileType=SpreadsheetFileType.Xlsx, abbreviated=True):
        spreadsheetType = sptSummaryResults if abbreviated else sptFullResults
        return HelperMethods.SaveSpreadsheetMem(self.handle, spreadsheetType, spreadsheetFileType, None)

    # deprecated, use SaveSummaryResults(filename, False) instead
    def SaveFullResults(self, filename):
        HelperMethods.SaveSpreadsheet(self.handle, sptFullResults, filename, None)

    def SaveDetailedPropertiesReport(self, filename):
        HelperMethods.SaveSpreadsheet(self.handle, sptDetailedProperties, filename, None)

    def SaveDetailedPropertiesReportMem(self, spreadsheetFileType=SpreadsheetFileType.Xlsx):
        return HelperMethods.SaveSpreadsheetMem(self.handle, sptDetailedProperties, spreadsheetFileType, None)


class OrcaFlexRangeGraphObject(OrcaFlexObject):

    def RangeGraphXaxis(self, varName, arclengthRange=None, period=None):
        varID = self.varID(varName)

        if period is None and HelperMethods.IsFrequencyDomainDynamics(self.modelHandle):
            period = Period(pnStaticState)  # so that it doesn't default to whole simulation
        else:
            period = HelperMethods.PreparePeriod(self.modelHandle, period)

        pointCount = HelperMethods.RangeGraphPointCount(self.handle, self.type, varID, arclengthRange, period)
        x = _allocateArray(pointCount)

        objectExtra = oeTurbine(1)  # we need a valid blade index for turbines
        status = ctypes.c_int()
        if arclengthRange is None:  # support 9.1 and earlier
            _GetRangeGraph3(
                self.handle,
                objectExtra,
                period,
                varID,
                x,
                None,
                None,
                None,
                None,
                None,
                None,
                status
            )
        else:
            _GetRangeGraph4(
                self.handle,
                objectExtra,
                period,
                arclengthRange,
                varID,
                x,
                None,
                None,
                None,
                None,
                None,
                None,
                status
            )
        _CheckStatus(status)
        return _finaliseArray(x)

    def RangeGraph(self, varName, period=None, objectExtra=None, arclengthRange=None, stormDurationHours=None):

        def allocIfCurveAvailable(curveName, pointCount):
            if hasattr(curveNames, curveName):
                return _allocateArray(pointCount)
            else:
                return None

        def returnArray(x):
            if x is None:
                return None
            else:
                return _finaliseArray(x)

        def frequencyDomainRangeGraph(period, objectExtra, arclengthRange, stormDurationHours):
            def objectExtraAtArclength(X):
                if objectExtra is None:
                    result = oeArcLength(X)
                else:
                    result = ObjectExtra()
                    # clone objectExtra, see http://stackoverflow.com/q/1470343/
                    ctypes.pointer(result)[0] = objectExtra
                    result.LinePoint = ptArcLength
                    result.ArcLength = X
                return result

            staticStateRangeGraph = self.RangeGraph(
                varName, pnStaticState, objectExtra, arclengthRange)
            fdr = [HelperMethods.FrequencyDomainResults(self.handle, varID, objectExtraAtArclength(X))
                   for X in staticStateRangeGraph.X]
            resultDict = {
                'X': staticStateRangeGraph.X,
                'StaticValue': staticStateRangeGraph.Mean,
                'StdDev': _array([item.StdDev for item in fdr]),
                'Upper': staticStateRangeGraph.Upper,
                'Lower': staticStateRangeGraph.Lower
            }
            if stormDurationHours is not None:
                resultDict['MPM'] = _array(
                    [FrequencyDomainMPM(stormDurationHours * 3600.0, item.StdDev, item.Tz) for item in fdr])
            return objectFromDict(resultDict)

        varID = self.varID(varName)
        period = HelperMethods.PreparePeriod(self.modelHandle, period)
        if HelperMethods.IsFrequencyDomainDynamics(self.modelHandle) and period.PeriodNum == pnWholeSimulation:
            return frequencyDomainRangeGraph(period, objectExtra, arclengthRange, stormDurationHours)

        curveNames = RangeGraphCurveNames()
        status = ctypes.c_int()
        _GetRangeGraphCurveNames(self.handle, objectExtra, period, varID, curveNames, status)
        _CheckStatus(status)

        pointCount = HelperMethods.RangeGraphPointCount(self.handle, self.type, varID, arclengthRange, period)
        x = _allocateArray(pointCount)
        min = allocIfCurveAvailable('Min', pointCount)
        max = allocIfCurveAvailable('Max', pointCount)
        mean = allocIfCurveAvailable('Mean', pointCount)
        stddev = allocIfCurveAvailable('StdDev', pointCount)
        upper = allocIfCurveAvailable('Upper', pointCount)
        lower = allocIfCurveAvailable('Lower', pointCount)
        if arclengthRange is None:  # support 9.1 and earlier
            _GetRangeGraph3(
                self.handle,
                objectExtra,
                period,
                varID,
                x,
                min,
                max,
                mean,
                stddev,
                upper,
                lower,
                status
            )
        else:
            _GetRangeGraph4(
                self.handle,
                objectExtra,
                period,
                arclengthRange,
                varID,
                x,
                min,
                max,
                mean,
                stddev,
                upper,
                lower,
                status
            )
        _CheckStatus(status)

        return objectFromDict({
            'X': returnArray(x),
            'Min': returnArray(min),
            'Max': returnArray(max),
            'Mean': returnArray(mean),
            'StdDev': returnArray(stddev),
            'Upper': returnArray(upper),
            'Lower': returnArray(lower)
        })


class OrcaFlexLineObject(OrcaFlexRangeGraphObject):

    def lineTypeAt(self, arclength):
        sectionLength = self.CumulativeLength
        index = 0
        count = len(sectionLength)
        while index < count - 1:
            if arclength <= sectionLength[index]:
                break
            else:
                index += 1
        objectInfo = HelperMethods.ObjectCalled(self.modelHandle, self.LineType[index])
        return HelperMethods.CreateOrcaFlexObject(self.modelHandle, objectInfo.ObjectHandle, objectInfo.ObjectType)

    @property
    def NodeArclengths(self):
        count = ctypes.c_int()
        status = ctypes.c_int()
        _GetNodeArclengths(self.handle, None, count, status)
        _CheckStatus(status)
        arclengths = _allocateArray(count.value)
        _GetNodeArclengths(self.handle, arclengths, None, status)
        _CheckStatus(status)
        return _finaliseArray(arclengths)

    def SaveShear7datFile(self, filename):
        HelperMethods.SaveExternalFile(self.handle, filename, eftShear7dat)

    def SaveShear7mdsFile(self, filename, firstMode=-1, lastMode=-1, includeCoupledObjects=False):
        params = Shear7MdsFileParameters(firstMode, lastMode, includeCoupledObjects)
        HelperMethods.SaveExternalFile(self.handle, filename, eftShear7mds, params)

    def SaveShear7catFile(self, filename):
        HelperMethods.SaveExternalFile(self.handle, filename, eftShear7cat)

    def SaveShear7inhystFile(self, filename):
        HelperMethods.SaveExternalFile(self.handle, filename, eftShear7inhyst)

    def SaveShear7outFile(self, filename):
        HelperMethods.SaveExternalFile(self.handle, filename, eftShear7out)

    def SaveShear7out1File(self, filename):
        HelperMethods.SaveExternalFile(self.handle, filename, eftShear7out1)

    def SaveShear7out2File(self, filename):
        HelperMethods.SaveExternalFile(self.handle, filename, eftShear7out2)

    def SaveShear7pltFile(self, filename):
        HelperMethods.SaveExternalFile(self.handle, filename, eftShear7plt)

    def SaveShear7anmFile(self, filename):
        HelperMethods.SaveExternalFile(self.handle, filename, eftShear7anm)

    def SaveShear7dmgFile(self, filename):
        HelperMethods.SaveExternalFile(self.handle, filename, eftShear7dmg)

    def SaveShear7fatFile(self, filename):
        HelperMethods.SaveExternalFile(self.handle, filename, eftShear7fat)

    def SaveShear7strFile(self, filename):
        HelperMethods.SaveExternalFile(self.handle, filename, eftShear7str)

    def SaveShear7curvFile(self, filename):
        HelperMethods.SaveExternalFile(self.handle, filename, eftShear7curv)

    def SaveShear7zetahystFile(self, filename):
        HelperMethods.SaveExternalFile(self.handle, filename, eftShear7zetahyst)

    def SaveShear7sthFile(self, filename):
        HelperMethods.SaveExternalFile(self.handle, filename, eftShear7sth)

    def SaveShear7allOutputFiles(self, basename):
        HelperMethods.SaveExternalFile(self.handle, basename, eftShear7allOutput)

    def SaveVIVAInputFiles(self, dirname):
        HelperMethods.SaveExternalFile(self.handle, dirname, eftVIVAInput)

    def SaveVIVAOutputFiles(self, basename):
        HelperMethods.SaveExternalFile(self.handle, basename, eftVIVAOutput)

    def SaveVIVAModesFiles(self, dirname, firstMode=-1, lastMode=-1, includeCoupledObjects=False):
        params = VIVAModesFilesParameters(firstMode, lastMode, includeCoupledObjects)
        HelperMethods.SaveExternalFile(self.handle, dirname, eftVIVAModes, params)

    def SaveLineClashingReport(self, filename, period=None):
        parameters = LineClashingReportParameters()
        parameters.Period = HelperMethods.PreparePeriod(self.modelHandle, period)
        HelperMethods.SaveSpreadsheet(self.handle, sptLineClashingReport, filename, parameters)

    def SaveLineClashingReportMem(self, spreadsheetFileType=SpreadsheetFileType.Xlsx, period=None):
        parameters = LineClashingReportParameters()
        parameters.Period = HelperMethods.PreparePeriod(self.modelHandle, period)
        return HelperMethods.SaveSpreadsheetMem(self.handle, sptLineClashingReport, spreadsheetFileType, parameters)


class OrcaFlexVesselObject(OrcaFlexObject):

    def SaveDisplacementRAOsSpreadsheet(self, filename):
        HelperMethods.SaveSpreadsheet(self.handle, sptVesselDisplacementRAOs, filename, None)

    def SaveDisplacementRAOsSpreadsheetMem(self, spreadsheetFileType=SpreadsheetFileType.Xlsx):
        return HelperMethods.SaveSpreadsheetMem(self.handle, sptVesselDisplacementRAOs, spreadsheetFileType, None)

    def SaveSpectralResponseSpreadsheet(self, filename):
        HelperMethods.SaveSpreadsheet(self.handle, sptVesselSpectralResponse, filename, None)

    def SaveSpectralResponseSpreadsheetMem(self, spreadsheetFileType=SpreadsheetFileType.Xlsx):
        return HelperMethods.SaveSpreadsheetMem(self.handle, sptVesselSpectralResponse, spreadsheetFileType, None)

    def SaveSupportGeometryTable(self, filename):
        HelperMethods.SaveSpreadsheet(self.handle, sptSupportGeometryTable, filename, None)

    def SaveSupportGeometryTableMem(self, spreadsheetFileType=SpreadsheetFileType.Xlsx):
        return HelperMethods.SaveSpreadsheetMem(self.handle, sptSupportGeometryTable, spreadsheetFileType, None)

    def SaveAirGapReport(self, filename, period=None):
        parameters = AirGapReportParameters()
        parameters.Period = HelperMethods.PreparePeriod(self.modelHandle, period)
        HelperMethods.SaveSpreadsheet(self.handle, sptAirGapReport, filename, parameters)

    def SaveAirGapReportMem(self, spreadsheetFileType=SpreadsheetFileType.Xlsx, period=None):
        parameters = AirGapReportParameters()
        parameters.Period = HelperMethods.PreparePeriod(self.modelHandle, period)
        return HelperMethods.SaveSpreadsheetMem(self.handle, sptAirGapReport, spreadsheetFileType, parameters)

    @property
    def AirGapPointsSpecifications(self):
        return [
            TimeHistorySpecification(self, 'Air gap', oeAirGap((x, y, z), factor))
            for x, y, z, factor in zip(
                self.AirGapPointX,
                self.AirGapPointY,
                self.AirGapPointZ,
                self.SeaSurfaceScalingFactor
            )
        ]


class OrcaFlex6DBuoyObject(OrcaFlexObject):

    def SaveSupportGeometryTable(self, filename):
        HelperMethods.SaveSpreadsheet(self.handle, sptSupportGeometryTable, filename, None)

    def SaveSupportGeometryTableMem(self, spreadsheetFileType=SpreadsheetFileType.Xlsx):
        return HelperMethods.SaveSpreadsheetMem(self.handle, sptSupportGeometryTable, spreadsheetFileType, None)


class OrcaFlexTurbineObject(OrcaFlexRangeGraphObject):

    @property
    def BladeNodeArclengths(self):
        count = ctypes.c_int()
        status = ctypes.c_int()
        _GetNodeArclengths(self.handle, None, count, status)
        _CheckStatus(status)
        arclengths = _allocateArray(count.value)
        _GetNodeArclengths(self.handle, arclengths, None, status)
        _CheckStatus(status)
        return _finaliseArray(arclengths)


class OrcaFlexWizardObject(OrcaFlexObject):

    def InvokeWizard(self):
        status = ctypes.c_int()
        _InvokeWizard(self.handle, status)
        _CheckStatus(status)


class FatigueAnalysis(DataObject):

    def __init__(self, filename=None, threadCount=None):
        handle = Handle()
        status = ctypes.c_int()
        _CreateFatigue(handle, status)
        _CheckStatus(status)
        DataObject.__init__(self, handle)
        self.progressHandler = None
        if filename:
            self.Load(filename)
        if threadCount is not None:
            self.threadCount = threadCount

    def __del__(self):
        try:
            _DestroyFatigue(self.handle, ctypes.c_int())
            # no point checking status here since we can't really do anything about a failure
        # swallow this since we get exceptions when Python terminates unexpectedly (e.g. CTRL+Z)
        except BaseException:
            pass

    def isBuiltInAttribute(self, name):
        return name in ('progressHandler', 'threadCount', 'latestFileName') \
            or DataObject.isBuiltInAttribute(self, name)

    @property
    def threadCount(self):
        return HelperMethods.GetModelThreadCount(self.handle)

    @threadCount.setter
    def threadCount(self, value):
        HelperMethods.SetModelThreadCount(self.handle, value)

    @property
    def latestFileName(self):
        return HelperMethods.GetDataString(self.handle, 'LatestFileName', 0)

    @latestFileName.setter
    def latestFileName(self, value):
        HelperMethods.SetDataString(self.handle, 'LatestFileName', 0, value)

    def Load(self, filename):
        HelperMethods.FileOperation(self.handle, _LoadFatigue, filename)

    def LoadMem(self, buffer, dataFileType=DataFileType.Binary):
        status = ctypes.c_int()
        _LoadFatigueMem(self.handle, dataFileType.Value, buffer, len(buffer), status)
        _CheckStatus(status)

    def Save(self, filename):
        HelperMethods.FileOperation(self.handle, _SaveFatigue, filename)

    def SaveMem(self, dataFileType=DataFileType.Binary):
        status = ctypes.c_int()
        buffer = Handle()
        bufferLen = ctypes.c_int64()
        _SaveFatigueMem(self.handle, dataFileType.Value, buffer, bufferLen, status)
        _CheckStatus(status)
        return HelperMethods.CopyAndFreeBuffer(buffer, bufferLen.value)

    def Calculate(self, resultsFileName=None):
        if self.progressHandler:
            def callback(handle, progress, cancel):
                cancel[0] = HelperMethods.ProgressCallbackCancel(
                    self.progressHandler(self, progress))
            progress = _StringProgressHandlerProc(callback)
        else:
            progress = None
        resultsFileName = _PrepareString(resultsFileName)
        status = ctypes.c_int()
        _CalculateFatigue(self.handle, resultsFileName, progress, status)
        _CheckStatus(status)

    @property
    def outputPointDetails(self):
        damageCalculation = self.DamageCalculation
        if damageCalculation == 'Homogeneous pipe stress':
            return HelperMethods.FatigueHomogeneousPipeOutputPointDetails(self.handle)
        if damageCalculation == 'Stress factors' or damageCalculation == 'Externally calculated stress':
            return HelperMethods.FatigueComponentOutputPointDetails(self.handle)
        if damageCalculation == 'Mooring':
            return HelperMethods.FatigueMooringOutputPointDetails(self.handle)
        if damageCalculation == 'SHEAR7':
            return HelperMethods.FatigueShear7OutputPointDetails(self.handle)
        if damageCalculation == 'Histograms':
            return HelperMethods.FatigueHistogramOutputPointDetails(self.handle)
        raise NotImplementedError('Unrecognised damage calculation')

    @property
    def theta(self):
        return HelperMethods.FatigueDoubleArray(self.handle, fotTheta)

    @property
    def loadCaseDamage(self):
        damageCalculation = self.DamageCalculation
        if damageCalculation == 'Histograms':
            raise NotImplementedError('Load case damage is not available for histograms')
        if damageCalculation == 'SHEAR7':
            return HelperMethods.FatigueShear7LoadCaseDamage(self.handle)
        analysisType = self.AnalysisType
        if analysisType == 'Regular' or analysisType == 'Rainflow':
            return HelperMethods.FatigueDeterministicLoadCaseDamage(self.handle)
        if analysisType == 'Spectral (frequency domain)' or analysisType == 'Spectral (response RAOs)':
            return HelperMethods.FatigueSpectralLoadCaseDamage(self.handle)
        raise NotImplementedError('Unrecognised combination of damage calculation and analysis type')

    @property
    def overallDamage(self):
        damageCalculation = self.DamageCalculation
        if damageCalculation == 'Histograms':
            raise NotImplementedError('Overall damage is not available for histograms')
        return HelperMethods.FatigueOverallDamage(self.handle)

    @property
    def bins(self):
        return HelperMethods.FatigueDoubleArray(self.handle, fotHistogramBins)

    @property
    def loadCaseCycleRate(self):
        damageCalculation = self.DamageCalculation
        if damageCalculation != 'Histograms':
            raise NotImplementedError('Histogram cycle rate is only available for histograms')
        loadCaseCount = HelperMethods.FatigueLoadCaseCount(self.handle)
        return HelperMethods.FatigueCycleRate(self.handle, fotHistogramLoadCaseCycleRate, loadCaseCount)

    @property
    def combinedCycleRate(self):
        damageCalculation = self.DamageCalculation
        if damageCalculation != 'Histograms':
            raise NotImplementedError('Histogram cycle rate is only available for histograms')
        return HelperMethods.FatigueCycleRate(self.handle, fotHistogramCombinedCycleRate, None)


class WaveScatter(DataObject):

    def __init__(self, filename=None):
        handle = Handle()
        status = ctypes.c_int()
        _CreateWaveScatter(handle, status)
        _CheckStatus(status)
        DataObject.__init__(self, handle)
        if filename:
            self.Load(filename)

    def __del__(self):
        try:
            _DestroyWaveScatter(self.handle, ctypes.c_int())
            # no point checking status here since we can't really do anything about a failure
        # swallow this since we get exceptions when Python terminates unexpectedly (e.g. CTRL+Z)
        except BaseException:
            pass

    def isBuiltInAttribute(self, name):
        return name == 'latestFileName' or DataObject.isBuiltInAttribute(self, name)

    @property
    def latestFileName(self):
        return HelperMethods.GetDataString(self.handle, 'LatestFileName', 0)

    @latestFileName.setter
    def latestFileName(self, value):
        HelperMethods.SetDataString(self.handle, 'LatestFileName', 0, value)

    def Load(self, filename):
        HelperMethods.FileOperation(self.handle, _LoadWaveScatter, filename)

    def LoadMem(self, buffer):
        status = ctypes.c_int()
        _LoadWaveScatterMem(self.handle, DataFileType.Binary.Value, buffer, len(buffer), status)
        _CheckStatus(status)

    def Save(self, filename):
        HelperMethods.FileOperation(self.handle, _SaveWaveScatter, filename)

    def SaveMem(self):
        status = ctypes.c_int()
        buffer = Handle()
        bufferLen = ctypes.c_int64()
        _SaveWaveScatterMem(self.handle, DataFileType.Binary.Value, buffer, bufferLen, status)
        _CheckStatus(status)
        return HelperMethods.CopyAndFreeBuffer(buffer, bufferLen.value)

    @property
    def scatterTable(self):
        status = ctypes.c_int()
        totalProbability = ctypes.c_double()
        TbinCount = self.NumberOfWavePeriods
        HbinCount = self.NumberOfWaveHeights
        if TbinCount is not None and HbinCount is not None:
            Tbins = (WaveScatterBin * TbinCount)()
            Hbins = (WaveScatterBin * HbinCount)()
            occurrences = _allocateArray(HbinCount * TbinCount)
        else:
            # the call to _GetWaveScatterTable will fail, but it does so with an informative error message
            Hbins = None
            Tbins = None
            occurrences = None
        _GetWaveScatterTable(self.handle, Tbins, Hbins, occurrences, totalProbability, status)
        _CheckStatus(status)
        return objectFromDict({
            'Tbins': [bin.asObject() for bin in Tbins],
            'Hbins': [bin.asObject() for bin in Hbins],
            'Occurrences': numpy.reshape(_finaliseArray(occurrences), (HbinCount, TbinCount), 'F'),
            'TotalProbability': totalProbability.value
        })

    def SaveBatchScript(self, filename):
        status = ctypes.c_int()
        spec = WaveScatterAutomationSpecification()
        spec.BatchScriptFileName = _PrepareString(filename)
        _SaveWaveScatterAutomationFiles(self.handle, spec, status)
        _CheckStatus(status)

    def SaveTextDataFiles(self, path):
        status = ctypes.c_int()
        spec = WaveScatterAutomationSpecification()
        spec.TextDataFilePath = _PrepareString(path)
        _SaveWaveScatterAutomationFiles(self.handle, spec, status)
        _CheckStatus(status)

    def SaveFatigueAnalysisFile(self, filename, loadCaseSimulationPath=''):
        status = ctypes.c_int()
        spec = WaveScatterAutomationSpecification()
        spec.FatigueAnalysisFileName = _PrepareString(filename)
        spec.FatigueLoadCaseSimulationPath = _PrepareString(loadCaseSimulationPath)
        _SaveWaveScatterAutomationFiles(self.handle, spec, status)
        _CheckStatus(status)


class Diffraction(DataObject):

    def __init__(self, filename=None, threadCount=None):
        handle = Handle()
        status = ctypes.c_int()
        _CreateDiffraction(handle, status)
        _CheckStatus(status)
        DataObject.__init__(self, handle)
        self.progressHandler = None
        self.calculationProgressHandler = None
        if filename:
            filename = _PrepareString(filename)
            status = ctypes.c_int()
            _LoadDiffractionResults(handle, filename, status)
            if status.value != stOK:
                _LoadDiffractionData(handle, filename, status)
                _CheckStatus(status)
        if threadCount is not None:
            self.threadCount = threadCount

    def __del__(self):
        try:
            _DestroyDiffraction(self.handle, ctypes.c_int())
            # no point checking status here since we can't really do anything about a failure
        # swallow this since we get exceptions when Python terminates unexpectedly (e.g. CTRL+Z)
        except BaseException:
            pass

    def __setattr__(self, name, value):
        DataObject.__setattr__(self, name, value)
        if name == 'progressHandler':
            status = ctypes.c_int()
            if self.progressHandler:
                def callback(handle, progress, cancel):
                    cancel[0] = HelperMethods.ProgressCallbackCancel(
                        self.progressHandler(self, progress))
                self.progressHandlerCallback = _ProgressHandlerProc(callback)
            else:
                self.progressHandlerCallback = None
            _SetDiffractionProgressHandler(self.handle, self.progressHandlerCallback, status)
            _CheckStatus(status)

    def isBuiltInAttribute(self, name):
        return name in ('progressHandler', 'progressHandlerCallback', 'calculationProgressHandler',
            'threadCount', 'latestFileName', 'type') or DataObject.isBuiltInAttribute(self, name)

    @property
    def threadCount(self):
        return HelperMethods.GetModelThreadCount(self.handle)

    @threadCount.setter
    def threadCount(self, value):
        HelperMethods.SetModelThreadCount(self.handle, value)

    @property
    def latestFileName(self):
        return HelperMethods.GetDataString(self.handle, 'LatestFileName', 0)

    @latestFileName.setter
    def latestFileName(self, value):
        HelperMethods.SetDataString(self.handle, 'LatestFileName', 0, value)

    @property
    def type(self):
        return ModelType[self.ModelType]

    @type.setter
    def type(self, value):
        self.ModelType = value.Value

    @property
    def state(self):
        state = ctypes.c_int()
        status = ctypes.c_int()
        _GetDiffractionState(self.handle, state, status)
        _CheckStatus(status)
        return DiffractionState[state.value]

    def Reset(self):
        status = ctypes.c_int()
        _ResetDiffraction(self.handle, status)
        _CheckStatus(status)

    def Clear(self):
        status = ctypes.c_int()
        _ClearDiffraction(self.handle, status)
        _CheckStatus(status)

    def NewVariationModel(self, parentFileName):
        status = ctypes.c_int()
        _NewDiffraction(self.handle, NewModelParams(ModelType.Variation, parentFileName), status)
        _CheckStatus(status)

    def NewRestartAnalysis(self, parentFileName):
        status = ctypes.c_int()
        _NewDiffraction(self.handle, NewModelParams(ModelType.Restart, parentFileName), status)
        _CheckStatus(status)

    def LoadData(self, filename):
        HelperMethods.FileOperation(self.handle, _LoadDiffractionData, filename)

    def LoadDataMem(self, buffer, dataFileType=DataFileType.Binary):
        status = ctypes.c_int()
        _LoadDiffractionDataMem(self.handle, dataFileType.Value, buffer, len(buffer), status)
        _CheckStatus(status)

    def LoadResults(self, filename):
        HelperMethods.FileOperation(self.handle, _LoadDiffractionResults, filename)

    def LoadResultsMem(self, buffer):
        status = ctypes.c_int()
        _LoadDiffractionResultsMem(self.handle, buffer, len(buffer), status)
        _CheckStatus(status)

    def SaveData(self, filename):
        HelperMethods.FileOperation(self.handle, _SaveDiffractionData, filename)

    def SaveDataMem(self, dataFileType=DataFileType.Binary):
        status = ctypes.c_int()
        buffer = Handle()
        bufferLen = ctypes.c_int64()
        _SaveDiffractionDataMem(self.handle, dataFileType.Value, buffer, bufferLen, status)
        _CheckStatus(status)
        return HelperMethods.CopyAndFreeBuffer(buffer, bufferLen.value)

    def SaveResults(self, filename):
        HelperMethods.FileOperation(self.handle, _SaveDiffractionResults, filename)

    def SaveResultsMem(self):
        status = ctypes.c_int()
        buffer = Handle()
        bufferLen = ctypes.c_int64()
        _SaveDiffractionResultsMem(self.handle, buffer, bufferLen, status)
        _CheckStatus(status)
        return HelperMethods.CopyAndFreeBuffer(buffer, bufferLen.value)

    def Calculate(self):
        if self.calculationProgressHandler:
            def callback(handle, progress, cancel):
                cancel[0] = HelperMethods.ProgressCallbackCancel(
                    self.calculationProgressHandler(self, progress))
            progress = _StringProgressHandlerProc(callback)
        else:
            progress = None
        status = ctypes.c_int()
        _CalculateDiffraction(self.handle, progress, status)
        _CheckStatus(status)

    def SaveWaveComponentsSpreadsheet(self, filename):
        HelperMethods.SaveSpreadsheet(self.handle, sptDiffractionWaveComponents, filename, None)

    def SaveWaveComponentsSpreadsheetMem(self, spreadsheetFileType=SpreadsheetFileType.Xlsx):
        return HelperMethods.SaveSpreadsheetMem(self.handle, sptDiffractionWaveComponents, spreadsheetFileType, None)

    def SaveMeshDetailsSpreadsheet(self, filename):
        HelperMethods.SaveSpreadsheet(self.handle, sptDiffractionMeshDetails, filename, None)

    def SaveMeshDetailsSpreadsheetMem(self, spreadsheetFileType=SpreadsheetFileType.Xlsx):
        return HelperMethods.SaveSpreadsheetMem(self.handle, sptDiffractionMeshDetails, spreadsheetFileType, None)

    def SaveResultsSpreadsheet(self, filename):
        HelperMethods.SaveSpreadsheet(self.handle, sptDiffractionResults, filename, None)

    def SaveResultsSpreadsheetMem(self, spreadsheetFileType=SpreadsheetFileType.Xlsx):
        return HelperMethods.SaveSpreadsheetMem(self.handle, sptDiffractionResults, spreadsheetFileType, None)

    @property
    def waveComponents(self):

        def componentGenerator():
            count = ctypes.c_int()
            status = ctypes.c_int()

            _GetDiffractionWaveComponents(self.handle, count, None, status)
            _CheckStatus(status)

            components = (DiffractionWaveComponent * count.value)()
            _GetDiffractionWaveComponents(self.handle, count, components, status)
            _CheckStatus(status)

            for component in components:
                obj = component.asObject()
                obj.Period = 1 / obj.Frequency
                obj.WaveLength = 2 * numpy.pi / obj.WaveNumber
                yield obj

        return tuple(componentGenerator())

    @property
    def headings(self):
        return HelperMethods.DiffractionDoubleArray(self.handle, dotHeadings)

    @property
    def frequencies(self):
        return HelperMethods.DiffractionDoubleArray(self.handle, dotFrequencies)

    @property
    def angularFrequencies(self):
        return HelperMethods.DiffractionDoubleArray(self.handle, dotAngularFrequencies)

    @property
    def periods(self):
        return HelperMethods.DiffractionDoubleArray(self.handle, dotPeriods)

    @property
    def periodsOrFrequencies(self):
        return HelperMethods.DiffractionDoubleArray(self.handle, dotPeriodsOrFrequencies)

    @property
    def hydrostaticResults(self):
        return HelperMethods.HydrostaticResults(self.handle)

    @property
    def addedMass(self):
        return HelperMethods.AddedMassDamping(self.handle, dotAddedMass)

    def addedMassRelativeTo(self, reportingOrigins):
        return HelperMethods.AddedMassDampingRelativeTo(self.handle, dotAddedMass, reportingOrigins)

    @property
    def infiniteFrequencyAddedMass(self):
        return HelperMethods.InfiniteFrequencyAddedMass(self.handle)

    def infiniteFrequencyAddedMassRelativeTo(self, reportingOrigins):
        return HelperMethods.InfiniteFrequencyAddedMassRelativeTo(self.handle, reportingOrigins)

    @property
    def damping(self):
        return HelperMethods.AddedMassDamping(self.handle, dotDamping)

    def dampingRelativeTo(self, reportingOrigins):
        return HelperMethods.AddedMassDampingRelativeTo(self.handle, dotDamping, reportingOrigins)

    @property
    def loadRAOsHaskind(self):
        return HelperMethods.DiffractionRAOs(self.handle, dotLoadRAOsHaskind)

    def loadRAOsHaskindRelativeTo(self, reportingOrigins):
        return HelperMethods.DiffractionRAOsRelativeTo(self.handle, dotLoadRAOsHaskind, reportingOrigins)

    @property
    def loadRAOsDiffraction(self):
        return HelperMethods.DiffractionRAOs(self.handle, dotLoadRAOsDiffraction)

    def loadRAOsDiffractionRelativeTo(self, reportingOrigins):
        return HelperMethods.DiffractionRAOsRelativeTo(self.handle, dotLoadRAOsDiffraction, reportingOrigins)

    @property
    def displacementRAOs(self):
        return HelperMethods.DiffractionRAOs(self.handle, dotDisplacementRAOs)

    def displacementRAOsRelativeTo(self, reportingOrigins):
        return HelperMethods.DiffractionRAOsRelativeTo(self.handle, dotDisplacementRAOs, reportingOrigins)

    @property
    def meanDriftHeadingPairs(self):
        return HelperMethods.QTFHeadingsOrPeriodsOrFrequencies(self.handle, dotMeanDriftHeadingPairs, 2)

    @property
    def QTFHeadingPairs(self):
        return HelperMethods.QTFHeadingsOrPeriodsOrFrequencies(self.handle, dotQTFHeadingPairs, 2)

    @property
    def QTFFrequencies(self):
        return HelperMethods.QTFHeadingsOrPeriodsOrFrequencies(self.handle, dotQTFFrequencies, 3)

    @property
    def QTFAngularFrequencies(self):
        return HelperMethods.QTFHeadingsOrPeriodsOrFrequencies(self.handle, dotQTFAngularFrequencies, 3)

    @property
    def QTFPeriods(self):
        return HelperMethods.QTFHeadingsOrPeriodsOrFrequencies(self.handle, dotQTFPeriods, 3)

    @property
    def QTFPeriodsOrFrequencies(self):
        return HelperMethods.QTFHeadingsOrPeriodsOrFrequencies(self.handle, dotQTFPeriodsOrFrequencies, 3)

    @property
    def meanDriftLoadPressureIntegration(self):
        return HelperMethods.MeanDriftLoad(self.handle, dotMeanDriftLoadPressureIntegration)

    @property
    def meanDriftLoadControlSurface(self):
        return HelperMethods.MeanDriftLoad(self.handle, dotMeanDriftLoadControlSurface)

    @property
    def fieldPointPressure(self):
        return HelperMethods.FieldPointOutput(self.handle, dotFieldPointPressure, 1)

    @property
    def fieldPointRAO(self):
        return HelperMethods.FieldPointOutput(self.handle, dotFieldPointRAO, 1)

    @property
    def fieldPointVelocity(self):
        return HelperMethods.FieldPointOutput(self.handle, dotFieldPointVelocity, 3)

    @property
    def fieldPointRAOGradient(self):
        return HelperMethods.FieldPointOutput(self.handle, dotFieldPointRAOGradient, 3)

    @property
    def panelGeometry(self):
        return HelperMethods.PanelGeometry(self.handle)

    @property
    def panelPressure(self):
        outerCount = HelperMethods.DiffractionDoubleArrayLength(self.handle, dotHeadings)
        return HelperMethods.PanelPressureVelocity(self.handle, dotPanelPressure, outerCount, 1)

    @property
    def panelPressureDiffraction(self):
        outerCount = HelperMethods.DiffractionDoubleArrayLength(self.handle, dotHeadings)
        return HelperMethods.PanelPressureVelocity(self.handle, dotPanelPressureDiffraction, outerCount, 1)

    @property
    def panelPressureRadiation(self):
        outerCount = 6 * HelperMethods.DiffractionIncludedBodyCount(self.handle)
        return HelperMethods.PanelPressureVelocity(self.handle, dotPanelPressureRadiation, outerCount, 1)

    @property
    def panelVelocity(self):
        outerCount = HelperMethods.DiffractionDoubleArrayLength(self.handle, dotHeadings)
        return HelperMethods.PanelPressureVelocity(self.handle, dotPanelVelocity, outerCount, 3)

    @property
    def panelVelocityDiffraction(self):
        outerCount = HelperMethods.DiffractionDoubleArrayLength(self.handle, dotHeadings)
        return HelperMethods.PanelPressureVelocity(self.handle, dotPanelVelocityDiffraction, outerCount, 3)

    @property
    def panelVelocityRadiation(self):
        outerCount = 6 * HelperMethods.DiffractionIncludedBodyCount(self.handle)
        return HelperMethods.PanelPressureVelocity(self.handle, dotPanelVelocityRadiation, outerCount, 3)

    @property
    def quadraticLoadFromPressureIntegration(self):
        return HelperMethods.SecondOrderLoad(self.handle, dotQuadraticLoadFromPressureIntegration)

    @property
    def quadraticLoadFromControlSurface(self):
        return HelperMethods.SecondOrderLoad(self.handle, dotQuadraticLoadFromControlSurface)

    @property
    def directPotentialLoad(self):
        return HelperMethods.SecondOrderLoad(self.handle, dotDirectPotentialLoad)

    @property
    def indirectPotentialLoad(self):
        return HelperMethods.SecondOrderLoad(self.handle, dotIndirectPotentialLoad)

    @property
    def extraRollDamping(self):
        return HelperMethods.ExtraRollDamping(self.handle)

    @property
    def rollDampingPercentCritical(self):
        return HelperMethods.RollDampingPercentCritical(self.handle)


class LinkedStatistics(object):

    __slots__ = 'handle', 'object',

    def __init__(self, object, varNames, period=None, objectExtra=None):
        self.handle = Handle()
        self.object = object

        varCount = len(varNames)
        vars = (ctypes.c_int * varCount)(
            *[object.varID(varNames[index]) for index in range(varCount)]
        )
        status = ctypes.c_int()
        _OpenLinkedStatistics2(
            self.object.handle,
            objectExtra,
            HelperMethods.PreparePeriod(self.object.modelHandle, period),
            varCount,
            vars,
            self.handle,
            status
        )
        _CheckStatus(status)

    def __del__(self):
        try:
            _CloseLinkedStatistics(self.handle, ctypes.c_int())
            # no point checking status here since we can't really do anything about a failure
        # swallow this since we get exceptions when Python terminates unexpectedly (e.g. CTRL+Z)
        except BaseException:
            pass

    def Query(self, varName, linkedVarName):
        varID = self.object.varID(varName)
        linkedVarID = self.object.varID(linkedVarName)
        result = StatisticsQuery()
        status = ctypes.c_int()
        _QueryLinkedStatistics(self.handle, varID, linkedVarID, result, status)
        _CheckStatus(status)
        return result.asObject()

    def TimeSeriesStatistics(self, varName):
        varID = self.object.varID(varName)
        result = TimeSeriesStats()
        status = ctypes.c_int()
        _CalculateLinkedStatisticsTimeSeriesStatistics(self.handle, varID, result, status)
        _CheckStatus(status)
        return result.asObject()


class ExtremeStatistics(object):

    __slots__ = 'handle',

    def __init__(self, values, sampleInterval):
        self.handle = Handle()
        values = _prepareArray(values)
        status = ctypes.c_int()
        _OpenExtremeStatistics(
            len(values),
            values,
            sampleInterval,
            self.handle,
            status
        )
        _CheckStatus(status)

    def __del__(self):
        try:
            _CloseExtremeStatistics(self.handle, ctypes.c_int())
            # no point checking status here since we can't really do anything about a failure
        # swallow this since we get exceptions when Python terminates unexpectedly (e.g. CTRL+Z)
        except BaseException:
            pass

    def ExcessesOverThresholdCount(self, specification=None):
        status = ctypes.c_int()
        count = _CalculateExtremeStatisticsExcessesOverThreshold(
            self.handle,
            specification,
            None,
            status
        )
        _CheckStatus(status)
        return count

    def ExcessesOverThreshold(self, specification=None):
        status = ctypes.c_int()
        count = _CalculateExtremeStatisticsExcessesOverThreshold(
            self.handle,
            specification,
            None,
            status
        )
        _CheckStatus(status)
        values = _allocateArray(count)

        _CalculateExtremeStatisticsExcessesOverThreshold(
            self.handle,
            specification,
            values,
            status
        )
        _CheckStatus(status)
        return _finaliseArray(values)

    def Fit(self, specification):
        status = ctypes.c_int()
        _FitExtremeStatistics(self.handle, specification, status)
        _CheckStatus(status)

    def Query(self, query):
        result = ExtremeStatisticsOutput()
        status = ctypes.c_int()
        _QueryExtremeStatistics(self.handle, query, result, status)
        _CheckStatus(status)
        return result.asObject()

    def ToleranceIntervals(self, SimulatedDataSetCount=1000):

        def generator():
            intervals = (Interval * self.ExcessesOverThresholdCount())()
            status = ctypes.c_int()
            _SimulateToleranceIntervals(self.handle, SimulatedDataSetCount, intervals, status)
            _CheckStatus(status)
            for interval in intervals:
                yield (interval.Lower, interval.Upper)

        return tuple(generator())


class Modes(object):

    __slots__ = 'handle', 'shapesAvailable', 'includeCoupledObjects', 'isWholeSystem', \
        'dofCount', 'modeCount', 'nodeNumber', 'dof', 'owner', 'modeNumber', 'period'

    def __init__(self, obj, specification=None):
        self.handle = Handle()

        if specification is None:
            specification = ModalAnalysisSpecification()
        self.shapesAvailable = bool(specification.CalculateShapes)
        self.includeCoupledObjects = bool(specification.IncludeCoupledObjects)
        self.isWholeSystem = isinstance(obj, Model)

        dofCount = ctypes.c_int()
        modeCount = ctypes.c_int()
        status = ctypes.c_int()
        _CreateModes(obj.handle, specification, self.handle, dofCount, modeCount, status)
        _CheckStatus(status)
        self.dofCount = dofCount.value
        self.modeCount = modeCount.value

        nodeNumber = _allocateIntArray(self.dofCount)
        dof = _allocateIntArray(self.dofCount)
        _GetModeDegreeOfFreedomDetails(self.handle, nodeNumber, dof, status)
        _CheckStatus(status)
        self.nodeNumber = _finaliseIntArray(nodeNumber)
        self.dof = _finaliseIntArray(dof)

        def generator():
            ownerHandle = (Handle * self.dofCount)()
            status = ctypes.c_int()
            _GetModeDegreeOfFreedomOwners(self.handle, ownerHandle, status)
            _CheckStatus(status)
            latestOwner = None
            if self.isWholeSystem:
                modelHandle = obj.handle
            else:
                modelHandle = obj.modelHandle
            for handle in ownerHandle:
                if (latestOwner is None) or (latestOwner.handle.value != handle):
                    latestOwner = HelperMethods.CreateOrcaFlexObject(modelHandle, handle)
                yield latestOwner
        self.owner = tuple(generator())

        modeNumber = _allocateIntArray(self.modeCount)
        period = _allocateArray(self.modeCount)
        _GetModeSummary(self.handle, modeNumber, period, status)
        _CheckStatus(status)
        self.modeNumber = _finaliseIntArray(modeNumber)
        self.period = _finaliseArray(period)

    def __del__(self):
        try:
            _DestroyModes(self.handle, ctypes.c_int())
            # no point checking status here since we can't really do anything about a failure
        # swallow this since we get exceptions when Python terminates unexpectedly (e.g. CTRL+Z)
        except BaseException:
            pass

    def modeDetails(self, index):
        if self.shapesAvailable:
            details = ModeDetails(self.dofCount)
        else:
            details = ModeDetails()
        status = ctypes.c_int()
        _GetModeDetails(self.handle, index, details, status)
        _CheckStatus(status)
        if self.shapesAvailable:
            ShapeWrtGlobal = _finaliseArray(details.ShapeWrtGlobal)
            ShapeWrtLocal = _finaliseArray(details.ShapeWrtLocal)
        else:
            ShapeWrtGlobal = None
            ShapeWrtLocal = None
        resultDict = {
            'modeNumber': details.ModeNumber,
            'period': details.Period,
            'shapeWrtGlobal': ShapeWrtGlobal,
            'shapeWrtLocal': ShapeWrtLocal
        }
        if hasattr(details, 'ModeType'):
            resultDict['modeType'] = details.ModeType
            resultDict['percentageInInlineDirection'] = details.PercentageInInlineDirection
            resultDict['percentageInAxialDirection'] = details.PercentageInAxialDirection
            resultDict['percentageInTransverseDirection'] = details.PercentageInTransverseDirection
            resultDict['percentageInRotationalDirection'] = details.PercentageInRotationalDirection
        else:
            resultDict['modeType'] = mtNotAvailable
            resultDict['percentageInInlineDirection'] = OrcinaNullReal()
            resultDict['percentageInAxialDirection'] = OrcinaNullReal()
            resultDict['percentageInTransverseDirection'] = OrcinaNullReal()
            resultDict['percentageInRotationalDirection'] = OrcinaNullReal()
        if hasattr(details, 'Mass'):
            resultDict['mass'] = details.Mass
            resultDict['stiffness'] = details.Stiffness
        else:
            resultDict['mass'] = OrcinaNullReal()
            resultDict['stiffness'] = OrcinaNullReal()
        return objectFromDict(resultDict)

    @property
    def modeLoadOutputPoints(self):

        def generator():
            outputPoints = (ModeLoadOutputPoint *
                            HelperMethods.ModeLoadOutputPointCount(self.handle))()
            status = ctypes.c_int()
            _GetModeLoadOutputPoints(self.handle, None, outputPoints, status)
            _CheckStatus(status)

            latestOwner = None
            model = None
            for point in outputPoints:
                if model is None:
                    modelHandle = HelperMethods.GetModelHandle(point.Owner)
                    model = Model(handle=modelHandle)
                if (latestOwner is None) or (latestOwner.handle.value != point.Owner):
                    latestOwner = HelperMethods.CreateOrcaFlexObject(model.handle, point.Owner)
                yield objectFromDict({
                    'owner': latestOwner,
                    'arclength': point.Arclength
                })

        return tuple(generator())

    def modeLoad(self, index):

        def generator():
            count = HelperMethods.ModeLoadOutputPointCount(self.handle)
            loads = _allocateArray(6 * count)
            status = ctypes.c_int()
            _GetModeLoad(self.handle, index, loads, status)
            _CheckStatus(status)
            loads = _finaliseArray(loads)
            for pointIndex in range(count):
                yield objectFromDict({
                    'force': loads[pointIndex * 6: pointIndex * 6 + 3],
                    'moment': loads[pointIndex * 6 + 3: pointIndex * 6 + 6]
                })

        return tuple(generator())


class AVIFile(object):

    __slots__ = 'handle', 'width', 'height'

    def __init__(self, filename, codec, interval, width, height):
        self.width = width
        self.height = height
        self.handle = Handle()
        filename = _PrepareString(filename)
        params = AVIFileParameters(codec, interval)
        status = ctypes.c_int()
        _AVIFileInitialise(self.handle, filename, params, status)
        _CheckStatus(status)

    def AddFrame(self, model, drawTime, viewParameters=None):
        if viewParameters is None:
            viewParameters = model.defaultViewParameters
        viewParameters.Height = self.height
        viewParameters.Width = self.width
        frame = ctypes.wintypes.HBITMAP()
        saveDrawTime = model.simulationDrawTime
        try:
            model.simulationDrawTime = drawTime
            status = ctypes.c_int()
            _CreateModel3DViewBitmap(model.handle, viewParameters, frame, status)
            _CheckStatus(status)
            try:
                _AVIFileAddBitmap(self.handle, frame, status)
                _CheckStatus(status)
            finally:
                if not _DeleteObject(frame):
                    raise ctypes.WinError()
        finally:
            model.simulationDrawTime = saveDrawTime

    def Close(self):
        if self.handle != 0:
            status = ctypes.c_int()
            _AVIFileFinalise(self.handle, status)
            _CheckStatus(status)
            self.handle = 0


@contextlib.contextmanager
def OpenAVIFile(filename, codec, interval, width, height):
    file = AVIFile(filename, codec, interval, width, height)
    try:
        yield file
    finally:
        file.Close()


def TimeHistorySpecification(modelObject, varName, objectExtra=None):
    return objectFromDict({
        'modelObject': modelObject,
        'objectExtra': objectExtra,
        'varName': varName
    })


def GetMultipleTimeHistories(specification, period=None):
    count = len(specification)
    if count == 0:
        return numpy.array([])

    status = ctypes.c_int()
    modelHandle = specification[0].modelObject.modelHandle
    period = HelperMethods.PreparePeriod(modelHandle, period)
    sampleCount = _GetNumOfSamples(modelHandle, period, status)
    _CheckStatus(status)

    specAPI = (_TimeHistorySpecification * count)()
    for index, item in enumerate(specification):
        specAPI[index].ObjectHandle = item.modelObject.handle
        specAPI[index].ObjectExtra = ctypes.pointer(item.objectExtra) if item.objectExtra is not None else None
        specAPI[index].VarID = item.modelObject.varID(item.varName)

    values = _allocateArray(count * sampleCount)
    _GetMultipleTimeHistories(count, specAPI, period, values, status)
    _CheckStatus(status)
    return numpy.reshape(_finaliseArray(values), (sampleCount, count))


def TimeSeriesStatistics(values, sampleInterval):
    values = _prepareArray(values)
    result = TimeSeriesStats()
    status = ctypes.c_int()
    _CalculateTimeSeriesStatistics(values, len(values), sampleInterval, result, status)
    _CheckStatus(status)
    return result.asObject()


def AnalyseExtrema(values):
    values = _prepareArray(values)
    max = ctypes.c_double()
    min = ctypes.c_double()
    indexOfMax = ctypes.c_int()
    indexOfMin = ctypes.c_int()
    status = ctypes.c_int()
    _AnalyseExtrema(values, len(values), max, min, indexOfMax, indexOfMin, status)
    _CheckStatus(status)
    return objectFromDict({
        'Min': min.value,
        'Max': max.value,
        'IndexOfMin': indexOfMin.value,
        'IndexOfMax': indexOfMax.value
    })


def SpectralDensity(times, values, fundamentalFrequency=None):
    return HelperMethods.TimeHistorySummary(thstSpectralDensity, times, values, fundamentalFrequency)


def EmpiricalDistribution(values):
    return HelperMethods.TimeHistorySummary(thstEmpiricalDistribution, None, values)


def RainflowHalfCycles(values):
    return HelperMethods.TimeHistorySummary(thstRainflowHalfCycles, None, values).X


def UnorderedRainflowHalfCycles(values):
    return HelperMethods.TimeHistorySummary(thstRainflowAssociatedMean, None, values).X


def RainflowAssociatedMean(values):
    summary = HelperMethods.TimeHistorySummary(thstRainflowAssociatedMean, None, values)
    if _CalculateRratioAvailable:
        return objectFromDict({'HalfCycleRange': summary.X, 'AssociatedMean': summary.Y,
                               'Rratio': Rratio(summary.X, summary.Y)})
    else:
        return objectFromDict({'HalfCycleRange': summary.X, 'AssociatedMean': summary.Y})


def Rratio(range, associatedMean):
    range = _prepareArray(range)
    associatedMean = _prepareArray(associatedMean)
    if len(range) != len(associatedMean):
        raise ValueError('range and associatedMean must have the same length')
    Rratio = _allocateArray(len(range))
    status = ctypes.c_int()
    _CalculateRratio(len(range), range, associatedMean, Rratio, status)
    _CheckStatus(status)
    return _finaliseArray(Rratio)


def CycleHistogramBins(halfCycleRanges, binSize=None):
    if binSize is None:
        binSize = OrcinaDefaultReal()
    halfCycleRanges = _prepareArray(halfCycleRanges)
    binCount = ctypes.c_int()
    bins = ctypes.POINTER(CycleBin)()
    status = ctypes.c_int()
    _CreateCycleHistogramBins(
        len(halfCycleRanges),
        halfCycleRanges,
        binSize,
        binCount,
        bins,
        status
    ),
    _CheckStatus(status)

    def generator():
        for index in range(binCount.value):
            # clone bins[index], see http://stackoverflow.com/q/1470343/
            bin = CycleBin()
            ctypes.pointer(bin)[0] = bins[index]
            yield bin

    result = tuple(generator())

    _DestroyCycleHistogramBins(bins, status)
    _CheckStatus(status)

    return result


def FrequencyDomainMPM(stormDuration, StdDev, Tz):
    result = ctypes.c_double()
    status = ctypes.c_int()
    _GetFrequencyDomainMPM(stormDuration, StdDev, Tz, result, status)
    _CheckStatus(status)
    return result.value


def MoveObjectDisplacementSpecification(displacement):
    result = MoveObjectSpecification()
    result.MoveSpecifiedBy = sbDisplacement
    result.Displacement = (ctypes.c_double * 3)(*displacement)
    return result


def MoveObjectPolarDisplacementSpecification(direction, distance):
    result = MoveObjectSpecification()
    result.MoveSpecifiedBy = sbPolarDisplacement
    result.PolarDisplacementDirection = direction
    result.PolarDisplacementDistance = distance
    return result


def MoveObjectNewPositionSpecification(referenceObject, referencePointIndex, newPosition):
    result = MoveObjectSpecification()
    result.MoveSpecifiedBy = sbNewPosition
    result.NewPositionReferencePoint = MoveObjectPoint(referenceObject, referencePointIndex)
    result.NewPosition = (ctypes.c_double * 3)(*newPosition)
    return result


def MoveObjectRotationSpecification(angle, centre):
    result = MoveObjectSpecification()
    result.MoveSpecifiedBy = sbRotation
    result.RotationAngle = angle
    result.RotationCentre = (ctypes.c_double * 2)(*centre)
    return result


def MoveObjects(specification, points):
    points = (MoveObjectPoint * len(points))(*points)
    status = ctypes.c_int()
    _MoveObjects(specification, len(points), points, status)
    _CheckStatus(status)


def CompoundProperties(objects, referenceObject=None, referencePoint=None):
    objects = (Handle * len(objects))(*[obj.handle for obj in objects])
    if referenceObject is not None:
        referenceObject = referenceObject.handle
    referencePoint = _PrepareString(referencePoint) if referencePoint is not None else _PrepareString('')
    properties = _CompoundProperties()
    status = ctypes.c_int()
    _GetCompoundProperties(
        len(objects),
        objects,
        referenceObject,
        referencePoint,
        properties,
        status
    )
    _CheckStatus(status)
    return objectFromDict({
        'Mass': properties.Mass,
        'CentreOfMass': numpy.array(properties.CentreOfMass[:]),
        'MassMomentOfInertia': numpy.reshape(properties.MassMomentOfInertia[:], (3, 3)),
        'Volume': properties.Volume,
        'CentreOfVolume': numpy.array(properties.CentreOfVolume[:])
    })


def ExchangeObjects(object1, object2):
    status = ctypes.c_int()
    _ExchangeObjects(object1.handle, object2.handle, status)
    _CheckStatus(status)


def SortObjects(objects, key):
    objects = list(objects)
    N = len(objects)
    indices = list(range(N))
    locations = indices[:]
    order = indices[:]
    order.sort(key=lambda i: key(objects[i]))
    indices = list(range(N))
    locations = indices[:]
    for i in range(N):
        index1, index2 = i, locations[order[i]]
        ExchangeObjects(objects[indices[index1]], objects[indices[index2]])
        locations[indices[index1]], locations[indices[index2]] = index2, index1
        indices[index1], indices[index2] = indices[index2], indices[index1]


def CalculateMooringStiffness(vessels):
    status = ctypes.c_int()
    N = len(vessels)
    vesselHandles = (Handle * N)(*map(lambda vessel: vessel.handle, vessels))
    dofCount = 6 * N
    result = numpy.empty(dofCount * dofCount, dtype=numpy.float64)
    _CalculateMooringStiffness(len(vesselHandles), vesselHandles, result, status)
    _CheckStatus(status)
    return result.reshape((dofCount, dofCount))


def ReadPanelMesh(filename, format, scale=1, bodyNumber=1, importDryPanels=True):
    with HelperMethods.PanelMeshImporter(filename, format, scale, bodyNumber, importDryPanels) as importer:
        panelCount = importer.panelCount
        symmetry = importer.symmetry
        panels = _allocateArray(panelCount * 12)
        status = ctypes.c_int()
        _GetPanels(importer.handle, panels, status)

    panels.shape = panelCount, 4, 3
    return objectFromDict({
        'panels': panels,
        'symmetry': symmetry
    })


def SetLibraryPolicy(name, value=None):
    status = ctypes.c_int()
    if value is not None:
        value = str(value)  # so that we can pass integers or booleans for policies of those types
    _SetLibraryPolicy(name, value, status)
    _CheckStatus(status)


def DLLBuildDate():
    return datetime.utcfromtimestamp(_GetDLLBuildDate())


def DLLLocation():
    filename = (_char * ctypes.wintypes.MAX_PATH)()
    returnValue = _GetModuleFileName(_lib._handle, filename, ctypes.wintypes.MAX_PATH)
    if returnValue == 0:
        raise ctypes.WinError()
    return _DecodeString(filename.value)


def DLLVersion():
    v = (_char * 16)()
    status = ctypes.c_int()
    _GetDLLVersion(None, v, ctypes.c_int(), status)
    _CheckStatus(status)
    return _DecodeString(v.value)


def RegisterLicenceNotFoundHandler(handler):
    global _licenceNotFoundCallback
    if handler:
        def callback(action, attemptReconnection, data):
            attemptReconnection[0] = ctypes.wintypes.BOOL(handler(action))
        _licenceNotFoundCallback = _LicenceNotFoundHandlerProc(callback)
    else:
        _licenceNotFoundCallback = None
    status = ctypes.c_int()
    _RegisterLicenceNotFoundHandler(_licenceNotFoundCallback, status)
    _CheckStatus(status)


def BinaryFileType(filename):
    filename = _PrepareString(filename)
    ft = ctypes.c_int()
    status = ctypes.c_int()
    _GetBinaryFileType(filename, ft, status)
    _CheckStatus(status)
    return FileType[ft.value]


def FileCreatorVersion(filename):
    filename = _PrepareString(filename)
    status = ctypes.c_int()
    length = _GetFileCreatorVersion(filename, None, status)
    _CheckStatus(status)
    result = (_char * length)()
    _GetFileCreatorVersion(filename, result, status)
    _CheckStatus(status)
    return _DecodeString(result.value)


def RestartParentFileName(filename):
    filename = _PrepareString(filename)
    status = ctypes.c_int()
    buffer = Handle()
    bufferLen = ctypes.c_int64()
    length = _GetRestartParentFileName(filename, buffer, bufferLen, status)
    _CheckStatus(status)
    parentFileName = HelperMethods.CopyToStringAndFreeBuffer(buffer, bufferLen.value)
    return parentFileName if parentFileName else None


def SolveEquation(calcY, initialX, targetY, params=None):
    def callback(data, X, callbackStatus):
        return calcY(X)
    solveEquationCalcYProc = _SolveEquationCalcYProc(callback)
    result = ctypes.c_double(initialX)
    status = ctypes.c_int()
    _SolveEquation(None, solveEquationCalcYProc, result, targetY, params, status)
    _CheckStatus(status)
    return result.value
