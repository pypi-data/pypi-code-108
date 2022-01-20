"""
Splunk AppInspect infrastructure code module
"""


from .log_utils import configure_logger

__all__ = ["configure_logger", "refine_tag_set"]


def refine_tag_set(included_tags, excluded_tags):
    """
    The Splunk AppInspect business rule
    If included_tags and excluded_tags are not specified then the check
    should be returned regardless A.K.A. a left join on the
    included_tags.
    If included_tags and excluded_tags contain the same tag then
    included_tags take precedent.
    If included_tags and excluded_tags contain the different tags then
    both of them will match.
    """
    included_tags_set = set(included_tags)
    excluded_tags_set = set(excluded_tags)
    included_excluded_intersection_set = included_tags_set.intersection(
        excluded_tags_set
    )
    if included_excluded_intersection_set:
        excluded_tags_set -= included_excluded_intersection_set
    return included_tags_set, excluded_tags_set
