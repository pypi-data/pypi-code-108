# SPDX-FileCopyrightText: 2020 Mintlab B.V.
#
# SPDX-License-Identifier: EUPL-1.2

import statsd  # type: ignore
from .. import Base
from ..infrastructure import InfrastructureFactory
from ..repository import RepositoryBase, RepositoryFactory
from .events import Event, EventService, event
from abc import ABC, abstractmethod
from copy import copy
from functools import partial
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Protocol,
    Set,
    Type,
    TypedDict,
    cast,
)
from uuid import UUID

__all__ = [
    "build_command_lookup_table",
    "CommandBase",
    "CQRS",
    "DomainCommandContainer",
    "DomainQueryContainer",
    "event",
    "Event",
    "EventService",
    "MiddlewareBase",
    "SplitCommandBase",
    "SplitQueryBase",
    "QueryBase",
    "UserInfo",
]


class UserInfo:
    "Data structure for user info"
    # Regular class because of this bug in Pydantic:
    # https://github.com/samuelcolvin/pydantic/issues/1536
    # (a defaultdict is used for platform key access)

    user_uuid: UUID
    permissions: Dict[str, bool]

    def __init__(self, user_uuid: UUID, permissions: Dict[str, bool]):
        self.user_uuid = user_uuid
        self.permissions = permissions


class SplitCommandBase(Base, ABC):
    """
    Base class for 'command' parts of domains.

    This version should be used when every command is split out to its own class.
    """

    name: str

    @abstractmethod
    def __call__(self) -> None:
        raise NotImplementedError

    @property
    def cmd(self) -> Any:
        """
        Reference to the DomainCommandContainer instance that this command is part of.

        Can be used to call other commands.
        """
        return self._command_instance

    @cmd.setter
    def cmd(self, value: "DomainCommandContainer"):
        self._command_instance = value

    def __init__(
        self,
        repository_factory: RepositoryFactory,
        context: str,
        user_uuid: UUID,
        event_service: EventService,
        command_instance: "DomainCommandContainer",
    ):
        self.repository_factory = repository_factory
        self.context = context
        self.user_uuid = user_uuid
        self.event_service = event_service
        self.cmd = command_instance

    def get_repository(self, name: str):
        """Initialize and retrieve a repository by name.

        This also passes the event service to the repository constructor.

        :param name: Name of the repository to retrieve
        :return: Initialized repository
        """

        return self.repository_factory.get_repository(
            name=name, context=self.context, event_service=self.event_service
        )

    def _user_has_permission(self, permission: str) -> bool:
        """
        Check if the currently logged in user has the specified permission,
        and return the result.
        """

        # Command instances do not have `user_info` when called from
        # consumers.
        # Once consumers have the full user_info, this entire condition should
        # be removed:
        if not hasattr(self.cmd, "user_info"):
            return True

        return self.cmd.user_info.permissions.get(permission, False)


class SplitQueryBase(Base, ABC):
    """
    Base class for 'query' parts of domains.

    This version should be used when every query is split out to its own class.
    """

    name: str

    @abstractmethod
    def __call__(self) -> Any:
        raise NotImplementedError

    @property
    def qry(self) -> Any:
        """
        Reference to the DomainQueryContainer instance that this query is part of.

        Can be used to call other queries.
        """
        return self._query_instance

    @qry.setter
    def qry(self, value: "DomainQueryContainer"):
        self._query_instance = value

    def __init__(
        self,
        repository_factory: RepositoryFactory,
        context: str,
        user_uuid: UUID,
        query_instance: "DomainQueryContainer",
    ):
        self.repository_factory = repository_factory
        self.context = context
        self.user_uuid = user_uuid
        self.qry = query_instance

    def get_repository(self, name: str):
        """Initialize and retrieve a repository by name.

        This does not pass an event service to the repository constructor, so
        no events can be triggered accidentally.

        :param name: Name of the repository to retrieve
        :return: Initialized repository
        """

        return self.repository_factory.get_repository(
            name=name, context=self.context, event_service=None
        )


_CommandLookupTable = Dict[str, Type[SplitCommandBase]]
_QueryLookupTable = Dict[str, Type[SplitQueryBase]]


