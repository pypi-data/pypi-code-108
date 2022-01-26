from typing import Dict

from enginelib.simple_insight import SimpleInsight
from schema.insight_engine_response import InsightType

from enginelib.decor.errors import InsightLookupError


class AbstractResult:
    """A class that inherits from this one stores information
    about all possible insights: type and text. The type is
    kept in one dictionary (class attribute insight_type) and
    the text in another dictionary (class attribute insight_text).

    Both dictionaries are indexed by the name of the branch in
    the decision tree that led to the insight (e.g. "100N").
    """

    #: stores the type of each insight.
    insight_type: Dict[str, InsightType]

    #: stores the text of each insight.
    insight_text: Dict[str, str]

    @classmethod
    def simple_insight(cls, branch: str) -> SimpleInsight:
        """
        Args:
            branch: the name of the branch (to be used as key in
        the dictionaries insight_type and insight_text).

        Returns:
            the SimpleInsight object corresponding to the given branch.

        Raises:
            InsightLookupError: in case the given branch is not found
        in either insight_type or insight_text.
        """
        try:
            return SimpleInsight(insight_type=cls.insight_type[branch], text=cls.insight_text[branch])
        except KeyError:
            raise InsightLookupError(f'Type or text of insight ref #{branch} not found.')

    @classmethod
    def is_valid(cls, branch: str) -> bool:
        """
        Args:
            branch: the name of the branch (to be used as key in
        the dictionaries insight_type and insight_text).

        Returns:
            True if branch is a valid key of the dictionary insight_type, False otherwise.
        """
        return branch in cls.insight_type

    @classmethod
    def validate(cls):
        text_keys = set(cls.insight_text.keys())
        type_keys = set(cls.insight_type.keys())

        text_but_no_type = text_keys.difference(type_keys)
        type_but_no_text = type_keys.difference(text_keys)

        assert text_but_no_type == set(), \
            f'Each insight label in {text_but_no_type} has an associated text, ' \
            f'but no associated type in class {cls.__name__}.'

        assert type_but_no_text == set(), \
            f'Each insight label in {type_but_no_text} has an associated type, ' \
            f'but no associated text in class {cls.__name__}.'
