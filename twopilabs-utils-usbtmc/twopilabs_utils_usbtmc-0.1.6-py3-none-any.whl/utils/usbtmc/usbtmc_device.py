import time
from typing import *
from .usbtmc_base import UsbTmcBase
from .usbtmc_device_info import UsbTmcDeviceInfo
from .usbtmc_device_address import UsbTmcDeviceAddress
from .usbtmc_exception import *
import usb.core
import usb.util

class UsbTmcDevice(UsbTmcBase):
    @classmethod
    def get_backend(cls):
        import usb.backend.libusb1
        backend = usb.backend.libusb1.get_backend()

        if backend is None:
            # No standard backend found, try loading one from libusb package
            try:
                import libusb
                backend = usb.backend.libusb1.get_backend(find_library=lambda x: libusb.dll._name)
            except:
                pass

        return backend

    @classmethod
    def list_devices(cls, usb_vid: Optional[int] = None, usb_pid: Optional[int] = None) -> List[UsbTmcDeviceInfo]:
        def match(dev):
            for cfg in dev:
                d = usb.util.find_descriptor(
                    cfg,
                    bInterfaceClass=UsbTmcBase.USBTMC_INTERFACE_CLASS,
                    bInterfaceSubClass=UsbTmcBase.USBTMC_INTERFACE_SUBCLASS)

                if d is None:
                    # Must have (at least) one interface with USBTMC_INTERFACE_CLASS/SUBCLASS
                    return False

                return True

        # Get a backend for searching USB devices
        backend = cls.get_backend()
        matches = {'custom_match': match}
        if usb_vid is not None: matches.update({'idVendor': usb_vid})
        if usb_pid is not None: matches.update({'idProduct': usb_pid})

        # usb.core.find returns an empty list when backend is None (i.e. no backend available)
        # thus silently ignoring the UsbTmc list_devices functionality
        return [UsbTmcDeviceInfo.from_device(device) for device in usb.core.find(backend=backend, find_all=True, **matches)]

    def __init__(self,
                 address: UsbTmcDeviceAddress,
                 timeout: Optional[float] = None,
                 transfer_size_max: Optional[int] = None,
                 **kwargs):
        super().__init__(**kwargs)

        self._opened = False
        self._reattach_kernel_driver = []
        self._ep_bulk_in = self._ep_bulk_out = self._ep_intr_in = None
        self._timeout_ms = int(timeout*1000) if timeout is not None else UsbTmcBase.DEFAULT_TIMEOUT_MS
        self._address = address
        self._transfer_btag_next = UsbTmcBase.DEFAULT_BTAG
        self._transfer_size_max = \
            transfer_size_max if transfer_size_max is not None else UsbTmcBase.DEFAULT_TRANSFER_SIZE_MAX
        self._backend = self.get_backend()

        if self._backend is None:
            raise UsbTmcConnectionException('No suitable backend for USB communication found')

        # Open device
        if self._address.serial_number is not None:
            self._device = usb.core.find(backend=self._backend,
                                         idVendor=self._address.vid, idProduct=self._address.pid,
                                         serial_number=self._address.serial_number)
        else:
            self._device = usb.core.find(backend=self._backend,
                                         idVendor=self._address.vid, idProduct=self._address.pid)

        if self._device is None:
            raise UsbTmcConnectionException(
                f'USB device with VID:PID {self._address.vid:04x}:{self._address.pid:04x}'
                + (f' (serial number: {self._address.serial_number})' if self._address.serial_number is not None else '')
                + ' was not found') from None

        # find first USBTMC interface with matching INTERFACE_CLASS/SUBCLASS
        # and matching bInterfaceNumber (if it is given)
        for cfg in self._device:
            for iface in cfg:
                if (iface.bInterfaceClass == UsbTmcBase.USBTMC_INTERFACE_CLASS and
                        iface.bInterfaceSubClass == UsbTmcBase.USBTMC_INTERFACE_SUBCLASS and
                        (self._address.interface_number is None or iface.bInterfaceNumber == self._address.interface_number)):
                    self._configuration = cfg
                    self._interface = iface
                    break
            else:
                # Inner loop was not broken
                continue

            # Inner loop was broken
            break
        else:
            raise UsbTmcConnectionException(
                f'USB device with VID:PID {self._address.vid:04x}:{self._address.pid:04x}'
                + (f' (serial number: {self._address.serial_number})' if self._address.serial_number is not None else '')
                + ' has no registered USBTMC interface') from None
            pass

        if self._interface.bInterfaceProtocol != UsbTmcBase.USB488_INTERFACE_PROTOCOL:
            pass

        try:
            if self._device.is_kernel_driver_active(self._interface.index):
                self._reattach_kernel_driver.append(self._interface)

                try:
                    self._device.detach_kernel_driver(self._interface.index)
                except usb.core.USBError as e:
                    raise UsbTmcConnectionException(
                        f'USB device with VID:PID {self._address.vid:04x}:{self._address.pid:04x}'
                        + (f' (serial number: {self._address.serial_number})' if self._address.serial_number is not None else '')
                        + f' could not be detached from kernel driver at interface index {self._interface.index} ({e})') from None
        except NotImplementedError:
            # We are on a platform that does not implement kernel driver detach/attach, just ignore then
            pass

        # set configuration
        try:
            self._device.set_configuration(self._configuration)
        except usb.core.USBError as e:
            raise UsbTmcConnectionException(
                f'USB device with VID:PID {self._address.vid:04x}:{self._address.pid:04x}'
                + (f' (serial number: {self._address.serial_number})' if self._address.serial_number is not None else '')
                + f' could not be set to configuration {self._configuration.index} ({e})') from None

        # claim interface
        usb.util.claim_interface(self._device, self._interface)

        # No altsetting required, only one altsetting per the USBTMC spec

        # find endpoints
        for ep in self._interface:
            ep_dir = usb.util.endpoint_direction(ep.bEndpointAddress)
            ep_type = usb.util.endpoint_type(ep.bmAttributes)

            if ep_type == usb.util.ENDPOINT_TYPE_BULK and ep_dir == usb.util.ENDPOINT_IN:
                self._ep_bulk_in = ep
            elif ep_type == usb.util.ENDPOINT_TYPE_BULK and ep_dir == usb.util.ENDPOINT_OUT:
                self._ep_bulk_out = ep
            elif ep_type == usb.util.ENDPOINT_TYPE_INTR and ep_dir == usb.util.ENDPOINT_IN:
                self._ep_intr_in = ep

        if self._ep_bulk_in is None or self._ep_bulk_out is None:
            raise UsbTmcConnectionException(
                f'USB device with VID:PID {self._address.vid:04x}:{self._address.pid:04x}'
                + (f' (serial number: {self._address.serial_number})' if self._address.serial_number is not None else '')
                + ' is missing at least one required endpoint') from None
            pass

        self._opened = True

        self.clear()

        self._capabilities = self.get_capabilities()

    def get_capabilities(self):
        if not self._opened:
            raise UsbTmcConnectionException('Connection is not open') from None

        caps = self._device.ctrl_transfer(
            usb.util.build_request_type(
                usb.util.CTRL_IN,
                usb.util.CTRL_TYPE_CLASS,
                usb.util.CTRL_RECIPIENT_INTERFACE),
            bRequest=UsbTmcBase.RequestValue.USBTMC_REQUEST_GET_CAPABILITIES.value,
            wValue=0x0000,
            wIndex=self._interface.index,
            data_or_wLength=UsbTmcBase.Capabilities.size(),
            timeout=self._timeout_ms
        )

        if caps[0] == UsbTmcBase.RequestStatus.USBTMC_STATUS_SUCCESS.value:
            capabilities = UsbTmcBase.Capabilities.unpack(caps)
            if capabilities is not None:
                return capabilities
        else:
            raise UsbTmcStatusException(f'Unexpected status reported by device: {UsbTmcBase.RequestStatus(caps[0])}') from None

    def clear(self) -> None:
        if not self._opened:
            raise UsbTmcConnectionException('Connection is not open') from None

        # initiate clearing
        initiate = self._device.ctrl_transfer(
            bmRequestType=usb.util.build_request_type(
                usb.util.CTRL_IN,
                usb.util.CTRL_TYPE_CLASS,
                usb.util.CTRL_RECIPIENT_INTERFACE),
            bRequest=UsbTmcBase.RequestValue.USBTMC_REQUEST_INITIATE_CLEAR.value,
            wValue=0x0000,
            wIndex=self._interface.index,
            data_or_wLength=0x0001,
            timeout=self._timeout_ms
        )

        if initiate[0] == UsbTmcBase.RequestStatus.USBTMC_STATUS_SUCCESS.value:
            timeout = time.time() + self._timeout_ms / 1000

            # Initiated, wait for completion
            while time.time() < timeout:
                status = self._device.ctrl_transfer(
                    bmRequestType=usb.util.build_request_type(
                        usb.util.CTRL_IN,
                        usb.util.CTRL_TYPE_CLASS,
                        usb.util.CTRL_RECIPIENT_INTERFACE),
                    bRequest=UsbTmcBase.RequestValue.USBTMC_REQUEST_CHECK_CLEAR_STATUS.value,
                    wValue=0x000,
                    wIndex=self._interface.index,
                    data_or_wLength=0x0002,
                    timeout=self._timeout_ms
                )

                if status[0] != UsbTmcBase.RequestStatus.USBTMC_STATUS_PENDING.value:
                    if status[0] != UsbTmcBase.RequestStatus.USBTMC_STATUS_SUCCESS.value:
                        raise UsbTmcStatusException(f'Unexpected status reported by device: {UsbTmcBase.RequestStatus(status[0])}') from None
                    break
            else:
                raise UsbTmcTimeoutException('Timeout during USBTMC_REQUEST_CHECK_CLEAR_STATUS') from None

            # Clear halt condition to resume Bulk-OUT endpoint
            self._ep_bulk_out.clear_halt()
        else:
            raise UsbTmcStatusException(f'Unexpected status reported by device: {UsbTmcBase.RequestStatus(initiate[0])}') from None

    def trigger(self) -> None:
        if not self._opened:
            raise UsbTmcConnectionException('Connection is not open') from None

        if not self._capabilities.support_trigger:
            raise UsbTmcUnsupportedException('USB488_MSGID_TRIGGER is not supported') from None

        header = UsbTmcBase.TransferHeader(
            message_id=UsbTmcBase.TransferMsgId.USB488_MSGID_TRIGGER.value,
            btag=self._transfer_btag_next
        )

        try:
            self._ep_bulk_out.write(header.pack(), timeout=self._timeout_ms)
        except usb.core.USBTimeoutError:
            self._abort_bulk_in(header.btag)
            raise UsbTmcTimeoutException('Timeout during USB488_MSGID_TRIGGER') from None

        self._transfer_btag_next = header.btag_next

    def locate(self) -> None:
        if not self._opened:
            raise UsbTmcConnectionException('Connection is not open') from None

        if not self._capabilities.support_pulse:
            raise UsbTmcUnsupportedException('USBTMC_REQUEST_INDICATOR_PULSE is not supported') from None

        try:
            pulse = self._device.ctrl_transfer(
                bmRequestType=usb.util.build_request_type(
                    usb.util.CTRL_IN,
                    usb.util.CTRL_TYPE_CLASS,
                    usb.util.CTRL_RECIPIENT_INTERFACE),
                bRequest=UsbTmcBase.RequestValue.USBTMC_REQUEST_INDICATOR_PULSE.value,
                wValue=0x0000,
                wIndex=self._interface.index,
                data_or_wLength=0x0001,
                timeout=self._timeout_ms
            )
        except usb.core.USBTimeoutError:
            raise UsbTmcTimeoutException('Timeout during USBTMC_REQUEST_INDICATOR_PULSE') from None

        if pulse[0] != UsbTmcBase.RequestStatus.USBTMC_STATUS_SUCCESS.value:
            raise UsbTmcStatusException('Unexpected status reported by device: {UsbTmcBase.RequestStatus(pulse[0])}') from None

    def write(self, data: bytes) -> int:
        if not self._opened:
            raise UsbTmcConnectionException('Connection is not open') from None

        remaining = len(data)
        index = 0

        # Start individual transfers up to self._transfer_size_max in length while there is data to be sent
        while remaining > 0:
            # New transfer with limited maximum size and a new send buffer used to prepend header and append padding
            transfer_size = remaining if remaining < self._transfer_size_max else self._transfer_size_max
            buffer = bytearray(UsbTmcBase.TransferHeader.size() + UsbTmcBase.aligned_length(transfer_size))

            # Create the transfer header
            header = UsbTmcBase.TransferHeader(
                message_id=UsbTmcBase.TransferMsgId.USBTMC_MSGID_DEV_DEP_MSG_OUT.value,
                btag=self._transfer_btag_next,
                transfer_size=transfer_size,
                transfer_attrs=
                # In last of all transfers, set the EOM (end of message) flag
                UsbTmcBase.TransferAttrs.USBTMC_TRANSFERATTR_EOM if remaining <= self._transfer_size_max else
                UsbTmcBase.TransferAttrs.USBTMC_TRANSFERATTR_NONE
            )

            # Copy data in new bytearray with created header and append padding
            buffer_view = memoryview(buffer)
            buffer_view[0:header.size()] = header.pack()
            buffer_view[header.size():header.size() + transfer_size] = data[index:index + transfer_size]

            # Send out the transfer
            try:
                self._ep_bulk_out.write(buffer, timeout=self._timeout_ms)
            except usb.core.USBTimeoutError:
                # timeout, abort transfer to regain synchronization
                self._abort_bulk_out(header.btag)
                raise UsbTmcTimeoutException('Timeout during USBTMC_MSGID_DEV_DEP_MSG_OUT') from None

            remaining -= transfer_size
            index += transfer_size
            self._transfer_btag_next = header.btag_next

        return len(data) - remaining

    def read(self, num: int = -1, term_char: bytes = None) -> bytes:
        if not self._opened:
            raise UsbTmcConnectionException('Connection is not open') from None

        remaining = num
        index = 0

        # Allocate read buffer ahead of time if length is known, else zero-length array
        data = bytearray(num) if num > 0 else bytearray()

        while remaining != 0:
            # Request a new IN transfer from device with known number of bytes or self._transfer_size_max if size is not known
            transfer_size = remaining if 0 < remaining < self._transfer_size_max else self._transfer_size_max

            # Generate the request header
            header = UsbTmcBase.TransferHeader(
                message_id=UsbTmcBase.TransferMsgId.USBTMC_MSGID_REQUEST_DEV_DEP_MSG_IN.value,
                btag=self._transfer_btag_next,
                transfer_size=transfer_size,
                transfer_attrs=
                # Request termination on TERM_CHAR when term_char is given as parameter
                UsbTmcBase.TransferAttrs.USBTMC_TRANSFERATTR_TERM_CHAR if term_char is not None and self._capabilities.support_term_char else
                UsbTmcBase.TransferAttrs.USBTMC_TRANSFERATTR_NONE,
                term_char=term_char
            )

            # Send out transfer request
            try:
                self._ep_bulk_out.write(header.pack(), timeout=self._timeout_ms)
            except usb.core.USBTimeoutError:
                # timeout, abort transfer
                self._abort_bulk_out(header.btag)
                raise UsbTmcTimeoutException('Timeout during USBTMC_MSGID_REQUEST_DEV_DEP_MSG_IN') from None

            # Receive the requested data from the device
            try:
                buffer = self._ep_bulk_in.read(
                    UsbTmcBase.TransferHeader.size() + UsbTmcBase.aligned_length(transfer_size),
                    timeout=self._timeout_ms)
                buffer_view = memoryview(buffer)
            except usb.core.USBTimeoutError:
                # timeout, abort transfer
                self._abort_bulk_in(header.btag)
                raise UsbTmcTimeoutException('Timeout during USBTMC_MSGID_DEV_DEP_MSG_IN') from None

            # Unpack header
            header = UsbTmcBase.TransferHeader.unpack(buffer_view)

            # Data processing depends on whether we already know the length of data or not
            if remaining < 0:
                # Append data to data array in endless read mode
                data.extend(buffer_view[header.size():header.size() + header.transfer_size])
            else:
                # Copy over data in known-length mode
                data[index:index + header.transfer_size] = buffer_view[header.size():header.size() + header.transfer_size]

                # Track remaining data length
                remaining = (remaining - header.transfer_size) if remaining > header.transfer_size else 0

            # In any case, abort on TERM_CHAR (only if requested) or EOM
            if (((header.transfer_attrs & UsbTmcBase.TransferAttrs.USBTMC_TRANSFERATTR_TERM_CHAR)
                 and term_char is not None)
                    or header.transfer_attrs & UsbTmcBase.TransferAttrs.USBTMC_TRANSFERATTR_EOM):
                remaining = 0

            # Advance variables for next transfer
            index += header.transfer_size
            self._transfer_btag_next = header.btag_next

        return data

    def _abort_bulk_in(self, btag: int) -> None:
        initiate = self._device.ctrl_transfer(
            bmRequestType=usb.util.build_request_type(
                usb.util.CTRL_IN,
                usb.util.CTRL_TYPE_CLASS,
                usb.util.CTRL_RECIPIENT_ENDPOINT),
            bRequest=UsbTmcBase.RequestValue.USBTMC_REQUEST_INITIATE_ABORT_BULK_IN.value,
            wValue=btag,
            wIndex=self._ep_bulk_in.bEndpointAddress,
            data_or_wLength=0x0002,
            timeout=self._timeout_ms
        )

        if initiate[0] == UsbTmcBase.RequestStatus.USBTMC_STATUS_SUCCESS.value:
            # "The Host should continue reading from the Bulk-IN endpoint until a short packet is received."
            try:
                while self._ep_bulk_in.read(self._ep_bulk_in.wMaxPacketSize,
                                            timeout=self._timeout_ms) == self._ep_bulk_in.wMaxPacketSize:
                    pass
            except usb.core.USBTimeoutError:
                # timeout
                raise UsbTmcTimeoutException('Timeout during USBTMC_REQUEST_INITIATE_ABORT_BULK_IN') from None

            # Check the status
            check = None
            timeout = time.time() + self._timeout_ms / 1000
            while time.time() < timeout:
                try:
                    check = self._device.ctrl_transfer(
                        bmRequestType=usb.util.build_request_type(
                            usb.util.CTRL_IN,
                            usb.util.CTRL_TYPE_CLASS,
                            usb.util.CTRL_RECIPIENT_ENDPOINT),
                        bRequest=UsbTmcBase.RequestValue.USBTMC_REQUEST_CHECK_ABORT_BULK_IN_STATUS.value,
                        wValue=0x0000,
                        wIndex=self._ep_bulk_in.bEndpointAddress,
                        data_or_wLength=0x0008,
                        timeout=self._timeout_ms
                    )
                except usb.core.USBError:
                    pass

                time.sleep(0.1)

                if check is not None and check[0] != UsbTmcBase.RequestStatus.USBTMC_STATUS_PENDING.value:
                    # While pending, continue 
                    break
            else:
                # Timeout waiting for abort
                raise UsbTmcTimeoutException('Timeout during USBTMC_REQUEST_CHECK_ABORT_BULK_IN_STATUS') from None

        elif initiate[0] == UsbTmcBase.RequestStatus.USBTMC_STATUS_TRANSFER_NOT_IN_PROGRESS.value:
            # bTag mismatch
            raise UsbTmcConnectionException('bTag mismatch during USBTMC_REQUEST_INITIATE_ABORT_BULK_IN') from None
        else:
            # Consider request failed, i.e. no Bulk-IN abort was initiated
            pass

    def _abort_bulk_out(self, btag: int) -> None:
        initiate = self._device.ctrl_transfer(
            bmRequestType=usb.util.build_request_type(
                usb.util.CTRL_IN,
                usb.util.CTRL_TYPE_CLASS,
                usb.util.CTRL_RECIPIENT_ENDPOINT),
            bRequest=UsbTmcBase.RequestValue.USBTMC_REQUEST_INITIATE_ABORT_BULK_OUT.value,
            wValue=btag,
            wIndex=self._ep_bulk_out.bEndpointAddress,
            data_or_wLength=0x0002,
            timeout=self._timeout_ms
        )

        if initiate[0] == UsbTmcBase.RequestStatus.USBTMC_STATUS_SUCCESS.value:
            # "The Host must send CHECK_ABORT_BULK_OUT_STATUS."
            check = None
            timeout = time.time() + self._timeout_ms / 1000
            while time.time() < timeout:
                try:
                    check = self._device.ctrl_transfer(
                        bmRequestType=usb.util.build_request_type(
                            usb.util.CTRL_IN,
                            usb.util.CTRL_TYPE_CLASS,
                            usb.util.CTRL_RECIPIENT_ENDPOINT),
                        bRequest=UsbTmcBase.RequestValue.USBTMC_REQUEST_CHECK_ABORT_BULK_OUT_STATUS.value,
                        wValue=0x0000,
                        wIndex=self._ep_bulk_in.bEndpointAddress,
                        data_or_wLength=0x0008,
                        timeout=self._timeout_ms
                    )
                except usb.core.USBError:
                    pass

                time.sleep(0.1)

                if check is not None and check[0] != UsbTmcBase.RequestStatus.USBTMC_STATUS_PENDING.value:
                    # While pending, continue
                    break
            else:
                # Timeout waiting for abort
                raise UsbTmcTimeoutException('Timeout during USBTMC_REQUEST_CHECK_ABORT_BULK_OUT_STATUS') from None

        elif initiate[0] == UsbTmcBase.RequestStatus.USBTMC_STATUS_TRANSFER_NOT_IN_PROGRESS.value:
            # bTag mismatch
            raise UsbTmcConnectionException('bTag mismatch during USBTMC_REQUEST_INITIATE_ABORT_BULK_OUT') from None
        else:
            # Consider request failed, i.e. no Bulk-OUT abort was initiated
            pass

    def readline(self, size: int = -1, term_char: Optional[bytes] = None) -> bytes:
        return self.read(size, term_char=term_char if term_char is not None else UsbTmcBase.DEFAULT_TERM_CHAR)

    def writelines(self, lines: Iterable[bytes]) -> None:
        for line in lines:
            self.write(line)

    def close(self) -> None:
        if not self._opened:
            return

        usb.util.release_interface(self._device, self._interface)
        usb.util.dispose_resources(self._device)

        # reattach kernel driver
        for iface in self._reattach_kernel_driver:
            try:
                self._device.attach_kernel_driver(iface.index)
            except usb.core.USBError:
                raise UsbTmcConnectionException(
                    f'USB device with VID:PID {self._address.vid}:{self._address.pid}'
                    + (f' (serial number: {self._address.serial_number})' if self._address.serial_number is not None else '')
                    + f' could not be reattached to kernel driver at interface index {self._interface.index}') from None

        self._reattach_kernel_driver = []
        self._opened = False

    @property
    def closed(self) -> bool:
        return True if not self._opened else False

    def __del__(self):
        self.close()
        pass