def build_command_lookup_table(
    commands: Set[Type[SplitCommandBase]],
) -> _CommandLookupTable:
    """
    Build a command lookup table (keyed on the command's "short name") containing
    the listed commands.
    """

    command_lookup_table: _CommandLookupTable = {}
    for command in commands:
        assert (
            command.name not in command_lookup_table
        ), f"Tried to register second command with name={command.name}"

        command_lookup_table[command.name] = command

    return command_lookup_table


def build_query_lookup_table(
    queries: Set[Type[SplitQueryBase]],
) -> _QueryLookupTable:
    """
    Build a lookup table for queries (keyed on the query's "short name")
    containing the listed queries.
    """

    query_lookup_table: _QueryLookupTable = {}
    for query in queries:
        assert (
            query.name not in query_lookup_table
        ), f"Tried to register second query with name={query.name}"

        query_lookup_table[query.name] = query

    return query_lookup_table


class DomainCommandContainer:
    def __init__(
        self,
        repository_factory: RepositoryFactory,
        context: str,
        user_uuid: UUID,
        event_service: EventService,
        command_lookup_table: _CommandLookupTable,
    ):
        self.repository_factory = repository_factory
        self.context = context
        self.user_uuid = user_uuid
        self.event_service = event_service
        self.command_lookup_table = command_lookup_table

    def __getattr__(self, name: str) -> SplitCommandBase:
        try:
            return self.command_lookup_table[name](
                repository_factory=self.repository_factory,
                context=self.context,
                user_uuid=self.user_uuid,
                event_service=self.event_service,
                command_instance=self,
            )
        except KeyError as e:
            raise AttributeError(name) from e


class DomainQueryContainer:
    def __init__(
        self,
        repository_factory: RepositoryFactory,
        context: str,
        user_uuid: UUID,
        query_lookup_table: _QueryLookupTable,
    ):
        self.repository_factory = repository_factory
        self.context = context
        self.user_uuid = user_uuid
        self.query_lookup_table = query_lookup_table

    def __getattr__(self, name: str) -> SplitQueryBase:
        try:
            return self.query_lookup_table[name](
                repository_factory=self.repository_factory,
                context=self.context,
                user_uuid=self.user_uuid,
                query_instance=self,
            )
        except KeyError as e:
            raise AttributeError(name) from e


class CommandBase(Base, ABC):
    "Base class for 'command' parts of domains"

    def __init__(
        self,
        repository_factory: RepositoryFactory,
        context: str,
        user_uuid: UUID,
        event_service: EventService,
    ):
        self.repository_factory = repository_factory
        self.context = context
        self.user_uuid = user_uuid
        self.event_service = event_service

    def get_repository(self, name):
        """Initialize and retrieve a repository by name.

        This also passes the event service to the repository constructor.

        :param name: Name of the repository to retrieve
        :type name: str
        :return: Initialized repository
        :rtype: RepositoryBase
        """

        return self.repository_factory.get_repository(
            name=name, context=self.context, event_service=self.event_service
        )


class QueryBase(Base, ABC):
    "Base class for 'query' parts of domains"

    def __init__(self, repository_factory, context, user_uuid: UUID):
        self.repository_factory = repository_factory
        self.context = context
        self.user_uuid = user_uuid

    def get_repository(self, name):
        """Initialize and retrieve a repository by name.

        Passes None as the `event_service`, so any calls to state-changing
        commands can raise the right exceptions.

        :param name: Name of the repository to retrieve
        :type name: str
        :return: Initialized repository
        :rtype: RepositoryBase
        """

        return self.repository_factory.get_repository(
            name=name, context=self.context, event_service=None
        )


