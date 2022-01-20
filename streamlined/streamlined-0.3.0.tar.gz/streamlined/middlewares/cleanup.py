from .action import Action
from .middleware import Context


class Cleanup(Action):
    async def _do_apply(self, context: Context):
        await context.next()
        await super()._do_apply(context.replace_with_void_next())
        return context.scoped


CLEANUP = Cleanup.get_name()
