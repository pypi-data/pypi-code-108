"""
Access to other grpc microservices. Functions:
- call_grpc - calls other grpc service
- async_call_grpc - awaitable version of call_grpc. Use if caller is "async def".
- get_description - to get other grpc's service description
- async_get_description - awaitable version of get_description. Use if caller is "async def".

See "Public API" section below.
"""

import asyncio
from base64 import b64encode
from collections import defaultdict
from functools import partial
import json
import logging
from time import perf_counter, sleep
from uuid import uuid4
import re

import grpc
from grpc_reflection.v1alpha import reflection_pb2, reflection_pb2_grpc
from google.protobuf import descriptor_pb2
from google.protobuf.descriptor_pool import DescriptorPool
from google.protobuf.symbol_database import SymbolDatabase
from google.protobuf import json_format
from kubernetes import client as k8s_client, config as k8s_config
from kubernetes.client.api_client import ApiClient as K8sApiClient
import requests
from memoization import cached

from delphai_backend_utils.caching import Cacher, register_cacher, get_cache
from delphai_backend_utils.config import get_config


GET_SERVICES_REQUEST = reflection_pb2.ServerReflectionRequest(list_services='services')
EXCUDED_NAMESPACES = set([
    'kube-public', 'kube-system', 'elasticsearch', 'gateway',
    'lens-metrics', 'nginx-ingress', 'default', 'kube-node-lease'])
CACHER_NAME = 'external services'
THIS_UUID = str(uuid4())  # Used to prevent self-gatewaying


