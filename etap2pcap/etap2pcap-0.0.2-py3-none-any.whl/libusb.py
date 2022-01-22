import ctypes.util
import os
import typing

from etap2pcap import common


default_lib_path = ctypes.util.find_library('usb-1.0')


class Lib:

    def __init__(self, lib_path: os.PathLike = default_lib_path):
        self._lib = _Lib(lib_path)
        self._ctx = self._lib.libusb_context_p(None)
        if self._lib.libusb_init(ctypes.byref(self._ctx)):
            raise Exception('libusb init error')

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __del__(self):
        self.close()

    def close(self):
        if self._lib is None:
            return
        self._lib.libusb_exit(self._ctx)
        self._lib = None

    def open_device(self,
                    vendor_id: int,
                    product_id: int
                    ) -> 'Device':
        handle = self._lib.libusb_open_device_with_vid_pid(
            self._ctx, vendor_id, product_id)
        if not handle:
            raise Exception('could not open device')

        device = Device()
        device._lib = self
        device._buff = ctypes.create_string_buffer(512)
        device._handle = handle

        if self._lib.libusb_claim_interface(handle, 0):
            raise Exception('could not claim interface 0')

        return device


class Device:

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __del__(self):
        self.close()

    def close(self):
        if self._lib is None:
            return
        self._lib._lib.libusb_close(self._handle)
        self._lib = None

    def read(self, endpoint: int) -> common.Data:
        transfered = ctypes.c_int(0)

        result = self._lib._lib.libusb_bulk_transfer(
            self._handle, (0x7F & endpoint) | 0x80, self._buff,
            len(self._buff), ctypes.byref(transfered), 0)

        if result:
            raise Exception('read error')

        return self._buff.raw[:transfered.value]

    def write(self,
              endpoint: int,
              data: common.Data,
              timeout: typing.Optional[float] = 5):
        buff = ctypes.create_string_buffer(data)
        transfered = ctypes.c_int(0)

        result = self._lib._lib.libusb_bulk_transfer(
            self._handle, 0x7F & endpoint, buff, len(data),
            ctypes.byref(transfered), int((timeout or 0) * 1000))

        if result or transfered.value < len(data):
            raise Exception('write error')


class _Lib:

    def __init__(self, path):
        lib = ctypes.cdll.LoadLibrary(str(path))

        self.libusb_context_p = ctypes.c_void_p
        self.libusb_device_handle_p = ctypes.c_void_p

        functions = [
            (ctypes.c_int, 'libusb_init', [
                ctypes.POINTER(self.libusb_context_p)]),
            (None, 'libusb_exit', [self.libusb_context_p]),
            (self.libusb_device_handle_p, 'libusb_open_device_with_vid_pid', [
                self.libusb_context_p, ctypes.c_uint16, ctypes.c_uint16]),
            (None, 'libusb_close', [self.libusb_device_handle_p]),
            (ctypes.c_int, 'libusb_claim_interface', [
                self.libusb_device_handle_p, ctypes.c_int]),
            (ctypes.c_int, 'libusb_bulk_transfer', [
                self.libusb_device_handle_p,
                ctypes.c_ubyte,
                ctypes.POINTER(ctypes.c_char),
                ctypes.c_int,
                ctypes.POINTER(ctypes.c_int),
                ctypes.c_uint])
        ]

        for restype, name, argtypes in functions:
            function = getattr(lib, name)
            function.argtypes = argtypes
            function.restype = restype
            setattr(self, name, function)
