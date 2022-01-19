class DatabaseError(Exception):
    code = None


class NoData(DatabaseError):
    code = '02000'


class NoAdditionalDynamicResultSetsReturned(DatabaseError):
    code = '02001'


class SqlStatementNotYetComplete(DatabaseError):
    code = '03000'


class ConnectionException(DatabaseError):
    code = '08000'


class SqlclientUnableToEstablishSqlconnection(DatabaseError):
    code = '08001'


class ConnectionDoesNotExist(DatabaseError):
    code = '08003'


class SqlserverRejectedEstablishmentOfSqlconnection(DatabaseError):
    code = '08004'


class ConnectionFailure(DatabaseError):
    code = '08006'


class TransactionResolutionUnknown(DatabaseError):
    code = '08007'


class ProtocolViolation(DatabaseError):
    code = '08P01'


class TriggeredActionException(DatabaseError):
    code = '09000'


class FeatureNotSupported(DatabaseError):
    code = '0A000'


class InvalidTransactionInitiation(DatabaseError):
    code = '0B000'


class LocatorException(DatabaseError):
    code = '0F000'


class InvalidLocatorSpecification(DatabaseError):
    code = '0F001'


class InvalidGrantor(DatabaseError):
    code = '0L000'


class InvalidGrantOperation(DatabaseError):
    code = '0LP01'


class InvalidRoleSpecification(DatabaseError):
    code = '0P000'


class DiagnosticsException(DatabaseError):
    code = '0Z000'


class StackedDiagnosticsAccessedWithoutActiveHandler(DatabaseError):
    code = '0Z002'


class CaseNotFound(DatabaseError):
    code = '20000'


class CardinalityViolation(DatabaseError):
    code = '21000'


class DataException(DatabaseError):
    code = '22000'


class StringDataRightTruncation(DatabaseError):
    code = '22001'


class NullValueNoIndicatorParameter(DatabaseError):
    code = '22002'


class NumericValueOutOfRange(DatabaseError):
    code = '22003'


class NullValueNotAllowed(DatabaseError):
    code = '22004'


class ErrorInAssignment(DatabaseError):
    code = '22005'


class InvalidDatetimeFormat(DatabaseError):
    code = '22007'


class DatetimeFieldOverflow(DatabaseError):
    code = '22008'


class InvalidTimeZoneDisplacementValue(DatabaseError):
    code = '22009'


class EscapeCharacterConflict(DatabaseError):
    code = '2200B'


class InvalidUseOfEscapeCharacter(DatabaseError):
    code = '2200C'


class InvalidEscapeOctet(DatabaseError):
    code = '2200D'


class ZeroLengthCharacterString(DatabaseError):
    code = '2200F'


class MostSpecificTypeMismatch(DatabaseError):
    code = '2200G'


class SequenceGeneratorLimitExceeded(DatabaseError):
    code = '2200H'


class NotAnXmlDocument(DatabaseError):
    code = '2200L'


class InvalidXmlDocument(DatabaseError):
    code = '2200M'


class InvalidXmlContent(DatabaseError):
    code = '2200N'


class InvalidXmlComment(DatabaseError):
    code = '2200S'


class InvalidXmlProcessingInstruction(DatabaseError):
    code = '2200T'


class InvalidIndicatorParameterValue(DatabaseError):
    code = '22010'


class SubstringError(DatabaseError):
    code = '22011'


class DivisionByZero(DatabaseError):
    code = '22012'


class InvalidPrecedingOrFollowingSize(DatabaseError):
    code = '22013'


class InvalidArgumentForNtileFunction(DatabaseError):
    code = '22014'


class IntervalFieldOverflow(DatabaseError):
    code = '22015'


class InvalidArgumentForNthValueFunction(DatabaseError):
    code = '22016'


class InvalidCharacterValueForCast(DatabaseError):
    code = '22018'


class InvalidEscapeCharacter(DatabaseError):
    code = '22019'


class InvalidRegularExpression(DatabaseError):
    code = '2201B'


class InvalidArgumentForLogarithm(DatabaseError):
    code = '2201E'


class InvalidArgumentForPowerFunction(DatabaseError):
    code = '2201F'


class InvalidArgumentForWidthBucketFunction(DatabaseError):
    code = '2201G'


class InvalidRowCountInLimitClause(DatabaseError):
    code = '2201W'


