"""Compare instanses of FHIR objects.

The idea of this module is to be completely independent with
Focus classes and other modules to be able to import it anywhere
without any dependencies.

Notes:
    If there will be some refactoring Focus classes, this module also
    should be considered.
"""
import abc
from enum import Enum

from fhir.resources.claim import Claim, ClaimItem
from pydantic.types import PositiveInt

from enginelib.errors import ClaimError


class CompareResult(Enum):
    EQ = "equal"
    NEQ = "not equal"


class _BaseComparator(abc.ABC):
    # Class name of compairing items.
    _restricted_class = None

    @staticmethod
    @abc.abstractmethod
    def compare(cls, first: object, second: object) -> CompareResult:
        pass

    @classmethod
    def _check_types(cls, first: object, second: object) -> None:
        """Check that objects have the same class.

        Raises:
            TypeError: if classes are different
        """
        if cls._restricted_class is not None and (
            not isinstance(first, cls._restricted_class)
            or not isinstance(second, cls._restricted_class)
        ):
            raise TypeError(
                f"{cls._restricted_class} object is comparable only "
                f"with another {cls._restricted_class} object. "
                f"Found {type(first)} and {type(second)}."
            )


class ClaimComparator(_BaseComparator):
    _restricted_class = Claim

    @classmethod
    def compare(cls, first: Claim, second: Claim) -> CompareResult:
        """
        Compare 2 `Claim`-s.

        Args:
            first: claim
            second: another claim
        """
        cls._check_types(first, second)
        # Check claimNum-s.
        try:
            claim_num_equal = cls._get_claim_num(first) == cls._get_claim_num(
                second
            )
        except ClaimError:
            claim_num_equal = None
        # Check id-s.
        try:
            id1 = first.id
            id2 = second.id
            if id1 is None or id2 is None:
                raise AttributeError("No id in claim")
            claim_id_equal = id1 == id2
        except AttributeError:
            claim_id_equal = None
        # Return an answer.
        is_equal = False
        if claim_num_equal is None and claim_id_equal is None:
            raise ClaimError("Not enough information to compare")
        elif claim_num_equal is None:
            # Compare only by id.
            is_equal = claim_id_equal
        elif claim_id_equal is None:
            # Compare only by claimNum.
            is_equal = claim_num_equal
        else:
            # Compare by both claimNum and id since they are available.
            is_equal = claim_num_equal and claim_id_equal
        return CompareResult.EQ if is_equal else CompareResult.NEQ

    # TODO: Refactor - duplicated method as in ClaimFocus class.
    @staticmethod
    def _get_claim_num(claim: Claim) -> str:
        try:
            return claim.identifier[0].value
        except (IndexError, AttributeError, TypeError) as exc:
            raise ClaimError("Could not find claimNum") from exc


class ClaimItemComparator(_BaseComparator):
    """Class to compare ClaimItem-s from the *same* Claim."""

    _restricted_class = ClaimItem

    @classmethod
    def compare(cls, first: ClaimItem, second: ClaimItem) -> CompareResult:
        """
        Compare 2 `ClaimItem`-s.

        Args:
            first: ClaimItem from the *same* Claim as second
            second: ClaimItem from the *same* Claim as first
        """
        cls._check_types(first, second)
        try:
            is_equal = cls._get_sequence(first) == cls._get_sequence(second)
        except ClaimError as exc:
            raise ClaimError("Not enough information to compare") from exc
        return CompareResult.EQ if is_equal else CompareResult.NEQ

    # TODO: Refactor - duplicated method as in ClaimLineFocus class.
    @staticmethod
    def _get_sequence(claim_item: ClaimItem) -> PositiveInt:
        try:
            return claim_item.sequence
        except (AttributeError, ClaimError) as exc:
            raise ClaimError(
                "No sequence value found for this claim."
            ) from exc
