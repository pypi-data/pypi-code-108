import os


def req(key):
    if key not in os.environ:
        raise Exception(f'Missing required environment property {key}!')

    return os.environ[key]


def opt(key, default):
    if key not in os.environ:
        print(f'Missing environment property <{key}> --- Using default value "{default}"')
    return os.getenv(key, default)
