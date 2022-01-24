#!/usr/bin/python3

#     Copyright 2021. FastyBird s.r.o.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

"""
Triggers module DI container
"""

# pylint: disable=no-value-for-parameter

# Python base dependencies
import logging

# Library dependencies
from kink import di
from sqlalchemy.orm import Session as OrmSession

# Library libs
from fastybird_triggers_module.managers.action import ActionsManager
from fastybird_triggers_module.managers.condition import ConditionsManager
from fastybird_triggers_module.managers.notification import NotificationsManager
from fastybird_triggers_module.managers.trigger import (
    TriggerControlsManager,
    TriggersManager,
)
from fastybird_triggers_module.repositories.action import ActionsRepository
from fastybird_triggers_module.repositories.condition import ConditionsRepository
from fastybird_triggers_module.repositories.notification import NotificationsRepository
from fastybird_triggers_module.repositories.trigger import (
    TriggersControlsRepository,
    TriggersRepository,
)
from fastybird_triggers_module.subscriber import (
    EntitiesSubscriber,
    EntityCreatedSubscriber,
)


def register_services(
    logger: logging.Logger = logging.getLogger("dummy"),
) -> None:
    """Register triggers module services"""
    if OrmSession not in di:
        logger.error("SQLAlchemy database session is not registered in container!")

        return

    di[TriggersRepository] = TriggersRepository(session=di[OrmSession])
    di["fb-triggers-module_trigger-repository"] = di[TriggersRepository]
    di[TriggersControlsRepository] = TriggersControlsRepository(session=di[OrmSession])
    di["fb-triggers-module_trigger-control-repository"] = di[TriggersControlsRepository]
    di[ActionsRepository] = ActionsRepository(session=di[OrmSession])
    di["fb-triggers-module_action-repository"] = di[ActionsRepository]
    di[ConditionsRepository] = ConditionsRepository(session=di[OrmSession])
    di["fb-triggers-module_condition-repository"] = di[ConditionsRepository]
    di[NotificationsRepository] = NotificationsRepository(session=di[OrmSession])
    di["fb-triggers-module_notification-repository"] = di[NotificationsRepository]

    di[TriggersManager] = TriggersManager(session=di[OrmSession])
    di["fb-triggers-module_triggers-manager"] = di[TriggersManager]
    di[TriggerControlsManager] = TriggerControlsManager(session=di[OrmSession])
    di["fb-triggers-module_trigger-controls-manager"] = di[TriggerControlsManager]
    di[ActionsManager] = ActionsManager(session=di[OrmSession])
    di["fb-triggers-module_actions-manager"] = di[ActionsManager]
    di[ConditionsManager] = ConditionsManager(session=di[OrmSession])
    di["fb-triggers-module_actions-manager"] = di[ConditionsManager]
    di[NotificationsManager] = NotificationsManager(session=di[OrmSession])
    di["fb-triggers-module_actions-manager"] = di[NotificationsManager]

    di[EntitiesSubscriber] = EntitiesSubscriber(session=di[OrmSession])
    di["fb-devices-module_entities-subscriber"] = di[EntitiesSubscriber]
    di[EntityCreatedSubscriber] = EntityCreatedSubscriber()
    di["fb-devices-module_entity-created-subscriber"] = di[EntityCreatedSubscriber]
