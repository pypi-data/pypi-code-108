# Copyright 2020-2021 Axis Communications AB.
#
# For a full list of individual contributors, please see the commit history.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""ETOS Library event helper module."""
from eiffellib.events import EiffelActivityTriggeredEvent
from eiffellib.events import EiffelActivityStartedEvent
from eiffellib.events import EiffelActivityFinishedEvent
from eiffellib.events import EiffelActivityCanceledEvent
from eiffellib.events import EiffelAnnouncementPublishedEvent
from eiffellib.events import EiffelConfidenceLevelModifiedEvent
from eiffellib.events import EiffelEnvironmentDefinedEvent
from eiffellib.events import EiffelTestSuiteStartedEvent
from eiffellib.events import EiffelTestSuiteFinishedEvent
from eiffellib.events import EiffelTestExecutionRecipeCollectionCreatedEvent
from eiffellib.events import EiffelTestCaseTriggeredEvent
from eiffellib.events import EiffelTestCaseStartedEvent
from eiffellib.events import EiffelTestCaseFinishedEvent
from eiffellib.events import EiffelArtifactCreatedEvent
from eiffellib.events import EiffelArtifactPublishedEvent
from eiffellib.events import EiffelCompositionDefinedEvent
from .debug import Debug


class Events:
    """Helper class for sending eiffel events."""

    def __init__(self, publisher):
        """Initialize event helper."""
        self.publisher = publisher
        self.debug = Debug()

    def __del__(self):
        """Delete reference to eiffel publisher."""
        self.publisher = None

    def send(self, event, links, data):
        """Build an event and send it with an eiffel publisher.

        :param event: Initialized event to send.
        :type event: :obj:`eiffel.events.base_event.BaseEvent`
        :param links: Dictionary of links to add to event.
        :type links: dict
        :param data: Dictionary of data to add to event.
        :type data: dict
        :return: The event that was created with data and links added.
        :rtype: :obj:`eiffel.events.base_event.BaseEvent`
        """
        for key, value in links.items():
            if isinstance(value, list):
                for link in value:
                    event.links.add(key.upper(), link)
            else:
                event.links.add(key.upper(), value)
        for key, value in data.items():
            event.data.add(key, value)
        event.validate()
        self.debug.events_published.append(event)
        event.tag = self.debug.routing_key_tag
        if not self.debug.disable_sending_events:
            self.publisher.send_event(event)
        return event

    def send_activity_triggered(self, name, links=None, **optional):
        """Send activity triggered event.

        https://github.com/eiffel-community/eiffel/blob/master/eiffel-vocabulary/EiffelActivityTriggeredEvent.md

        :param name: Name of the activity
        :type name: str
        :param links: Optional links to add to event.
        :type links: dict
        :param optional: Dictionary of optional data to add.
        :type optional: dict
        :return: The event that was created with data and links added.
        :rtype: :obj:`eiffel.events.EiffelActivityTriggeredEvent`
        """
        links = links if links is not None else {}
        data = {"name": name}
        data.update(**optional)
        return self.send(EiffelActivityTriggeredEvent(), links, data)

    def send_activity_canceled(self, triggered, links=None, **optional):
        """Send activity canceled event.

        https://github.com/eiffel-community/eiffel/blob/master/eiffel-vocabulary/EiffelActivityCanceledEvent.md

        :param triggered: Event ID of activity triggered event which is canceled.
        :type triggered: str
        :param links: Optional links to add to event.
        :type links: dict
        :param optional: Dictionary of optional data to add.
        :type optional: dict
        """
        links = links if links is not None else {}
        links.update({"ACTIVITY_EXECUTION": triggered})
        data = optional
        return self.send(EiffelActivityCanceledEvent(), links, data)

    def send_activity_started(self, triggered, links=None, **optional):
        """Send activity started event.

        https://github.com/eiffel-community/eiffel/blob/master/eiffel-vocabulary/EiffelActivityStartedEvent.md

        :param triggered: Event ID of activity triggered event which is started.
        :type triggered: str
        :param links: Optional links to add to event.
        :type links: dict
        :param optional: Dictionary of optional data to add.
        :type optional: dict
        """
        links = links if links is not None else {}
        links.update({"ACTIVITY_EXECUTION": triggered})
        data = optional
        return self.send(EiffelActivityStartedEvent(), links, data)

    def send_activity_finished(self, triggered, outcome, links=None, **optional):
        """Send activity finished event.

        https://github.com/eiffel-community/eiffel/blob/master/eiffel-vocabulary/EiffelActivityFinishedEvent.md

        :param triggered: Event ID of activity triggered event which is finished.
        :type triggered: str
        :param outcome: Outcome of the activity.
        :type outcome: dict
        :param links: Optional links to add to event.
        :type links: dict
        :param optional: Dictionary of optional data to add.
        :type optional: dict
        """
        links = links if links is not None else {}
        links.update({"ACTIVITY_EXECUTION": triggered})
        data = {"outcome": outcome}
        data.update(**optional)
        return self.send(EiffelActivityFinishedEvent(), links, data)

    def send_environment_defined(self, name, links=None, **optional):
        """Send environment defined event.

        https://github.com/eiffel-community/eiffel/blob/master/eiffel-vocabulary/EiffelEnvironmentDefinedEvent.md

        :param name: Name of environment.
        :type name: str
        :param links: Optional links to add to event.
        :type links: dict
        :param optional: Dictionary of optional data to add.
        :type optional: dict
        """
        if (
            optional.get("image") is None
            and optional.get("host") is None
            and optional.get("uri") is None
        ):
            raise Exception("At least one of 'host', 'image' or 'uri' must be provided")
        links = links if links is not None else {}
        data = {"name": name}
        data.update(**optional)
        return self.send(EiffelEnvironmentDefinedEvent(), links, data)

    def send_test_suite_started(self, name, links=None, **optional):
        """Publish a test suite started event.

        https://github.com/eiffel-community/eiffel/blob/master/eiffel-vocabulary/EiffelTestSuiteStartedEvent.md

        :param name: Name of testsuite.
        :type name: str
        :param links: Optional links to add to event.
        :type links: dict
        :param optional: Dictionary of optional data to add.
        :type optional: dict
        """
        links = links if links is not None else {}
        data = {"name": name}
        data.update(**optional)
        return self.send(EiffelTestSuiteStartedEvent(), links, data)

    def send_test_suite_finished(self, test_suite, links=None, **optional):
        """Publish a test suite finished event.

        https://github.com/eiffel-community/eiffel/blob/master/eiffel-vocabulary/EiffelTestSuiteFinishedEvent.md

        :param test_suite: A reference to the started test suite.
        :type test_suite: :obj:`eiffel.events.base_event.BaseEvent`
        :param links: Optional links to add to event.
        :type links: dict
        :param optional: Dictionary of optional data to add.
        :type optional: dict
        """
        links = links if links is not None else {}
        links.update({"TEST_SUITE_EXECUTION": test_suite})
        data = optional
        return self.send(EiffelTestSuiteFinishedEvent(), links, data)

    def send_announcement_published(
        self, heading, body, severity, links=None, **optional
    ):
        """Publish an announcement event.

        https://github.com/eiffel-community/eiffel/blob/master/eiffel-vocabulary/EiffelAnnouncementPublishedEvent.md

        :param heading: Heading for the announcement.
        :type heading: str
        :param body: Body for the announcement.
        :type body: str
        :param severity: Severity of the incident.
        :type severity: str
        :param links: Optional links to add to event.
        :type links: dict
        :param optional: Dictionary of optional data to add.
        :type optional: dict
        """
        links = links if links is not None else {}
        data = {"heading": heading, "body": body, "severity": severity}
        data.update(**optional)
        return self.send(EiffelAnnouncementPublishedEvent(), links, data)

    def send_test_execution_recipe_collection_created(
        self, selection_strategy, links=None, **optional
    ):
        """Publish a TERCC event.

        https://github.com/eiffel-community/eiffel/blob/master/eiffel-vocabulary/EiffelTestExecutionRecipeCollectionCreatedEvent.md

        :param selection_strategy: Selection strategy used by tercc
        :type selection_strategy: dict
        :param links: Optional links to add to event.
        :type links: dict
        :param optional: Dictionary of optional data to add.
        :type optional: dict
        """
        if optional.get("batches") is None and optional.get("batchesUri") is None:
            raise Exception(
                "At least one of 'batches' or 'batchesUri' must be provided"
            )
        links = links if links is not None else {}
        data = {"selectionStrategy": selection_strategy}
        data.update(**optional)
        return self.send(EiffelTestExecutionRecipeCollectionCreatedEvent(), links, data)

    def send_confidence_level_modified(self, name, value, links=None, **optional):
        """Publish a confidence level event.

        https://github.com/eiffel-community/eiffel/blob/master/eiffel-vocabulary/EiffelConfidenceLevelModifiedEvent.md

        :param name: Name of confidence level.
        :type name: str
        :param value: Value of confidence.
        :type value: str
        :param links: Optional links to add to event.
        :type links: dict
        :param optional: Dictionary of optional data to add.
        :type optional: dict
        """
        links = links if links is not None else {}
        data = {"name": name, "value": value}
        data.update(**optional)
        return self.send(EiffelConfidenceLevelModifiedEvent(), links, data)

    def send_test_case_triggered(self, test_case, iut, links=None, **optional):
        """Publish a confidence level event.

        https://github.com/eiffel-community/eiffel/blob/master/eiffel-vocabulary/EiffelTestCaseTriggeredEvent.md

        :param test_case: TestCase that has been triggered.
        :type test_case: dict
        :param iut: Item under test.
        :type iut: :obj:`eiffel.events.base_event.BaseEvent`
        :param links: Optional links to add to event.
        :type links: dict
        :param optional: Dictionary of optional data to add.
        :type optional: dict
        """
        links = links if links is not None else {}
        links.update({"IUT": iut})
        data = {"testCase": test_case}
        data.update(**optional)
        return self.send(EiffelTestCaseTriggeredEvent(), links, data)

    def send_test_case_started(self, test_case, links=None, **optional):
        """Publish a confidence level event.

        https://github.com/eiffel-community/eiffel/blob/master/eiffel-vocabulary/EiffelTestCaseStartedEvent.md

        :param test_case: Item under test.
        :type test_case: :obj:`eiffel.events.base_event.BaseEvent`
        :param links: Optional links to add to event.
        :type links: dict
        :param optional: Dictionary of optional data to add.
        :type optional: dict
        """
        links = links if links is not None else {}
        links.update({"TEST_CASE_EXECUTION": test_case})
        data = optional
        return self.send(EiffelTestCaseStartedEvent(), links, data)

    def send_test_case_finished(self, test_case, outcome, links=None, **optional):
        """Publish a confidence level event.

        https://github.com/eiffel-community/eiffel/blob/master/eiffel-vocabulary/EiffelTestCaseFinishedEvent.md

        :param test_case: Item under test.
        :type test_case: :obj:`eiffel.events.base_event.BaseEvent`
        :param outcome: Outcome of the test case.
        :type outcome: dict
        :param links: Optional links to add to event.
        :type links: dict
        :param optional: Dictionary of optional data to add.
        :type optional: dict
        """
        links = links if links is not None else {}
        links.update({"TEST_CASE_EXECUTION": test_case})
        data = {"outcome": outcome}
        data.update(**optional)
        return self.send(EiffelTestCaseFinishedEvent(), links, data)

    def send_artifact_created_event(self, identity, links=None, **optional):
        """Publish an artifact created event.

        https://github.com/eiffel-community/eiffel/blob/master/eiffel-vocabulary/EiffelArtifactCreatedEvent.md

        :param identity: PURL identity specification
        :type identity: str
        :param links: Optional links to add to event.
        :type links: dict
        :param optional: Dictionary of optional data to add.
        :type optional: dict
        """
        links = links if links is not None else {}
        data = {"identity": identity}
        data.update(**optional)
        return self.send(EiffelArtifactCreatedEvent(), links, data)

    def send_artifact_published_event(
        self, locations, artifact, links=None, **optional
    ):
        """Publish an artifact created event.

        https://github.com/eiffel-community/eiffel/blob/master/eiffel-vocabulary/EiffelArtifactPublishedEvent.md

        :param locations: Locations for this artifact.
        :type locations: list
        :param artifact: Artifact created link.
        :type artifact: :obj:`eiffel.events.base_event.BaseEvent`
        :param links: Optional links to add to event.
        :type links: dict
        :param optional: Dictionary of optional data to add.
        :type optional: dict
        """
        links = links if links is not None else {}
        links.update({"ARTIFACT": artifact})
        data = {"locations": locations}
        data.update(**optional)
        return self.send(EiffelArtifactPublishedEvent(), links, data)

    def send_composition_defined_event(self, name, links=None, **optional):
        """Publish a composition defined event.

        https://github.com/eiffel-community/eiffel/blob/master/eiffel-vocabulary/EiffelCompositionDefinedEvent.md

        :param name: Name of composition
        :type name: str
        :param links: Optional links to add to event.
        :type links: dict
        :param optional: Dictionary of optional data to add.
        :type optional: dict
        """
        links = links if links is not None else {}
        data = {"name": name}
        data.update(**optional)
        return self.send(EiffelCompositionDefinedEvent(), links, data)
