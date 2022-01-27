env_prod = {
    'deploy_dir': 'pyape_prod',
    '_env': {
        'FLASK_ENV': 'production',
    },
    'uwsgi_ini': {
        'processes': 4,
    },
    'config_json': {
        'FLASK': {
            'SECRET_KEY': 'JDvzd1yfBxuD6jylc9AwZqGXBdE17Udhb3PmNFBs3mQ=',
        },
    },
}
