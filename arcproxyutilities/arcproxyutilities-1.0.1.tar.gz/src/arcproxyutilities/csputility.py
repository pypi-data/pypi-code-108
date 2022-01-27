import os
import platform
import stat
import json
import urllib.request
import yaml
import time
import sys
from .constants import *
from ._utils import *
from base64 import b64decode
from glob import glob
from knack.log import get_logger
from azure.cli.core._profile import Profile
from subprocess import Popen, DEVNULL
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core import telemetry
from azure.cli.core.azclierror import ManualInterrupt, UnclassifiedUserFault, CLIInternalError, FileOperationError, ClientRequestError

logger = get_logger(__name__)


def is_csp_running(clientproxy_process):
    if clientproxy_process.poll() is None:
        return True
    else:
        return False


def client_side_proxy_wrapper(cmd,
                              client,
                              csp_version,
                              resource_group_name,
                              resource_provider_name,
                              resource_type_name,
                              cli_extension_name,
                              cluster_name,
                              client_proxy_port,
                              api_server_port,
                              release_date_windows,
                              release_date_linux,
                              token=None,
                              path=os.path.join(os.path.expanduser(
                                  '~'), '.kube', 'config'),
                              context_name=None):

    cloud = send_cloud_telemetry(cmd, cli_extension_name)
    if int(client_proxy_port) == int(api_server_port):
        raise ClientRequestError(f'Proxy uses port {api_server_port} internally.',
                                 recommendation='Please pass some other unused port through --port option.')

    operating_system = platform.system()
    args = []
    proc_name = f'arcProxy{operating_system}'

    telemetry.set_debug_info('CSP Version is ', csp_version)
    telemetry.set_debug_info('OS is ', operating_system)

    if(check_process(proc_name)):
        raise ClientRequestError(
            'Another instance of arc proxy is already running')

    port_error_string = ""
    if check_if_port_is_open(api_server_port):
        port_error_string += f'Port {api_server_port} is already in use. Please select a different port with --port option.\n'
    if check_if_port_is_open(client_proxy_port):
        telemetry.set_exception(exception='Client proxy port was in use.', fault_type=Client_Proxy_Port_Fault_Type,
                                summary=f'ArcProxyUtilities:Client proxy port was in use.')
        port_error_string += f"Port {client_proxy_port} is already in use for a different purpose. This is a port which is used by arc proxy internally. Please ensure that this port is open before running 'az {cli_extension_name} proxy'.\n"
    if port_error_string != "":
        raise ClientRequestError(port_error_string)

    # Creating installation location, request uri and older version exe location depending on OS
    if(operating_system == 'Windows'):
        install_location_string = f'.clientproxy\\{resource_provider_name}\\arcProxy{operating_system}{csp_version}.exe'
        requestUri = f'{CSP_Storage_Url}/{release_date_windows}/arcProxy{operating_system}{csp_version}.exe'
        older_version_string = f'.clientproxy\\{resource_provider_name}\\arcProxy{operating_system}*.exe'
        creds_string = r'.azure\accessTokens.json'

    elif(operating_system == 'Linux' or operating_system == 'Darwin'):
        install_location_string = f'.clientproxy/{resource_provider_name}/arcProxy{operating_system}{csp_version}'
        requestUri = f'{CSP_Storage_Url}/{release_date_linux}/arcProxy{operating_system}{csp_version}'
        older_version_string = f'.clientproxy/{resource_provider_name}/arcProxy{operating_system}*'
        creds_string = r'.azure/accessTokens.json'

    else:
        telemetry.set_exception(exception='Unsupported OS', fault_type=Unsupported_Fault_Type,
                                summary=f'ArcProxyUtilities:{operating_system} is not supported yet')
        raise ClientRequestError(
            f'The {operating_system} platform is not currently supported.')

    install_location = os.path.expanduser(
        os.path.join('~', install_location_string))
    args.append(install_location)
    install_dir = os.path.dirname(install_location)

    # If version specified by install location doesn't exist, then download the executable
    if not os.path.isfile(install_location):

        print("Setting up environment for first time use. This can take few minutes...")
        # Downloading the executable
        try:
            response = urllib.request.urlopen(requestUri)
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=Download_Exe_Fault_Type,
                                    summary='ArcProxyUtilities:Unable to download clientproxy executable.')
            raise CLIInternalError("Failed to download executable with client.",
                                   recommendation="Please check your internet connection." + str(e))

        responseContent = response.read()
        response.close()

        # Creating the .clientproxy folder if it doesnt exist
        if not os.path.exists(install_dir):
            try:
                os.makedirs(install_dir)
            except Exception as e:
                telemetry.set_exception(exception=e, fault_type=Create_Directory_Fault_Type,
                                        summary='ArcProxyUtilities:Unable to create installation directory')
                raise ClientRequestError(
                    "Failed to create installation directory." + str(e))
        else:
            older_version_string = os.path.expanduser(
                os.path.join('~', older_version_string))
            older_version_files = glob(older_version_string)

            # Removing older executables from the directory
            for f in older_version_files:
                try:
                    os.remove(f)
                except:
                    logger.warning("failed to delete older version files")

        try:
            with open(install_location, 'wb') as f:
                f.write(responseContent)
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=Create_CSPExe_Fault_Type,
                                    summary='ArcProxyUtilities:Unable to create proxy executable')
            raise ClientRequestError(
                "Failed to create proxy executable." + str(e))

        os.chmod(install_location, os.stat(
            install_location).st_mode | stat.S_IXUSR)

    # Creating config file to pass config to clientproxy
    config_file_location = os.path.join(install_dir, 'config.yml')

    if os.path.isfile(config_file_location):
        try:
            os.remove(config_file_location)
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=Remove_Config_Fault_Type,
                                    summary='ArcProxyUtilities:Unable to remove old config file')
            raise FileOperationError(
                "Failed to remove old config." + str(e))

    # initializations
    user_type = 'sat'
    creds = ''

    # if service account token is not passed
    if token is None:
        # Identifying type of logged in entity
        account = get_subscription_id(cmd.cli_ctx)
        account = Profile().get_subscription(account)
        user_type = account['user']['type']
        tenantId = graph_client_factory(cmd.cli_ctx).config.tenant_id

        if user_type == 'user':
            dict_file = {'server': {'httpPort': int(client_proxy_port), 'httpsPort': int(
                api_server_port)}, 'identity': {'tenantID': tenantId, 'clientID': CLIENTPROXY_CLIENT_ID}}
        else:
            dict_file = {'server': {'httpPort': int(client_proxy_port), 'httpsPort': int(
                api_server_port)}, 'identity': {'tenantID': tenantId, 'clientID': account['user']['name']}}

        if cloud == 'DOGFOOD':
            dict_file['cloud'] = 'AzureDogFood'

        # Fetching creds
        creds_location = os.path.expanduser(os.path.join('~', creds_string))
        try:
            with open(creds_location) as f:
                creds_list = json.load(f)
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=Load_Creds_Fault_Type,
                                    summary='ArcProxyUtilities:Unable to load accessToken.json')
            raise FileOperationError("Failed to load credentials." + str(e))

        user_name = account['user']['name']

        if user_type == 'user':
            key = 'userId'
            key2 = 'refreshToken'
        else:
            key = 'servicePrincipalId'
            key2 = 'accessToken'

        for i in range(len(creds_list)):
            creds_obj = creds_list[i]

            if key in creds_obj and creds_obj[key] == user_name:
                creds = creds_obj[key2]
                break

        if creds == '':
            telemetry.set_exception(exception='Credentials of user not found.', fault_type=Creds_NotFound_Fault_Type,
                                    summary='ArcProxyUtilities:Unable to find creds of user')
            raise UnclassifiedUserFault("Credentials of user not found.")

        if user_type != 'user':
            dict_file['identity']['clientSecret'] = creds
    else:
        dict_file = {'server': {'httpPort': int(
            client_proxy_port), 'httpsPort': int(api_server_port)}}

    telemetry.set_debug_info('User type is ', user_type)

    try:
        with open(config_file_location, 'w') as f:
            yaml.dump(dict_file, f, default_flow_style=False)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=Create_Config_Fault_Type,
                                summary='ArcProxyUtilities:Unable to create config file for proxy.')
        raise FileOperationError("Failed to create config for proxy." + str(e))

    args.append("-c")
    args.append(config_file_location)

    debug_mode = False
    if '--debug' in cmd.cli_ctx.data['safe_params']:
        args.append("-d")
        debug_mode = True
    client_side_proxy_main(cmd, client, resource_group_name, resource_provider_name, resource_type_name, cluster_name, args, client_proxy_port,
                           api_server_port, operating_system, creds, user_type, cloud, debug_mode, token=token, path=path, context_name=context_name, clientproxy_process=None)


