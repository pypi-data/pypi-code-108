# SPDX-FileCopyrightText: 2020 Mintlab B.V.
#
# SPDX-License-Identifier: EUPL-1.2

from . import Base
from .infrastructure import InfrastructureFactory
from typing import TYPE_CHECKING, Any, Dict, Type

if TYPE_CHECKING:
    # This causes an import loop if imported outside of type checking
    import minty.cqrs


class RepositoryBase(Base):
    """Base class for repositories using the Minty CQRS/DDD framework"""

    REQUIRED_INFRASTRUCTURE: Dict[str, Any]
    REQUIRED_INFRASTRUCTURE_RO: Dict[str, Any]
    REQUIRED_INFRASTRUCTURE_RW: Dict[str, Any]

    def __init__(
        self,
        infrastructure_factory: InfrastructureFactory,
        context: str,
        event_service,
    ):
        self.infrastructure_factory = infrastructure_factory
        self.context = context
        self.cache: Dict[str, Any] = {}
        self.event_service = event_service

    def _get_infrastructure(self, name):
        return self.infrastructure_factory.get_infrastructure(
            context=self.context, infrastructure_name=name
        )


class Repository(RepositoryBase):
    _for_entity: str
    _events_to_calls: Dict[str, str]

    def save(
        self, user_info: "minty.cqrs.UserInfo" = None, dry_run: bool = False
    ) -> None:
        """Uses the mapping _events_to_calls for calling the repo methods"""

        for ev in self.event_service.get_events_by_type(
            entity_type=self._for_entity
        ):
            method_to_call = getattr(
                self, self._events_to_calls[ev.event_name]
            )

            method_to_call(ev, user_info, dry_run)


class RepositoryFactory(Base):
    """Create context-specific "repository" instances for domains"""

    __slots__ = ["infrastructure_factory", "repositories"]

    def __init__(self, infra_factory: InfrastructureFactory):
        """Initialize the repository factory with an infrastructure factory

        :param infra_factory: Infrastructure factory
        :type infra_factory: InfrastructureFactory
        """
        self.infrastructure_factory = infra_factory
        self.repositories: Dict[str, Type[RepositoryBase]] = {}

    def register_repository(self, name: str, repository: Type[RepositoryBase]):
        """Register a repository class with the repository factory.

        :param repository: repository class; will be instantiated when the
            domain code asks for it by name.
        :type repository: object
        """
        self.repositories[name] = repository

    def get_repository(self, name: str, context=None, event_service=None):
        """Retrieve a repository, given a name and optionally a context.

        :param name: name of repository to instantiate
        :type repository: str
        :param context: Context for which to retrieve the repository.
        :type context: object, optional
        :param event_service: Event service instance
        :type event_service: EventService
        :return: An instance of the configured repository, for the specified
            context.
        :rtype: object
        """
        repo_class = self.repositories[name]

        self.logger.debug(
            f"Creating repository of type '{name}' with context "
            + f"'{context}'"
        )

        repo = repo_class(
            context=context,
            infrastructure_factory=self.infrastructure_factory,
            event_service=event_service,
        )

        return repo
