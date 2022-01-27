import yaml
import errno
import platform
import os
import stat
import tempfile
import requests
import time
from .constants import *
from knack.log import get_logger
from knack.prompting import prompt_y_n
from knack.prompting import NoTTYException
from azure.cli.core import telemetry
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
from msrest.exceptions import AuthenticationError, HttpOperationError, TokenExpiredError
from azure.cli.core.azclierror import CLIInternalError, ClientRequestError, AzureResponseError, AzureInternalError
from msrest.exceptions import ValidationError as MSRestValidationError
from psutil import process_iter, NoSuchProcess, AccessDenied, ZombieProcess, net_connections
from azure.cli.core import telemetry
from azure.cli.core.azclierror import CLIInternalError, FileOperationError, ClientRequestError, ResourceNotFoundError
from azure.cli.core import get_default_cli
from azure.cli.core._profile import Profile
from azure.graphrbac import GraphRbacManagementClient
from azure.cli.core.commands.client_factory import configure_common_settings

logger = get_logger(__name__)


def arm_exception_handler(ex, fault_type, summary, return_if_not_found=False):
    if isinstance(ex, AuthenticationError):
        telemetry.set_exception(
            exception=ex, fault_type=fault_type, summary=summary)
        raise AzureResponseError(
            "Authentication error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, TokenExpiredError):
        telemetry.set_exception(
            exception=ex, fault_type=fault_type, summary=summary)
        raise AzureResponseError(
            "Token expiration error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, HttpOperationError):
        status_code = ex.response.status_code
        if status_code == 404 and return_if_not_found:
            return
        if status_code // 100 == 4:
            telemetry.set_user_fault()
        telemetry.set_exception(
            exception=ex, fault_type=fault_type, summary=summary)
        if status_code // 100 == 5:
            raise AzureInternalError(
                "Http operation error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))
        raise AzureResponseError(
            "Http operation error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, MSRestValidationError):
        telemetry.set_exception(
            exception=ex, fault_type=fault_type, summary=summary)
        raise AzureResponseError(
            "Validation error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, HttpResponseError):
        status_code = ex.status_code
        if status_code == 404 and return_if_not_found:
            return
        if status_code // 100 == 4:
            telemetry.set_user_fault()
        telemetry.set_exception(
            exception=ex, fault_type=fault_type, summary=summary)
        if status_code // 100 == 5:
            raise AzureInternalError(
                "Http response error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))
        raise AzureResponseError(
            "Http response error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, ResourceNotFoundError) and return_if_not_found:
        return

    telemetry.set_exception(
        exception=ex, fault_type=fault_type, summary=summary)
    raise ClientRequestError(
        "Error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))


def check_process(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    for proc in process_iter():
        try:
            if proc.name().startswith(processName):
                return True
        except (NoSuchProcess, AccessDenied, ZombieProcess):
            pass
    return False


def send_cloud_telemetry(cmd, cli_extension_name):
    telemetry.add_extension_event(
        cli_extension_name, {'Context.Default.AzureCLI.AzureCloud': cmd.cli_ctx.cloud.name})
    cloud_name = cmd.cli_ctx.cloud.name.upper()
    # Setting cloud name to format that is understood by golang SDK.
    if cloud_name == PublicCloud_OriginalName:
        cloud_name = Azure_PublicCloudName
    elif cloud_name == USGovCloud_OriginalName:
        cloud_name = Azure_USGovCloudName
    return cloud_name


def load_kubernetes_configuration(filename):
    try:
        with open(filename) as stream:
            return yaml.safe_load(stream)
    except (IOError, OSError) as ex:
        if getattr(ex, 'errno', 0) == errno.ENOENT:
            telemetry.set_exception(exception=ex, fault_type=Kubeconfig_Failed_To_Load_Fault_Type,
                                    summary='ArcProxyUtilities:{} does not exist'.format(filename))
            raise FileOperationError('{} does not exist'.format(filename))
    except (yaml.parser.ParserError, UnicodeDecodeError) as ex:
        telemetry.set_exception(exception=ex, fault_type=Kubeconfig_Failed_To_Load_Fault_Type,
                                summary='ArcProxyUtilities:Error parsing {} ({})'.format(filename, str(ex)))
        raise FileOperationError(
            'Error parsing {} ({})'.format(filename, str(ex)))


def merge_kubernetes_configurations(existing_file, addition_file, replace, context_name=None):
    try:
        existing = load_kubernetes_configuration(existing_file)
        addition = load_kubernetes_configuration(addition_file)
    except Exception as ex:
        telemetry.set_exception(exception=ex, fault_type=Failed_To_Load_K8s_Configuration_Fault_Type,
                                summary='ArcProxyUtilities:Exception while loading kubernetes configuration')
        raise CLIInternalError(
            'Exception while loading kubernetes configuration.' + str(ex))

    if context_name is not None:
        addition['contexts'][0]['name'] = context_name
        addition['contexts'][0]['context']['cluster'] = context_name
        addition['clusters'][0]['name'] = context_name
        addition['current-context'] = context_name

    # rename the admin context so it doesn't overwrite the user context
    for ctx in addition.get('contexts', []):
        try:
            if ctx['context']['user'].startswith('clusterAdmin'):
                admin_name = ctx['name'] + '-admin'
                addition['current-context'] = ctx['name'] = admin_name
                break
        except (KeyError, TypeError):
            continue

    if addition is None:
        telemetry.set_exception(exception='Failed to load additional configuration', fault_type=Failed_To_Load_K8s_Configuration_Fault_Type,
                                summary='ArcProxyUtilities:failed to load additional configuration from {}'.format(addition_file))
        raise CLIInternalError(
            'failed to load additional configuration from {}'.format(addition_file))

    if existing is None:
        existing = addition
    else:
        handle_merge(existing, addition, 'clusters', replace)
        handle_merge(existing, addition, 'users', replace)
        handle_merge(existing, addition, 'contexts', replace)
        existing['current-context'] = addition['current-context']

    # check that ~/.kube/config is only read- and writable by its owner
    if platform.system() != 'Windows':
        existing_file_perms = "{:o}".format(
            stat.S_IMODE(os.lstat(existing_file).st_mode))
        if not existing_file_perms.endswith('600'):
            logger.warning('%s has permissions "%s".\nIt should be readable and writable only by its owner.',
                           existing_file, existing_file_perms)

    with open(existing_file, 'w+') as stream:
        try:
            yaml.safe_dump(existing, stream, default_flow_style=False)
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=Failed_To_Merge_Kubeconfig_File,
                                    summary='ArcProxyUtilities:Exception while merging the kubeconfig file')
            raise CLIInternalError(
                'Exception while merging the kubeconfig file.' + str(e))

    current_context = addition.get('current-context', 'UNKNOWN')
    msg = 'Merged "{}" as current context in {}'.format(
        current_context, existing_file)
    print(msg)


def handle_merge(existing, addition, key, replace):
    if not addition[key]:
        return
    if existing[key] is None:
        existing[key] = addition[key]
        return

    i = addition[key][0]
    temp_list = []
    for j in existing[key]:
        remove_flag = False
        if not i.get('name', False) or not j.get('name', False):
            continue
        if i['name'] == j['name']:
            if replace or i == j:
                remove_flag = True
            else:
                msg = 'A different object named {} already exists in your kubeconfig file.\nOverwrite?'
                overwrite = False
                try:
                    overwrite = prompt_y_n(msg.format(i['name']))
                except NoTTYException:
                    pass
                if overwrite:
                    remove_flag = True
                else:
                    msg = 'A different object named {} already exists in {} in your kubeconfig file.'
                    telemetry.set_exception(exception='A different object with same name exists in the kubeconfig file', fault_type=Different_Object_With_Same_Name_Fault_Type,
                                            summary="ArcProxyUtilities:" + msg.format(i['name'], key))
                    raise FileOperationError(msg.format(i['name'], key))
        if not remove_flag:
            temp_list.append(j)

    existing[key][:] = temp_list
    existing[key].append(i)


def load_kubernetes_configuration(filename):
    try:
        with open(filename) as stream:
            return yaml.safe_load(stream)
    except (IOError, OSError) as ex:
        if getattr(ex, 'errno', 0) == errno.ENOENT:
            telemetry.set_exception(exception=ex, fault_type=Kubeconfig_Failed_To_Load_Fault_Type,
                                    summary='ArcProxyUtilities:{} does not exist'.format(filename))
            raise FileOperationError('{} does not exist'.format(filename))
    except (yaml.parser.ParserError, UnicodeDecodeError) as ex:
        telemetry.set_exception(exception=ex, fault_type=Kubeconfig_Failed_To_Load_Fault_Type,
                                summary='ArcProxyUtilities:Error parsing {} ({})'.format(filename, str(ex)))
        raise FileOperationError(
            'Error parsing {} ({})'.format(filename, str(ex)))


def close_subprocess_and_raise_cli_error(proc_subprocess, msg):
    proc_subprocess.terminate()
    raise CLIInternalError(msg)


def make_api_call_with_retries(uri, data, method, tls_verify, fault_type, summary, cli_error, proc_subprocess=None):
    for i in range(API_CALL_RETRIES):
        try:
            response = requests.request(method, uri, json=data, verify=tls_verify)
            return response
        except Exception as e:
            time.sleep(5)
            if i != API_CALL_RETRIES - 1:
                pass
            else:
                telemetry.set_exception(
                    exception=e, fault_type=fault_type, summary=summary)
                if proc_subprocess is not None:
                    close_subprocess_and_raise_cli_error(
                        proc_subprocess, cli_error + str(e))


def print_or_merge_credentials(path, kubeconfig, overwrite_existing, context_name):
    """Merge an unencrypted kubeconfig into the file at the specified path, or print it to
    stdout if the path is "-".
    """
    # Special case for printing to stdout
    if path == "-":
        print(kubeconfig)
        return

    # ensure that at least an empty ~/.kube/config exists
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as ex:
            if ex.errno != errno.EEXIST:
                telemetry.set_exception(exception=ex, fault_type=Failed_To_Merge_Credentials_Fault_Type,
                                        summary='ArcProxyUtilities:Could not create a kubeconfig directory.')
                raise FileOperationError(
                    "Could not create a kubeconfig directory." + str(ex))
    if not os.path.exists(path):
        with os.fdopen(os.open(path, os.O_CREAT | os.O_WRONLY, 0o600), 'wt'):
            pass

    # merge the new kubeconfig into the existing one
    fd, temp_path = tempfile.mkstemp()
    additional_file = os.fdopen(fd, 'w+t')
    try:
        additional_file.write(kubeconfig)
        additional_file.flush()
        merge_kubernetes_configurations(
            path, temp_path, overwrite_existing, context_name)
    except yaml.YAMLError as ex:
        logger.warning(
            'Failed to merge credentials to kube config file: %s', ex)
    finally:
        additional_file.close()
        os.remove(temp_path)


def check_if_port_is_open(port):
    try:
        connections = net_connections(kind='inet')
        for tup in connections:
            if int(tup[3][1]) == int(port):
                return True
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=Port_Check_Fault_Type,
                                summary='ArcProxyUtilities:Failed to check if port is in use.')
        if platform.system() != 'Darwin':
            logger.info("Failed to check if port is in use. " + str(e))
        return False
    return False


def arm_end_point(cloud):
    if cloud == Azure_DogfoodCloudName:
        return Dogfood_RMEndpoint
    elif cloud == Azure_USGovCloudName:
        return USGov_RMEndpoint
    else:
        return Public_RMEndpoint


def az_cli (args_str):
    args = args_str.split()
    cli = get_default_cli()
    cli.invoke(args,  out_file = open(os.devnull, 'w'))
    if cli.result.result:
        return cli.result.result
    elif cli.result.error:
        raise Exception(cli.result.error)
    return True


def graph_client_factory(cli_ctx, **_):
    profile = Profile(cli_ctx=cli_ctx)
    cred, _, tenant_id = profile.get_login_credentials(
        resource=cli_ctx.cloud.endpoints.active_directory_graph_resource_id)
    client = GraphRbacManagementClient(cred, tenant_id,
                                       base_url=cli_ctx.cloud.endpoints.active_directory_graph_resource_id)
    configure_common_settings(cli_ctx, client)
    return client