class InvalidRowCountInResultOffsetClause(DatabaseError):
    code = '2201X'


class CharacterNotInRepertoire(DatabaseError):
    code = '22021'


class IndicatorOverflow(DatabaseError):
    code = '22022'


class InvalidParameterValue(DatabaseError):
    code = '22023'


class UnterminatedCString(DatabaseError):
    code = '22024'


class InvalidEscapeSequence(DatabaseError):
    code = '22025'


class StringDataLengthMismatch(DatabaseError):
    code = '22026'


class TrimError(DatabaseError):
    code = '22027'


class ArraySubscriptError(DatabaseError):
    code = '2202E'


class InvalidTablesampleRepeat(DatabaseError):
    code = '2202G'


class InvalidTablesampleArgument(DatabaseError):
    code = '2202H'


class DuplicateJsonObjectKeyValue(DatabaseError):
    code = '22030'


class InvalidArgumentForSqlJsonDatetimeFunction(DatabaseError):
    code = '22031'


class InvalidJsonText(DatabaseError):
    code = '22032'


class InvalidSqlJsonSubscript(DatabaseError):
    code = '22033'


class MoreThanOneSqlJsonItem(DatabaseError):
    code = '22034'


class NoSqlJsonItem(DatabaseError):
    code = '22035'


class NonNumericSqlJsonItem(DatabaseError):
    code = '22036'


class NonUniqueKeysInAJsonObject(DatabaseError):
    code = '22037'


class SingletonSqlJsonItemRequired(DatabaseError):
    code = '22038'


class SqlJsonArrayNotFound(DatabaseError):
    code = '22039'


class SqlJsonMemberNotFound(DatabaseError):
    code = '2203A'


class SqlJsonNumberNotFound(DatabaseError):
    code = '2203B'


class SqlJsonObjectNotFound(DatabaseError):
    code = '2203C'


class TooManyJsonArrayElements(DatabaseError):
    code = '2203D'


class TooManyJsonObjectMembers(DatabaseError):
    code = '2203E'


class SqlJsonScalarRequired(DatabaseError):
    code = '2203F'


class FloatingPointException(DatabaseError):
    code = '22P01'


class InvalidTextRepresentation(DatabaseError):
    code = '22P02'


class InvalidBinaryRepresentation(DatabaseError):
    code = '22P03'


class BadCopyFileFormat(DatabaseError):
    code = '22P04'


class UntranslatableCharacter(DatabaseError):
    code = '22P05'


class NonstandardUseOfEscapeCharacter(DatabaseError):
    code = '22P06'


class IntegrityConstraintViolation(DatabaseError):
    code = '23000'


class RestrictViolation(DatabaseError):
    code = '23001'


class NotNullViolation(DatabaseError):
    code = '23502'


class ForeignKeyViolation(DatabaseError):
    code = '23503'


class UniqueViolation(DatabaseError):
    code = '23505'


class CheckViolation(DatabaseError):
    code = '23514'


class ExclusionViolation(DatabaseError):
    code = '23P01'


class InvalidCursorState(DatabaseError):
    code = '24000'


class InvalidTransactionState(DatabaseError):
    code = '25000'


class ActiveSqlTransaction(DatabaseError):
    code = '25001'


class BranchTransactionAlreadyActive(DatabaseError):
    code = '25002'


class InappropriateAccessModeForBranchTransaction(DatabaseError):
    code = '25003'


class InappropriateIsolationLevelForBranchTransaction(DatabaseError):
    code = '25004'


class NoActiveSqlTransactionForBranchTransaction(DatabaseError):
    code = '25005'


class ReadOnlySqlTransaction(DatabaseError):
    code = '25006'


class SchemaAndDataStatementMixingNotSupported(DatabaseError):
    code = '25007'


class HeldCursorRequiresSameIsolationLevel(DatabaseError):
    code = '25008'


class NoActiveSqlTransaction(DatabaseError):
    code = '25P01'


class InFailedSqlTransaction(DatabaseError):
    code = '25P02'


class IdleInTransactionSessionTimeout(DatabaseError):
    code = '25P03'


class InvalidSqlStatementName(DatabaseError):
    code = '26000'


class TriggeredDataChangeViolation(DatabaseError):
    code = '27000'


class InvalidAuthorizationSpecification(DatabaseError):
    code = '28000'


