from pyasn1.type import univ, namedtype, namedval, tag, constraint

from .common import Diagnostics, IntPosShort, ParameterName
from .raf_structure import LockStatusReport, CurrentReportingCycle,\
    TimeoutPeriod


class DiagnosticRcfGet(univ.Choice):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('common', Diagnostics().subtype(
            implicitTag=tag.Tag(
                tag.tagClassContext, tag.tagFormatSimple, 0))),
        namedtype.NamedType('specific', univ.Integer(
            namedValues=namedval.NamedValues(
                ('unknownParameter', 0))).subtype(
                    implicitTag=tag.Tag(
                        tag.tagClassContext, tag.tagFormatSimple, 1)))
    )


class DiagnosticRcfStart(univ.Choice):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('common', Diagnostics().subtype(
            implicitTag=tag.Tag(
                tag.tagClassContext, tag.tagFormatSimple, 0))),
        namedtype.NamedType('specific', univ.Integer(
            namedValues=namedval.NamedValues(
                ('outOfService', 0),
                ('unableToComply', 1),
                ('invalidStartTime', 2),
                ('invalidStopTime', 3),
                ('missingTimeValue', 4),
                ('invalidGvcId', 5),
                )).subtype(
                    implicitTag=tag.Tag(
                        tag.tagClassContext, tag.tagFormatSimple, 1)))
    )


class RcfProductionStatus(univ.Integer):
    namedValues = namedval.NamedValues(
        ('running', 0),
        ('interrupted', 1),
        ('halted', 2)
    )


class Notification(univ.Choice):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('lossFrameSync', LockStatusReport().subtype(
            implicitTag=tag.Tag(
                tag.tagClassContext, tag.tagFormatConstructed, 0))),
        namedtype.NamedType(
            'productionStatusChange', RcfProductionStatus().subtype(
                implicitTag=tag.Tag(
                    tag.tagClassContext, tag.tagFormatSimple, 1))),
        namedtype.NamedType('excessiveDataBacklog', univ.Null().subtype(
            implicitTag=tag.Tag(
                tag.tagClassContext, tag.tagFormatSimple, 2))),
        namedtype.NamedType('endOfData', univ.Null().subtype(
            implicitTag=tag.Tag(
                tag.tagClassContext, tag.tagFormatSimple, 3)))
    )


class RcfDeliveryMode(univ.Integer):
    namedValues = namedval.NamedValues(
        ('rtnTimelyOnline', 0),
        ('rtnCompleteOnline', 1),
        ('rtnOffline', 2),
    )


class SpacecraftId(univ.Integer):
    subtypeSpec = constraint.ValueRangeConstraint(0, 1023)


class VersionNumber(univ.Integer):
    subtypeSpec = constraint.ValueRangeConstraint(0, 3)


class VcId(univ.Integer):
    subtypeSpec = constraint.ValueRangeConstraint(0, 63)


class VcIdSet(univ.SetOf):
    componentType = VcId()


class MasterChannelComposition(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('spacecraftId', SpacecraftId()),
        namedtype.NamedType('versionNumber', VersionNumber()),
        namedtype.NamedType('mcOrVcList', univ.Choice(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('masterChannel', univ.Null().subtype(
                    implicitTag=tag.Tag(
                        tag.tagClassContext, tag.tagFormatSimple, 0))),
                namedtype.NamedType('vcList', VcIdSet().subtype(
                    implicitTag=tag.Tag(
                        tag.tagClassContext, tag.tagFormatSimple, 1)))
            ))
        )
    )


class GvcId(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('spacecraftId', SpacecraftId()),
        namedtype.NamedType('versionNumber', VersionNumber()),
        namedtype.NamedType('vcId', univ.Choice(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('masterChannel', univ.Null().subtype(
                    implicitTag=tag.Tag(
                        tag.tagClassContext, tag.tagFormatSimple, 0))),
                namedtype.NamedType('virtualChannel', VcId().subtype(
                    implicitTag=tag.Tag(
                        tag.tagClassContext, tag.tagFormatSimple, 1)))
            ))
        )
    )


class GvcIdSet(univ.SetOf):
    componentType = MasterChannelComposition()


class RequestedGvcId(univ.Choice):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('gvcid', GvcId().subtype(
            implicitTag=tag.Tag(
                tag.tagClassContext, tag.tagFormatConstructed, 0))),
        namedtype.NamedType('undefined', univ.Null().subtype(
                implicitTag=tag.Tag(
                    tag.tagClassContext, tag.tagFormatSimple, 1))),
    )


class RcfGetParameter(univ.Choice):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('parBufferSize', univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('parameterName', ParameterName()),
                namedtype.NamedType('parameterValue', IntPosShort())
            )).subtype(
                implicitTag=tag.Tag(
                    tag.tagClassContext, tag.tagFormatConstructed, 0))),

        namedtype.NamedType('parDeliveryMode', univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('parameterName', ParameterName()),
                namedtype.NamedType('parameterValue', RcfDeliveryMode())
            )).subtype(
                implicitTag=tag.Tag(
                    tag.tagClassContext, tag.tagFormatConstructed, 1))),

        namedtype.NamedType('parLatencyLimit', univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('parameterName', ParameterName()),
                namedtype.NamedType('parameterValue', univ.Choice(
                    componentType=namedtype.NamedTypes(
                        namedtype.NamedType('online', IntPosShort().subtype(
                            implicitTag=tag.Tag(
                                tag.tagClassContext, tag.tagFormatSimple, 0))),
                        namedtype.NamedType('offline', univ.Null().subtype(
                            implicitTag=tag.Tag(
                                tag.tagClassContext, tag.tagFormatSimple, 1)))
                    )))
            )).subtype(
                implicitTag=tag.Tag(
                    tag.tagClassContext, tag.tagFormatConstructed, 2))),

        namedtype.NamedType('parMinReportingCycle', univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('parameterName', ParameterName()),
                namedtype.NamedType('parameterValue', IntPosShort())
            )).subtype(
                implicitTag=tag.Tag(
                    tag.tagClassContext, tag.tagFormatConstructed, 7))),

        namedtype.NamedType('parPermittedGvcedSet', univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('parameterName', ParameterName()),
                namedtype.NamedType('parameterValue', GvcIdSet())
            )).subtype(
                implicitTag=tag.Tag(
                    tag.tagClassContext, tag.tagFormatConstructed, 3))),

        namedtype.NamedType('parReportingCycle', univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('parameterName', ParameterName()),
                namedtype.NamedType('parameterValue', CurrentReportingCycle())
            )).subtype(
                implicitTag=tag.Tag(
                    tag.tagClassContext, tag.tagFormatConstructed, 4))),

        namedtype.NamedType('parReqGvcId', univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('parameterName', ParameterName()),
                namedtype.NamedType('parameterValue', RequestedGvcId())
            )).subtype(
                implicitTag=tag.Tag(
                    tag.tagClassContext, tag.tagFormatConstructed, 5))),

        namedtype.NamedType('parReturnTimeout', univ.Sequence(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('parameterName', ParameterName()),
                namedtype.NamedType('parameterValue', TimeoutPeriod())
            )).subtype(
                implicitTag=tag.Tag(
                    tag.tagClassContext, tag.tagFormatConstructed, 6))),
    )


class RcfParameterName(univ.Integer):
    namedValues = namedval.NamedValues(
        ('bufferSize', 4),
        ('deliveryMode', 6),
        ('latencyLimit', 15),
        ('minReportingCycle', 301),
        ('permittedGvcidSet', 24),
        ('reportingCycle', 26),
        ('requestedGvcid', 28),
        ('returnTimeoutPeriod', 29),
    )
