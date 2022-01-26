from typing import Dict, List, Tuple, Union

import pandas as pd

from cognite.air import AIRClient
from cognite.air.utils import is_string_truthy
from cognite.client.data_classes import Event, EventList
from cognite.client.exceptions import CogniteDuplicatedError, CogniteNotFoundError

from .ts_utils import current_time_in_ms

EVENT_END = "event_end"


def create_event_list(datapoints: List[List]) -> List[List[int]]:
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


def retrieve_event_end(existing_open_event: Event) -> int:
    meta: Dict = existing_open_event.metadata or {}
    try:
        event_end: int = int(meta.get(EVENT_END, 0))
    except ValueError:
        raise ValueError("Event end time is not a string.")
    return event_end


def set_event_end_time_and_show(
    existing_open_event: Event, end: int, event_end: int, min_length_of_alert: int, merge_period: int
) -> Event:
    if event_end < end - merge_period:
        existing_open_event.end_time = event_end
    if (
        not is_string_truthy(existing_open_event.metadata.get("show"))
        and event_end - existing_open_event.start_time > min_length_of_alert
    ):
        existing_open_event.metadata["show"] = "True"
    return existing_open_event


def close_event(
    existing_events: Union[EventList, List[Event]],
    new_events: List[List[int]],
    end: int,
    min_length_of_alert: int = 0,
    merge_period: int = 0,
) -> Tuple[List[Event], List[List[int]]]:
    """`Identified open Events and check with current events if they should be closed. Manipulates new
        event if overlaps with open Event.`_

    Args:
        existing_events (Union[EventList, List[Event]]): List of Events.
        new_events (List[List[int]]): List of lists with two integers. First indicates the start time
        and the second the end time.
        end (int): The last timestamp to consider.
        min_length_of_alert (int): The minimum length of an alert until which it should be considered.
        merge_period (int): When events should be merged together.

    Returns:
        Tuple[List[Event], List[List[int]]]: A tuple with a list of open (or maybe now, closed) alerts and a
        list of new events (always sorted on start time).

    Examples:

            >>> from cognite.air.event_utils import close_event
            >>> close_event(existing_events=[Event(start_time=0, end_time=5), Event(start_time=10)],
            ...             new_events=[[15, 20]], end=20)

    """
    new_events = sorted(map(sorted, new_events))
    existing_events.sort(key=lambda e: e.start_time)
    remaining_new_events: List = []
    # first remove new alerts that are exactly the same
    existing_open_events = list(filter(lambda e: e.end_time is None, existing_events))
    if len(existing_open_events) == 0:
        return [], new_events
    if len(new_events) == 0:
        for existing_open_event in existing_open_events:
            event_end = retrieve_event_end(existing_open_event)
            existing_open_event = set_event_end_time_and_show(
                existing_open_event, end, event_end, min_length_of_alert, merge_period
            )
        return existing_open_events, []
    for existing_open_event in existing_open_events:
        for i, new_event in enumerate(new_events):
            event_end = retrieve_event_end(existing_open_event)
            # Check if the new event is suitable for closing the old event.
            # This means the new event should overlap or be sufficiently close
            # to the open event to be considered a "closing event".
            if can_new_event_close_open_event(event_end, new_event, min_length_of_alert, merge_period):
                event_end = new_event[1]
                existing_open_event = set_event_end_time_and_show(
                    existing_open_event, end, event_end, min_length_of_alert, merge_period
                )
                existing_open_event.metadata[EVENT_END] = str(event_end)
            else:
                remaining_new_events.append(new_event)
        # when end time in metadata is smaller than end - merge period, set end time to metadata end time
        final_event_end = retrieve_event_end(existing_open_event)
        if final_event_end < end - merge_period:
            existing_open_event.end_time = final_event_end
    return existing_open_events, remaining_new_events


