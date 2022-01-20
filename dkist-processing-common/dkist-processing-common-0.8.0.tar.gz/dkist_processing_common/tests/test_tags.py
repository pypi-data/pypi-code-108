"""
Tests for the tag cloud manager
"""
import random
from typing import Callable

import pytest


@pytest.fixture()
def tag_data(tag_db):
    tags = ["A", "B", "C"]
    intersection = "Intersect"
    union = {f"Union{t}" for t in tags}
    union.update({intersection})
    for t in tags:
        tag_db.add(t, f"Union{t}")
        tag_db.add(t, intersection)
    return tags, {intersection}, union


@pytest.fixture()
def tag_db2_data(tag_db2):
    tags = ["D", "E", "F"]
    for t in tags:
        tag_db2.add(t, f"value_of_{t}")
    return tags


def test_tag_db_add(tag_db):
    """
    Given: Connection to a tag database
    When: Adding a tag
    Then: Tag is retrievable
    """
    tag = "ADD"
    values = [f"add{x}" for x in range(100)]
    # When
    for v in values:
        tag_db.add(tag, v)
    # Then
    assert tag_db.any(tag) == set(values)


def test_tag_db_clear_tag(tag_db, tag_data):
    """
    Given: Connection to a tag database with data
    When: Clearing a tag
    Then: Cleared tag returns an empty set, but other keys are not affected
    """
    tags, intersection, _ = tag_data
    tag_idx_to_clear = random.randint(0, len(tags) - 1)
    tag_to_clear = tags[tag_idx_to_clear]
    del tags[tag_idx_to_clear]
    union = {f"Union{t}" for t in tags}
    union.update(intersection)
    tag_db.clear_tag(tag_to_clear)
    assert len(tag_db.any(tag_to_clear)) == 0
    assert tag_db.any(tags) == union
    assert tag_db.all(tags) == intersection


def test_tag_db_any(tag_db, tag_data):
    """
    Given: Connection to a tag database with data
    When: When searching for the results of any tags
    Then: Union of values returned
    """
    tags, _, union = tag_data
    # When
    result = tag_db.any(tags)
    # Then
    assert result == union


def test_tag_db_all(tag_db, tag_data):
    """
    Given: Connection to a tag database with data
    When: When searching for the results of all tags
    Then: Intersection of values returned
    """
    tags, intersection, _ = tag_data
    # When
    result = tag_db.all(tags)
    # Then
    assert result == intersection


@pytest.mark.parametrize(
    "func, attr",
    [
        pytest.param(repr, "__repr__", id="repr"),
        pytest.param(str, "__str__", id="str"),
    ],
)
def test_tag_db_dunder(tag_db, func: Callable, attr):
    """
    Given: Connection to a tag database
    When: retrieving dunder method that should be implemented
    Then: It is implemented
    """
    assert getattr(tag_db, attr, None)
    assert func(tag_db)


def test_tag_db_purge(tag_db, tag_db2, tag_data, tag_db2_data):
    """
    Given: Given a connection to a 2 tag_db instances with data
        in the same redis db (have same db # but different namespace)
    When: tag_db 1 is purged
    Then: No tags remain for the tag_db 1 instance; tags still remain in tag_db 2
    """
    # When
    tag_db.purge()
    # Then
    assert not tag_db._namespace_keys
    assert len(tag_db2._namespace_keys) == len(tag_db2_data)


def test_tag_db_tags(tag_db):
    """
    Given: A connection to a tag db with a single tag
    When: Asking for a list of tags that are defined
    Then: The correct values are returned as a list of strings
    """
    tag_db.add("TAG", "value")
    tags = tag_db.tags
    assert tags == ["TAG"]


def test_tag_db_clear_value(tag_db, tag_data):
    """
    Given: A connection to a tag db with multiple tags that each have values
    When: clearing a known value from all tags
    Then: that value is not found in any of the tags
    """
    tags, _, _ = tag_data
    tag_db.clear_value(value="Intersect")
    assert "Intersect" not in tag_db.any(tags=tags)


def test_tags_for_value(tag_db, tag_data):
    """
    Given: A connection to a tag db with multiple tags that each have values
    When: asking for the tags associated with each value
    Then: the correct tag list is returned for each value
    """
    tags, intersection, union = tag_data
    intersect_val = intersection.pop()
    assert sorted(tag_db.tags_for_value(intersect_val)) == tags
    for v in union:
        if v == intersect_val:
            continue
        inferred_tag = v[-1]
        assert tag_db.tags_for_value(v) == [inferred_tag]
