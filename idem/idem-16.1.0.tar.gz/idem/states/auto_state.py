# States for exec modules that implement the "auto_state" contract
import uuid

import dict_tools.differ as differ
import pop.contract

__contracts__ = ["resource"]


async def present(hub, ctx, name: str, exec_mod_ref=None, **kwargs):
    """
    Create a resource if it doesn't exist, update it if it does exist
    """
    result = dict(comment="", old_state={}, new_state={}, name=name, result=True)
    before = await hub.pop.loop.wrap(hub.exec[exec_mod_ref].get, ctx, name, **kwargs)

    if not before:
        if ctx.test:
            result["comment"] = f"Would create {exec_mod_ref}:{name}"
            return result
        result["result"] = (
            await hub.pop.loop.wrap(hub.exec[exec_mod_ref].create, ctx, name, **kwargs)
        ).result
        if result["result"]:
            result["comment"] = f"Created '{exec_mod_ref}:{name}'"
        else:
            # There was an error in creation
            result["comment"] = f"Could not create '{exec_mod_ref}:{name}'"
            return result
    else:
        result["comment"] = f"'{exec_mod_ref}:{name}' already exists"
        if ctx.test:
            result["comment"] = f"Would update {exec_mod_ref}:{name}"
            return result

        # Update the resource
        result["result"] = (
            await hub.pop.loop.wrap(hub.exec[exec_mod_ref].update, ctx, name, **kwargs)
        ).result

    after = await hub.pop.loop.wrap(hub.exec[exec_mod_ref].get, ctx, name, **kwargs)
    result["changes"] = differ.deep_diff(before.ret, after.ret)
    if before.ret and result["changes"]:
        result["comment"] = f"Updated '{exec_mod_ref}:{name}'"

    result["old_state"] = before.ret
    result["new_state"] = after.ret
    return result


async def absent(hub, ctx, name: str, exec_mod_ref=None, **kwargs):
    """
    Remove a resource if it exists
    """
    result = dict(comment="", old_state={}, new_state={}, name=name, result=True)
    before = await hub.pop.loop.wrap(hub.exec[exec_mod_ref].get, ctx, name, **kwargs)

    if before:
        if ctx.test:
            result["comment"] = f"Would delete {exec_mod_ref}:{name}"
            return result

        await hub.pop.loop.wrap(hub.exec[exec_mod_ref].delete, ctx, name, **kwargs)
        result["comment"] = f"Deleted '{exec_mod_ref}:{name}'"
    else:
        result["comment"] = f"'{exec_mod_ref}:{name}' already absent"
        return result

    after = await hub.pop.loop.wrap(hub.exec[exec_mod_ref].get, ctx, name, **kwargs)

    result["old_state"] = before.ret
    result["new_state"] = after.ret
    return result


async def describe(hub, ctx):
    """
    Create "present" states for a resource based on an "auto_state" exec module plugin
    """
    exec_mod_ref = ctx.exec_mod_ref
    result = {}

    ret = await hub.pop.loop.unwrap(hub.exec[exec_mod_ref].list(ctx))

    if not (ret["result"] and ret["ret"]):
        return result

    for name, resource in ret["ret"].items():
        create_contract: pop.contract.Contracted = hub.exec[exec_mod_ref].create
        present_state = [{"name": name}]

        # Add the keyword arguments in the proper order
        for param, inspection in create_contract.signature.parameters.items():
            if param in ("hub", "ctx", "name", "kwargs"):
                # Skip over the ones we know about
                continue
            if param in resource:
                present_state.append({param: resource.pop(param)})
            else:
                present_state.append({param: inspection.default})

        result[f"{name}-{uuid.uuid4()}"] = {f"{exec_mod_ref}.present": present_state}

    return result
