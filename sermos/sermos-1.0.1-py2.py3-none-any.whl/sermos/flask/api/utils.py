""" Utilities for Sermos APIs and interacting with Pipelines/Schedules
"""
import logging
from typing import Union
from sermos.utils.task_utils import PipelineGenerator

logger = logging.getLogger(__name__)


def chain_helper(pipeline_id: str,
                 access_key: Union[str, None] = None,
                 chain_payload: Union[dict, None] = None,
                 add_retry: bool = True,
                 queue: Union[str, None] = None,
                 default_task_ttl: int = None):
    """ Helper method to generate a pipeline chain *with* error handling.

        Usage:
          my_chain = chain_helper('pipeline-name')
          my_chain.delay()
    """
    # Get our pipeline. The PipelineGenerator will use the PipelineRunWrapper
    # to cache this "run" of the pipeline.
    gen = PipelineGenerator(pipeline_id,
                            access_key=access_key,
                            queue=queue,
                            default_task_ttl=default_task_ttl,
                            add_retry=add_retry,
                            chain_payload=chain_payload)
    if gen.good_to_go:
        # Generate our 'chain', which is the grouping of celery constructs that
        # allows our dag to run asynchronously and synchronously according to
        # the adjacency list defined in our pipeline configuration.
        gen.generate_chain()

    return gen