class QueryMiddleware(Base, ABC):
    __slots__ = [
        "infrastructure_factory",
        "correlation_id",
        "domain",
        "context",
        "user_uuid",
    ]

    def __init__(
        self,
        infrastructure_factory: InfrastructureFactory,
        correlation_id: UUID,
        domain: str,
        context: str,
        user_uuid: UUID,
    ):
        """Initialize the middleware with an infrastructure factory and some
        parameters from the current request.

        :param infrastructure_factory: [description]
        :type infrastructure_factory: InfrastructureFactory
        :param correlation_id: Unique identifier for the current "chain of
            events"
        :type correlation_id: UUID
        :param domain: Domain the command is a part of
        :type domain: str
        :param context: Context the command is being executed in
        :type context: str
        :param user_uuid: UUID of the user executing the command
        :type user_uuid: UUID
        """

        self.infrastructure_factory = infrastructure_factory
        self.correlation_id = correlation_id
        self.domain = domain
        self.context = context
        self.user_uuid = user_uuid

    @abstractmethod
    def __call__(self, func):
        """Call the specified function.

        Override this method (including the defined params) in your middleware
        class. The logic or functionality you want to implement should go
        before and after your call to `func()`.

        Remember to return whatever `func()` returns!

        :param func: function to execute
        :type func: partial function
        """
        pass


class MiddlewareBase(Base, ABC):
    __slots__ = [
        "infrastructure_factory",
        "event_service",
        "correlation_id",
        "domain",
        "context",
        "user_uuid",
    ]

    def __init__(
        self,
        infrastructure_factory: InfrastructureFactory,
        event_service: EventService,
        correlation_id: UUID,
        domain: str,
        context: str,
        user_uuid: UUID,
    ):
        """Initialize the middleware with an infrastructure factory and some
        parameters from the current request.

        :param infrastructure_factory: Infrastructure factory to use
        :type infrastructure_factory: InfrastructureFactory
        :param event_service: Event service instance to use
        :type event_service: EventService
        :param correlation_id: Unique identifier for the current "chain of
            events"
        :type correlation_id: UUID
        :param domain: Domain the command is a part of
        :type domain: str
        :param context: Context the command is being executed in
        :type context: str
        :param user_uuid: UUID of the user executing the command
        :type user_uuid: UUID
        """

        self.infrastructure_factory = infrastructure_factory
        self.event_service = event_service
        self.correlation_id = correlation_id
        self.domain = domain
        self.context = context
        self.user_uuid = user_uuid

    @abstractmethod
    def __call__(self, func):
        """Call instantiated class.

        Override this method (including the defined params) in your middleware
        class. The logic or functionality you want to implement should go
        before and after your call to `func()`.

        :param func: function to execute
        :type func: partial function
        """
        pass


class EventServiceCleanup(MiddlewareBase):
    """Clears the event list when completed."""

    def __call__(self, func):
        try:
            func()
        finally:
            self.event_service.event_list = []


class CommandInfrastructureCleanup(MiddlewareBase):
    """Set current event in infrastructure factory and clear it after the event is finished."""

    def __call__(self, func):
        try:
            func()
        finally:
            self.infrastructure_factory.flush_local_storage()


class QueryInfrastructureCleanup(QueryMiddleware):
    """Set current event in infrastructure factory and clear it after the query is finished."""

    def __call__(self, func):
        try:
            rv = func()
            return rv
        finally:
            self.infrastructure_factory.flush_local_storage()


class QueryWrapper(Base):
    """Wrapper class for query instances that applies middleware."""

    def __init__(self, query_instance, middleware: list, domain: str):
        self.middleware = middleware
        self.query_instance = query_instance
        self.domain = domain

    def __getattr__(self, attr):
        """Get an attribute on the wrapped class, wrapped by "event" code.

        This event code ensures the command can't return anything, and creates
        an Event instance.

        :param attr: attribute to retrieve
        :type attr: str
        :return: wrapped method
        :rtype: callable
        """
        original_attribute = getattr(self.query_instance, attr)

        if callable(original_attribute):

            def wrapped(*args, **kwargs):
                """Return attribute wrapped in middlewares."""

                timer = cast(
                    statsd.Timer,
                    self.statsd.get_timer(
                        f"query,domain={self.domain},query={attr}"
                    ),
                )

                with timer.time():
                    wrapped_func = partial(original_attribute, *args, **kwargs)

                    for middleware in self.middleware:
                        wrapped_func = partial(middleware, wrapped_func)
                    return wrapped_func()

            return wrapped
        else:
            return original_attribute


