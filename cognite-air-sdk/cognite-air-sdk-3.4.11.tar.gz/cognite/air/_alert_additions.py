from typing import List, Tuple, Union

from cognite.client import CogniteClient
from cognite.client.data_classes import Event
from cognite.client.exceptions import CogniteNotFoundError

EVENT_END = "event_end"


def _remove_duplicates(existing_events: List[Event], new_events: List[List[int]]) -> Union[List[int], List]:
    """`Run new events against old events to remove exact duplicates or events that fit into the existing events`_
    Note that overlapping events should be handled with the closed event function.
    """
    # filter events that already exist
    non_duplicated_events: List[List] = []
    event_is_duplicated = False
    for i, event in enumerate(new_events):
        for ev in existing_events:
            event_end = ev.end_time or int(ev.metadata.get(EVENT_END, 0))
            event_is_duplicated = ev.start_time <= event[0] and event_end >= event[1]
            if event_is_duplicated:
                break

        if not event_is_duplicated:
            non_duplicated_events.append(event)
    return non_duplicated_events


def _create_event_list(datapoints: List[List]) -> List[List[int]]:
    """`Creates a list of list with timestamp in ms when an even starts and when an event ends.`_

    Args:
        datapoints (List[List]): A list of lists with one integer (timestamp in ms)
        and a bool if a condition is met.

    Returns:
        List[List[int]]: A list of lists with two integers.
            Both integers are timestamps in ms. The first one determines when an event starts and
            the last one when it ends.

    Examples:

        >>> from cognite.air.event_utils import create_event_list
        >>> print(create_event_list([[158000000000, False], [159000000000 , True], [160000000000, True],
                                    [161000000000, False]]))
        [[159000000000, 160000000000]]


    """
    if len(datapoints) < 2:
        return [[]]
    appended_datapoints: List[Tuple[List, List]] = list(zip(datapoints[:-1], datapoints[1:]))
    # change: either switch from False to True or the other way around
    only_changes: List[Tuple[List, List]] = list(filter(lambda x: x[0][1] != x[1][1], appended_datapoints))

    # if there is no change ...
    if len(only_changes) == 0:
        # ... check if the all datapoints indicate a change by checking the first one
        if appended_datapoints[0][0][1]:
            # ... return one datapoint that stretches from start to end
            return [[datapoints[0][0], datapoints[-1][0]]]
        # ... return no datapoint because the condition is not met anywhere
        return [[]]

    # create a list with lists of start and end: [[0, 5], [10, 11]]
    intervals = []
    for i, x in enumerate(only_changes):
        # deal with edge cases first: what if we start with an end of a condition? [True, False]
        # if the first is the end of the event, set the beginning to first timestamp of datapoints
        if i == 0 and x[0][1]:
            intervals.append([datapoints[0][0], x[0][0]])
        # what if we end with start? [False, True]
        # if the last one is the start of a event, set the end to last timestampstamp of datapoints
        elif i == len(only_changes) - 1 and x[1][1]:
            if len(intervals) == 0 or len(intervals[-1]) == 2:
                intervals.append([x[1][0], datapoints[-1][0]])
            else:
                intervals[-1].append(datapoints[-1][0])
        # for the normal run
        else:
            # check if we open a new interval
            if len(intervals) == 0 or len(intervals[-1]) == 2:
                # the timestamp of the second datapoint is used, because it is a change from False to True
                new_interval = [x[1][0]]
                intervals.append(new_interval)
            # otherwise close the interval
            else:
                # the timestamp of the first datapoint is used because it is a change from True to False
                intervals[-1].append(x[0][0])
    return intervals


def _update_events(client: CogniteClient, events: List[Event]) -> Union[List, List[Event]]:
    updated_events = []
    for event in events:
        print(event.id)
        try:
            updated_event = client.events.update(event)
            updated_events.append(updated_event)
        except CogniteNotFoundError:
            asset_ids = event.asset_ids
            correct_asset_ids = []
            for asset_id in asset_ids:
                asset = client.assets.retrieve(asset_id)
                if asset is not None:
                    correct_asset_ids.append(asset.id)
            event.asset_ids = correct_asset_ids
            updated_event = client.events.update(event)
            updated_events.append(updated_event)
    return updated_events


def _duplication_removal(new_events: List, existing_alerts: List[Event]):
    if len(new_events) == 0:
        return new_events
    non_duplicated_new_events = new_events
    if len(existing_alerts) > 0:
        non_duplicated_new_events = _remove_duplicates([i for i in existing_alerts], non_duplicated_new_events)
    return non_duplicated_new_events
