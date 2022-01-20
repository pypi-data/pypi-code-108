import re

def _last_exception_message(exception_message):
    """Extract just the LAST message from the provided exception stack trace.
    """
    try:
        lines = str.splitlines(exception_message)
        message = []
        for line in reversed(lines):
            if re.search(r'line \d+, in', line):
                break
            message.insert(0, line)
        return "\n".join(message)
    except TypeError:
        return str(exception_message)


class ReturnValues:
    def __init__(self, return_values_raw_data):
        """Represents the Ansible ReturnValues that are produced when an Ansible Task 
        is executed against a targetted host.

        This data structure corresponds to the 'common' 
        https://docs.ansible.com/ansible/latest/reference_appendices/common_return_values.html#common

        Args:
            return_values_raw_data (Dict): The raw 'ReturnValues' data.
        """
        self._data = return_values_raw_data

    @property
    def data(self):
        return self._data

    @property
    def failed(self) -> bool:
        if 'failed' not in self.data:
            return False
        # Convert to a bool -- e.g. `failed` might be a string or an object! 
        return True if self.data['failed'] else False

    @property
    def changed(self) -> bool:
        if 'changed' not in self.data:
            return False
        # Convert to a bool -- e.g. `changed` might be a string or an object! 
        return True if self.data['changed'] else False

    def pretty_error(self):
        if 'results' in self.data:
            for return_values in self.data['results']:
                # TODO: How to use the factory here instead of directly building the devault ReturnValues? (circular dependency issue)
                # TODO: Should we accumulate child-failures before returning?
                child = ReturnValues(return_values)
                if child.failed:
                    return f"(loop_item='{child.data['item']}') {child.pretty_error()}"
        if 'error' in self.data:
            return str(self.data['error'])
        if 'exception' in self.data:
            return _last_exception_message(self.data['exception'])
        if 'msg' in self.data:
            return str(self.data['msg'])
        return "[ntsbuildtools] Unable to parse error."

    def pretty_diff(self):
        if not self.changed:
            return "[ntsbuildtools] No changes."
        if 'diff' in self.data:
            return str(self.data['diff'])
        if 'changed' in self.data:
            return f"[ntsbuildtools] Changed status: {str(self.data['changed'])}"
        return "[ntsbuildtools] Unable to parse diff."