class ExternalServices(Cacher):
    """
    Explored external services cache
    """
    name = CACHER_NAME
    renew_interval = 300  # renew every 5 min
    timeout = 60
    incluster = None  # initially

    def get_data_func(self):
        """Returns dict: function full name -> dict:
        - None: default branch definition
        - <branch name>: branch definition
        where branch definition is a dict:
        - host (str)
        - is_default (bool)
        - For functions that called in "natural" way
          - service_name (str)
          - method_name (str)
          - method_descriptor
          - input_descriptor
          - output_descriptor
          - input_prototype
          - output_prototype
        - For functions that called through gateway:
          - gateway: address of gateway
        """
        sleep(1)  # Sleep a second to allow this server to start

        strt = perf_counter()
        res = defaultdict(dict)
        is_first_update = not self.is_ready()

        if self.incluster is None:
            self.incluster = False
            try:
                k8s_config.load_incluster_config()
                self.incluster = True
                logging.info('Connected to kubernetes in cluster')
            except Exception:
                logging.warn('Working outside a kubernetes cluster')
                # k8s_config.load_kube_config()
                # with K8sApiClient() as api:
                #     logging.info(f'Connected to external kubernetes: {api.configuration.host}')

        def _clean_addr(addr: str) -> str:
            if not addr:
                return None
            while addr.endswith('/'):
                addr = addr[:-1]
            return addr or None

        grpc_config = get_config('grpc') or {}
        cfg_verbose = bool(grpc_config.get('verbose'))
        cfg_explore_localhost = bool(grpc_config.get('explore_localhost'))
        cfg_default_gateway = _clean_addr(grpc_config.get('default_gateway'))
        cfg_function_branches = {}
        for func_name, func_inst in (grpc_config.get('function_branches') or {}).items():
            if func_name and func_inst:
                clean_func_name = func_name.replace('/', '.')
                while clean_func_name.endswith('.*'):
                    clean_func_name = clean_func_name[:-2]
                if '*' in clean_func_name:
                    if is_first_update:
                        logging.warn(f'Bad config key "grpc.function_branches.{func_name}". Wrong position of "*".')
                    continue
                cfg_function_branches[clean_func_name + '.'] = func_inst

        gw_data = None
        if cfg_default_gateway:
            # Explore gatewayed functions
            gw_err = None
            try:
                gw_data_resp = requests.get(cfg_default_gateway)
                if gw_data_resp.status_code < 400:
                    gw_data = gw_data_resp.json()
                else:
                    gw_err = f'Status code from default gateway {cfg_default_gateway}: {gw_data_resp.status_code}'
            except Exception as exc:
                gw_err = f'Failed to use default gateway {cfg_default_gateway}: {exc}'
            if gw_data:
                if 'gateway_id' not in gw_data or 'status' not in gw_data or 'functions' not in gw_data:
                    gw_err = f'Wrong response from the default gateway {cfg_default_gateway}'
                    gw_data = None
                elif gw_data['gateway_id'] == THIS_UUID:
                    gw_err = f'Will not use myself as a default gateway {cfg_default_gateway}'
                    gw_data = None
                elif gw_data['status'] != 'active':
                    gw_err = f'Status of the default gateway {cfg_default_gateway} is "{gw_data["status"]}"'
                    gw_data = None
                else:
                    if cfg_verbose and is_first_update:
                        logging.info(f'Will use {cfg_default_gateway} as a default gateway')
            if gw_err:
                if is_first_update:
                    logging.warn(gw_err)

        # >>>> nested func connect_n_explore start
        def _connect_n_explore(host: str, branch_name: str, namespace_name: str):
            try:
                # Request reflection info
                with grpc.insecure_channel(host) as channel:
                    reflection_client = reflection_pb2_grpc.ServerReflectionStub(channel)
                    for response in reflection_client.ServerReflectionInfo(x for x in [GET_SERVICES_REQUEST]):
                        service_names = [service.name for service in response.list_services_response.service]
                        file_requests = (
                            reflection_pb2.ServerReflectionRequest(file_containing_symbol=service_name)
                            for service_name in service_names
                        )
                        file_descriptor_proto_bytes = _get_proto_bytes_for_requests(reflection_client, file_requests)

                        descriptor_pool = DescriptorPool()
                        _add_protos_to_descriptor_pool(reflection_client, descriptor_pool, file_descriptor_proto_bytes)
                        symbol_database = SymbolDatabase(descriptor_pool)

                        for sname in service_names:
                            sdescr = descriptor_pool.FindServiceByName(sname)
                            for methdescr in sdescr.methods:
                                meth_full_name = methdescr.full_name
                                if meth_full_name.startswith('grpc.reflection.v1alpha.ServerReflection'):
                                    continue
                                if branch_name not in res[meth_full_name]:
                                    inst_definition = {
                                        'host': host,
                                        'branch': branch_name,
                                        'is_default': False,
                                        'service_name': sname,
                                        'method_name': methdescr.name,
                                        'method_descriptor': methdescr,
                                        'input_descriptor': methdescr.input_type,
                                        'output_descriptor': methdescr.output_type,
                                        'input_prototype': symbol_database.GetPrototype(methdescr.input_type),
                                        'output_prototype': symbol_database.GetPrototype(methdescr.output_type),
                                    }
                                    res[meth_full_name][branch_name] = inst_definition
            except Exception:  # as exc:
                pass
        # <<<< nested func connect_n_explore end

        # Explore addresses specified in grpc.function_branches
        fpatterns_by_addr = defaultdict(dict)
        localhost_finder = re.compile('^https?://([^:/]+?):([0-9]+)$')
        if not self.incluster and cfg_function_branches:
            for func_pattern, br_str in cfg_function_branches.items():
                lh_match = localhost_finder.match(br_str)
                if lh_match:
                    host, port = lh_match.groups()
                    fpatterns_by_addr[(host, port)][func_pattern] = 1
            for host_port in fpatterns_by_addr.keys():
                if cfg_verbose and is_first_update:
                    logging.info(f'Exploring gRPC services on local port {host_port[1]}...')
                svc_local_addr = f'{host_port[0]}:{host_port[1]}'
                _connect_n_explore(svc_local_addr, f'{svc_local_addr}', svc_local_addr)

        # Connect to Kubernetes and explore registered services.
        if self.incluster:
            with K8sApiClient() as api:
                v1 = k8s_client.CoreV1Api(api)
                namespaces = v1.list_namespace()
                for namespace in filter(lambda ns: ns.metadata.name not in EXCUDED_NAMESPACES, namespaces.items):
                    for service in v1.list_namespaced_service(namespace.metadata.name).items:
                        svc_md = service.metadata
                        if svc_md is not None and service.spec is not None \
                           and service.spec.ports:
                            all_ports = set(str(el.target_port) for el in service.spec.ports if el is not None)
                            if '8080' in all_ports:
                                svc_local_addr = f'{svc_md.name}.{svc_md.namespace}:8080'
                                _connect_n_explore(svc_local_addr, svc_md.name, svc_md.namespace)
        elif cfg_explore_localhost:
            for local_port in range(8080, 8089):  # Explore local ports 8080..8088
                if ('localhost', str(local_port)) not in fpatterns_by_addr:
                    if cfg_verbose and is_first_update:
                        logging.info(f'Exploring gRPC services on local port {local_port}...')
                    svc_local_addr = f'localhost:{local_port}'
                    _connect_n_explore(svc_local_addr, f'{svc_local_addr}', svc_local_addr)

        if gw_data:
            for func_gw_descr in gw_data['functions']:
                func_gw_name = func_gw_descr['function_name']
                for inst_gw_descr in func_gw_descr['branches']:
                    branch_name = inst_gw_descr['name']
                    if branch_name not in res[func_gw_name]:
                        res[func_gw_name][branch_name] = {
                            'host': f'{cfg_default_gateway} -> {inst_gw_descr["host"]}',
                            'branch': branch_name,
                            'is_default': False,
                            'gateway': cfg_default_gateway,
                        }

        # Set default definitions
        reported_wrongs = set()
        for meth_name, definitions in res.items():
            # Apply priority specified in grpc.function_branches
            for func_pattern, br_str in cfg_function_branches.items():
                if not (meth_name + '.').startswith(func_pattern):
                    continue
                lh_match = localhost_finder.match(br_str)
                if lh_match:
                    host, port = lh_match.groups()
                    svc_local_addr = f'{host}:{port}'
                    if svc_local_addr in definitions:
                        definitions[None] = definitions[svc_local_addr]
                        break
                    elif is_first_update:
                        logging.warn(f'Function "{meth_name}" not found on {br_str}')
                else:
                    if br_str.startswith('branch://'):
                        branch = br_str[9:]
                        if branch in definitions:
                            definitions[None] = definitions[branch]
                            break
                        elif branch.startswith('svc-') and branch[4:] in definitions:
                            definitions[None] = definitions[branch[4:]]
                            break
                        elif not branch.startswith('svc-') and f'svc-{branch}' in definitions:
                            definitions[None] = definitions[f'svc-{branch}']
                            break
                        elif is_first_update and br_str not in reported_wrongs:
                            logging.warn(f'Branch "{branch}" not found')
                            reported_wrongs.add(br_str)
                    else:
                        if is_first_update and br_str not in reported_wrongs:
                            logging.warn(
                                f'Wrong branch definition "{br_str}" in grpc.function_branches. '
                                f'Use "branch://" or "http://" prefixes.')
                            reported_wrongs.add(br_str)
            if None not in definitions:
                if 'svc-master' in definitions:
                    definitions[None] = definitions['svc-master']
                else:
                    definitions[None] = definitions[list(definitions.keys())[0]]
            definitions[None]['is_default'] = True

        if cfg_verbose:
            if is_first_update:
                if res:
                    ffuncs = []
                    for fidx, ffullname in enumerate(sorted(res.keys())):
                        ffuncs.append(
                            f'{fidx+1}. {ffullname}:\n' + '\n'.join(
                                f' {"*" if bv["is_default"] else " "} branch {bk} at {bv["host"]}'
                                for bk, bv in res[ffullname].items() if bk))
                    found_msg = '\n' + '\n'.join(ffuncs)
                    logging.info(f'Functions found: {found_msg}')
                else:
                    logging.warn('NO functions found')
            logging.info(f'{self.name} cache was updated in {perf_counter()-strt:.3f}s.')
        return res