class CommandWrapper(Base):
    """Wrapper class for command instances. Handles creation of Events."""

    def __init__(self, command_instance, domain: str):
        self.command_instance = command_instance
        self.middlewares: List[MiddlewareBase] = []
        self.domain = domain

    def register_middleware(self, middleware: MiddlewareBase):
        """Register middleware to be wrapped around command.

        From inner to outer layer, the last middleware class to get registered will be
        the outer shell and will be executed first and last.

        :param middleware: middleware to register
        :type middleware: MiddlewareBase
        """
        self.middlewares.append(middleware)

    def __getattr__(self, attr):
        """Get an attribute on the wrapped class, wrapped by "event" code.

        This event code ensures the command can't return anything, and creates
        an Event instance.

        :param attr: attribute to retrieve
        :type attr: str
        :return: wrapped method
        :rtype: callable
        """

        original_attribute = getattr(self.command_instance, attr)
        if callable(original_attribute):

            def wrapped(*args, **kwargs):
                """Return attribute wrapped in middlewares."""

                timer = cast(
                    statsd.Timer,
                    self.statsd.get_timer(
                        f"command,domain={self.domain},query={attr}"
                    ),
                )

                with timer.time():
                    wrapped_func = partial(original_attribute, **kwargs)
                    for middleware in self.middlewares:
                        wrapped_func = partial(middleware, wrapped_func)

                    wrapped_func()
                return

            return wrapped
        else:
            return original_attribute


class CQRSDomain(Protocol):
    """
    Type for CQRS domains.

    Every domain should define which repositories it has/needs, a function
    to return a "query" instance, and one to return a "command" instance.
    """

    REQUIRED_REPOSITORIES: Dict[str, Type[RepositoryBase]]

    __name__: str

    @staticmethod
    def get_query_instance(
        repository_factory: RepositoryFactory, context: str, user_uuid: UUID
    ) -> QueryBase:
        ...

    @staticmethod
    def get_command_instance(
        repository_factory: RepositoryFactory,
        context: str,
        user_uuid: UUID,
        event_service: EventService,
    ) -> CommandBase:
        ...


class CQRSDomainDescriptor(TypedDict):
    module: CQRSDomain
    repository_factory: RepositoryFactory
    repository_factory_ro: RepositoryFactory


