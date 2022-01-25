from ctypes import cdll, c_void_p, c_int, c_size_t, byref, RTLD_GLOBAL, CDLL
import os.path as path


class ProtectOnceInterface:
    def __init__(self):
        CDLL(path.join(path.dirname(
            path.abspath(path.join(__file__, "../.."))), 'lib/libnode.so'), RTLD_GLOBAL)
        core_lib_path = path.join(path.dirname(path.abspath(
            path.join(__file__, "../.."))), 'out/libprotectonce.so')
        self._core_interface = cdll.LoadLibrary(core_lib_path)

    def init_core(self):
        core_index_file = path.join(path.dirname(path.abspath(
            path.join(__file__, "../.."))), 'core/index.js')
        self._core_interface.protectOnceStart(
            self._to_bytes(core_index_file))

    def invoke(self, function_name, data, dataSize):
        out_data_type = c_int(0)
        out_data_size = c_size_t(0)
        mem_buffer_id = c_size_t(0)

        self._core_interface.protectOnceInvoke.restype = c_void_p
        in_data = self._to_bytes(data)
        result = self._core_interface.protectOnceInvoke(
            self._to_bytes(function_name), dataSize, in_data, len(in_data), byref(out_data_type), byref(out_data_size), byref(mem_buffer_id))

        return result, out_data_type.value, out_data_size.value, mem_buffer_id

    def release(self, mem_buffer_id):
        return self._core_interface.protectOnceRelease(mem_buffer_id)

    def shutdown_core(self):
        self._core_interface.protectOnceShutdown()

    def _to_bytes(self, strValue):
        try:
            if (isinstance(strValue, bytes)):
                return strValue

            return strValue.encode('utf-8')
        except:
            # TODO: print exception
            return b''
