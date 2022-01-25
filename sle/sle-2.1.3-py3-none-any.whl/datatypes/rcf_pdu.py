from pyasn1.type import univ, namedtype, tag, constraint

from .common import ConditionalTime, Credentials, InvokeId, IntUnsignedLong,\
    SpaceLinkDataUnit, Time
from .pdu import SleScheduleStatusReportInvocation, SleStopInvocation,\
    SleAcknowledgement, SleScheduleStatusReportReturn
from .raf_structure import AntennaId, CarrierLockStatus, FrameQuality,\
    FrameSyncLockStatus, LockStatus, Notification, SymbolLockStatus
from .rcf_structure import RcfParameterName, RcfGetParameter,\
    RcfProductionStatus, DiagnosticRcfGet, DiagnosticRcfStart, GvcId
from .bind import SleBindInvocation, SleBindReturn, SlePeerAbort,\
    SleUnbindInvocation, SleUnbindReturn


# Incoming PDUs

class RcfStartInvocation(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('invokerCredentials', Credentials()),
        namedtype.NamedType('invokeId', InvokeId()),
        namedtype.NamedType('startTime', ConditionalTime()),
        namedtype.NamedType('stopTime', ConditionalTime()),
        namedtype.NamedType('requestedGvcId', GvcId())
    )


class RcfGetParameterInvocation(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('invokerCredentials', Credentials()),
        namedtype.NamedType('invokeId', InvokeId()),
        namedtype.NamedType('RcfParameter', RcfParameterName())
    )


class RcfUserToProviderPdu(univ.Choice):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('RcfBindInvocation', SleBindInvocation().subtype(
            implicitTag=tag.Tag(
                tag.tagClassContext, tag.tagFormatConstructed, 100))),
        namedtype.NamedType('RcfBindReturn', SleBindReturn().subtype(
            implicitTag=tag.Tag(
                tag.tagClassContext, tag.tagFormatConstructed, 101))),
        namedtype.NamedType(
            'RcfUnbindInvocation', SleUnbindInvocation().subtype(
                implicitTag=tag.Tag(
                    tag.tagClassContext, tag.tagFormatConstructed, 102))),
        namedtype.NamedType('RcfUnbindReturn', SleUnbindReturn().subtype(
            implicitTag=tag.Tag(
                tag.tagClassContext, tag.tagFormatConstructed, 103))),
        namedtype.NamedType('RcfStartInvocation', RcfStartInvocation().subtype(
            implicitTag=tag.Tag(
                tag.tagClassContext, tag.tagFormatConstructed, 0))),
        namedtype.NamedType('RcfStopInvocation', SleStopInvocation().subtype(
            implicitTag=tag.Tag(
                tag.tagClassContext, tag.tagFormatConstructed, 2))),
        namedtype.NamedType(
            'RcfScheduleStatusReportInvocation',
            SleScheduleStatusReportInvocation().subtype(
                implicitTag=tag.Tag(
                    tag.tagClassContext, tag.tagFormatConstructed, 4))),
        namedtype.NamedType(
            'RcfGetParameterInvocation', RcfGetParameterInvocation().subtype(
                implicitTag=tag.Tag(
                    tag.tagClassContext, tag.tagFormatConstructed, 6))),
        namedtype.NamedType('RcfPeerAbortInvocation', SlePeerAbort().subtype(
            implicitTag=tag.Tag(
                tag.tagClassContext, tag.tagFormatSimple, 104)))
    )


# Outgoing PDUs


class RcfStartReturn(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('performerCredentials', Credentials()),
        namedtype.NamedType('invokeId', InvokeId()),
        namedtype.NamedType('result', univ.Choice(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType(
                    'positiveResult', univ.Null().subtype(
                        implicitTag=tag.Tag(
                            tag.tagClassContext, tag.tagFormatSimple, 0))),
                namedtype.NamedType(
                    'negativeResult', DiagnosticRcfStart().subtype(
                        implicitTag=tag.Tag(
                            tag.tagClassContext, tag.tagFormatConstructed, 1)))
            )))
    )


class RcfTransferDataInvocation(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('invokerCredentials', Credentials()),
        namedtype.NamedType('earthReceiveTime', Time()),
        namedtype.NamedType('antennaId', AntennaId()),
        namedtype.NamedType('dataLinkContinuity', univ.Integer().subtype(
            subtypeSpec=constraint.ValueRangeConstraint(-1, 16777215))),
        namedtype.OptionalNamedType('deliveredFrameQuality', FrameQuality()),
        namedtype.NamedType('privateAnnotation', univ.Choice(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType('null', univ.Null().subtype(
                    implicitTag=tag.Tag(
                        tag.tagClassContext, tag.tagFormatSimple, 0))),
                namedtype.NamedType('notNull', univ.OctetString().subtype(
                    subtypeSpec=constraint.ValueSizeConstraint(
                        1, 128)).subtype(
                            implicitTag=tag.Tag(
                                tag.tagClassContext, tag.tagFormatSimple, 1)))
            ))),
        namedtype.NamedType('data', SpaceLinkDataUnit())
    )


