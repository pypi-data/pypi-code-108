from infosystem.common import subsystem
from infosystem.subsystem.timeline_event \
    import resource, controller, manager


subsystem = subsystem.Subsystem(resource=resource.TimelineEvent,
                                controller=controller.Controller,
                                manager=manager.Manager)
