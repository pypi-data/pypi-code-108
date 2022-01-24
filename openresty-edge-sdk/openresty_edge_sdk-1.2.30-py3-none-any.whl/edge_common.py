# -*- coding: utf-8 -*-

def process_rule_cond(condition):
    if not condition:
        raise Exception('No condition field specified')

    if not isinstance(condition, list):
        raise Exception(
            'Bad condition field value type: ' + str(type(condition)))

    i = 0
    cond_specs = []

    for cond in condition:
        i += 1
        operator = cond.get('op', 'eq')
        var = cond.get('var')
        global_var = cond.get('global_var')
        user_var = cond.get('user_var')
        if not var and not global_var and not user_var:
            raise Exception(
                'No var or global_var or user_var '
                'specified in the {}-th condition'.format(str(i)))

        var_arg = None
        if isinstance(var, list):
            if len(var) != 2:
                raise Exception(
                    'variable spec must take 2 '
                    'elements in the {}-th condition'.format(str(i)))
            var, var_arg = var

        val = cond.get('val')
        vals = cond.get('vals')
        if val is not None:
            if vals is not None:
                raise Exception(
                    'The val and vals fields cannot be '
                    'specified at the same time')
            vals = [val]
            del val

        val_specs = []
        if operator not in ('is-empty', '!is-empty'):
            for val in vals:
                val_type = 'str'
                if isinstance(val, list):
                    if len(val) != 2:
                        raise Exception(
                            'variable spec must take 2 elements in the '
                            '{}-th condition'.format(str(i)))
                    val, val_type = val
                val_specs.append({'type': val_type, 'val': val})

        if var:
            variable = {'name': var}
            if var_arg:
                variable['args'] = var_arg
        elif global_var:
            variable = {'global_var': global_var}
        else:
            variable = {'user_var': user_var}

        cond_spec = {
            'variable': variable,
            'operator': {'name': operator},
        }

        if val_specs:
            cond_spec['values'] = val_specs

        caseless = cond.get('caseless')
        if caseless:
            cond_spec['caseless'] = caseless

        cond_specs.append(cond_spec)

    return cond_specs


def process_conseq(conseq):
    if not conseq:
        raise Exception('No conseq field specified')
    if isinstance(conseq, dict):
        conseq = [conseq]
    elif not isinstance(conseq, list):
        raise Exception('Bad conseq field value type: '
                        + str(type(conseq)))

    conseq_specs = []

    for item in conseq:
        for action_name, action_spec in item.items():
            if action_name == "global_action":
                conseq_specs.append({'global_action_id': action_spec})
                continue

            conseq_spec = {'type': action_name}
            if action_spec:
                conseq_spec[action_name] = action_spec
            conseq_specs.append(conseq_spec)

    return conseq_specs


def process_waf(waf):
    name2id = {
        'robots': 1,
        'generic': 2,
        'inject': 3,
        'trojans': 4,
        'xss': 5,
        'scanner_detection': 6,
        'protocol_enforcement': 7,
        'protocol_attack': 8,
        'application_attack_lfi': 9,
        'application_attack_rfi': 10,
        'application_attack_rce': 11,
        'application_attack_php': 12,
        'application_attack_nodejs': 13,
        'application_attack_xss': 14,
        'application_attack_sqli': 15,
        'application_attack_session_fixation': 16,
        'application_attack_java': 17,
    }

    rule_sets = waf.get('rule_sets', [])

    for (name, _) in name2id.items():
        if waf.get(name, None):
            rule_sets.append(name2id[name])

    action = waf.get('action', None)
    threshold = waf.get('threshold', 'medium')
    clearance = waf.get('clearance', 60)
    redirect_url = waf.get('redirect_url', None)

    if not action:
        raise Exception('No action field specified')

    if action == '403 Forbidden':
        action = 'block'

    threshold_score = 100
    if threshold == 'high':
        threshold_score = 1000
    elif threshold == 'medium':
        threshold_score = 100
    elif threshold == 'low':
        threshold_score = 10
    else:
        raise Exception('No value of threshold field')

    body = {
        'rule_sets': rule_sets,
        'action': action,
        'threshold_score': threshold_score
    }

    if action == 'edge-captcha' and clearance:
        body['clearance_time'] = clearance

    if action == 'redirect' and redirect_url:
        body['redirect_url'] = redirect_url

    return body


