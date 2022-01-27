"""Library for adaptively throttling events."""

import logging
import time

logger = logging.getLogger(__name__)


class ThrottleQueue:
    """A throttle queue is used to regulate the rate of events.

    The throttle queue queues a history of past events in order to
    moderate the rate at which expensive events occur.
    """

    def __init__(
        self, desired_events_per_epoch: int, epoch_duration_sec: float
    ) -> None:
        """Create a new throttle queue for a given desired event rate.

        Args:
            desired_events_per_epoch: int
                The number events that are desired for the given epoch.
            epoch_duration_sec: float
                The lenth of the epoch in seconds.
        """
        # A circular queue of past event timestamps that is 3 times the size of
        # the number of desired events.
        self._timestamp_queue = [0.0] * (3 * desired_events_per_epoch)
        self._timestamp_index = 0

        self._desired_events_per_epoch = desired_events_per_epoch
        self._epoch_duration_sec = epoch_duration_sec
        self._desired_interval = (
            self._epoch_duration_sec / self._desired_events_per_epoch
        )

    def throttle(self, throttling_msg: str) -> bool:
        """Register a new event and throttles it according to the past events.

        Returns:
            Whether or not this event was throttled.
        """
        now = time.time()
        # Compute the number of events in the current epoch above the desired number.
        events_in_epoch = sum(
            [now - x < self._epoch_duration_sec for x in self._timestamp_queue]
        )
        excess_events = events_in_epoch - self._desired_events_per_epoch
        throttled = excess_events >= 0
        if throttled:
            logger.warning("Throttling: {}".format(throttling_msg))

        # Add an exponential sleep penalty to throttle the events toward the desired
        # interval.
        # Note: small amounts of throttling occur while excess_events < 0. The total
        # contribution of this delay is
        #    T = DI * sum_{t=1}{N} 2^-t
        #      < DI * sum_{t=1}{inf} 2^-t
        #      = DI
        # where DI is the desired interval and N is the desired events per epoch.
        # Thus, there will be at most 1 unit of desired interval in delays before
        # full throttling is applied.
        time.sleep(self._desired_interval * 2.0 ** excess_events)

        # Record the latest event in the circular queue.
        self._timestamp_queue[self._timestamp_index] = time.time()
        self._timestamp_index = (self._timestamp_index + 1) % len(self._timestamp_queue)
        return throttled