class InvalidPassword(DatabaseError):
    code = '28P01'


class DependentPrivilegeDescriptorsStillExist(DatabaseError):
    code = '2B000'


class DependentObjectsStillExist(DatabaseError):
    code = '2BP01'


class InvalidTransactionTermination(DatabaseError):
    code = '2D000'


class SqlRoutineException(DatabaseError):
    code = '2F000'


class ModifyingSqlDataNotPermitted(DatabaseError):
    code = '2F002'


class ProhibitedSqlStatementAttempted(DatabaseError):
    code = '2F003'


class ReadingSqlDataNotPermitted(DatabaseError):
    code = '2F004'


class FunctionExecutedNoReturnStatement(DatabaseError):
    code = '2F005'


class InvalidCursorName(DatabaseError):
    code = '34000'


class ExternalRoutineException(DatabaseError):
    code = '38000'


class ContainingSqlNotPermitted(DatabaseError):
    code = '38001'


class ModifyingSqlDataNotPermittedExt(DatabaseError):
    code = '38002'


class ProhibitedSqlStatementAttemptedExt(DatabaseError):
    code = '38003'


class ReadingSqlDataNotPermittedExt(DatabaseError):
    code = '38004'


class ExternalRoutineInvocationException(DatabaseError):
    code = '39000'


class InvalidSqlstateReturned(DatabaseError):
    code = '39001'


class NullValueNotAllowedExt(DatabaseError):
    code = '39004'


class TriggerProtocolViolated(DatabaseError):
    code = '39P01'


class SrfProtocolViolated(DatabaseError):
    code = '39P02'


class EventTriggerProtocolViolated(DatabaseError):
    code = '39P03'


class SavepointException(DatabaseError):
    code = '3B000'


class InvalidSavepointSpecification(DatabaseError):
    code = '3B001'


class InvalidCatalogName(DatabaseError):
    code = '3D000'


class InvalidSchemaName(DatabaseError):
    code = '3F000'


class TransactionRollback(DatabaseError):
    code = '40000'


class SerializationFailure(DatabaseError):
    code = '40001'


class TransactionIntegrityConstraintViolation(DatabaseError):
    code = '40002'


class StatementCompletionUnknown(DatabaseError):
    code = '40003'


class DeadlockDetected(DatabaseError):
    code = '40P01'


class SyntaxErrorOrAccessRuleViolation(DatabaseError):
    code = '42000'


class InsufficientPrivilege(DatabaseError):
    code = '42501'


class SyntaxError(DatabaseError):
    code = '42601'


class InvalidName(DatabaseError):
    code = '42602'


class InvalidColumnDefinition(DatabaseError):
    code = '42611'


class NameTooLong(DatabaseError):
    code = '42622'


class DuplicateColumn(DatabaseError):
    code = '42701'


class AmbiguousColumn(DatabaseError):
    code = '42702'


class UndefinedColumn(DatabaseError):
    code = '42703'


class UndefinedObject(DatabaseError):
    code = '42704'


class DuplicateObject(DatabaseError):
    code = '42710'


class DuplicateAlias(DatabaseError):
    code = '42712'


class DuplicateFunction(DatabaseError):
    code = '42723'


class AmbiguousFunction(DatabaseError):
    code = '42725'


class GroupingError(DatabaseError):
    code = '42803'


class DatatypeMismatch(DatabaseError):
    code = '42804'


class WrongObjectType(DatabaseError):
    code = '42809'


class InvalidForeignKey(DatabaseError):
    code = '42830'


class CannotCoerce(DatabaseError):
    code = '42846'


class UndefinedFunction(DatabaseError):
    code = '42883'


class GeneratedAlways(DatabaseError):
    code = '428C9'


class ReservedName(DatabaseError):
    code = '42939'


class UndefinedTable(DatabaseError):
    code = '42P01'


class UndefinedParameter(DatabaseError):
    code = '42P02'


class DuplicateCursor(DatabaseError):
    code = '42P03'


class DuplicateDatabase(DatabaseError):
    code = '42P04'


class DuplicatePreparedStatement(DatabaseError):
    code = '42P05'


class DuplicateSchema(DatabaseError):
    code = '42P06'


class DuplicateTable(DatabaseError):
    code = '42P07'


class AmbiguousParameter(DatabaseError):
    code = '42P08'


class AmbiguousAlias(DatabaseError):
    code = '42P09'


