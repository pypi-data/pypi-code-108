
def is_action_blocked(data):
    return data['result'] and isinstance(data['result'], dict) and data['result'].get('action', '') == 'block'
