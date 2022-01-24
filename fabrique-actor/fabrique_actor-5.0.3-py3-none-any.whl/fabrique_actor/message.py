from fabrique_atelier.message import Message, Header, MessageType
import uuid


class PipelineMetricsMessage(Message):
    def __init__(self, source, metrics=None, alerts=None, named_features=None, error=None,
                 session_id=None,
                 message_type=None,
                 corr_id=None,
                 pipeline_name=None,
                 pipeline_ver=None,
                 session_start_time=None):

        if not session_id:
            session_id = str(uuid.uuid4())

        if not message_type:
            message_type = MessageType.DATA.value

        header = Header(session_id=session_id,
                        message_type=message_type,
                        corr_id=corr_id,
                        pipeline_name=pipeline_name,
                        pipeline_ver=pipeline_ver,
                        session_start_time=session_start_time,
                        source=source)

        body = {}
        if metrics:
            body['metrics'] = metrics
        if alerts:
            body['alerts'] = alerts
        if named_features:
            body['named_features'] = named_features
        if error:
            body['error'] = error

        super().__init__(header, body)


class StandaloneActorMetricsMessage(PipelineMetricsMessage):
    def __init__(self, source, metrics=None,
                 alerts=None, named_features=None, error=None,
                 session_id=None, message_type=None):

        super().__init__(source,
                         metrics=metrics,
                         alerts=alerts,
                         named_features=named_features,
                         error=error,
                         session_id=session_id,
                         message_type=message_type,
                         corr_id=None,
                         pipeline_name=None,
                         pipeline_ver=None,
                         session_start_time=None)
