from typing import List, Optional

from .constants import AlertPlacement, AlertIntent


class Intervention:
    """
    A class specifying guidance toward the next course of action within a Protocol.
    """

    def __init__(self,
                 title: Optional[str] = None,
                 narrative: Optional[str] = None,
                 href: str = ''):

        self.title = title
        self.narrative = narrative
        self.href = href


class BannerAlertIntervention(Intervention):
    """
    An intervention that will appear as a banner alert in the UI, specifying a narrative, where it should appear, and what intent it has
    """

    def __init__(
            self, narrative: str, placement: List[AlertPlacement],
            intent: AlertIntent, href: str = ''):

        if len(narrative) > 90 or len(narrative) < 1:
            raise ValueError(
                'Narrative of Banner Alert Intervention must be between 1 and 90 characters')

        placement_options = [p.value for p in AlertPlacement]
        if not isinstance(placement, list):
            raise TypeError(
                f'Placement of Banner Alert Intervention must be a List of strings. The options are: {placement_options}')
        if len(placement) < 1:
            raise ValueError(
                f'Placement of Banner Alert Intervention must have at least one value. The options are: {placement_options}')
        for p in placement:
            if p not in placement_options:
                raise ValueError(
                    f'"{p}" is not an accepted option for Banner Alert Intervention placement. The options are: {placement_options}')

        intent_options = [i.value for i in AlertIntent]
        if intent not in intent_options:
            raise ValueError(
                f'"{intent}" is not an accepted option for Banner Alert Intervention intent. The options are: {intent_options}')

        super().__init__(narrative=narrative, href=href)
        self.placement = placement
        self.intent = intent
