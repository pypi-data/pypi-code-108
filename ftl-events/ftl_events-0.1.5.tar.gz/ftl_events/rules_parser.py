import ftl_events.rule_types as rule_types


def parse_rule_sets(rule_sets):
    rule_set_list = []
    for rule_set in rule_sets:
        rule_set_list.append(rule_types.RuleSet(name=rule_set['name'],
                                                hosts=rule_set['hosts'],
                                                sources=parse_event_sources(rule_set['sources']),
                                                rules=parse_rules(rule_set['rules'])))
    return rule_set_list


def parse_event_sources(sources):
    source_list = []
    for source in sources:
        name = source['name']
        del source['name']
        transform = source.get('transform')
        if transform in source:
            del source['transform']
        source_name = list(source.keys())[0]
        source_args = {k: v for k, v in source[source_name].items()}
        source_list.append(rule_types.EventSource(name=name,
                                                  source_name=source_name,
                                                  source_args=source_args,
                                                  transform=transform))

    return source_list


def parse_rules(rules):
    rule_list = []
    for rule in rules:
        name = rule.get('name')
        rule_list.append(rule_types.Rule(name=name,
                                         condition=parse_condition(rule['condition']),
                                         action=parse_action(rule['action'])))

    return rule_list


def parse_action(action):
    module_name = list(action.keys())[0]
    module_args = {k: v for k, v in action[module_name].items()}
    return rule_types.Action(module=module_name, module_args=module_args)


def parse_condition(condition):
    return rule_types.Condition(condition)
