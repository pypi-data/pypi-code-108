# -*- coding: utf-8 -*-


def proc_cond(conds):
    if conds is None:
        return None

    conditions = []

    for cond in conds:
        condition = {}

        vals = []
        for value in cond.get('values', []):
            val = [value.get('val'), value.get('type')]
            vals.append(val)

        condition['vals'] = vals

        if cond.get('variable'):
            variable = cond.get('variable')

            if variable.get('global_var'):
                condition['global_var'] = variable.get('global_var')

            if variable.get('user_var'):
                condition['user_var'] = variable.get('user_var')

            if variable.get('name'):
                if variable.get('args'):
                    condition['var'] = [
                        variable.get('name'), variable.get('args')
                    ]
                else:
                    condition['var'] = variable.get('name')

        if cond.get('operator'):
            condition['op'] = cond.get('operator').get('name')
        if cond.get('caseless'):
            condition['caseless'] = cond.get('caseless')

        conditions.append(condition)

    return conditions


def proc_conseq(conseq):
    if conseq is None:
        return None

    conseqs = []

    for c in conseq:
        spec = {}

        if c.get('global_action_id'):
            spec['global_action'] = c.get('global_action_id')
        else:
            spec[c.get('type')] = c.get(c.get('type'), {})

        conseqs.append(spec)

    return conseqs


# rule_sets, action, threshold, clearance, redirect_url
def proc_waf(waf):
    if waf is None:
        return waf

    waf_rule = {}

    waf_rule['rule_sets'] = waf.get('rule_sets', [])

    if waf.get('threshold_score') >= 1000:
        waf_rule['threshold'] = 'high'
    elif waf.get('threshold_score') >= 100:
        waf_rule['threshold'] = 'medium'
    else:
        waf_rule['threshold'] = 'low'

    action = waf.get('action')

    if action == 'block':
        waf_rule['action'] = '403 Forbidden'
    else:
        waf_rule['action'] = action

    if action == 'edge-captcha' and waf.get('clearance'):
        waf_rule['clearance_time'] = waf.get('clearance')

    elif action == 'redirect' and waf.get('redirect_url'):
        waf_rule['redirect_url'] = waf.get('redirect_url')

    return waf_rule


def proc_proxy(proxy):
    if proxy is None:
        return None

    upstreams = []
    for upstream in proxy.get('upstream', []):
        upstreams.append({
            'upstream': upstream.get('id', None),
            'global_upstream': upstream.get('global_cluster', None),
            'weight': upstream.get('weight')
        })

    backup_upstreams = []
    for upstream in proxy.get('back_upstream', []):
        backup_upstreams.append({
            'upstream': upstream.get('id', None),
            'global_upstream': upstream.get('global_cluster', None),
            'weight': upstream.get('weight')
        })

    balancer_vars = None
    balancer_algorithm = None
    if proxy.get('balancer'):
        balancer_vars = proxy.get('balancer').get('variables')
        balancer_algorithm = proxy.get('balancer').get('algorithm')

    data = {
        'upstreams': upstreams,
        'connect_timeout': proxy.get('connect_timeout'),
        'read_timeout': proxy.get('read_timeout'),
        'send_timeout': proxy.get('send_timeout'),
        'retries': proxy.get('retries'),
        'retry_condition': proxy.get('retry_condition'),
        'multi_tier': proxy.get('layer_policty'),
    }

    if backup_upstreams:
        data['backup_upstreams'] = backup_upstreams

    if balancer_algorithm is not None:
        data['balancer_algorithm'] = balancer_algorithm

        if balancer_vars is not None:
            data['balancer_vars'] = balancer_vars

    return data


# cache_key, enable_default_ttl, default_ttl, default_ttl_unit, enforce_cache
def proc_cache(cache_rule):
    if cache_rule is None:
        return None

    cache_keys = []
    for cache_key in cache_rule.get('cache_key'):
        cache_keys.append(cache_key.get('name'))

    data = {
        'cache_key': cache_keys,
        'enable_default_ttl': cache_rule.get('enable_default_ttl', False),
        'default_ttl': cache_rule.get('default_ttl', 1),
        'default_ttl_unit': cache_rule.get('default_ttl_unit', 'min'),
    }

    if cache_rule.get('enforce_cache'):
        data['enforce_cache'] = cache_rule.get('enforce_cache')

    return data


def proc_content(content_rule):
    if content_rule is None:
        return None

    content = {}

    if content_rule.get('favicon'):
        content['favicon'] = content_rule.get('favicon')

    if content_rule.get('empty_gif'):
        content['empty_gif'] = content_rule.get('empty_gif')

    return content
