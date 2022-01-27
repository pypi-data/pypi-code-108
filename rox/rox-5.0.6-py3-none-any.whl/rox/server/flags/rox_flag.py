from rox.core.entities.flag import Flag


class RoxFlag(Flag):
    def is_enabled(self, context=None):
        return super(RoxFlag, self).is_enabled(context)

    def enabled(self, action, context=None):
        super(RoxFlag, self).enabled(context, action)

    def disabled(self, action, context=None):
        super(RoxFlag, self).disabled(context, action)
