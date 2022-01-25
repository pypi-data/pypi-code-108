def is_pending(hub, ret):
    # Default implementation of pending plugin
    # Pending plugin returns 'True' when the state is still 'pending'
    # and reconciliation is required.
    # This implementation require reconciliation until 'result' is 'True'
    # and there are no 'changes'
    return not ret["result"] is True or bool(ret["changes"])