register_cacher(ExternalServices, True)


def _get_proto_bytes_for_requests(reflection_client, file_requests):
    """
    Borrowed from eagr.reflection.reflection_descriptor_database.get_proto_bytes_for_requests
    """
    file_descriptors_responses = reflection_client.ServerReflectionInfo(file_requests)
    proto_bytes = [
        file_descriptor_proto
        for response in file_descriptors_responses
        for file_descriptor_proto in response.file_descriptor_response.file_descriptor_proto
    ]
    return proto_bytes


def _add_protos_to_descriptor_pool(reflection_client, descriptor_pool, file_descriptor_proto_bytes):
    """
    Borrowed from eagr.reflection.reflection_descriptor_database.add_protos_to_descriptor_pool
    """
    # Set of already imported names
    imported_names = set()
    # Map of file descriptor proto names to the respective file descriptor protos
    reflected_names = {}
    # Stack of file descriptor proto names to be imported
    proto_names = []

    # Load the initial proto name stack and reflected names hash with root-level protos to import
    for serialized_proto in file_descriptor_proto_bytes:
        parsed_file_descriptor_proto = descriptor_pb2.FileDescriptorProto()
        parsed_file_descriptor_proto.ParseFromString(serialized_proto)
        file_descriptor_proto_name = parsed_file_descriptor_proto.name  # pylint: disable=no-member
        proto_names.append(file_descriptor_proto_name)
        reflected_names[file_descriptor_proto_name] = parsed_file_descriptor_proto

    # Recursively find file descriptor proto dependencies, and import the entire tree bottom-up
    for proto_name in proto_names:
        _import_dependencies_then_proto(
            reflection_client, descriptor_pool, proto_name, imported_names, reflected_names
        )


