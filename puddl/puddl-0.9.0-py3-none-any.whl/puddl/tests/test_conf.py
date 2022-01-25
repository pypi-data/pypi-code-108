def test_empty_env():
    import os
    from puddl.db.alchemy import DBConfig
    for k in DBConfig.__slots__:
        if k in os.environ:
            del os.environ[k]
    x = DBConfig('sunrise')
    assert x is not None
