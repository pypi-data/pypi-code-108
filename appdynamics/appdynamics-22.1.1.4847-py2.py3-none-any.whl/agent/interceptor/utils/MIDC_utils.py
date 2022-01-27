import appdynamics.agent
from appdynamics.lang import import_module, wraps


def _parse_basic_data(method_info):
    """Extracts the class and method to be patched out of MIDC config
    """
    module = import_module(method_info.module)
    cls = getattr(module, method_info.cls)
    method = getattr(cls, method_info.method)
    return cls, method


def _add_midc_data_to_bt(midc_config, name, value):
    """Attaches the passed key value pair to the BT for further reporting.
    Appends the key, value, enabled_for_snapshots, enabled_for_analytics to current_bt.midc_data
    """
    agent = appdynamics.agent.get_agent_instance()
    current_bt_id = agent.get_current_bt().registered_id
    if (current_bt_id and (current_bt_id in agent.data_gatherer_registry.data_gatherer_bt_entries) and
            midc_config.id in agent.data_gatherer_registry.data_gatherer_bt_entries[current_bt_id]):
        agent.get_current_bt().midc_data.append((name, value, midc_config.enabled_for_snapshots,
                                                 midc_config.enabled_for_analytics))


def _test_match_conditions_and_add_reporting_data_to_bt(invoked_object, args, kwargs, ret_value,
                                                        method_data_gatherer_config):
    """Tests the invoked object, arguments and return value against the MIDC match conditions
    If all the match conditions are satsified, adds MIDC data to BT

    Note - args and kwargs are a tuple and dict of arguments and keyword arguments respectively
    """
    match_conditions = method_data_gatherer_config.match_conditions
    data_to_collect = method_data_gatherer_config.data_to_collect

    # Run all the conditions to make sure that the match conditions are satisified
    allow_to_collect = True
    for condition in match_conditions.invoked_object:
        allow_to_collect &= condition(invoked_object)
    for condition in match_conditions.method_parameter:
        allow_to_collect &= condition(*args, **kwargs)
    for condition in match_conditions.return_value:
        allow_to_collect &= condition(ret_value)

    if allow_to_collect:
        for collector in data_to_collect.invoked_object:
            _add_midc_data_to_bt(method_data_gatherer_config, collector['name'],
                                 collector['getter'](invoked_object))
        for collector in data_to_collect.method_parameter:
            _add_midc_data_to_bt(method_data_gatherer_config, collector['name'],
                                 collector['getter'](*args, **kwargs))
        for collector in data_to_collect.return_value:
            _add_midc_data_to_bt(method_data_gatherer_config, collector['name'], collector['getter'](ret_value))


def patch_method_to_report_data(method_info, method_data_gatherer_configs):
    cls, method = _parse_basic_data(method_info)

    @wraps(method)
    def wrapper(*args, **kwargs):
        """Wraps the needed method to report data according to MIDC config
        """
        # As of now, the method is always an instance method, so extracting invoked_object from args
        invoked_object = args[0]
        # args will now contain original_arguments - self
        args = args[1:]
        ret_value = method(invoked_object, *args, **kwargs)

        for method_data_gatherer_config in method_data_gatherer_configs:
            _test_match_conditions_and_add_reporting_data_to_bt(invoked_object, args, kwargs, ret_value,
                                                                method_data_gatherer_config)
        return ret_value

    wrapper._appd_intercepted = True
    wrapper._original = method
    setattr(cls, method_info.method, wrapper)


def reset_patch(method_info):
    """Resets the patch on method according the module cls method tuple
    """
    cls, method = _parse_basic_data(method_info)
    if method._appd_intercepted:
        setattr(cls, method_info.method, method._original)
