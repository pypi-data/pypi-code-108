import datetime as dt
from string import Formatter
from typing import Dict, List, Optional, Callable, Tuple, Any, Iterator

from fhir.resources.claim import Claim
from schema.insight_engine_request import InsightEngineRequest

from enginelib.claim_focus import ClaimFocus
from enginelib.claim_line_focus import ClaimLineFocus
from enginelib.rds.client import db_client

ClaimDirectory = Dict[str, ClaimFocus]
ClaimLineDirectory = Dict[str, List[ClaimLineFocus]]


class Registry:
    """Keeps the "state" of tree traversals:

    1. keeps track of qualifying claims and claim lines while the one CLUE is
    going along the branches of a decision tree.

    2. Serves as a storage for custom parameters that are set along the way,
    i.e. the traversal of the tree(s)."""

    #: Keeps a dictionary of qualifying OCs (claimNum is the index)
    dict_oc: ClaimDirectory

    #: list of qualifying OCL-S
    list_ocl_s: List[ClaimLineFocus]

    #: for each OC, keeps a list of its qualifying OCLs
    dict_ocl_d: ClaimLineDirectory

    _computed_parameters_values: Dict[str, Any]

    def __init__(self, cue: ClaimFocus, clue: ClaimLineFocus, ocs: Optional[List[ClaimFocus]] = None,
                 data: Optional[Dict[str, Any]] = None):
        #: the auxiliary data needed in certain predicate functions
        self.data: Dict[str, Any] = data or dict()

        #: the claim under evaluation
        self.cue = cue

        #: the claim line under evaluation
        self.clue = clue

        self._computed_parameters_values = dict()

        self.dict_oc = dict()
        self.list_ocl_s = list()
        self.dict_ocl_d = dict()
        self._historical_claims = ocs
        self._index_oc_and_ocl(ocs)

    def _index_oc_and_ocl(self, historical_claims: Optional[List[ClaimFocus]] = None):
        self.dict_oc = dict()
        self.list_ocl_s = list()
        self.dict_ocl_d = dict()

        if historical_claims is not None:
            clue_seq = self.clue.sequence

            self.dict_oc = {oc.claim_num: oc for oc in historical_claims if oc != self.cue}
            self.list_ocl_s = [clf for clf in self.cue.lines if clf.sequence != clue_seq]
            self.dict_ocl_d = {oc.claim_num: oc.lines for oc in self.dict_oc.values()}

    def fetch_history(self, max_days_back: int, min_days_back: int):
        """Calls GetHistory(transaction_id, start_date, end_date) with the requested
        period given by:

            start_date = clue.service_period.start - max_days_back
            end_date = clue.service_period.end - min_days_back

        This function does not return any value, but rather updates the set of
        qualifying OC/OCL-S/OCL-D in the registry to the set of returned claim and
        claim lines.

        You may give negative values to the parameters to retrieve claims in the
        "future" of the CLUE.
        """

        if max_days_back < min_days_back:
            max_days_back, min_days_back = min_days_back, max_days_back

        start_date = self.clue.service_period.start - dt.timedelta(days=max_days_back)
        end_date = self.clue.service_period.end - dt.timedelta(days=min_days_back)

        history, err = db_client.GetHistory(self.clue.request.transaction_id, start_date, end_date)

        historical_claims: List[ClaimFocus] = list()
        for claim_obj in history:
            claim = Claim.parse_obj(claim_obj)
            cf = ClaimFocus(
                claim=claim,
                request=InsightEngineRequest.construct(claim=claim)
            )
            historical_claims.append(cf)

        self._historical_claims = historical_claims
        self._index_oc_and_ocl(historical_claims)

    def reset_history(self):
        """Used by a MPEs. Sometimes, when going from a tree to another, history needs to
        be considered again and filtered according to different criteria. This function
        makes it easy to start anew with the original set of qualifying claims and claim
        lines as it was fetched from the platform the first time."""
        self._index_oc_and_ocl(self._historical_claims)

    def __getitem__(self, param_name: str):
        """Returns the value of a custom parameter."""
        return self._computed_parameters_values[param_name]

    def __setitem__(self, param_name: str, param_value: Any):
        """Sets the value of a custom parameter."""
        self._computed_parameters_values[param_name] = param_value

    def __contains__(self, param_name: str) -> bool:
        """Checks whether a custom parameter has been defined."""
        return param_name in self._computed_parameters_values

    def is_there_oc_such_that(self, func: Callable[..., bool]) -> bool:
        """Filter qualifying OCs with the given function.
        Updates dict_ocl_d and dict_oc if at least one OC satisfies
        the given predicate function.

        Whenever OCs are filtered, OCLs are filtered implicitly as well:
        only claim lines inside OCs that passed the filter should stay in
        the registry (i.e. in dict_ocl_d).

        Args:
            func: a predicate function accepting exactly one parameter
        named 'oc' of type ClaimFocus.

        Returns:
            True if at least one OC satisfies the given predicate function and False otherwise.
        """
        dict_oc = {oc_id: oc for oc_id, oc in self.dict_oc.items() if func(oc=oc)}
        if not dict_oc:
            # Filter failed: no OC satisfied the given func.
            return False

        # Filter succeeded: at least one OC satisfied the given predicate,
        #     so we update everything with filtered objects (OCs and OCLs).
        self.dict_oc = dict_oc
        self.dict_ocl_d = {oc_id: self.dict_ocl_d[oc_id] for oc_id, oc in dict_oc.items()}

        # Attribute list_ocl_s remains the same, because the filter was
        #     not about claim lines in the CUE.
        return True

    def _get_ocl_d_such_that(self, func: Callable[..., bool], param_name: str) \
            -> Tuple[ClaimDirectory, ClaimLineDirectory]:
        dict_oc: ClaimDirectory = dict()
        dict_ocl_d: ClaimLineDirectory = dict()

        for claim_id, lines in self.dict_ocl_d.items():
            remaining_lines = [line for line in lines if func(**{param_name: line})]
            if remaining_lines:
                dict_ocl_d.setdefault(claim_id, remaining_lines)
                dict_oc[claim_id] = self.dict_oc[claim_id]

        return dict_oc, dict_ocl_d

    def is_there_ocl_such_that(self, func: Callable[..., bool]) -> bool:
        """Filter qualifying OCLs (same or different claim) with the given
        predicate function.
        Updates dict_ocl_d, list_ocl_s and dict_oc if at least one OCL
        (same or different claim) satisfies the given predicate function.
        Keep dict_ocl_d, list_ocl_s and dict_oc unchanged otherwise.

        Whenever OCLs are filtered, OCs are filtered implicitly as well:
        only claims containing some OCL that passed the filter should stay
        in the registry (i.e. in dict_oc).

        Args:
            func: a predicate function accepting exactly one parameter
        named 'ocl' of type ClaimLineFocus.

        Returns:
            True if at least one OCL (same or different claim) satisfies the
        given predicate function and False otherwise.
        """
        list_ocl_s = [clf for clf in self.list_ocl_s if func(ocl=clf)]
        dict_oc, dict_ocl_d = self._get_ocl_d_such_that(func, 'ocl')

        if list_ocl_s or dict_ocl_d:
            # Filter succeeded: at least one OCL satisfied the given predicate,
            #     so we update everything with filtered objects (OCs and OCLs).
            self.dict_oc = dict_oc
            self.list_ocl_s = list_ocl_s
            self.dict_ocl_d = dict_ocl_d
            return True

        return False

    def is_there_ocl_s_such_that(self, func: Callable[..., bool]) -> bool:
        """Filter qualifying OCL-S according to the given predicate function.
        Update list_ocl_s only if at least one OCL (same claim) satisfies
        the given predicate.

        Args:
            func: a predicate function accepting exactly one parameter
        named 'ocl_s' of type ClaimLineFocus.

        Returns:
            True if at least one OCL (same claim) satisfies the given
        predicate function, False otherwise.
            """
        list_ocl_s = [clf for clf in self.list_ocl_s if func(ocl_s=clf)]

        if list_ocl_s:
            # Filter succeeded: at least one OCL (same claim) satisfied the given
            #     predicate, so we update list_ocl_s.
            self.list_ocl_s = list_ocl_s

            # Attributes dict_oc and dict_ocl_d remain the same, because the filter
            #     was not about claim lines in other claims.
            return True

        return False

    def is_there_ocl_d_such_that(self, func: Callable[..., bool]) -> bool:
        """Filter qualifying OCL (different claim) according to the given
        predicate function.
        Update dict_ocl_d and dict_oc only if at least one OCL (different claim)
        satisfies the given predicate.
        Keep dict_ocl_d and dict_oc unchanged otherwise.

        Args:
            func: a predicate function accepting exactly one parameter
        named 'ocl_d' of type ClaimLineFocus.

        Returns:
            True if at least one OCL (different claim) satisfies the given
        predicate function, False otherwise.
        """
        dict_oc, dict_ocl_d = self._get_ocl_d_such_that(func, 'ocl_d')

        if dict_ocl_d:
            # Filter succeeded: at least one OCL (different claim) satisfied the given
            #     predicate, so we update everything with filtered objects (OCs and OCLs).
            self.dict_oc = dict_oc
            self.dict_ocl_d = dict_ocl_d

            # Attribute list_ocl_s remains the same, because the filter was
            #     not about claim lines in the CUE.
            return True

        return False

    def is_there_acl_such_that(self, func: Callable[..., bool]) -> bool:
        """Not implemented."""
        # Here, acl = any claim line
        raise NotImplementedError('Predicates involving ACL need to be better understood (by this developer).')

    @property
    def computed_parameters_values(self):
        return self._computed_parameters_values

    def iter_oc(self) -> Iterator[ClaimFocus]:
        for oc in self.dict_oc.values():
            yield oc

    def iter_ocl(self) -> Iterator[ClaimLineFocus]:
        for ocl_s in self.list_ocl_s:
            yield ocl_s

        for list_ocl_d in self.dict_ocl_d.values():
            for ocl_d in list_ocl_d:
                yield ocl_d

    def iter_ocl_s(self) -> Iterator[ClaimLineFocus]:
        for ocl_s in self.list_ocl_s:
            yield ocl_s

    def iter_ocl_d(self) -> Iterator[ClaimLineFocus]:
        for list_ocl_d in self.dict_ocl_d.values():
            for ocl_d in list_ocl_d:
                yield ocl_d

    def iter_acl(self) -> Iterator[ClaimLineFocus]:
        yield self.clue

        for ocl_s in self.list_ocl_s:
            yield ocl_s

        for list_ocl_d in self.dict_ocl_d.values():
            for ocl_d in list_ocl_d:
                yield ocl_d

    def format_text(self, text: str) -> str:
        lookup = self._computed_parameters_values
        keys = [i[1] for i in Formatter().parse(text) if i[1] is not None]
        data_dict = {
            key: str(lookup[key]) if key in lookup else '{' f'{key}' '}'
            for key in keys
        }
        return text.format(**data_dict)
