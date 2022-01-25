import asyncio
import fnmatch
import warnings
from typing import Any
from typing import Dict

import jmespath
import pop.contract
import pop.hub
import pop.loader
import tqdm


async def run(
    hub,
    desc_glob: str = "*",
    acct_file: str = None,
    acct_key: str = None,
    acct_profile: str = "default",
    progress: bool = False,
    search_path: str = None,
    hard_fail: bool = False,
) -> Dict[str, Dict[str, Any]]:
    """
    :param hub:
    :param desc_glob:
    :param acct_file:
    :param acct_key:
    :param acct_profile:
    :param progress:
    :return:
    """
    ctx = await hub.idem.ex.ctx(
        path=desc_glob,
        acct_file=acct_file,
        acct_key=acct_key,
        acct_profile=acct_profile,
    )
    result = {}
    coros = [_ async for _ in hub.idem.describe.recurse(ctx, hub.states, desc_glob)]
    async for coro in hub.idem.describe.recurse(ctx, hub.exec, desc_glob):
        coros.append(coro)

    progress_bar = None
    if progress:
        progress_bar = tqdm.tqdm(total=len(coros))

    for ret in asyncio.as_completed(coros):
        if progress:
            progress_bar.update(1)
        try:
            result.update(await ret)
        except Exception as e:
            hub.log.error(f"Error during describe: {e.__class__.__name__}: {e}")
            if hard_fail:
                raise
    if progress:
        progress_bar.close()
    if search_path:
        prepped = hub.output.jmespath.prepare(result)
        searched = jmespath.search(search_path, prepped)
        if hub.OPT.rend.get("output") == "jmespath":
            # Don't post-process the result, it's already in jmespath format
            return searched
        else:
            return hub.output.jmespath.revert(searched)
    return result


async def recurse(
    hub, ctx, mod: pop.loader.LoadedMod or pop.hub.Sub, glob: str, ref: str = ""
):
    if hasattr(mod, "_subs"):
        for sub in mod._subs:
            if ref:
                r = ".".join([ref, sub])
            else:
                r = sub
            async for c in hub.idem.describe.recurse(ctx, mod[sub], glob, r):
                yield c
    if hasattr(mod, "_loaded"):
        for loaded in mod._loaded:
            if ref:
                r = ".".join([ref, loaded])
            else:
                r = loaded
            async for c in hub.idem.describe.recurse(ctx, mod[loaded], glob, r):
                yield c

    # Only describe functions that implement the "describe" contract
    if hasattr(mod, "__contracts__"):
        if "auto_state" in mod.__contracts__:
            # Handle auto state describe functions
            ctx.exec_mod_ref = ref
            coro = hub.states.auto_state.describe(ctx)
            yield hub.pop.Loop.create_task(coro)
        elif "resource" in mod.__contracts__:
            if fnmatch.fnmatch(ref, glob):
                if isinstance(mod.describe, pop.contract.ContractedAsync):
                    coro = mod.describe(ctx)
                else:

                    async def _async_desc():
                        return mod.describe(ctx)

                    coro = _async_desc()
                yield hub.pop.Loop.create_task(coro)

    if hasattr(mod, "_funcs") and "describe" in mod._funcs:
        # TODO Raise an error here instead of a warning
        warnings.warn(
            f"Running 'describe' without implementing the `resource` contract for {mod} is deprecated.\n"
            "Implement the resource contract for this mod for it to continue functioning in future releases.\n"
            "__contracts__ = ['resource']",
            DeprecationWarning,
        )
        if fnmatch.fnmatch(ref, glob):
            if isinstance(mod.describe, pop.contract.ContractedAsync):
                coro = mod.describe(ctx)
            else:

                async def _async_desc():
                    return mod.describe(ctx)

                coro = _async_desc()
            yield hub.pop.Loop.create_task(coro)
