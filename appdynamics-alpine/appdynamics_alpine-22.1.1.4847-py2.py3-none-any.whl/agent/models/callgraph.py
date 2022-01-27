# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Models for call graphs and frames.

"""

from __future__ import unicode_literals

from appdynamics.lang import filter, range, values, zip
from appdynamics.agent.core.logs import setup_logger
from appdynamics.agent.models.frames import get_stack

logger = setup_logger('appdynamics.callgraph')


class Call(object):
    """Represents a call made by the program.

    Attributes
    ----------
    frame : FrameInfo
    num_samples : int
    time_taken_ms : int
    parent : Call or None
    children : iterable[Call]
    exit_calls : set[appdynamics.agent.models.exitcalls.ExitCall]

    """
    __slots__ = ('frame', 'time_taken_ms', 'parent', 'children', 'exit_calls', 'num_samples',
                 'descendent_exit_calls', 'correction')

    def __init__(self, frame):
        super(Call, self).__init__()
        self.frame = frame
        self.parent = None
        self.children = []
        # set of exit calls that are started directly in this call.
        self.exit_calls = set()
        # set of exit calls for which this call is a LCA of their start_call frame and end_frame call
        self.descendent_exit_calls = set()
        self.time_taken_ms = 0
        self.num_samples = 0
        self.correction = 0


class SampleData(object):
    """Represents the data associated with profiler samples for a BT.

    """
    __slots__ = ('samples', 'sample_time', 'sample_last_time', 'greenlet_ref', 'thread_id', 'frame_cache')

    def __init__(self, thread_id, greenlet_ref):
        super(SampleData, self).__init__()
        self.samples = []
        self.sample_time = 0
        self.sample_last_time = None
        self.thread_id = thread_id
        self.greenlet_ref = greenlet_ref
        self.frame_cache = {}

    @property
    def time_per_sample(self):
        if self.samples:
            return float(self.sample_time) / len(self.samples)
        else:
            return 0

    def _add_stack(self, stack, now, exit_calls):
        stack_with_exit = (stack, exit_calls)
        self.samples.append(stack_with_exit)
        self.sample_time += now - self.sample_last_time
        self.sample_last_time = now

    def take_full_stack(self, now, exit_calls):
        stack = get_stack(self.frame_cache, thread_id=self.thread_id, greenlet_ref=self.greenlet_ref)
        if stack:
            self._add_stack(stack, now, exit_calls)

    def take_outer_frames(self, now, exit_calls):
        stack = get_stack(self.frame_cache, from_root=False)
        if stack:
            self._add_stack(stack, now, exit_calls)


def make_call_graph(sample_data, total_time_taken_ms, include_internal_frames=False):
    """Create a call graph from a iterable of samples.

    Each sample is an iterable of FrameInfo instances in the
    order returned by FrameIterator (that is, starting from the
    leaf up to the root).

    Parameters
    ----------
    sample_data : appdynamics.agent.models.callgraph.SampleData
    total_time_taken_ms : int
        The precise time taken in the business transaction.

    Other Parameters
    ----------------
    include_internal_frames : bool, optional

    Returns
    -------
    root : Call
        The call graph

    """
    root = Call(None)  # Always have a common root node.

    samples = sample_data.samples
    calls_cache = {}
    assigned_exit_calls = set()

    def get_call(stack):
        try:
            return calls_cache[stack]
        except:
            call = Call(stack[0])
            call.parent = calls_cache[stack[1:]] if len(stack) > 1 else root
            call.parent.children.append(call)
            calls_cache[stack] = call
            return call

    for sample, exit_calls in samples:
        if not include_internal_frames:
            sample = tuple(filter(lambda f: not f.internal, sample))

        if not sample:  # Nothing to do
            continue

        depth = len(sample)
        calls = [get_call(sample[-i:]) for i in range(1, depth + 1)]

        if calls:
            for exit_call in exit_calls:
                assign_exit_call(exit_call, calls, assigned_exit_calls)

        for call in calls:
            call.num_samples += 1

    for call in values(calls_cache):
        call.time_taken_ms = int(call.num_samples * sample_data.time_per_sample)

    calls_with_exit_calls = collect_calls_with_exit_calls(assigned_exit_calls)
    fix_exit_call_timings(calls_with_exit_calls)
    root.time_taken_ms = max(total_time_taken_ms, sum(node.time_taken_ms for node in root.children))
    return root


def fix_exit_call_timings(calls):
    """Fix frames where the exit call times exceed the sampled time.

    Since our call graph timings are gathered from a sampler, it's possible
    that we under-sample a frame. This is normally hard to see and relatively
    benign. But in the case of a frame with an exit call, the exit call
    timing is "exact", while the frame time is sampled, and it's possible for
    the user visible exit call timing to exceed the sampled frame time.

    This is confusing for the user and wrong. So when we have better info,
    and we can detect that we under-sampled, make the frame at least as long
    as the sum of the times spent in its exit calls.

    Note:  As exit calls may have different start exit call frame and end exit call frame
    the timing adjustment is done for least common ancestor although the exit call is assigned
    to the start frame.

    Parameters
    ----------
    calls : iterable[Call]

    """
    calls_with_correction = set([])
    for call in calls:
        for exit_call in call.descendent_exit_calls:
            if exit_call.start_caller == exit_call.end_caller:
                exit_call_delta = exit_call.time_taken_ms - exit_call.start_caller.time_taken_ms
            else:
                exit_call_delta = exit_call.time_taken_ms - (exit_call.start_caller.time_taken_ms +
                                                             exit_call.end_caller.time_taken_ms)
            call.correction += max(exit_call_delta, 0)

        if call.correction > 0:
            logger.debug('A correction of %dms is being applied to under sampled call: %s', call.correction,
                         ('(%s, %s, %s)' % (call.frame.filename, call.frame.class_name, call.frame.name) if call.frame
                          else '{request}'))
            calls_with_correction.add(call)

    for call in calls_with_correction:
        call_delta = call.correction
        while call:
            call.time_taken_ms += call_delta
            call = call.parent


def assign_exit_call(exit_call, callers, assigned_exit_calls):
    """
    Assigns exit_call to the correct caller. In the process
    assign start frame and end frame that started and ended exit call.

    """

    if not exit_call.was_assigned:
        for caller in callers:
            if caller.frame == exit_call.start_frame_info:
                exit_call.start_caller = caller
                caller.exit_calls.add(exit_call)  # The call the exit call started.
            if caller.frame == exit_call.end_frame_info:
                exit_call.end_caller = caller

    if exit_call.start_caller and exit_call.end_caller:
        assigned_exit_calls.add(exit_call)
        exit_call.was_assigned = True


def collect_calls_with_exit_calls(assigned_exit_calls):
    """
    parses all exit calls and collects call in which
    started and ended in its context (lca of calls that started
    and ended the exit call.)

    Args:
        assigned_exit_calls: exit calls for which start frame and end frame are figured.

    Returns:

    """
    calls_with_exit_calls = set()
    for exit_call in assigned_exit_calls:
        start_caller, end_caller = exit_call.start_caller, exit_call.end_caller
        lca_call, exit_call.start_caller, exit_call.end_caller = least_common_ancestor(start_caller, end_caller)
        lca_call.descendent_exit_calls.add(exit_call)
        calls_with_exit_calls.add(lca_call)
    return calls_with_exit_calls


def least_common_ancestor(start_caller, end_caller):
    """
    Returns nearest ancestor of start_caller and end_caller
    along with the start and end sub trees

    Args:
        start_caller: Caller which started the exit call.
        end_caller: Caller which ended the exit call.

    Returns: The common ancestor of start_caller and end_caller.

    """
    start_tree = start_caller
    end_tree = end_caller

    if start_caller == end_caller:
        return start_caller, start_tree, end_tree

    start_ancestors = get_ancestors(start_caller)
    end_ancestors = get_ancestors(end_caller)
    common_ancestor = start_ancestors[0]

    for caller1, caller2 in zip(start_ancestors, end_ancestors):
        if caller1 == caller2:
            common_ancestor = caller1
        else:
            start_tree = caller1
            end_tree = caller2
            break
    return common_ancestor, start_tree, end_tree


def get_ancestors(caller):
    """
    Returns all ancestors of the caller node.

    Args:
        caller: Call object

    Returns: list of ancestors in decreasing order ([root, root.child, root,child.child ...  caller])

    """
    ancestors = []
    while caller:
        ancestors.insert(0, caller)
        caller = caller.parent
    return ancestors
