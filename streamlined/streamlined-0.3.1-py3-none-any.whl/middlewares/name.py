from typing import Any, Dict, Iterable, List

from ..common import IDENTITY_FACTORY, IS_NOT_CALLABLE, IS_STR, VALUE
from ..services import Scoped
from .middleware import APPLY_INTO, Context, Middleware, WithMiddlewares


class Name(Middleware, WithMiddlewares):
    @classmethod
    def verify(cls, value: Any) -> None:
        super().verify(value)

        if IS_NOT_CALLABLE(value):
            raise TypeError(f"{value} should be either a callable or a string")

    def _init_simplifications(self) -> None:
        super()._init_simplifications()

        self.simplifications.append((IS_STR, IDENTITY_FACTORY))

    def _init_middleware_types(self) -> None:
        super()._init_middleware_types()

        from .action import Action

        self.middleware_types.append(Action)

    def _init_middleware_apply_methods(self) -> None:
        super()._init_middleware_apply_methods()
        self.middleware_apply_methods.append(APPLY_INTO)

    def create_middlewares_from(self, value: Dict[str, Any]) -> Iterable[Middleware]:
        for middleware_type, middleware_name in zip(
            self.middleware_types, self.get_middleware_names()
        ):
            # assert middleware_type is Action
            new_value = {middleware_name: value}
            yield middleware_type(new_value)

    def _do_parse(self, value: Dict[str, Any]) -> Dict[str, List[Middleware]]:
        self.verify(value)

        return {"middlewares": list(self.create_middlewares_from(value))}

    async def get_register_name(self, context: Context) -> str:
        coroutine = WithMiddlewares.apply(self, context.replace_with_void_next())
        await coroutine()

        return context.scoped.getmagic(VALUE)

    async def _do_apply(self, context: Context) -> Scoped:
        name = await self.get_register_name(context)

        context.scoped.setmagic(NAME, name, num_scope_up=1)

        await context.next()
        return context.scoped


NAME = Name.get_name()