class InvalidColumnReference(DatabaseError):
    code = '42P10'


class InvalidCursorDefinition(DatabaseError):
    code = '42P11'


class InvalidDatabaseDefinition(DatabaseError):
    code = '42P12'


class InvalidFunctionDefinition(DatabaseError):
    code = '42P13'


class InvalidPreparedStatementDefinition(DatabaseError):
    code = '42P14'


class InvalidSchemaDefinition(DatabaseError):
    code = '42P15'


class InvalidTableDefinition(DatabaseError):
    code = '42P16'


class InvalidObjectDefinition(DatabaseError):
    code = '42P17'


class IndeterminateDatatype(DatabaseError):
    code = '42P18'


class InvalidRecursion(DatabaseError):
    code = '42P19'


class WindowingError(DatabaseError):
    code = '42P20'


class CollationMismatch(DatabaseError):
    code = '42P21'


class IndeterminateCollation(DatabaseError):
    code = '42P22'


class WithCheckOptionViolation(DatabaseError):
    code = '44000'


class InsufficientResources(DatabaseError):
    code = '53000'


class DiskFull(DatabaseError):
    code = '53100'


class OutOfMemory(DatabaseError):
    code = '53200'


class TooManyConnections(DatabaseError):
    code = '53300'


class ConfigurationLimitExceeded(DatabaseError):
    code = '53400'


class ProgramLimitExceeded(DatabaseError):
    code = '54000'


class StatementTooComplex(DatabaseError):
    code = '54001'


class TooManyColumns(DatabaseError):
    code = '54011'


class TooManyArguments(DatabaseError):
    code = '54023'


class ObjectNotInPrerequisiteState(DatabaseError):
    code = '55000'


class ObjectInUse(DatabaseError):
    code = '55006'


class CantChangeRuntimeParam(DatabaseError):
    code = '55P02'


class LockNotAvailable(DatabaseError):
    code = '55P03'


class UnsafeNewEnumValueUsage(DatabaseError):
    code = '55P04'


class OperatorIntervention(DatabaseError):
    code = '57000'


class QueryCanceled(DatabaseError):
    code = '57014'


class AdminShutdown(DatabaseError):
    code = '57P01'


class CrashShutdown(DatabaseError):
    code = '57P02'


class CannotConnectNow(DatabaseError):
    code = '57P03'


class DatabaseDropped(DatabaseError):
    code = '57P04'


class IdleSessionTimeout(DatabaseError):
    code = '57P05'


class SystemError(DatabaseError):
    code = '58000'


class IoError(DatabaseError):
    code = '58030'


class UndefinedFile(DatabaseError):
    code = '58P01'


class DuplicateFile(DatabaseError):
    code = '58P02'


class SnapshotTooOld(DatabaseError):
    code = '72000'


class ConfigFileError(DatabaseError):
    code = 'F0000'


class LockFileExists(DatabaseError):
    code = 'F0001'


class FdwError(DatabaseError):
    code = 'HV000'


class FdwOutOfMemory(DatabaseError):
    code = 'HV001'


class FdwDynamicParameterValueNeeded(DatabaseError):
    code = 'HV002'


class FdwInvalidDataType(DatabaseError):
    code = 'HV004'


class FdwColumnNameNotFound(DatabaseError):
    code = 'HV005'


class FdwInvalidDataTypeDescriptors(DatabaseError):
    code = 'HV006'


class FdwInvalidColumnName(DatabaseError):
    code = 'HV007'


class FdwInvalidColumnNumber(DatabaseError):
    code = 'HV008'


class FdwInvalidUseOfNullPointer(DatabaseError):
    code = 'HV009'


class FdwInvalidStringFormat(DatabaseError):
    code = 'HV00A'


class FdwInvalidHandle(DatabaseError):
    code = 'HV00B'


class FdwInvalidOptionIndex(DatabaseError):
    code = 'HV00C'


class FdwInvalidOptionName(DatabaseError):
    code = 'HV00D'


class FdwOptionNameNotFound(DatabaseError):
    code = 'HV00J'


class FdwReplyHandle(DatabaseError):
    code = 'HV00K'


class FdwUnableToCreateExecution(DatabaseError):
    code = 'HV00L'


class FdwUnableToCreateReply(DatabaseError):
    code = 'HV00M'


