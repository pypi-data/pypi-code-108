DEFAULT = {
    'opa': {
        'enabled': True,
        'endpoint': 'http://localhost:8181',
        'poll_period_seconds': 30
    },
    'blocking_config': {
        'enabled': False,
        'debug_log': False,
        'evaluate_body': True,
        'modsecurity': {
            'enabled': True
        },
        'skip_internal_request': True,
        'regionBlocking': {
            'enabled': True
        },
        'remote_config': {
            'enabled': True,
            'endpoint': 'localhost:5441',
            'poll_period_seconds': 30
        }
    }
}
