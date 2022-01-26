import json
import os
from ctypes import *
from ctypes.util import find_library
from daltons_tensorflow.python.core.binding import lib

_libc = CDLL(find_library('c'))
_libc.free.argtypes = [c_void_p]
_libc.free.restype = c_void_p

_daltons_new_policymanagementservice_client = lib.daltons_new_policymanagementservice_client
_daltons_new_policymanagementservice_client.argtypes = [c_char_p, POINTER(c_char_p)]
_daltons_new_policymanagementservice_client.restype = c_void_p

_list_policies = lib.daltons_policymanagementservice_client_list_policies
_list_policies.argtypes = [c_void_p, POINTER(c_int), POINTER(c_char_p)]
_list_policies.restype = c_void_p

_get_policy = lib.daltons_policymanagementservice_client_get_policy
_get_policy.argtypes = [c_void_p, c_char_p, POINTER(c_int), POINTER(c_char_p)]
_get_policy.restype = c_void_p

_update_policy = lib.daltons_policymanagementservice_client_update_policy
_update_policy.argtypes = [c_void_p, c_char_p, POINTER(c_char_p)]
_update_policy.restype = None

_create_policy = lib.daltons_policymanagementservice_client_create_policy
_create_policy.argtypes = [c_void_p, c_char_p, POINTER(c_char_p)]
_create_policy.restype = None

_create_policy_model_from_files = lib.daltons_policymanagementservice_client_create_policy_model_from_files
_create_policy_model_from_files.argtypes = [
    c_void_p, 
    c_char_p, 
    c_char_p, 
    c_long, 
    POINTER(c_char_p),
    POINTER(c_char_p), 
    c_int, 
    POINTER(c_char_p)
]
_create_policy_model_from_files.restype = None

class PolicyManagementClient:
    def __init__(self, address):
        err = c_char_p()
        caddr = c_char_p(address.encode('utf-8'))
        self._cli_ptr = _daltons_new_policymanagementservice_client(caddr, byref(err))

        if err.value != None:
            raise Exception(err.value.decode('utf-8'))

    def list_policies(self):
        length = c_int(0)
        err = c_char_p()
        data = _list_policies(self._cli_ptr, byref(length), byref(err))
        json_payload = string_at(data, length.value)

        if err.value != None:
            raise Exception(err.value.decode('utf-8'))

        obj = json.loads(json_payload)
        _libc.free(data)

        return obj['policies']
  
    def get_policy(self, id):
        length = c_int(0)
        err = c_char_p()
        id = c_char_p(id.encode('utf-8'))
        data = _get_policy(self._cli_ptr, id, byref(length), byref(err))
        json_payload = string_at(data, length.value)

        if err.value != None:
            raise Exception(err.value.decode('utf-8'))

        obj = json.loads(json_payload)
        _libc.free(data)

        return obj

    def update_policy(self, policy):
        policy_json = c_char_p(json.dumps(policy).encode('utf-8'))
        err = c_char_p()

        _update_policy(self._cli_ptr, policy_json, byref(err))
        if err.value != None:
            raise Exception(err.value.decode('utf-8'))

    def create_policy(self, policy):
        policy_json = c_char_p(json.dumps(policy).encode('utf-8'))
        err = c_char_p()

        _create_policy(self._cli_ptr, policy_json, byref(err))
        if err.value != None:
            raise Exception(err.value.decode('utf-8'))

        
    def upload_model(self, policy_id, model_id, version, directory):
        absolute_dir = os.path.abspath(directory)
        all_files = []

        for root, subdirs, files in os.walk(absolute_dir):
            for filename in files:
                file_path = os.path.abspath(os.path.join(absolute_dir, root, filename))
                all_files.append(file_path)

        c_files = (c_char_p*len(all_files))()
        c_names = (c_char_p*len(all_files))()

        for i in range(len(all_files)):
            file = all_files[i]
            name = os.path.relpath(file, absolute_dir)

            c_files[i] = c_char_p(file.encode('utf-8'))
            c_names[i] = c_char_p(name.encode('utf-8'))

        c_policy_id = c_char_p(policy_id.encode('utf-8'))
        c_model_id = c_char_p(model_id.encode('utf-8'))

        err = c_char_p()
        _create_policy_model_from_files(
            self._cli_ptr, 
            c_policy_id, 
            c_model_id, 
            c_long(version), 
            cast(byref(c_names), POINTER(c_char_p)), 
            cast(byref(c_files), POINTER(c_char_p)), 
            c_int(len(all_files)),
            byref(err)
        )

        if err.value != None:
            raise Exception(err.value.decode('utf-8'))
