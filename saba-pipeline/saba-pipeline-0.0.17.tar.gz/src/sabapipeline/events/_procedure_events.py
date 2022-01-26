from .._private._concepts import Event


class ProcedureEvent(Event):
    def __str__(self):
        return ""


class PipelineStartEvent(ProcedureEvent):
    pass


class PipelineStopEvent(ProcedureEvent):
    pass