def can_new_event_close_open_event(
    event_end: int, new_event: List[int], min_length_of_alert: int = 0, merge_period: int = 0
) -> bool:
    """`Checks if the new event can be considered a closing event for the open event`_

    Args:
        event_end (int): The end of the open event.
        new_event (List[int]): List of two integers denoting the start and end of the new event in ms.
        min_length_of_alert (int): The minimum length of an alert until which it should be considered.
        merge_period (int): When events should be merged together.

    Returns:
        bool: Either if the new event closes the open event (True) or not (False)

    Examples:

            >>> from cognite.air.event_utils import can_new_event_close_open_event
            >>> print(can_new_event_close_open_event(10, [9, 12]))
            True
            >>> print(can_new_event_close_open_event(10, [11, 12]))
            False
    """
    # if event end equals the start of the new event it should be considered as a closer
    if event_end == new_event[0]:
        return True
    event_long_enough = new_event[1] - new_event[0] >= min_length_of_alert
    event_end_close_enough = new_event[0] - merge_period <= event_end
    new_event_ends_later = event_end < new_event[1]
    return event_long_enough and event_end_close_enough and new_event_ends_later


def merge_time_intervals(
    intervals: List[List[int]], min_length_of_alert: int = 0, merge_period: int = 0
) -> Union[List[List[int]], List]:
    """`Takes a list of time intervals and returns a list with non-overlapping intervals`_

    Args:
        intervals (List[List[int]]]): List of lists with two integers denoting
        start- and end time of each interval.
        min_length_of_alert (int=0): Minimum length of an interval to be considered for merging.
        merge_period (int): Maximum distance between intervals to be merged.
    """

    intervals_sorted: List = sorted(map(sorted, intervals))
    merged: List[List] = []
    too_small_to_merge: List = []
    for higher in intervals_sorted:
        if len(higher) == 0:
            continue
        if higher[1] - higher[0] < min_length_of_alert:
            too_small_to_merge.append(higher)
        elif not merged:
            merged.append(higher)
        else:
            lower = merged[-1]
            if higher[0] - merge_period <= lower[1]:
                upper_bound = max(lower[1], higher[1])
                merged[-1] = [lower[0], upper_bound]
            else:
                merged.append(higher)

    keep_small = []
    for small in too_small_to_merge:
        if not any(small[0] > x[0] and small[1] < x[1] for x in merged):
            keep_small.append(small)
    merged_and_sorted = merged + keep_small
    merged_and_sorted = sorted(map(sorted, merged_and_sorted))
    return merged_and_sorted


def remove_duplicates(existing_events: List[Event], new_events: List[List[int]]) -> Union[List[int], List]:
    """`Run new events against old events to remove exact duplicates or events that fit into the existing events`_
    Note that overlapping events should be handled with the closed event function.
    """
    # filter events that already exist
    non_duplicated_events: List[List] = []
    event_is_duplicated = False
    for i, event in enumerate(new_events):
        for ev in existing_events:
            event_end = ev.end_time or int(ev.metadata.get("event_end", 0))
            event_is_duplicated = ev.start_time <= event[0] and event_end >= event[1]
            if event_is_duplicated:
                break

        if not event_is_duplicated:
            non_duplicated_events.append(event)
    return non_duplicated_events


def create_open_event(
    new_event: List[int],
    end: int,
    notification_message: str = "",
    alert_window: int = int(12 * 3600 * 1e3),
    min_length_of_alert: int = 0,
    merge_period: int = 0,
) -> Event:
    """`Create AIR ready events that can be parsed into AIREventsAPI.create_alerts`_

    Args:
        new_event (List[int]): A list of two integers denoting start and end time in ms.
        end (int): End time of the evaluation period in ms.
        notification_message (str): A message that is going to be sent to the subscriber.
        alert_window (int): How old is the event to be allowed to sent a notification?
                            Defaults to not older than 12 hours.
        min_length_of_alert (int=0): Minimum length of an interval to be considered for merging.
        merge_period (int): Maximum distance between intervals to be merged.

    """
    start_time, end_time = new_event
    show = show_alert(start_time, end_time, min_length_of_alert)
    notification = send_notification(start_time, end_time, alert_window, min_length_of_alert)
    event = Event(
        start_time=start_time,
        metadata={
            "sendNotification": str(notification),
            "show": str(show),
            "notification_message": notification_message,
        },
    )
    if end_time >= end - merge_period:
        event.metadata[EVENT_END] = str(end_time)
    else:
        event.end_time = end_time
    return event


def show_alert(start_time: int, end_time: int, min_length_of_alert: int) -> bool:
    return end_time - start_time > min_length_of_alert