class CQRS(Base):
    """Keep commands and queries separated.

    CQRS: Command Query Responsibility Separation
    """

    __slots__ = [
        "domains",
        "infrastructure_factory",
        "infrastructure_factory_ro",
        "command_wrapper_middleware",
        "query_middleware",
    ]

    def __init__(
        self,
        domains: Iterable[CQRSDomain],
        infrastructure_factory: InfrastructureFactory,
        command_wrapper_middleware=None,
        query_middleware=None,
    ):
        """Create a new CQRS instance from a list of domains.

        :param domains: iterable returning domains. Domains are classes or
            packages with at least a "REQUIRED_REPOSITORIES" variable defining
            which repositories are necessary to use the domain.
        :type domains: object
        :param infrastructure_factory: Infrastructure factory, created with
            the required configuration, that the repositories can use to
            create infrastructure instances.
        :type infrastructure_factory: InfrastructureFactory
        :param command_wrapper_middleware: Middlewares to be wrapped around
            command.
        :type command_wrapper_middleware: list of MiddlewareBase
        """
        self.domains: Dict[str, CQRSDomainDescriptor] = {}

        if command_wrapper_middleware is None:
            command_wrapper_middleware = []

        if query_middleware is None:
            query_middleware = []

        self.command_wrapper_middleware = command_wrapper_middleware
        self.query_middleware = query_middleware

        self.infrastructure_factory = infrastructure_factory
        self.infrastructure_factory_ro = copy(infrastructure_factory)

        for domain in domains:
            repo_factory = RepositoryFactory(self.infrastructure_factory)
            repo_factory_ro = RepositoryFactory(self.infrastructure_factory_ro)

            for name, repo in domain.REQUIRED_REPOSITORIES.items():
                repo_factory.register_repository(name=name, repository=repo)
                repo_factory_ro.register_repository(name=name, repository=repo)

                for name, infra in repo.REQUIRED_INFRASTRUCTURE.items():
                    self.infrastructure_factory.register_infrastructure(
                        name=name, infrastructure=infra
                    )
                    self.infrastructure_factory_ro.register_infrastructure(
                        name=name, infrastructure=infra
                    )

                for name, infra in getattr(
                    repo, "REQUIRED_INFRASTRUCTURE_RW", {}
                ).items():
                    self.infrastructure_factory.register_infrastructure(
                        name=name, infrastructure=infra
                    )

                for name, infra in getattr(
                    repo, "REQUIRED_INFRASTRUCTURE_RO", {}
                ).items():
                    self.infrastructure_factory_ro.register_infrastructure(
                        name=name, infrastructure=infra
                    )

            self.domains[domain.__name__] = {
                "module": domain,
                "repository_factory": repo_factory,
                "repository_factory_ro": repo_factory_ro,
            }

    def get_query_instance(
        self, correlation_id: UUID, domain: str, context: str, user_uuid: UUID
    ):
        """Instantiate and return the "query" part of the specified domain.

        :param domain: name of the domain to get the query instance for
        :type domain: str
        :param context: context for this query instance
        :type context: str
        :param user_uuid: UUID of the user that's going to execute commands
        :type user_uuid: uuid
        """

        self.logger.debug(
            f"Creating query instance for domain '{domain}' with context "
            + f"'{context}' for user '{user_uuid}'"
        )

        short_domain = domain.split(".")[-1]
        timer = cast(
            statsd.Timer,
            self.statsd.get_timer(f"get_query_instance,domain={short_domain}"),
        )
        with timer.time():
            query_instance = self.domains[domain]["module"].get_query_instance(
                self.domains[domain]["repository_factory_ro"],
                context=context,
                user_uuid=user_uuid,
            )

            initialized_middleware = []

            # Outermost layer: cleanup infrastructure when we're done
            for mw in [*self.query_middleware, QueryInfrastructureCleanup]:
                initialized_middleware.append(
                    mw(
                        infrastructure_factory=self.infrastructure_factory_ro,
                        correlation_id=correlation_id,
                        domain=domain,
                        context=context,
                        user_uuid=user_uuid,
                    )
                )

            wrapped_query = QueryWrapper(
                query_instance=query_instance,
                middleware=initialized_middleware,
                domain=short_domain,
            )

        return wrapped_query

    def get_command_instance(
        self, correlation_id: UUID, domain: str, context: str, user_uuid: UUID
    ):
        """Instantiate and return the "command" instance of the specified domain.

        Command instance is instantiated with optional layers of middleware to handle
        various functions when executing a command. `InfrastructureStateManager` is
        always registered as the outermost layer.

        :param correlation_id: unique identifier for the current chain of
            events.
        :param domain: name of the domain to get the query instance for
        :type domain: str
        :param context: context for this command instance
        :type context: str
        :param user_uuid: UUID of the user that's going to execute commands
        :type user_uuid: uuid
        """
        self.logger.debug(
            f"Creating command instance for domain '{domain}' with context "
            + f"'{context}' for user '{user_uuid}'"
        )

        short_domain = domain.split(".")[-1]
        timer = cast(
            statsd.Timer,
            self.statsd.get_timer(
                f"get_command_instance,domain={short_domain}"
            ),
        )
        with timer.time():
            event_service = EventService(
                correlation_id=correlation_id,
                domain=domain,
                context=context,
                user_uuid=user_uuid,
            )

            cmd_instance = self.domains[domain]["module"].get_command_instance(
                self.domains[domain]["repository_factory"],
                context=context,
                user_uuid=user_uuid,
                event_service=event_service,
            )

            cmd_wrapped = CommandWrapper(
                command_instance=cmd_instance, domain=short_domain
            )

            # Always "outer layer" to clean up infrastructure
            for middleware in [
                *self.command_wrapper_middleware,
                CommandInfrastructureCleanup,
                EventServiceCleanup,
            ]:
                initialized_middleware = middleware(
                    infrastructure_factory=self.infrastructure_factory,
                    correlation_id=correlation_id,
                    domain=domain,
                    context=context,
                    user_uuid=user_uuid,
                    event_service=event_service,
                )
                cmd_wrapped.register_middleware(initialized_middleware)

        return cmd_wrapped