def process_proxy(proxy):
    upstream_el_code = proxy.get('upstream_el_code', '')
    upstreams = proxy.get('upstreams', None) or proxy.get('upstream', [])
    if not upstreams and not upstream_el_code:
        raise Exception('No upstreams specified')
    if upstreams and upstream_el_code:
        raise Exception('upstreams and upstream_el_code are conflicting')

    backup_upstreams = proxy.get('backup_upstreams', None) or proxy.get('backup_upstream', {})
    timeout = proxy.get('timeout', 3)
    connect_timeout = proxy.get('connect_timeout', timeout)
    read_timeout = proxy.get('read_timeout', timeout)
    send_timeout = proxy.get('send_timeout', timeout)
    retries = proxy.get('retries', 5)
    retry_condition = proxy.get('retry_condition',
                                ["error",
                                 "timeout",
                                 "invalid_header",
                                 "http_500",
                                 "http_502",
                                 "http_504",
                                 "http_404"])
    balancer = proxy.get('balancer', {})
    balancer_algorithm = proxy.get('balancer_algorithm', None) or balancer.get('algorithm', "roundrobin")
    balancer_vars = proxy.get('balancer_vars', None) or balancer.get('variables', [])
    multi_tier = proxy.get('multi_tier', None) or proxy.get('layer_policy', None)
    sticky = proxy.get('sticky', {'level': 'upstream','enable': False,
                                'ttl': 0,'key': 'Edge-Sticky','mode': 'none'})


    if balancer_algorithm != 'roundrobin' and balancer_vars == []:
        raise Exception('No balancer vars specified')

    up_specs = []
    for upstream in upstreams:
        up_id = upstream.get('upstream', None)
        k8s_up_id = upstream.get('k8s_upstream', None)
        global_up_id = upstream.get('global_upstream', None)
        global_k8s_up_id = upstream.get('global_k8s_upstream', None)
        weight = upstream.get('weight', 1)

        up_spec = {
            'cluster': up_id,
            'k8s_cluster': k8s_up_id,
            'global_cluster': global_up_id,
            'global_k8s_cluster': global_k8s_up_id,
            'weight': weight,
        }
        up_specs.append(up_spec)

    bup_specs = []
    for upstream in backup_upstreams:
        up_id = upstream.get('upstream', None)
        k8s_up_id = upstream.get('k8s_upstream', None)
        global_up_id = upstream.get('global_upstream', None)
        global_k8s_up_id = upstream.get('global_k8s_upstream', None)
        weight = upstream.get('weight', 1)

        bup_spec = {
            'cluster': up_id,
            'k8s_cluster': k8s_up_id,
            'global_cluster': global_up_id,
            'global_k8s_cluster': global_k8s_up_id,
            'weight': weight,
        }
        bup_specs.append(bup_spec)

    data = {
        'upstream': up_specs,
        'upstream_el_code': upstream_el_code,
        'connect_timeout': connect_timeout,
        'send_timeout': send_timeout,
        'read_timeout': read_timeout,
        'retries': retries,
        'retry_condition': retry_condition,
        'balancer': {
            'algorithm': balancer_algorithm,
            'variables': balancer_vars
        },
        'sticky': sticky,
    }

    if bup_specs:
        data['backup_upstream'] = bup_specs

    if multi_tier:
        data['layer_policy'] = multi_tier

    return data


def process_proxy_patch(proxy):
    upstream_el_code = proxy.get('upstream_el_code', '')
    upstreams = proxy.get('upstreams', None)
    if not upstreams and not upstream_el_code:
        raise Exception('No upstreams specified')
    if upstreams and upstream_el_code:
        raise Exception('upstreams and upstream_el_code are conflicting')

    backup_upstreams = proxy.get('backup_upstreams')
    connect_timeout = proxy.get('connect_timeout')
    read_timeout = proxy.get('read_timeout')
    send_timeout = proxy.get('send_timeout')
    retries = proxy.get('retries')
    retry_condition = proxy.get('retry_condition')
    balancer_algorithm = proxy.get('balancer_algorithm')
    balancer_vars = proxy.get('balancer_vars')
    multi_tier = proxy.get('multi_tier')

    if balancer_algorithm:
        if balancer_algorithm != 'roundrobin' and not balancer_vars:
            raise Exception('No balancer vars specified')

    up_specs = []
    for upstream in upstreams:
        up_id = upstream.get('upstream')
        global_up_id = upstream.get('global_upstream')
        weight = upstream.get('weight')

        # weight is zero means remove it from proxy_rule.
        if weight == 0:
            continue

        up_spec = {
            'cluster': up_id,
            'global_cluster': global_up_id,
            'weight': weight,
        }
        up_specs.append(up_spec)

    bup_specs = []
    if backup_upstreams:
        for upstream in backup_upstreams:
            up_id = upstream.get('upstream')
            weight = upstream.get('weight')

            # weight is zero means remove it from proxy_rule.
            if weight == 0:
                continue
            bup_spec = {
                'cluster': up_id,
                'weight': weight,
            }
            bup_specs.append(bup_spec)

    data = {'upstream': up_specs}

    if connect_timeout:
        data['connect_timeout'] = connect_timeout
    if send_timeout:
        data['send_timeout'] = send_timeout
    if read_timeout:
        data['read_timeout'] = read_timeout
    if retries:
        data['retries'] = retries
    if retry_condition:
        data['retry_condition'] = retry_condition
    if balancer_algorithm:
        data['balancer'] = {'algorithm': balancer_algorithm}

        if balancer_vars:
            data['balancer']['variables'] = balancer_vars

    if bup_specs:
        data['backup_upstream'] = bup_specs

    if multi_tier:
        data['layer_policy'] = multi_tier

    if upstream_el_code is not None:
        data['upstream_el_code'] = upstream_el_code

    return data

