from cloudshell.cp.vcenter.constants import SHELL_NAME
from cloudshell.cp.vcenter.resource_config import ShutdownMethod, VCenterResourceConfig


def test_resource_config(resource_command_context, cs_api):
    user = "user name"
    password = "password"
    default_datacenter = "default datacenter"
    default_dv_switch = "default dvSwitch"
    holding_network = "holding network"
    vm_cluster = "vm cluster"
    vm_resource_pool = "vm resource pool"
    vm_storage = "vm storage"
    saved_sandbox_storage = "saved sandbox storage"
    behavior_during_save = "behavior during save"
    vm_location = "vm location"
    shutdown_method = "soft"
    expected_shutdown_method = ShutdownMethod.SOFT
    ovf_tool_path = "ovf tool path"
    reserved_networks = "10.1.0.0/24;10.1.1.0/24"
    expected_reserved_networks = ["10.1.0.0/24", "10.1.1.0/24"]
    execution_server_selector = "Execution Server Selector"
    promiscuous_mode = "true"
    expected_promiscuous_mode = True

    a_name = VCenterResourceConfig.ATTR_NAMES
    get_full_a_name = lambda n: f"{SHELL_NAME}.{n}"  # noqa: E731
    resource_command_context.resource.attributes.update(
        {
            get_full_a_name(a_name.user): user,
            get_full_a_name(a_name.password): password,
            get_full_a_name(a_name.default_datacenter): default_datacenter,
            get_full_a_name(a_name.default_dv_switch): default_dv_switch,
            get_full_a_name(a_name.holding_network): holding_network,
            get_full_a_name(a_name.vm_cluster): vm_cluster,
            get_full_a_name(a_name.vm_resource_pool): vm_resource_pool,
            get_full_a_name(a_name.vm_storage): vm_storage,
            get_full_a_name(a_name.saved_sandbox_storage): saved_sandbox_storage,
            get_full_a_name(a_name.behavior_during_save): behavior_during_save,
            get_full_a_name(a_name.vm_location): vm_location,
            get_full_a_name(a_name.shutdown_method): shutdown_method,
            get_full_a_name(a_name.ovf_tool_path): ovf_tool_path,
            get_full_a_name(a_name.reserved_networks): reserved_networks,
            get_full_a_name(
                a_name.execution_server_selector
            ): execution_server_selector,
            get_full_a_name(a_name.promiscuous_mode): promiscuous_mode,
        }
    )
    conf = VCenterResourceConfig.from_context(
        context=resource_command_context,
        shell_name=SHELL_NAME,
        api=cs_api,
        supported_os=None,
    )

    assert conf.user == user
    assert conf.password == password
    assert conf.default_datacenter == default_datacenter
    assert conf.default_dv_switch == default_dv_switch
    assert conf.holding_network == holding_network
    assert conf.vm_cluster == vm_cluster
    assert conf.vm_resource_pool == vm_resource_pool
    assert conf.vm_storage == vm_storage
    assert conf.saved_sandbox_storage == saved_sandbox_storage
    assert conf.behavior_during_save == behavior_during_save
    assert conf.vm_location == vm_location
    assert conf.shutdown_method == expected_shutdown_method
    assert conf.ovf_tool_path == ovf_tool_path
    assert conf.reserved_networks == expected_reserved_networks
    assert conf.execution_server_selector == execution_server_selector
    assert conf.promiscuous_mode == expected_promiscuous_mode