def client_side_proxy_main(cmd,
                           client,
                           resource_group_name,
                           resource_provider_name,
                           resource_type_name,
                           cluster_name,
                           args,
                           client_proxy_port,
                           api_server_port,
                           operating_system,
                           creds,
                           user_type,
                           cloud,
                           debug_mode,
                           token=None,
                           path=os.path.join(os.path.expanduser(
                               '~'), '.kube', 'config'),
                           context_name=None,
                           clientproxy_process=None):
    expiry, clientproxy_process = client_side_proxy(cmd, client, resource_group_name, resource_provider_name, resource_type_name, cluster_name, 0, args, client_proxy_port,
                                                    api_server_port, operating_system, creds, user_type, cloud, debug_mode, token=token, path=path, context_name=context_name, clientproxy_process=None)
    next_refresh_time = expiry - CSP_REFRESH_TIME

    while(True):
        time.sleep(60)
        if(is_csp_running(clientproxy_process)):
            if time.time() >= next_refresh_time:
                expiry, clientproxy_process = client_side_proxy(cmd, client, resource_group_name, resource_provider_name, resource_type_name, cluster_name, 1, args, client_proxy_port,
                                                                api_server_port, operating_system, creds, user_type, cloud, debug_mode, token=token, path=path, context_name=context_name, clientproxy_process=clientproxy_process)
                next_refresh_time = expiry - CSP_REFRESH_TIME
        else:
            telemetry.set_exception(exception='Process closed externally.', fault_type=Proxy_Closed_Externally_Fault_Type,
                                    summary='ArcProxyUtilities:Process closed externally.')
            raise ManualInterrupt('Proxy closed externally.')