def is_valid_unit(unit):
    if unit == 's' or unit == 'min' or unit == 'hour' or unit == 'day':
        return True

    return False

def is_valid_cache_status(status):
    if status == 200 or status == 301 or status == 302:
        return True

    return False

def process_cache(cache):
    cache_key = cache.get('cache_key', None)
    default_ttls = cache.get('default_ttls', None)
    browser_ttl  = cache.get('browser_ttl', None)
    browser_ttl_unit = cache.get('browser_ttl_unit', 'min')
    enable_global = cache.get('enable_global', False)
    enforce_cache = cache.get('enforce_cache', False)
    cluster_hash = cache.get('cluster_hash', False)
    disable_convert_head = cache.get('disable_convert_head', True)

    if not cache_key:
        raise Exception('Missing value for the required field: cache_key')
    if not isinstance(cache_key, list):
        raise Exception('Bad cache_key field value type: ' + str(type(cache_key)))

    if default_ttls and not isinstance(default_ttls, list):
        raise Exception('Bad cache_key field value type: ' + str(type(default_ttls)))

    cache_key_specs = []
    for item in cache_key:
        if isinstance(item, str):
            cache_key_specs.append({'name': item})
        else:
            name = item.get('name')
            args = item.get('args', None)

            cache_key_specs.append({'name': name, 'args': args})

    data = {'cache_key': cache_key_specs}

    if enforce_cache:
        data['enforce_cache'] = enforce_cache
        if not default_ttls:
            raise Exception('Missing default_ttls for enforce_cache')

    if default_ttls:
        data['default_ttls'] = list()
        for item in default_ttls:
            ttl = item.get('ttl', 1)
            ttl_unit = item.get('ttl_unit', 'min')
            if not is_valid_unit(ttl_unit):
                raise Exception('Bad default_ttls unit: ' + str(ttl_unit))

            status = item.get('status', 200)
            if not is_valid_cache_status(status):
                raise Exception('Bad default_ttls status: ' + str(status))

            data['default_ttls'].append({'ttl': ttl, 'ttl_unit': ttl_unit, 'status': status})

    if browser_ttl:
        data['browser_ttl'] = browser_ttl
        data['browser_ttl_unit'] = browser_ttl_unit
        if not is_valid_unit(browser_ttl_unit):
            raise Exception('Bad browser_ttl unit: ' + str(browser_ttl_unit))

    data['cluster_hash'] = cluster_hash
    data['enable_global'] = enable_global
    data['disable_convert_head'] = disable_convert_head

    return data


def process_content(content):
    favicon = content.get('favicon', None)
    empty_gif = content.get('empty_gif', None)

    if favicon:
        return {'favicon': favicon}
    if empty_gif:
        return {'empty_gif': True}

    raise Exception(
        'Missing value for the required field: favicon or empty_gif')

def proxy_upstream_transform(upstream):
    if upstream.get('cluster') is not None:
        upstream_id = upstream.get('cluster')
        upstream['upstream'] = upstream_id
        del upstream['cluster']
    if upstream.get('k8s_cluster') is not None:
        upstream_id = upstream.get('k8s_cluster')
        upstream['k8s_upstream'] = upstream_id
        del upstream['k8s_cluster']
    if upstream.get('global_cluster') is not None:
        upstream_id = upstream.get('global_cluster')
        upstream['global_upstream'] = upstream_id
        del upstream['global_cluster']
    if upstream.get('global_k8s_cluster') is not None:
        upstream_id = upstream.get('global_k8s_cluster')
        upstream['global_k8s_upstream'] = upstream_id
        del upstream['global_k8s_cluster']

