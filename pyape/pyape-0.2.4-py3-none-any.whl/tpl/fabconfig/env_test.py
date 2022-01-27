env_test = {
    'deploy_dir': 'pyape_test',
    '_env': {
        'FLASK_ENV': 'development',
    },
    'uwsgi_ini': {
        'socket': '127.0.0.1:5001'
    },
    'config_json': {
        'FLASK': {
            'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://test:123456@127.0.0.1/pyape_test',
            # SQLALCHEMY 使用 bind_key_db
            'SQLALCHEMY_BINDS': {
                'test1000': 'mysql+pymysql://test:123456@127.0.0.1/test1000',
                'test2000': 'mysql+pymysql://test:123456@127.0.0.1/test2000',
            },
            # REDIS 使用 bind_key_redis，REDIS_URI 的 bind_key_redis 为 None
            # 对 REDIS 的使用遵循了最大利用率+最大灵活性原则，可能出现：
            # 1. 单个 Regional 使用单个 REDIS 实例（少量情况）
            # 2. 多个 Regional 使用同一个 REDIS 实例，分 DB 存储（多数情况）
            # 3. 多个 Regional 使用同一个 REDIS 实例和同一个 DB（测试情况）
            # 4. 单个 Regional 使用多个 REDIS 实例（暂未如此部署）
            'REDIS_URI': 'redis://localhost:6379/0',
            'REDIS_BINDS': {
                'db0': 'redis://localhost:6379/0',
                'db1': 'redis://localhost:6379/1',
            }
        },
        'ADMIN': {
            'password': 'WYi3jfd1bl3L',
        },
        'PATH': {
            'STATIC_URL_PATH': '/mjptest',
            'modules': {
                'cf': '/mjptest/cf'
            }
        },
        'REGIONALS': [
            {
                'name': '微信测试服1000',
                'r': 1000,  # 测试服使用
                'index': 1,
                'bind_key_db': 'test1000',
                'bind_key_redis': 'db0',
            },
        ],
    },
}