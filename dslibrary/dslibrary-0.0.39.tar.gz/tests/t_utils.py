import os

from dslibrary import ENV_DSLIBRARY_SPEC, ENV_DSLIBRARY_TARGET


def reset_env(msg: str):
    if os.environ.get(ENV_DSLIBRARY_SPEC):
        print(f"WARNING: {ENV_DSLIBRARY_SPEC} was not cleared by prior tests ({msg})")
        os.environ[ENV_DSLIBRARY_SPEC] = ""
    if os.environ.get(ENV_DSLIBRARY_TARGET):
        print(f"WARNING: {ENV_DSLIBRARY_TARGET} was not cleared by prior tests ({msg})")
        os.environ[ENV_DSLIBRARY_TARGET] = ""