def _import_dependencies_then_proto(
    reflection_client, descriptor_pool, proto_name, imported_names, reflected_names
):
    """
    Borrowed from eagr.reflection.reflection_descriptor_database.import_dependencies_then_proto
    """
    if proto_name in imported_names:
        return

    # Anything in the proto_name depth-first search stack should already be reflected
    if proto_name not in reflected_names:
        raise RuntimeError(
            "Something went wrong. Stacked planned imports should either "
            "be already reflected or already imported. Please fix."
        )

    dependencies = reflected_names[proto_name].dependency  # pylint: disable=no-member
    # Reflect not-yet-reflected dependencies the same way we run server reflection on root protos
    not_yet_reflected_dependencies = []
    for dependency in dependencies:
        if (dependency not in imported_names) and (dependency not in reflected_names):
            not_yet_reflected_dependencies.append(dependency)

    if not_yet_reflected_dependencies:
        file_requests = (
            reflection_pb2.ServerReflectionRequest(file_by_filename=dependency)
            for dependency in not_yet_reflected_dependencies
        )
        file_descriptor_proto_bytes = _get_proto_bytes_for_requests(reflection_client, file_requests)
        for serialized_proto in file_descriptor_proto_bytes:
            parsed_file_descriptor_proto = descriptor_pb2.FileDescriptorProto()
            parsed_file_descriptor_proto.ParseFromString(serialized_proto)
            file_descriptor_proto_name = (
                parsed_file_descriptor_proto.name  # pylint: disable=no-member
            )
            reflected_names[file_descriptor_proto_name] = parsed_file_descriptor_proto

    # Recursively import dependencies
    for dependency in dependencies:
        _import_dependencies_then_proto(
            reflection_client, descriptor_pool, dependency, imported_names, reflected_names
        )

    # Import the proto itself, update memos
    descriptor_pool.Add(reflected_names[proto_name])
    imported_names.add(proto_name)
    del reflected_names[proto_name]


def _find_meth_definition(function: str, branch: str) -> dict:
    branch = branch or None
    cacher = get_cache(ExternalServices.name)
    methods_dict = cacher.get_data()
    if function not in methods_dict:
        raise ServiceFunctionNotFound(f'Service function "{function}" not found')
    meth_definitions = methods_dict[function]

    if branch:
        if branch not in meth_definitions:
            branch_found = False
            if branch.startswith('svc-'):
                # try to find without "svc-"
                if branch[4:] in meth_definitions:
                    branch = branch[4:]
                    branch_found = True
            else:
                # try to find with "svc-"
                if f'svc-{branch}' in meth_definitions:
                    branch = f'svc-{branch}'
                    branch_found = True
            if not branch_found:
                raise ServiceNotFound(f'Branch "{branch}" of for function "{function}" not found')
    else:
        branch = None
    return meth_definitions[branch]


def _message_template(message_descriptor, lvls: int = 10):
    """
    Returns descriptive template for message.
    """
    if lvls == 0:
        return '...'
    res = {}
    for fld in message_descriptor.fields:
        if fld.message_type:
            fld_content = _message_template(fld.message_type, lvls - 1)
        else:
            fld_content = fld.default_value
        if fld.default_value == []:
            if fld.message_type:
                fld_content = [fld_content, ]
            elif fld.type == 9:  # string
                fld_content = ['', ]
            elif fld.type == 2:  # float
                fld_content = [0., ]
            elif fld.type == 8:  # boolean
                fld_content = [False, ]
            elif fld.type in [3, 5]:  # int32, int64
                fld_content = [0, ]
        res[fld.name] = fld_content
    return res