def client_side_proxy(cmd,
                      client,
                      resource_group_name,
                      resource_provider_name,
                      resource_type_name,
                      cluster_name,
                      is_csp_invoked_already,
                      args,
                      client_proxy_port,
                      api_server_port,
                      operating_system,
                      creds,
                      user_type,
                      cloud,
                      debug_mode,
                      token=None,
                      path=os.path.join(os.path.expanduser(
                          '~'), '.kube', 'config'),
                      context_name=None,
                      clientproxy_process=None):

    subscription_id = get_subscription_id(cmd.cli_ctx)
    rm_endpoint = arm_end_point(cloud)
    parent_resource_id = f'subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/{resource_provider_name}/{resource_type_name}/{cluster_name}'
    list_ingress_gateway_credential_request_uri = f'{rm_endpoint}{parent_resource_id}/providers/Microsoft.HybridConnectivity/endpoints/default/listIngressGatewayCredentials?api-version={List_Ingress_Gateway_Credential_Api_Version}' # default expiry = 3hr
    cmd_list_ingress_gateway_credential = "rest --method post -u" + list_ingress_gateway_credential_request_uri

    # Fetching relay + static user authentication information from the AC-RP.
    try:
        # TODO:call listIngressGateWayCredentials using client if python sdk is available
        list_ingress_gateway_credential_response = az_cli(cmd_list_ingress_gateway_credential)
    except Exception as e:
        if is_csp_invoked_already == 1:
            clientproxy_process.terminate()
        arm_exception_handler(
            e, Get_Ingress_Gateway_Credentials_Fault_Type, 'Unable to fetch relay and static user authentication information')
        raise CLIInternalError(
            "Failed to get relay and static user authentication information." + str(e))

    # Starting the client proxy process, if this is the first time that this function is invoked
    if is_csp_invoked_already == 0:
        try:
            if debug_mode:
                clientproxy_process = Popen(args)
            else:
                clientproxy_process = Popen(
                    args, stdout=DEVNULL, stderr=DEVNULL)
            print(f'Proxy is listening on port {api_server_port}')

        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=Run_Clientproxy_Fault_Type,
                                    summary='ArcProxyUtilities:Unable to run client proxy executable')
            raise CLIInternalError("Failed to start proxy process." + str(e))

        if user_type == 'user':
            identity_data = {}
            identity_data['refreshToken'] = creds
            identity_uri = f'https://localhost:{api_server_port}/identity/rt'

            # To prevent skip tls warning from printing to the console
            original_stderr = sys.stderr
            f = open(os.devnull, 'w')
            sys.stderr = f

            make_api_call_with_retries(identity_uri, identity_data, "post", False, Post_RefreshToken_Fault_Type,
                                             'Unable to post refresh token details to clientproxy',
                                             "Failed to pass refresh token details to proxy.", clientproxy_process)
            sys.stderr = original_stderr

    if token is not None:
        data = prepare_data_for_csp_token_case(
            list_ingress_gateway_credential_response)
    else:
        data = list_ingress_gateway_credential_response

    expiry = data['relay']['expiresOn']

    uri = f'http://localhost:{client_proxy_port}/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/{resource_provider_name}/{resource_type_name}/{cluster_name}/createkubeconfig?api-version={ProxyConfigurations_Kubeconfig_Api_Version}'

    # Post relay + static user authentication information to CSP
    response = make_api_call_with_retries(uri, data, "post", False, Post_Relay_Auth_Info,
                                                'Unable to post relay and static user authentication information to clientproxy',
                                                "Failed to pass relay and static user authentication information to proxy.", clientproxy_process)

    if is_csp_invoked_already == 0:
        # Decoding kubeconfig into a string
        try:
            kubeconfig = json.loads(response.text)
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=Load_Kubeconfig_Fault_Type,
                                    summary='ArcProxyUtilities:Unable to load Kubeconfig')
            close_subprocess_and_raise_cli_error(
                clientproxy_process, "Failed to load kubeconfig." + str(e))

        kubeconfig = kubeconfig['kubeconfigs'][0]['value']
        kubeconfig = b64decode(kubeconfig).decode("utf-8")

        if token is not None:
            kubeconfig = insert_token_in_kubeconfig(kubeconfig, token)

        try:
            print_or_merge_credentials(
                path, kubeconfig, True, context_name)
            if path != "-":
                if context_name is None:
                    kubeconfig_obj = load_kubernetes_configuration(path)
                    temp_context_name = kubeconfig_obj['current-context']
                else:
                    temp_context_name = context_name
                print("Start sending kubectl requests on '{}' context using kubeconfig at {}".format(
                    temp_context_name, path))

            print("Press Ctrl+C to close proxy.")

        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=Merge_Kubeconfig_Fault_Type,
                                    summary='ArcProxyUtilities:Unable to merge kubeconfig.')
            close_subprocess_and_raise_cli_error(
                clientproxy_process, "Failed to merge kubeconfig." + str(e))

    return expiry, clientproxy_process


def prepare_data_for_csp_token_case(response):
    data = response
    data['ingress']['aadProfile']['serverId'] = ""
    data['ingress']['aadProfile']['tenantId'] = ""
    return data


def insert_token_in_kubeconfig(decoded_kubeconfig_str, token):
    dict_yaml = yaml.safe_load(decoded_kubeconfig_str)
    dict_yaml['users'][0]['user']['token'] = token
    kubeconfig = yaml.dump(dict_yaml)
    return kubeconfig
