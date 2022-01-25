import datetime
from enum import Enum, unique
from typing import cast, List, Tuple, Union

from fhir.resources.claim import Claim, ClaimItem
from schema.insight_engine_request import InsightEngineRequest

from enginelib.claim_focus import ClaimFocus, ClaimTypeFocus
from enginelib.claim_line_focus import ClaimLineFocus
from enginelib.errors import ClaimError
from enginelib.types import Period
from fhir.resources.period import Period as FHIRPeriod


@unique
class SameDateResult(str, Enum):
    NotApplicable100N = 'This classification tree is looking only at same date relationships for professional claims.'
    NotApplicable200N = 'No other historical claim have the same start dates for its claim lines.'
    Partial = 'CUE and OC have the same dateFrom, in all claim lines, but dateTo differs for at least one claim line.'
    Same400Y = 'CUE and OC take place on the same day, for all claim lines.'
    Same400N = 'CUE and OC take place during the exact same date range, for all claim lines.'
    Error = 'Error'


@unique
class LineSameDateResult(str, Enum):
    NotApplicable200N = 'No other claim lines in history that have the same start date, therefore cannot be "same date"'
    Partial300N = 'CLUE and OCL have same Date From but Different Date To',
    Same400Y = 'CLUE and OCL take place on the same day'
    Same400N = 'CLUE and OCL take place during the exact same date range'
    Error = 'Error'


ClaimOrItem = Union[Claim, ClaimItem]


def same_date(a: ClaimOrItem, b: ClaimOrItem) -> Union[SameDateResult, LineSameDateResult]:
    if isinstance(a, Claim):
        return claim_same_date(a, b)
    elif isinstance(a, ClaimItem):
        return claim_line_same_date(a, b)


def claim_same_date(cue: Claim, oc: Claim) -> SameDateResult:
    """Verify if two claims are for the same date or the same date range.

    Args:
        cue: the claim under investigation
        oc: the claim we want to compare with the cue
    """
    # noinspection PyBroadException
    try:
        return SameDatePolicy(ClaimFocus(cue)).evaluate(ClaimFocus(oc))
    except Exception:
        return SameDateResult.Error


def claim_line_same_date(clue: ClaimItem, ocl: ClaimItem) -> LineSameDateResult:
    """Verify if two claim lines are for the same date or the same date range.

    """
    try:
        return LineSameDatePolicy(clue).evaluate(ocl)
    except Exception:
        return LineSameDateResult.Error


class SameDatePolicy:
    """Class that implements same date verification policy for claim level."""
    # [(dateFrom, dateTo), (dateFrom, dateTo), ...], one pair of dates for each claim line.
    _oc_date_tuples: List[Tuple[datetime.date, datetime.date]]

    def __init__(self, cue: ClaimFocus):
        self.cue = cue
        self.cue_date_tuples = self._extract_date_fields(cue)

    def evaluate(self, oc: ClaimFocus) -> SameDateResult:
        """Check whether a given claim oc has same date (or same date range) as the cue."""
        # 100
        if ClaimTypeFocus.from_string(self.cue.claim_type) != ClaimTypeFocus.PROFESSIONAL:
            return SameDateResult.NotApplicable100N

        self._oc_date_tuples = self._extract_date_fields(oc)

        # 200
        if not self._verify_all_start_dates_match():
            return SameDateResult.NotApplicable200N

        # 300
        if not self._verify_all_end_dates_match():
            return SameDateResult.Partial

        # 400
        if self._verify_all_on_the_same_day():
            return SameDateResult.Same400Y

        return SameDateResult.Same400N

    @staticmethod
    def _extract_date_fields(cf: ClaimFocus) -> List[Tuple[datetime.date, datetime.date]]:
        """Extracts list of pairs of the form (datrFrom, dateTo) for each claim line in the given ClaimFocus.

        Args:
            cf: an instance of ClaimFocus.

        Returns:
             A list of pairs (start_date, end_date), one for each claim line in cf.
        """
        date_fields = list()
        for claim_line in cf.claim.item:
            clue = ClaimLineFocus(
                claim_line=cast(ClaimItem, claim_line),
                request=InsightEngineRequest.construct(claim=cf.claim)
            )
            date_from, date_to = clue.service_period
            date_fields.append((date_from, date_to))

        # sort tuples by 1. increasing order of lineServicedDateFrom, and in case of a draw,
        #     sort by 2. increasing order of lineServicedDateTo:
        date_fields.sort()
        return date_fields

    def _verify_all_start_dates_match(self) -> bool:
        cue_date_from = [date_from for date_from, date_to in self.cue_date_tuples]
        oc_date_form = [date_from for date_from, date_to in self._oc_date_tuples]

        return cue_date_from == oc_date_form

    def _verify_all_end_dates_match(self) -> bool:
        cue_date_to = [date_to for date_from, date_to in self.cue_date_tuples]
        oc_date_to = [date_to for date_from, date_to in self._oc_date_tuples]

        return cue_date_to == oc_date_to

    def _verify_all_on_the_same_day(self) -> bool:
        first_date = self.cue_date_tuples[0]
        last_date = self.cue_date_tuples[-1]
        return first_date == last_date and first_date[0] == first_date[1]


class LineSameDatePolicy:
    """Class that implements same date verification policy for line level."""
    def __init__(self, clue: ClaimItem):
        self.clue = clue
        self.start, self.end = self.service_period(clue)

    def evaluate(self, ocl: ClaimItem) -> LineSameDateResult:
        ocl_start, ocl_end = self.service_period(ocl)
        # 200
        if self.start != ocl_start:
            return LineSameDateResult.NotApplicable200N
        # 300
        elif self.end != ocl_end:
            return LineSameDateResult.Partial300N
        # 400
        elif self.start == self.end:
            return LineSameDateResult.Same400Y
        else:
            return LineSameDateResult.Same400N

    # This should use ClaimLineFocus,
    # but the request parameter makes that tricky right now
    # so I am reimplementing the method we need here
    @staticmethod
    def service_period(clue: ClaimItem) -> Period:
        serv_date = clue.servicedDate
        if serv_date:
            return Period(serv_date, serv_date)
        else:
            period = cast(FHIRPeriod, clue.servicedPeriod)
            if not (period.start and period.end):
                raise ClaimError('Service period not found for this claim line')
            return Period(period.start, period.end)
