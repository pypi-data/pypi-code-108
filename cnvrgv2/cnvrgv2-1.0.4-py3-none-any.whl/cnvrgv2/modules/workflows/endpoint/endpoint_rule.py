from cnvrgv2.modules.base.dynamic_attributes import DynamicAttributes
import pprint


class EndpointRule(DynamicAttributes):

    available_attributes = {
        "is_active": str,
        "title": str,
        "description": dict,
        "frequency": dict,
        "action": int,
        "severity": list,
        "min_events": str,
        "created_at": dict,
        "metric": str,
        "threshold": str,
        "operation": str,
    }

    def __init__(self, context, slug, attributes):
        self.slug = slug
        self._context = context
        self._attributes = attributes or {}

    def __str__(self):
        return pprint.pformat(self._attributes)
