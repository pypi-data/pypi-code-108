import asyncio
import copy
from typing import List

import dict_tools.differ as differ

# Reconciliation loop stops after MAX_RERUNS_WO_CHANGE reruns without change.
# This is to make sure we do not retry forever on failures that cannot be fixed by
# reconciliation.
MAX_RERUNS_WO_CHANGE = 3
# Sleep time in seconds between re-runs
DEFAULT_RECONCILE_WAIT = 3
# Dictionary for the default static sleep time
DEFAULT_STATIC_RECONCILE_WAIT = {"static": {"wait_in_seconds": DEFAULT_RECONCILE_WAIT}}
# Dictionary keeping state's reconcile wait time in seconds
_state_to_sleep_map = {}


async def loop(
    hub,
    pending_plugin,
    name,
    sls_sources,
    render,
    runtime,
    cache_dir,
    sls,
    test,
    acct_file: str = None,
    acct_key: str = None,
    acct_profile: str = None,
    acct_blob: str = None,
    subs: List[str] = None,
):
    """
    This loop attempts to apply states.
    This function returns once all the states are successful or after MAX_RERUNS_WO_CHANGE, whichever occur first.
    The sleep time between each attempt will be determined by a "wait" plugin and might change between each iterations.
    Reconciliation is required if the state is "pending" as defined by the pending plugin.
    The default pending plugin defines pending state if result  is not 'True' or there are 'changes'.

    @param hub:
    @param pending_plugin:
    @param name:
    @param sls_sources:
    @param render:
    @param runtime:
    @param cache_dir:
    @param sls:
    @param test:
    @param acct_file:
    @param acct_key:
    @param acct_profile:
    @param acct_blob
    @param subs
    :return: dictionary { "re_runs_count": <number of re-runs that occurred>,
                "require_re_run": <True/False whether the last run require more reconciliation> }
    """
    last_run = hub.idem.RUNS[name]["running"]
    if hub.reconcile.basic.has_passed(pending_plugin, last_run):
        return {"re_runs_count": 0, "require_re_run": False}

    # Populate wait time algorithm and values for the different states
    # in this run. State has to define __reconciliation_wait__
    # with values such as:
    # { "exponential": {"wait_in_seconds": 2, "multiplier": 10} }
    # { "static": {"wait_in_seconds": 3} }
    # { "random": {"min_value": 1, "max_value": 10} }
    hub.reconcile.basic.populate_wait_times(last_run)

    tag_to_old_state_map = _populate_old_states(last_run)

    count = 0
    count_wo_change = 0
    while count_wo_change < MAX_RERUNS_WO_CHANGE:
        sleep_time_sec = get_max_wait_time(hub, pending_plugin, last_run, count)
        hub.log.debug(f"Sleeping {sleep_time_sec} seconds for {name}")
        await asyncio.sleep(sleep_time_sec)

        count = count + 1
        hub.log.debug(f"Retry {count} for {name}")
        await hub.idem.state.apply(
            name=name,
            sls_sources=sls_sources,
            render=render,
            runtime=runtime,
            subs=subs,
            cache_dir=cache_dir,
            sls=sls,
            test=test,
            acct_file=acct_file,
            acct_key=acct_key,
            acct_profile=acct_profile,
            acct_blob=acct_blob,
        )

        current_run = hub.idem.RUNS[name]["running"]
        if hub.reconcile.basic.has_passed(pending_plugin, current_run):
            hub.reconcile.basic.update_changes(current_run, tag_to_old_state_map)
            return {"re_runs_count": count, "require_re_run": False}

        if _is_same_result(last_run, current_run):
            count_wo_change = count_wo_change + 1
        else:
            # reset the count w/o changes upon a change
            count_wo_change = 0

        last_run = current_run

    hub.log.debug(
        f"Reconciliation loop returns after {count} runs total, and {count_wo_change} runs without any change."
    )

    hub.reconcile.basic.update_changes(last_run, tag_to_old_state_map)
    return {
        "re_runs_count": count,
        "require_re_run": True,
    }


def has_passed(hub, pending_plugin, runs):
    # invoke pending plugin
    for tag in runs:
        if hub.reconcile.pending[pending_plugin].is_pending(runs[tag]):
            return False
    return True


def populate_wait_times(hub, runs):
    # Populate sleep times per state
    for tag in runs:
        state = _tag_2_state(tag)
        if state not in _state_to_sleep_map.keys():
            _state_to_sleep_map[state] = getattr(
                hub.states[state], "__reconcile_wait__", DEFAULT_STATIC_RECONCILE_WAIT
            )


def get_max_wait_time(hub, pending_plugin, runs, run_count):
    max_sleep_time = DEFAULT_RECONCILE_WAIT
    for tag in runs:
        if hub.reconcile.pending[pending_plugin].is_pending(runs[tag]):
            state_wait = _state_to_sleep_map.get(
                _tag_2_state(tag), DEFAULT_STATIC_RECONCILE_WAIT
            )
            wait_alg = list(state_wait.keys())[0]
            wait_val = state_wait[wait_alg]
            sleep_time = hub.reconcile.wait[wait_alg].get(
                **wait_val, run_count=run_count
            )
            if sleep_time > max_sleep_time:
                max_sleep_time = sleep_time

    return max_sleep_time


def update_changes(hub, last_run, tag_to_old_state_map):
    # Update last_run with 'old_state' from the original run
    # and recalculate last_run 'changes' to reflect
    # all the changes that occurred during reconciliation:
    # the delta between original run's old_state and last_run 'new_state'
    for tag in last_run:
        orig_old_state = tag_to_old_state_map.get(tag, None)
        last_old_state = last_run[tag].get("old_state", None)
        if orig_old_state != last_old_state:
            hub.log.debug(
                f"Replacing 'old_state' for '{_tag_2_state(tag)}': {last_old_state} with {orig_old_state}"
            )

        last_run[tag]["old_state"] = orig_old_state
        last_run[tag]["changes"] = differ.deep_diff(
            orig_old_state if orig_old_state else dict(),
            last_run[tag].get("new_state", dict()),
        )


def _is_same_result(run1, run2):
    for tag in run1:
        if (
            run2[tag]
            and run1[tag]["result"] == run2[tag]["result"]
            and run1[tag]["changes"] == run2[tag]["changes"]
        ):
            continue
        else:
            result1 = run1[tag]["result"]
            result2 = run2[tag]["result"]
            print(
                f"Changes between runs: run1 result: {result1} - run2 result: {result2}"
            )
            changes1 = run1[tag]["changes"]
            changes2 = run2[tag]["changes"]
            print(
                f"Changes between runs: run1 changes: {changes1} - run2 changes: {changes2}"
            )
            return False
    return True


def _populate_old_states(run):
    # Keep old_state per tag from the original run
    tag_to_old_state = {}
    for tag in run:
        if run[tag].get("old_state", None):
            tag_to_old_state[tag] = copy.deepcopy(run[tag]["old_state"])
    return tag_to_old_state


def _tag_2_state(tag):
    # Get state from the tag
    return tag[0 : tag.find("_|")]
