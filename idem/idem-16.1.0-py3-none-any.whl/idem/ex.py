from typing import Any
from typing import Dict
from typing import Iterable
from typing import Tuple

import aiofiles
import pop.hub
from dict_tools import data

__func_alias__ = {"ctx_": "ctx"}


async def run(
    hub,
    path: str,
    args: Tuple[Any],
    kwargs: Dict[str, Any],
    acct_file: str = None,
    acct_key: str = None,
    acct_blob: bytes = None,
    acct_profile: str = "default",
):
    args = [a for a in args]

    if not path.startswith("exec."):
        path = f"exec.{path}"

    func = hub[path]
    if isinstance(func, pop.hub.ReverseSub):
        params = func._resolve().signature.parameters
    else:
        params = func.signature.parameters

    if "ctx" in params:
        ctx = await hub.idem.ex.ctx(
            path,
            acct_file=acct_file,
            acct_key=acct_key,
            acct_profile=acct_profile,
            acct_blob=acct_blob,
        )
        args.insert(0, ctx)

    ret = func(*args, **kwargs)
    return await hub.pop.loop.unwrap(ret)


async def ctx_(
    hub,
    path: str,
    acct_profile: str = "default",
    acct_file: str = None,
    acct_key: str = None,
    acct_blob: bytes = None,
):
    """
    :param hub:
    :param path:
    :param acct_profile:
    :param acct_file:
    :param acct_key:
    :param acct_blob:
    :return:
    """
    ctx = data.NamespaceDict()

    parts = path.split(".")
    if parts[0] in ("exec", "states"):
        parts = parts[1:]

    sname = parts[0]

    acct_paths = (f"exec.{sname}.ACCT", f"states.{sname}.ACCT")

    acct_data = {}
    if acct_key:
        if acct_file:
            async with aiofiles.open(acct_file, "rb") as fh:
                acct_blob = await fh.read()
        if acct_blob:
            acct_data = await hub.acct.init.unlock_blob(acct_blob, acct_key=acct_key)

    subs = set()
    for name in acct_paths:
        if hasattr(hub, name):
            sub = getattr(hub, name)
            if isinstance(sub, Iterable) and sub:
                subs.update(set(sub))

    ctx.acct = await hub.acct.init.gather(
        subs,
        acct_profile,
        profiles=acct_data.get("profiles"),
    )

    return ctx


async def single(hub, path: str, *args, **kwargs):
    acct_file = hub.OPT.acct.acct_file
    acct_key = hub.OPT.acct.acct_key
    acct_profile = hub.OPT.acct.get("acct_profile", hub.acct.DEFAULT)

    ret = await hub.idem.ex.run(
        path,
        args=args,
        kwargs=kwargs,
        acct_file=acct_file,
        acct_key=acct_key,
        acct_profile=acct_profile,
    )
    return ret