# ====================== Public API ======================


class GrpcException(Exception):
    """General gRPC exception"""


class ServiceNotFound(GrpcException):
    """Service not found"""


class ServiceFunctionNotFound(GrpcException):
    """Service function not found"""


def call_grpc(function: str, params: dict, metadata: dict = None, branch: str = None) -> dict:
    """
    Calls other grpc service.
    :param function: function name, e.g. "delphai.textgen.Textgen.macro"
    :param params: request data as dict
    :param metadata: metadata as a dict to pass to service
    :param branch: specify branch name if you need particular service instance
    :return: response object as dict
    """
    meth_definition = _find_meth_definition(function, branch)

    res = None
    if 'gateway' in meth_definition:
        try:
            gw_addr = f'{meth_definition["gateway"]}/{function}'
            if branch:
                gw_addr = f'{gw_addr}?branch={branch}'
            headers = {}
            if metadata:
                headers['gRPC-Metadata'] = b64encode(json.dumps(metadata).encode())
            gw_data_resp = requests.post(gw_addr, json=params, headers=headers)
            if gw_data_resp.status_code < 400:
                res = gw_data_resp.json()
            else:
                raise GrpcException(
                    f'Status code from the gateway {meth_definition["gateway"]}: {gw_data_resp.status_code}')
        except Exception as exc:
            raise GrpcException(f'Failed to call through the gateway {meth_definition["gateway"]}: {exc}')
    else:
        with grpc.insecure_channel(meth_definition['host'], (("grpc.lb_policy_name", "round_robin"),)) as channel:
            method_callable = channel.unary_unary(
                "/{}/{}".format(meth_definition['service_name'], meth_definition['method_descriptor'].name),
                request_serializer=meth_definition['input_prototype'].SerializeToString,
                response_deserializer=meth_definition['output_prototype'].FromString,
            )
            res = json_format.MessageToDict(
                method_callable(
                    meth_definition['input_prototype'](**params), metadata=metadata.items()
                    if isinstance(metadata, dict) else None),
                preserving_proto_field_name=True, including_default_value_fields=False)
    if res is None:
        raise GrpcException(f'Function {function} was not called')
    elif len(res) == 1 and 'error' in res:
        raise GrpcException(f'Function {function} call failed: {res["error"]}')
    return res


async def async_call_grpc(function: str, params: dict, metadata: dict = None, branch: str = None) -> dict:
    """
    Awaitable version of call_grpc. Use if caller is "async def".
    """
    loop = asyncio.get_event_loop()
    func = partial(call_grpc, function, params, metadata, branch)
    return await loop.run_in_executor(None, func)


@cached(ttl=30)
def get_description(function: str, branch: str = None) -> dict:
    """
    Get other grpc's service description.
    :param function: function name, e.g. "delphai.textgen.Textgen.macro"
    :param branch: specify branch name if you need particular service instance
    :return: dict(function_name, branch, host, input template, output template)
    """
    meth_definition = _find_meth_definition(function, branch)

    if 'gateway' in meth_definition:
        res = None
        try:
            gw_addr = f'{meth_definition["gateway"]}/{function}'
            if branch:
                gw_addr = f'{gw_addr}?branch={branch}'
            gw_data_resp = requests.get(gw_addr)
            if gw_data_resp.status_code < 400:
                res = gw_data_resp.json()
            else:
                raise GrpcException(
                    f'Status code from the gateway {meth_definition["gateway"]}: {gw_data_resp.status_code}')
        except Exception as exc:
            raise GrpcException(f'Failed to get description through the gateway {meth_definition["gateway"]}: {exc}')
        res['host'] = meth_definition['host']
        return res
    else:
        return {
            'function_name': function,
            'branch': meth_definition['branch'],
            'host': meth_definition['host'],
            'input': _message_template(meth_definition['input_descriptor']),
            'output': _message_template(meth_definition['output_descriptor']),
        }


async def async_get_description(function: str, branch: str = None) -> dict:
    """
    Awaitable version of get_description. Use if caller is "async def".
    """
    loop = asyncio.get_event_loop()
    func = partial(get_description, function, branch)
    return await loop.run_in_executor(None, func)
