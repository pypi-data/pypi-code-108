from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from cognite.air._alert_additions import _create_event_list, _duplication_removal, _update_events
from cognite.air.client import AIRClient
from cognite.air.ts_utils import current_time_in_ms
from cognite.air.utils import is_string_truthy
from cognite.client.data_classes import Event, EventList
from cognite.client.exceptions import CogniteDuplicatedError

EVENT_END = "event_end"
MTD_SHOW = "show"
EVENT_ERROR_MESSAGE = "Event end time is not a string."
MTD_SENDNOTIFICATION = "sendNotification"
MTD_NOTIFICATION_MESSAGE = "notification_message"
ERROR_MSG_VALIDATION_DF = "df does not have a column named deviation"
ERROR_MSG_NOTLIST = "df is not pd.DataFrame nor a List of [int, bool]"


class AlertCreator:
    """Create alerts and make sure to merge them together if necessary

    Args:
        air_client (AIRClient): Instance of AIRClient
        merge_period (int): In ms. Maxmimal distance between two valid alerts to have them merged together.
        minimum_length_of_alert (int): In ms. The length an alert needs to have to be a valid alert (inclusive).
        maximum_length_of_alert (int): In ms. (not implemented) If the alert is longer
            than this parameter, a new alert will be created.
        alert_window (Optional[int]): In ms. If the end of an alert is older than now minus alert_window it will not be
            stored as an active alert.

    """

    def __init__(
        self,
        air_client: AIRClient,
        merge_period: int,
        minimum_length_of_alert: int,
        maximum_length_of_alert: Optional[int] = None,
        alert_window: Optional[int] = None,
    ):
        self.air_client = air_client
        self.merge_period = merge_period
        self.minimum_length_of_alert = minimum_length_of_alert
        self.maximum_length_of_alert = maximum_length_of_alert
        self.alert_window = 0 if alert_window is None else alert_window
        self.events_cache: List[Event] = []

    def _show_alert(self, start_time: int, end_time: int) -> bool:
        return end_time - start_time >= self.minimum_length_of_alert

    def _send_notification(self, start_time: int, end_time: int) -> bool:
        is_event_fresh = end_time >= current_time_in_ms() - self.alert_window
        is_event_long = self._show_alert(start_time, end_time)
        return is_event_fresh and is_event_long

    def _merge_time_intervals(self, intervals: List[List[int]]) -> Union[List[List[int]], List]:
        """`Takes a list of time intervals and returns a list with non-overlapping intervals`_

        Args:
            intervals (List[List[int]]]): List of lists with two integers denoting
            start- and end time of each interval.
        """
        intervals_sorted: List = sorted(map(sorted, intervals))
        merged: List[List] = []
        too_small_to_merge: List = []
        for higher in intervals_sorted:
            if len(higher) == 0:
                continue
            if higher[1] - higher[0] < self.minimum_length_of_alert:
                too_small_to_merge.append(higher)
            elif not merged:
                merged.append(higher)
            else:
                lower = merged[-1]
                if higher[0] - self.merge_period <= lower[1]:
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

    def _create_deviation_events_from_pandas(self, df: pd.DataFrame) -> List[List]:
        df.columns = ["deviation"]
        df.loc[:, "timestamp"] = df.index.view(np.int64)
        # transform df into List
        possible_events: List[List] = []
        for i in df.itertuples():
            # repeat previous deviation if the alert would be a one point alert
            if (len(possible_events) > 0 and not i.deviation and possible_events[-1][1]) or (
                len(possible_events) > 1 and possible_events[-1][1] and not possible_events[-2][1] and not i.deviation
            ):
                possible_event1 = [int(i.Index.timestamp() * 1e3), possible_events[-1][1]]
                possible_event2 = [int(i.Index.timestamp() * 1e3), i.deviation]
                possible_events.extend([possible_event1, possible_event2])
            else:
                possible_event = [int(i.Index.timestamp() * 1e3), i.deviation]
                possible_events.append(possible_event)
        return possible_events

    def _validate_df(self, df):
        if isinstance(df, pd.DataFrame):
            if "deviation" not in df.columns:
                raise ValueError(ERROR_MSG_VALIDATION_DF)
        else:
            if not all([isinstance(i[0], int) and isinstance(i[1], bool) for i in df]):
                raise ValueError(ERROR_MSG_NOTLIST)

    def _retrieve_previous_open_alerts(self, end_point: int) -> List[Event]:
        previous_alerts_all = self.air_client.events.list_alerts(limit=-1)
        self._update_events_cache(previous_alerts_all)
        open_alerts = self.events_cache
        for previous_alert in previous_alerts_all:
            if previous_alert.id not in [j.id for j in open_alerts]:
                open_alerts.append(previous_alert)

        open_alerts = self._filter_open_alerts(open_alerts, end_point)
        return open_alerts

    def _write_events(
        self,
        non_duplicated_new_events: List,
        end_point: int,
        notification_message: str,
        metadata: Optional[Dict] = None,
    ) -> Union[List, List[Event]]:
        counter = 0
        written_events = []
        if len(non_duplicated_new_events) > 0:
            for event in non_duplicated_new_events:
                ev = self._create_open_event(
                    event,
                    end=end_point,
                    notification_message=notification_message,
                    metadata=metadata,
                )
                # if event is not open and to short: ignore it
                if ev.end_time is not None and ev.end_time - ev.start_time < self.minimum_length_of_alert:
                    continue
                # if an event is open but ends before the end time is given
                # and is shorter than minimum_length_of_alert: ignore it!
                if (
                    ev.end_time is None
                    and int(ev.metadata[EVENT_END]) < end_point
                    and int(ev.metadata[EVENT_END]) - ev.start_time < self.minimum_length_of_alert
                ):
                    continue
                try:
                    alert = self.air_client.events.create_alert(ev)
                    print(ev.id)
                    written_events.append(alert)
                    counter += 1
                except CogniteDuplicatedError:
                    pass
        return written_events

    def _get_existing_alerts(self, min_timestamp: int) -> Union[List[Event], List]:
        return [
            event
            for event in self.events_cache
            if event.start_time + self.merge_period >= min_timestamp
            or (event.end_time is not None and event.end_time + self.merge_period >= min_timestamp)
            or int(event.metadata.get(EVENT_END, 0)) + self.merge_period >= min_timestamp
        ]

    def create_alerts(
        self,
        df: Union[pd.DataFrame, List[List]],
        end_point: int,
        notification_message: str,
        max_events_to_be_processed: int = -1,
        metadata: Optional[Dict] = None,
    ) -> Tuple[List, List, int]:
        """Create non-overlapping alerts.

        **Note:** alerts with different alert messages will not be merged.

        Args:
            df (Union[pd.DataFrame, List[List]): Either pandas DataFrame with a boolean column named "deviation" or
                a list of lists.
                The inner most list with two entries: timestamp in ms and a boolean if it was a deviation or not.
            end_point (int): The end of the evaluation under question. When backfilling in batches this needs
                to be adapted.
            notification_message (str): The message that will be attached to the alert and will be
                visible in the Front End and sent by notification to the subscribed users.
            max_events_to_be_processed (int): When creating a lot of events it makes sense.
                The end_point will be altered and returned.
            metadata (Optional[Dict]): Additional metadata that will be written to the metadata of the alert


        Returns:
            List: Updated Events
            List: Written Events
            int: Updated end when more events than max_events_to_be_processed. Use as new end.

        """
        self._validate_df(df)
        if isinstance(df, pd.DataFrame):
            possible_events = self._create_deviation_events_from_pandas(df)
        else:
            possible_events = df

        # create deviation events
        deviation_events: List[List[int]] = _create_event_list(possible_events)
        # merge time intervals if necessary
        merged_events = self._merge_time_intervals(deviation_events)
        if self.air_client.backfilling.in_progress and len(merged_events) > max_events_to_be_processed:
            merged_events = merged_events[:max_events_to_be_processed]
            end_point = merged_events[-1][1]

        # retrieve previous events and only keep open ones
        open_alerts = self._retrieve_previous_open_alerts(end_point)

        # close events
        events_to_be_updated, new_events = self._close_event(
            open_alerts, merged_events, end_point, notification_message
        )
        # check if events need to be updated and update
        if len(events_to_be_updated) > 0:
            updated_events = _update_events(self.air_client._config.client, events_to_be_updated)
            print(f"Updated {len(updated_events)} Events")
            self._update_events_cache(updated_events)

            if len(new_events) == 0:
                print("no new events")
                return events_to_be_updated, [], end_point
        # if there are no new events left return nothing
        elif len(new_events) == 0:
            print("nothing to write")
            return [], [], end_point

        # remove duplicates
        smallest_timestamp = new_events[0][0]
        existing_alerts = self._get_existing_alerts(smallest_timestamp)
        non_duplicated_new_events = _duplication_removal(new_events, existing_alerts)
        non_duplicated_new_events = _duplication_removal(non_duplicated_new_events, open_alerts)
        non_duplicated_new_events = _duplication_removal(non_duplicated_new_events, events_to_be_updated)

        # if non duplicates exists create events
        written_events = self._write_events(non_duplicated_new_events, end_point, notification_message, metadata)
        if len(written_events) > 0:
            self._update_events_cache(written_events)
        print(f"Wrote {len(written_events)} Alerts")
        return events_to_be_updated, written_events, end_point

    def _validate_metadata(self, metadata: Dict = {}):
        for key in metadata.keys():
            if key in [MTD_SENDNOTIFICATION, MTD_SHOW, MTD_NOTIFICATION_MESSAGE]:
                raise ValueError(f"Invalid metadata field: {key} is a reserved key for AIR.")

    def _create_open_event(
        self, new_event: List[int], end: int, notification_message: str = "", metadata: Optional[Dict] = None
    ) -> Event:
        """`Create AIR ready events that can be parsed into AIREventsAPI.create_alerts`_

        Args:
            new_event (List[int]): A list of two integers denoting start and end time in ms.
            end (int): End time of the evaluation period in ms.
            notification_message (str): A message that is going to be sent to the subscriber.
            metadata (Optional[Dict]): Additional metadata written to the alert


        """
        if metadata is None:
            metadata = {}
        self._validate_metadata(metadata)

        start_time, end_time = new_event
        show = self._show_alert(start_time, end_time)
        notification = self._send_notification(start_time, end_time)
        metadata[MTD_SENDNOTIFICATION] = str(notification)
        metadata[MTD_SHOW] = str(show)
        metadata[MTD_NOTIFICATION_MESSAGE] = notification_message

        event = Event(
            start_time=start_time,
            metadata=metadata,
        )

        event.metadata[EVENT_END] = str(end_time)
        if end_time < end - self.merge_period:
            event.end_time = end_time

        return event

    def _close_event(
        self,
        existing_events: Union[EventList, List[Event]],
        new_events: List[List[int]],
        end: int,
        notification: str,
    ) -> Tuple[List[Event], List[List[int]]]:
        """`Identified open Events and check with current events if they should be closed. Manipulates new
            event if overlaps with open Event.`_

        Args:
            existing_events (Union[EventList, List[Event]]): List of Events.
            new_events (List[List[int]]): List of lists with two integers. First indicates the start time
            and the second the end time.
            end (int): The last timestamp to consider.
            notification (str): A string that is going to be sent to the end user and visible in the Front End

        Returns:
            Tuple[List[Event], List[List[int]]]: A tuple with a list of open (or maybe now, closed) alerts and a
            list of new events (always sorted on start time).

        Examples:

                >>> from cognite.air.event_utils import _close_event
                >>> _close_event(existing_events=[Event(start_time=0, end_time=5), Event(start_time=10)],
                ...             new_events=[[15, 20]], end=20)

        """
        new_events = sorted(map(sorted, new_events))
        existing_events.sort(key=lambda e: e.start_time)
        remaining_new_events: List = []
        # first remove new alerts that are exactly the same
        existing_open_events = list(
            filter(lambda e: e.end_time is None or e.end_time > end - self.merge_period, existing_events)
        )
        if len(existing_open_events) == 0:
            return [], new_events

        # try to close open events with a different notification message
        open_events_with_different_notification = list(
            filter(
                lambda e: e.metadata is not None and e.metadata.get(MTD_NOTIFICATION_MESSAGE) != notification,
                existing_open_events,
            )
        )
        events_to_be_closed = []
        if len(open_events_with_different_notification):
            for open_event in open_events_with_different_notification:
                event_end = self._retrieve_event_end(open_event)
                open_event = self._set_event_end_time_and_show(open_event, end, event_end)
                events_to_be_closed.append(open_event)

        # only keep existing open events with the same notification message
        existing_open_events = list(
            filter(
                lambda e: e.metadata is None or e.metadata.get(MTD_NOTIFICATION_MESSAGE) == notification,
                existing_open_events,
            )
        )

        if len(existing_open_events) == 0:
            return events_to_be_closed, new_events

        # if there are no new events, try to close existing ones
        if len(new_events) == 0:
            for existing_open_event in existing_open_events:
                event_end = self._retrieve_event_end(existing_open_event)
                existing_open_event = self._set_event_end_time_and_show(existing_open_event, end, event_end)
                events_to_be_closed.append(existing_open_event)
            return events_to_be_closed, []
        for existing_open_event in existing_open_events:
            for i, new_event in enumerate(new_events):
                event_end = self._retrieve_event_end(existing_open_event)
                # Check if the new event is suitable for closing the old event.
                # This means the new event should overlap or be sufficiently close
                # to the open event to be considered a "closing event".
                # if self._can_new_event_close_open_event(event_end, new_event):
                if self._can_existing_event_be_prolonged(event_end, new_event):
                    new_event_end = new_event[1]
                    # check if new event is actually fitting in existing event if not try to close and update
                    # if new event end is smaller ignore
                    if new_event_end > event_end:
                        existing_open_event = self._set_event_end_time_and_show(existing_open_event, end, new_event_end)
                        existing_open_event.metadata[EVENT_END] = str(new_event_end)
                else:
                    remaining_new_events.append(new_event)
            # when end time in metadata is smaller than end - merge period, set end time to metadata end time
            final_event_end = self._retrieve_event_end(existing_open_event)
            existing_open_event = self._set_event_end_time_and_show(existing_open_event, end, final_event_end)
            events_to_be_closed.append(existing_open_event)
        return events_to_be_closed, remaining_new_events

    def _can_existing_event_be_prolonged(self, event_end: int, new_event: List[int]) -> bool:

        """`Checks if the new event can be considered a closing event for the open event`_

        Args:
            event_end (int): The end of the open event.
            new_event (List[int]): List of two integers denoting the start and end of the new event in ms.

        Returns:
            bool: Either if the new event closes the open event (True) or not (False)

        Examples:

                >>> from cognite.air.alert_utils import _can_new_event_close_open_event
                >>> print(_can_new_event_close_open_event(10, [9, 12]))
                True
                >>> print(_can_new_event_close_open_event(10, [11, 12]))
                False
        """
        # if event end equals the start of the new event it should be considered as a closer
        if event_end == new_event[0]:
            return True
        event_long_enough = new_event[1] - new_event[0] >= self.minimum_length_of_alert
        event_end_close_enough = new_event[0] - self.merge_period <= event_end
        new_event_ends_later = event_end < new_event[1]
        return event_long_enough and event_end_close_enough and new_event_ends_later

    def _set_event_end_time_and_show(self, existing_open_event: Event, end: int, event_end: int) -> Event:
        if event_end < end - self.merge_period:
            existing_open_event.end_time = event_end
        if (
            not is_string_truthy(existing_open_event.metadata.get(MTD_SHOW))
            and event_end - existing_open_event.start_time >= self.minimum_length_of_alert
        ):
            existing_open_event.metadata[MTD_SHOW] = "True"
        return existing_open_event

    def _retrieve_event_end(self, existing_open_event: Event) -> int:
        meta: Dict = existing_open_event.metadata or {}
        try:
            event_end: int = int(meta.get(EVENT_END, 0))
        except ValueError:
            raise ValueError(EVENT_ERROR_MESSAGE)
        return event_end

    def _filter_open_alerts(self, alerts: List[Event], end_point: int) -> Union[List[Event], List]:
        open_alerts = [
            alert for alert in alerts if alert.end_time is None or alert.end_time > end_point - self.merge_period
        ]
        return open_alerts

    def _update_events_cache(self, events: Union[EventList, List[Event]]):
        self._validate_events_list(events)
        events_cache_ids = [i.id for i in self.events_cache]
        added = []
        removed = []
        for event in events:
            if event.id in events_cache_ids:
                # update
                cached_event = [i for i in self.events_cache if event.id == i.id][0]
                cached_event_end = int(cached_event.metadata[EVENT_END])
                event_end = int(event.metadata[EVENT_END])
                if cached_event_end < event_end:
                    removed.append(cached_event)
                    added.append(event)

            else:
                added.append(event)

        self._remove_from_events_cache(removed)
        self._add_to_events_cache(added)

    def _add_to_events_cache(self, events: List[Event]):
        """Updating new_events so that we have it on the next run."""
        self._validate_events_list(events)
        self.events_cache += events

    def _remove_from_events_cache(self, events: List[Event]):
        if len(events) == 0:
            return
        event_ids = [i.id for i in events]
        events_cache_ids = [i.id for i in self.events_cache]
        self.events_cache = [
            self.events_cache[i] for i in range(len(events_cache_ids)) if events_cache_ids[i] not in event_ids
        ]

    def _validate_events_list(self, events: Union[List[Event], EventList]):
        if isinstance(events, EventList):
            return
        if not isinstance(events, list):
            raise ValueError("events is not a list")
        if len(events) == 0:
            return
        for i in events:
            if not isinstance(i, Event):
                raise ValueError("Contents are not Events.")