class RcfSyncNotifyInvocation(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('invokerCredentials', Credentials()),
        namedtype.NamedType('notification', Notification())
    )


class FrameOrNotification(univ.Choice):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType(
            'annotatedFrame', RcfTransferDataInvocation().subtype(
                implicitTag=tag.Tag(
                    tag.tagClassContext, tag.tagFormatConstructed, 0))),
        namedtype.NamedType(
            'syncNotification', RcfSyncNotifyInvocation().subtype(
                implicitTag=tag.Tag(
                    tag.tagClassContext, tag.tagFormatConstructed, 1)))
    )


class RcfTransferBuffer(univ.SequenceOf):
    componentType = FrameOrNotification()


class RcfStatusReportInvocation(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('invokerCredentials', Credentials()),
        namedtype.NamedType('deliveredFrameNumber', IntUnsignedLong()),
        namedtype.NamedType('frameSyncLockStatus', FrameSyncLockStatus()),
        namedtype.NamedType('symbolSyncLockStatus', SymbolLockStatus()),
        namedtype.NamedType('subcarrierLockStatus', LockStatus()),
        namedtype.NamedType('carrierLockStatus', CarrierLockStatus()),
        namedtype.NamedType('productionStatus', RcfProductionStatus())
    )


class RcfGetParameterReturn(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('performerCredentials', Credentials()),
        namedtype.NamedType('invokeId', InvokeId()),
        namedtype.NamedType('result', univ.Choice(
            componentType=namedtype.NamedTypes(
                namedtype.NamedType(
                    'positiveResult', RcfGetParameter().subtype(
                        implicitTag=tag.Tag(
                            tag.tagClassContext,
                            tag.tagFormatConstructed, 0))),
                namedtype.NamedType(
                    'negativeResult', DiagnosticRcfGet().subtype(
                        implicitTag=tag.Tag(
                            tag.tagClassContext, tag.tagFormatConstructed, 1)))
            )))
    )


class RcfProviderToUserPdu(univ.Choice):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('RcfBindInvocation', SleBindInvocation().subtype(
            implicitTag=tag.Tag(
                tag.tagClassContext, tag.tagFormatConstructed, 100))),
        namedtype.NamedType('RcfBindReturn', SleBindReturn().subtype(
            implicitTag=tag.Tag(
                tag.tagClassContext, tag.tagFormatConstructed, 101))),
        namedtype.NamedType(
            'RcfUnbindInvocation', SleUnbindInvocation().subtype(
                implicitTag=tag.Tag(
                    tag.tagClassContext, tag.tagFormatConstructed, 102))),
        namedtype.NamedType('RcfUnbindReturn', SleUnbindReturn().subtype(
            implicitTag=tag.Tag(
                tag.tagClassContext, tag.tagFormatConstructed, 103))),
        namedtype.NamedType('RcfStartReturn', RcfStartReturn().subtype(
            implicitTag=tag.Tag(
                tag.tagClassContext, tag.tagFormatConstructed, 1))),
        namedtype.NamedType('RcfStopReturn', SleAcknowledgement().subtype(
            implicitTag=tag.Tag(
                tag.tagClassContext, tag.tagFormatConstructed, 3))),
        namedtype.NamedType('RcfTransferBuffer', RcfTransferBuffer().subtype(
            implicitTag=tag.Tag(
                tag.tagClassContext, tag.tagFormatConstructed, 8))),
        namedtype.NamedType(
            'RcfScheduleStatusReportReturn',
            SleScheduleStatusReportReturn().subtype(
                implicitTag=tag.Tag(
                    tag.tagClassContext, tag.tagFormatConstructed, 5))),
        namedtype.NamedType(
            'RcfStatusReportInvocation', RcfStatusReportInvocation().subtype(
                implicitTag=tag.Tag(
                    tag.tagClassContext, tag.tagFormatConstructed, 9))),
        namedtype.NamedType(
            'RcfGetParameterReturn', RcfGetParameterReturn().subtype(
                implicitTag=tag.Tag(
                    tag.tagClassContext, tag.tagFormatConstructed, 7))),
        namedtype.NamedType('RcfPeerAbortInvocation', SlePeerAbort().subtype(
            implicitTag=tag.Tag(
                tag.tagClassContext, tag.tagFormatSimple, 104)))
    )
