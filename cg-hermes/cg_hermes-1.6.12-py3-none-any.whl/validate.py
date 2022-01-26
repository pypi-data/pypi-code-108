"""Code for validating files from different sources"""
import logging
from typing import Dict, FrozenSet, List, Optional

from cg_hermes.config.pipelines import AnalysisType, Pipeline
from cg_hermes.config.tags import COMMON_TAG_CATEGORIES
from cg_hermes.deliverables import Deliverables
from cg_hermes.models.tags import TagMap

LOG = logging.getLogger(__name__)


def get_deliverables_obj(
    deliverables: Dict[str, List[Dict[str, str]]],
    pipeline: Pipeline,
    analysis_type: Optional[AnalysisType] = None,
) -> Deliverables:
    if pipeline == Pipeline.BALSAMIC and not analysis_type:
        LOG.info("Please specify analysis type for balsamic")
        raise SyntaxError
    return Deliverables(deliverables=deliverables, pipeline=pipeline, analysis_type=analysis_type)


def validate_common_tags() -> bool:
    """Validate the common tags"""
    for category in COMMON_TAG_CATEGORIES:
        tag_map: Dict[str, Dict[str, str]] = COMMON_TAG_CATEGORIES[category]
        for tag_name, value in tag_map.items():
            try:
                assert isinstance(tag_map[tag_name], dict)
            except AssertionError as err:
                LOG.warning("Tag %s in %s is on the wrong format", tag_name, category.upper())
                raise err
            try:
                assert "description" in value
            except AssertionError as err:
                LOG.warning("Tag %s in %s does not have a description", tag_name, category.upper())
                raise err
    return True


def validate_tag_map(tag_map: Dict[FrozenSet[str], dict]) -> bool:
    """Validate if a tag map is on the correct format"""
    for pipeline_tags, value in tag_map.items():
        assert isinstance(pipeline_tags, frozenset)
        TagMap.validate(value)
    return True