def send_notification(start_time: int, end_time: int, alert_window: int, min_length_of_alert: int) -> bool:
    is_event_fresh = end_time >= current_time_in_ms() - alert_window
    is_event_long = show_alert(start_time, end_time, min_length_of_alert)
    return is_event_fresh and is_event_long


def update_events(client, events):
    for event in events:
        print(event.id)
        try:
            client.events.update(event)
        except CogniteNotFoundError:
            asset_ids = event.asset_ids
            correct_asset_ids = []
            for asset_id in asset_ids:
                asset = client.assets.retrieve(asset_id)
                if asset is not None:
                    correct_asset_ids.append(asset.id)
            event.asset_ids = correct_asset_ids
            client.events.update(event)


def create_alerts(
    air_client: AIRClient,
    df: pd.DataFrame,
    end_point: int,
    alert_window: int,
    min_length_of_alert: int,
    max_length_of_alert: int,
    merge_period: int,
    notification_message: str,
    max_events_to_be_processed: int = -1,
):
    df.columns = ["deviation"]

    # transform df into List
    possible_events = []
    for i in df.itertuples():
        possible_event = [int(i.Index.timestamp() * 1e3), i.deviation]
        possible_events.append(possible_event)
    # create deviation events
    deviation_events: List[List[int]] = create_event_list(possible_events)
    # merge time intervals if necessary
    merged_events = merge_time_intervals(
        deviation_events, min_length_of_alert=min_length_of_alert, merge_period=merge_period
    )
    if air_client.backfilling.in_progress and len(merged_events) > max_events_to_be_processed:
        merged_events = merged_events[:max_events_to_be_processed]
        end_point = merged_events[-1][1]

    # retrieve previous events and only keep open ones
    previous_alerts_all = air_client.events.list_alerts(limit=0)
    open_alerts = [alert for alert in previous_alerts_all if alert.end_time is None]

    # close events
    events_to_be_updated, new_events = close_event(
        open_alerts,
        merged_events,
        end=end_point,
        min_length_of_alert=min_length_of_alert,
        merge_period=merge_period,
    )
    # check if events need to be updated and update
    if len(events_to_be_updated) > 0:
        print(f"trying to close {len(events_to_be_updated)} events.")
        update_events(air_client._config.client, events_to_be_updated)
        if len(new_events) == 0:
            print("no new events")
            return events_to_be_updated, [], end_point
    # if there are no new events left return nothing
    elif len(new_events) == 0:
        print("nothing to write")
        return [], [], end_point

    # remove duplicates
    non_duplicated_new_events = duplication_removal(new_events, previous_alerts_all)
    non_duplicated_new_events = duplication_removal(non_duplicated_new_events, events_to_be_updated)

    # if non duplicates exists create events
    counter = 0
    written_events = []
    if len(non_duplicated_new_events) > 0:
        print(f"trying to write {len(non_duplicated_new_events)} events.")
        for event in non_duplicated_new_events:
            ev = create_open_event(
                event,
                end=end_point,
                notification_message=notification_message,
                alert_window=alert_window,
                min_length_of_alert=min_length_of_alert,
                merge_period=merge_period,
            )
            # if event is not open and to short: ignore it
            if ev.end_time is not None and ev.end_time - ev.start_time < min_length_of_alert:
                continue
            # if an event is open but ends before the end time is given
            # and is shorter than min_length_of_alert: ignore it!
            if (
                ev.end_time is None
                and int(ev.metadata["event_end"]) < end_point
                and int(ev.metadata["event_end"]) - ev.start_time < min_length_of_alert
            ):
                continue
            try:
                air_client.events.create_alert(ev)
                print(ev.id)
                written_events.append([ev.start_time, ev.end_time or int(ev.metadata["event_end"])])
                counter += 1
            except CogniteDuplicatedError:
                pass
    print(f"Wrote {counter} Alerts")
    return events_to_be_updated, written_events, end_point


def duplication_removal(new_events: List, existing_alerts: List[Event]):
    if len(new_events) == 0:
        return new_events
    non_duplicated_new_events = new_events
    if len(existing_alerts) > 0:
        non_duplicated_new_events = remove_duplicates([i for i in existing_alerts], non_duplicated_new_events)
    return non_duplicated_new_events
