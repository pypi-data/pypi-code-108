# The order of the sequence that needs to be implemented:
# Start with a single sls file, just like you started with salt
# Stub out the routines around gathering the initial sls file
# Just use a yaml renderer and get it to where we can manage some basic
# includes to drive to highdata
# Then we can start to fill out renderers while at the same time
# deepening the compiler
import pathlib
import sys

from idem.exec.init import ExecReturn


def __init__(hub):
    hub.pop.sub.load_subdirs(hub.idem, recurse=True)
    hub.idem.RUNS = {}
    hub.pop.sub.add(dyne_name="log")
    hub.pop.sub.add(dyne_name="acct")
    hub.pop.sub.add(dyne_name="rend")
    hub.pop.sub.add(dyne_name="output")
    hub.pop.sub.add(dyne_name="evbus")
    hub.pop.sub.add(dyne_name="reconcile")
    hub.pop.sub.load_subdirs(hub.reconcile, recurse=True)
    hub.pop.sub.add(dyne_name="tool")
    hub.pop.sub.load_subdirs(hub.tool, recurse=True)
    hub.pop.sub.add(dyne_name="exec")
    hub.pop.sub.load_subdirs(hub.exec, recurse=True)
    hub.pop.sub.add(dyne_name="states")
    hub.pop.sub.load_subdirs(hub.states, recurse=True)
    hub.idem.req.init.req_map()


def cli(hub):
    """
    Execute a single idem run from the cli
    """
    hub.pop.config.load(["idem", "acct", "rend", "evbus"], cli="idem")
    hub.pop.loop.create()
    retcode = hub.pop.Loop.run_until_complete(hub.idem.init.cli_apply())
    sys.exit(retcode)


# If the gathering and cli def funcs grow they should be moved to a plugin
def get_refs(hub):
    """
    Determine where the sls sources are
    """
    sls_sources = []
    slses = []
    if hub.OPT.idem.tree:
        tree = f"file://{hub.OPT.idem.tree}"
        sls_sources.append(tree)
    for sls in hub.OPT.idem.sls:
        path = pathlib.Path(sls)
        if path.is_file():
            ref = str(path.stem if path.suffix == ".sls" else path.name)
            slses.append(ref)
            implied = f"file://{path.parent}"
            if implied not in sls_sources:
                sls_sources.append(implied)
        else:
            slses.append(sls)

    sls_sources.extend(hub.OPT.idem.sls_sources)

    return {"sls_sources": sls_sources, "sls": slses}


async def cli_apply(hub):
    """
    Run the CLI routine in a loop
    """
    if hub.SUBPARSER in ("encrypt", "decrypt"):
        # Break early for acct commands
        return await hub.acct.init.cli_apply()

    # Initialize the broker queue for evbus
    await hub.evbus.broker.init()

    # Specify the serializing plugin for evbus
    hub.serialize.PLUGIN = hub.OPT.evbus.serialize_plugin

    # Collect ingress profiles from acct
    ingress_profiles = await hub.evbus.acct.profiles(
        acct_file=hub.OPT.acct.acct_file,
        acct_key=hub.OPT.acct.acct_key,
    )

    # Start the listener in it's own task
    listener = hub.pop.Loop.create_task(hub.evbus.init.start(ingress_profiles))
    # Let the task switcher have a free cycle to start the listener
    await hub.pop.loop.sleep(0)

    if hub.SUBPARSER == "state":
        retcode = await hub.idem.init.cli_sls()
    elif hub.SUBPARSER == "exec":
        retcode = await hub.idem.init.cli_exec()
    elif hub.SUBPARSER == "describe":
        retcode = await hub.idem.init.cli_desc()
    else:
        print(hub.args.parser.help())
        retcode = 2

    await hub.evbus.init.stop()
    await listener

    return retcode


async def cli_sls(hub) -> int:
    """
    Execute the cli routine to run states
    """
    src = hub.idem.init.get_refs()
    name = hub.OPT.idem.run_name
    await hub.idem.state.apply(
        name=name,
        sls_sources=src["sls_sources"],
        render=hub.OPT.idem.render,
        runtime=hub.OPT.idem.runtime,
        subs=["states"],
        cache_dir=hub.OPT.idem.cache_dir,
        sls=src["sls"],
        test=hub.OPT.idem.test,
        acct_file=hub.OPT.acct.acct_file,
        acct_key=hub.OPT.acct.acct_key,
        acct_profile=hub.OPT.idem.acct_profile,
    )

    errors = hub.idem.RUNS[name]["errors"]
    if errors:
        display = hub.output.nested.display(errors)
        print(display)
        # Return a non-zero error code
        return len(errors)

    # Reconciliation loop
    await hub.reconcile.init.run(
        plugin=hub.OPT.idem.reconciler,
        pending_plugin=hub.OPT.idem.pending,
        name=name,
        sls_sources=src["sls_sources"],
        render=hub.OPT.idem.render,
        runtime=hub.OPT.idem.runtime,
        cache_dir=hub.OPT.idem.cache_dir,
        sls=src["sls"],
        test=hub.OPT.idem.test,
        acct_file=hub.OPT.acct.acct_file,
        acct_key=hub.OPT.acct.acct_key,
        acct_profile=hub.OPT.idem.acct_profile,
    )

    running = hub.idem.RUNS[name]["running"]
    output = hub.OPT.rend.output or "state"
    display = hub.output[output].display(running)
    print(display)
    return 0


async def cli_exec(hub) -> int:
    exec_path = hub.OPT.idem.exec_func
    exec_args = hub.OPT.idem.exec_args
    if not exec_path.startswith("exec"):
        exec_path = f"exec.{exec_path}"
    args = []
    kwargs = {}
    for arg in exec_args:
        if isinstance(arg, dict):
            kwargs.update(arg)
        else:
            args.append(arg)
    ret = await hub.idem.ex.run(
        exec_path,
        args,
        kwargs,
        hub.OPT.acct.acct_file,
        hub.OPT.acct.acct_key,
        hub.OPT.idem.acct_profile,
    )

    output = hub.OPT.rend.output or "exec"
    display = hub.output[output].display(ret)
    print(display)

    if isinstance(ret, ExecReturn):
        return int(not ret.result)

    return 1


async def cli_desc(hub) -> int:
    state_path = hub.OPT.idem.desc_glob
    ret = await hub.idem.describe.run(
        state_path,
        hub.OPT.acct.acct_file,
        hub.OPT.acct.acct_key,
        hub.OPT.idem.acct_profile,
        progress=hub.OPT.idem.progress,
        hard_fail=hub.OPT.idem.hard_fail,
        search_path=hub.OPT.idem.filter,
    )

    output = hub.OPT.rend.output or "yaml"
    display = hub.output[output].display(ret)
    print(display)
    return 0