class FdwUnableToEstablishConnection(DatabaseError):
    code = 'HV00N'


class FdwNoSchemas(DatabaseError):
    code = 'HV00P'


class FdwSchemaNotFound(DatabaseError):
    code = 'HV00Q'


class FdwTableNotFound(DatabaseError):
    code = 'HV00R'


class FdwFunctionSequenceError(DatabaseError):
    code = 'HV010'


class FdwTooManyHandles(DatabaseError):
    code = 'HV014'


class FdwInconsistentDescriptorInformation(DatabaseError):
    code = 'HV021'


class FdwInvalidAttributeValue(DatabaseError):
    code = 'HV024'


class FdwInvalidStringLengthOrBufferLength(DatabaseError):
    code = 'HV090'


class FdwInvalidDescriptorFieldIdentifier(DatabaseError):
    code = 'HV091'


class PlpgsqlError(DatabaseError):
    code = 'P0000'


class RaiseException(DatabaseError):
    code = 'P0001'


class NoDataFound(DatabaseError):
    code = 'P0002'


class TooManyRows(DatabaseError):
    code = 'P0003'


class AssertFailure(DatabaseError):
    code = 'P0004'


class InternalError(DatabaseError):
    code = 'XX000'


class DataCorrupted(DatabaseError):
    code = 'XX001'


class IndexCorrupted(DatabaseError):
    code = 'XX002'


