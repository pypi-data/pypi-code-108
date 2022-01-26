import os
from typing import List, Optional, Callable

from helios import HeliosBase, HeliosTags, version
from helios.instrumentation import default_instrumentation_list

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.util import types
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.trace import set_span_in_context
from opentelemetry.context import attach

SAMPLING_RATIO_RESOURCE_ATTRIBUTE_NAME = 'telemetry.sdk.sampling_ratio'
_OPENTELEMETRY_SDK_VERSION = version.__version__


class Helios(HeliosBase):
    def init_tracer_provider(self) -> TracerProvider:
        if self.resource_tags:
            resource_tags = self.resource_tags.copy()
        else:
            resource_tags = dict()
        resource_tags.update({
            ResourceAttributes.DEPLOYMENT_ENVIRONMENT:
                self.get_deployment_environment(),
            HeliosTags.ACCESS_TOKEN:
                self.api_token,
            ResourceAttributes.SERVICE_NAME:
                self.service_name,
            ResourceAttributes.SERVICE_VERSION:
                self.get_commit_hash(),
            ResourceAttributes.TELEMETRY_SDK_VERSION:
                _OPENTELEMETRY_SDK_VERSION,
            ResourceAttributes.TELEMETRY_SDK_NAME:
                'helios-opentelemetry-sdk',
            SAMPLING_RATIO_RESOURCE_ATTRIBUTE_NAME:
                self.sampling_ratio
        })

        return TracerProvider(
            id_generator=self.id_generator,
            sampler=self.get_sampler(),
            resource=Resource.create(resource_tags),
        )

    def get_deployment_environment(self) -> str:

        if self.environment:
            return self.environment

        environment = None
        if os.environ.get('CI'):
            environment = self.get_ci_environment()

        if os.environ.get('JENKINS_URL'):
            environment = 'Jenkins'

        if not environment and self.resource_tags:
            environment = \
                self.resource_tags.get(
                    ResourceAttributes.DEPLOYMENT_ENVIRONMENT)

        return environment or os.environ.get('DEPLOYMENT_ENV', '')

    def get_ci_environment(self) -> str:
        if os.environ.get('GITHUB_ACTIONS'):
            return 'Github Actions'

        if os.environ.get('TRAVIS'):
            return 'Travis CI'

        if os.environ.get('GITLAB_CI'):
            return 'Gitlab Pipeline'

        if os.environ.get('CIRCLECI'):
            return 'CircleCI'

        return None

    def get_commit_hash(self) -> str:

        if self.commit_hash:
            return self.commit_hash

        commit_hash = None
        if os.environ.get('CI'):
            commit_hash = self.get_ci_commit_hash()

        if not commit_hash and self.resource_tags:
            commit_hash = \
                self.resource_tags.get(
                    ResourceAttributes.SERVICE_VERSION)

        return commit_hash or os.environ.get('COMMIT_HASH', '')

    def get_ci_commit_hash(self):
        if os.environ.get('GITHUB_ACTIONS'):
            return os.environ.get('GITHUB_SHA')

        if os.environ.get('TRAVIS'):
            return os.environ.get('TRAVIS_COMMIT')

        if os.environ.get('GITLAB_CI'):
            return os.environ.get('CI_COMMIT_SHA')

        if os.environ.get('CIRCLECI'):
            return os.environ.get('CIRCLE_SHA1')

        return None

    def get_sampler(self):
        if self.custom_sampler:
            return self.custom_sampler

        ratio = self.sampling_ratio or 1.0

        return TraceIdRatioBased(ratio)

    def create_custom_span(self, name: str, attributes: types.Attributes = None, wrapped_fn: Optional[Callable[[], any]] = None, set_as_current_context: bool = False):
        tracer = self.tracer_provider.get_tracer('helios')
        new_context = None
        result = None
        with tracer.start_as_current_span(name, attributes=attributes) as custom_span:
            custom_span.set_attribute('hs-custom-span', 'true')
            if set_as_current_context:
                new_context = set_span_in_context(custom_span)

            if wrapped_fn is None:
                custom_span.end()
            else:
                try:
                    result = wrapped_fn()
                except Exception as e:
                    custom_span.set_status(Status(status_code=StatusCode.ERROR, description=str(e)))
                    custom_span.record_exception(e)
                    raise e
                finally:
                    custom_span.end()

        attach(new_context) if new_context else None
        return result

    def get_instrumentations(self) -> List[BaseInstrumentor]:
        return default_instrumentation_list
