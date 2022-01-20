from __future__ import annotations

import time
from datetime import datetime, timedelta

from pyVmomi import vim

from cloudshell.cp.vcenter.handlers.si_handler import SiHandler


class EventManager:
    class VMOSCustomization:
        START_EVENT = "CustomizationStartedEvent"
        SUCCESS_END_EVENT = "CustomizationSucceeded"
        FAILED_END_EVENT = "CustomizationFailed"
        FAILED_NETWORKING_END_EVENT = "CustomizationNetworkSetupFailed"
        FAILED_UNKNOWN_END_EVENT = "CustomizationUnknownFailure"
        START_EVENT_TIMEOUT = 5 * 60
        END_EVENT_TIMEOUT = 20 * 60
        START_EVENT_WAIT_TIME = 10
        END_EVENT_WAIT_TIME = 30

    def _get_vm_events(
        self,
        si: SiHandler,
        vm,
        event_type_id_list,
        event_start_time: datetime | None = None,
    ):
        time_filter = vim.event.EventFilterSpec.ByTime()
        time_filter.beginTime = event_start_time

        # noinspection PyUnresolvedReferences
        vm_events = vim.event.EventFilterSpec.ByEntity(entity=vm, recursion="self")

        # noinspection PyArgumentList
        filter_spec = vim.event.EventFilterSpec(
            entity=vm_events, eventTypeId=event_type_id_list, time=time_filter
        )

        return si.query_event(filter_spec)

    def _wait_for_event(
        self,
        si: SiHandler,
        vm,
        event_type_id_list,
        timeout,
        wait_time,
        logger,
        event_start_time: datetime | None = None,
    ):
        timeout_time = datetime.now() + timedelta(seconds=timeout)

        while True:
            logger.info(f"Getting VM '{vm.name}' events {event_type_id_list}")
            events = self._get_vm_events(
                si,
                vm,
                event_type_id_list=event_type_id_list,
                event_start_time=event_start_time,
            )

            if events:
                logger.info(f"Found VM '{vm.name}' events: {events}")
                return next(iter(events))

            time.sleep(wait_time)

            if datetime.now() > timeout_time:
                logger.info(
                    f"Timeout for VM '{vm.name}' events {event_type_id_list} reached"
                )
                return

    def wait_for_vm_os_customization_start_event(
        self,
        si: SiHandler,
        vm,
        logger,
        event_start_time: datetime | None = None,
        timeout=None,
        wait_time=None,
    ):
        timeout = timeout or self.VMOSCustomization.START_EVENT_TIMEOUT
        wait_time = wait_time or self.VMOSCustomization.START_EVENT_WAIT_TIME

        start_event = self._wait_for_event(
            si,
            vm,
            logger=logger,
            event_type_id_list=[self.VMOSCustomization.START_EVENT],
            timeout=timeout,
            wait_time=wait_time,
            event_start_time=event_start_time,
        )

        if start_event is None:
            raise Exception(
                "Unable to Apply Customization Spec for the VM. "
                "See logs for the details."
            )

    def wait_for_vm_os_customization_end_event(
        self,
        si: SiHandler,
        vm,
        logger,
        event_start_time: datetime | None = None,
        timeout=None,
        wait_time=None,
    ):
        timeout = timeout or self.VMOSCustomization.END_EVENT_TIMEOUT
        wait_time = wait_time or self.VMOSCustomization.END_EVENT_WAIT_TIME

        return self._wait_for_event(
            si,
            vm,
            logger=logger,
            event_type_id_list=[
                self.VMOSCustomization.SUCCESS_END_EVENT,
                self.VMOSCustomization.FAILED_END_EVENT,
                self.VMOSCustomization.FAILED_UNKNOWN_END_EVENT,
                self.VMOSCustomization.FAILED_NETWORKING_END_EVENT,
            ],
            timeout=timeout,
            wait_time=wait_time,
            event_start_time=event_start_time,
        )