sqlstate_errors = {
    '02000': NoData,
    '02001': NoAdditionalDynamicResultSetsReturned,
    '03000': SqlStatementNotYetComplete,
    '08000': ConnectionException,
    '08001': SqlclientUnableToEstablishSqlconnection,
    '08003': ConnectionDoesNotExist,
    '08004': SqlserverRejectedEstablishmentOfSqlconnection,
    '08006': ConnectionFailure,
    '08007': TransactionResolutionUnknown,
    '08P01': ProtocolViolation,
    '09000': TriggeredActionException,
    '0A000': FeatureNotSupported,
    '0B000': InvalidTransactionInitiation,
    '0F000': LocatorException,
    '0F001': InvalidLocatorSpecification,
    '0L000': InvalidGrantor,
    '0LP01': InvalidGrantOperation,
    '0P000': InvalidRoleSpecification,
    '0Z000': DiagnosticsException,
    '0Z002': StackedDiagnosticsAccessedWithoutActiveHandler,
    '20000': CaseNotFound,
    '21000': CardinalityViolation,
    '22000': DataException,
    '22001': StringDataRightTruncation,
    '22002': NullValueNoIndicatorParameter,
    '22003': NumericValueOutOfRange,
    '22004': NullValueNotAllowed,
    '22005': ErrorInAssignment,
    '22007': InvalidDatetimeFormat,
    '22008': DatetimeFieldOverflow,
    '22009': InvalidTimeZoneDisplacementValue,
    '2200B': EscapeCharacterConflict,
    '2200C': InvalidUseOfEscapeCharacter,
    '2200D': InvalidEscapeOctet,
    '2200F': ZeroLengthCharacterString,
    '2200G': MostSpecificTypeMismatch,
    '2200H': SequenceGeneratorLimitExceeded,
    '2200L': NotAnXmlDocument,
    '2200M': InvalidXmlDocument,
    '2200N': InvalidXmlContent,
    '2200S': InvalidXmlComment,
    '2200T': InvalidXmlProcessingInstruction,
    '22010': InvalidIndicatorParameterValue,
    '22011': SubstringError,
    '22012': DivisionByZero,
    '22013': InvalidPrecedingOrFollowingSize,
    '22014': InvalidArgumentForNtileFunction,
    '22015': IntervalFieldOverflow,
    '22016': InvalidArgumentForNthValueFunction,
    '22018': InvalidCharacterValueForCast,
    '22019': InvalidEscapeCharacter,
    '2201B': InvalidRegularExpression,
    '2201E': InvalidArgumentForLogarithm,
    '2201F': InvalidArgumentForPowerFunction,
    '2201G': InvalidArgumentForWidthBucketFunction,
    '2201W': InvalidRowCountInLimitClause,
    '2201X': InvalidRowCountInResultOffsetClause,
    '22021': CharacterNotInRepertoire,
    '22022': IndicatorOverflow,
    '22023': InvalidParameterValue,
    '22024': UnterminatedCString,
    '22025': InvalidEscapeSequence,
    '22026': StringDataLengthMismatch,
    '22027': TrimError,
    '2202E': ArraySubscriptError,
    '2202G': InvalidTablesampleRepeat,
    '2202H': InvalidTablesampleArgument,
    '22030': DuplicateJsonObjectKeyValue,
    '22031': InvalidArgumentForSqlJsonDatetimeFunction,
    '22032': InvalidJsonText,
    '22033': InvalidSqlJsonSubscript,
    '22034': MoreThanOneSqlJsonItem,
    '22035': NoSqlJsonItem,
    '22036': NonNumericSqlJsonItem,
    '22037': NonUniqueKeysInAJsonObject,
    '22038': SingletonSqlJsonItemRequired,
    '22039': SqlJsonArrayNotFound,
    '2203A': SqlJsonMemberNotFound,
    '2203B': SqlJsonNumberNotFound,
    '2203C': SqlJsonObjectNotFound,
    '2203D': TooManyJsonArrayElements,
    '2203E': TooManyJsonObjectMembers,
    '2203F': SqlJsonScalarRequired,
    '22P01': FloatingPointException,
    '22P02': InvalidTextRepresentation,
    '22P03': InvalidBinaryRepresentation,
    '22P04': BadCopyFileFormat,
    '22P05': UntranslatableCharacter,
    '22P06': NonstandardUseOfEscapeCharacter,
    '23000': IntegrityConstraintViolation,
    '23001': RestrictViolation,
    '23502': NotNullViolation,
    '23503': ForeignKeyViolation,
    '23505': UniqueViolation,
    '23514': CheckViolation,
    '23P01': ExclusionViolation,
    '24000': InvalidCursorState,
    '25000': InvalidTransactionState,
    '25001': ActiveSqlTransaction,
    '25002': BranchTransactionAlreadyActive,
    '25003': InappropriateAccessModeForBranchTransaction,
    '25004': InappropriateIsolationLevelForBranchTransaction,
    '25005': NoActiveSqlTransactionForBranchTransaction,
    '25006': ReadOnlySqlTransaction,
    '25007': SchemaAndDataStatementMixingNotSupported,
    '25008': HeldCursorRequiresSameIsolationLevel,
    '25P01': NoActiveSqlTransaction,
    '25P02': InFailedSqlTransaction,
    '25P03': IdleInTransactionSessionTimeout,
    '26000': InvalidSqlStatementName,
    '27000': TriggeredDataChangeViolation,
    '28000': InvalidAuthorizationSpecification,
    '28P01': InvalidPassword,
    '2B000': DependentPrivilegeDescriptorsStillExist,
    '2BP01': DependentObjectsStillExist,
    '2D000': InvalidTransactionTermination,
    '2F000': SqlRoutineException,
    '2F002': ModifyingSqlDataNotPermitted,
    '2F003': ProhibitedSqlStatementAttempted,
    '2F004': ReadingSqlDataNotPermitted,
    '2F005': FunctionExecutedNoReturnStatement,
    '34000': InvalidCursorName,
    '38000': ExternalRoutineException,
    '38001': ContainingSqlNotPermitted,
    '38002': ModifyingSqlDataNotPermittedExt,
    '38003': ProhibitedSqlStatementAttemptedExt,
    '38004': ReadingSqlDataNotPermittedExt,
    '39000': ExternalRoutineInvocationException,
    '39001': InvalidSqlstateReturned,
    '39004': NullValueNotAllowedExt,
    '39P01': TriggerProtocolViolated,
    '39P02': SrfProtocolViolated,
    '39P03': EventTriggerProtocolViolated,
    '3B000': SavepointException,
    '3B001': InvalidSavepointSpecification,
    '3D000': InvalidCatalogName,
    '3F000': InvalidSchemaName,
    '40000': TransactionRollback,
    '40001': SerializationFailure,
    '40002': TransactionIntegrityConstraintViolation,
    '40003': StatementCompletionUnknown,
    '40P01': DeadlockDetected,
    '42000': SyntaxErrorOrAccessRuleViolation,
    '42501': InsufficientPrivilege,
    '42601': SyntaxError,
    '42602': InvalidName,
    '42611': InvalidColumnDefinition,
    '42622': NameTooLong,
    '42701': DuplicateColumn,
    '42702': AmbiguousColumn,
    '42703': UndefinedColumn,
    '42704': UndefinedObject,
    '42710': DuplicateObject,
    '42712': DuplicateAlias,
    '42723': DuplicateFunction,
    '42725': AmbiguousFunction,
    '42803': GroupingError,
    '42804': DatatypeMismatch,
    '42809': WrongObjectType,
    '42830': InvalidForeignKey,
    '42846': CannotCoerce,
    '42883': UndefinedFunction,
    '428C9': GeneratedAlways,
    '42939': ReservedName,
    '42P01': UndefinedTable,
    '42P02': UndefinedParameter,
    '42P03': DuplicateCursor,
    '42P04': DuplicateDatabase,
    '42P05': DuplicatePreparedStatement,
    '42P06': DuplicateSchema,
    '42P07': DuplicateTable,
    '42P08': AmbiguousParameter,
    '42P09': AmbiguousAlias,
    '42P10': InvalidColumnReference,
    '42P11': InvalidCursorDefinition,
    '42P12': InvalidDatabaseDefinition,
    '42P13': InvalidFunctionDefinition,
    '42P14': InvalidPreparedStatementDefinition,
    '42P15': InvalidSchemaDefinition,
    '42P16': InvalidTableDefinition,
    '42P17': InvalidObjectDefinition,
    '42P18': IndeterminateDatatype,
    '42P19': InvalidRecursion,
    '42P20': WindowingError,
    '42P21': CollationMismatch,
    '42P22': IndeterminateCollation,
    '44000': WithCheckOptionViolation,
    '53000': InsufficientResources,
    '53100': DiskFull,
    '53200': OutOfMemory,
    '53300': TooManyConnections,
    '53400': ConfigurationLimitExceeded,
    '54000': ProgramLimitExceeded,
    '54001': StatementTooComplex,
    '54011': TooManyColumns,
    '54023': TooManyArguments,
    '55000': ObjectNotInPrerequisiteState,
    '55006': ObjectInUse,
    '55P02': CantChangeRuntimeParam,
    '55P03': LockNotAvailable,
    '55P04': UnsafeNewEnumValueUsage,
    '57000': OperatorIntervention,
    '57014': QueryCanceled,
    '57P01': AdminShutdown,
    '57P02': CrashShutdown,
    '57P03': CannotConnectNow,
    '57P04': DatabaseDropped,
    '57P05': IdleSessionTimeout,
    '58000': SystemError,
    '58030': IoError,
    '58P01': UndefinedFile,
    '58P02': DuplicateFile,
    '72000': SnapshotTooOld,
    'F0000': ConfigFileError,
    'F0001': LockFileExists,
    'HV000': FdwError,
    'HV001': FdwOutOfMemory,
    'HV002': FdwDynamicParameterValueNeeded,
    'HV004': FdwInvalidDataType,
    'HV005': FdwColumnNameNotFound,
    'HV006': FdwInvalidDataTypeDescriptors,
    'HV007': FdwInvalidColumnName,
    'HV008': FdwInvalidColumnNumber,
    'HV009': FdwInvalidUseOfNullPointer,
    'HV00A': FdwInvalidStringFormat,
    'HV00B': FdwInvalidHandle,
    'HV00C': FdwInvalidOptionIndex,
    'HV00D': FdwInvalidOptionName,
    'HV00J': FdwOptionNameNotFound,
    'HV00K': FdwReplyHandle,
    'HV00L': FdwUnableToCreateExecution,
    'HV00M': FdwUnableToCreateReply,
    'HV00N': FdwUnableToEstablishConnection,
    'HV00P': FdwNoSchemas,
    'HV00Q': FdwSchemaNotFound,
    'HV00R': FdwTableNotFound,
    'HV010': FdwFunctionSequenceError,
    'HV014': FdwTooManyHandles,
    'HV021': FdwInconsistentDescriptorInformation,
    'HV024': FdwInvalidAttributeValue,
    'HV090': FdwInvalidStringLengthOrBufferLength,
    'HV091': FdwInvalidDescriptorFieldIdentifier,
    'P0000': PlpgsqlError,
    'P0001': RaiseException,
    'P0002': NoDataFound,
    'P0003': TooManyRows,
    'P0004': AssertFailure,
    'XX000': InternalError,
    'XX001': DataCorrupted,
    'XX002': IndexCorrupted,
}
