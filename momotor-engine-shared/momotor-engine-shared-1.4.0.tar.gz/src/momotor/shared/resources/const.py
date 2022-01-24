import math

#: Match value for tags. ``STRONGEST`` indicates the best possible match: both task and worker require this tag
STRONGEST = -math.inf

#: Match value for tags. ``STRONG`` indicates a good match: the task requires this tag, for the worker it is optional
STRONG = -1.0

#: Match value for tags. ``NEUTRAL`` indicates there are no matching tags between task and worker.
NEUTRAL = 0.0

#: Match value for tags. ``WEAK`` indicates a slightly worst match: the worker requires the tag,
#: for the task it is optional
WEAK = 1.0

#: Match value for tags. ``WEAKEST`` indicates a worst possible match: for both worker and task the tag is optional
WEAKEST = math.inf
