from sys import stderr, stdout

from papyru.logger_types import Message, Sequence, Trace


def make_stdout_sink():
    return StdoutSink()


class StdoutSink:
    def _choose_stream(item):
        IS_ERROR_MAP = {
            Message.SUCCESS: False,
            Message.INFO: False,
            Message.WARNING: False,
            Message.FAILURE: True,
            Message.CRITICAL: True,
        }

        if isinstance(item, Message):
            return (stderr
                    if IS_ERROR_MAP[item.severity]
                    else stdout)
        elif isinstance(item, Trace):
            return stderr
        elif isinstance(item, Sequence):
            if item.resolution == Message.SUCCESS:
                return stdout
            else:
                return stderr
        else:
            raise NotImplementedError()

    def commit(self, item):
        stream = StdoutSink._choose_stream(item)
        stream.write(_encode_text(item))
        stream.write('\n')
        stream.flush()


_DECORATION_MAP = {
    Message.SUCCESS: '✓ ',
    Message.INFO: '- ',
    Message.WARNING: '⚠ ',
    Message.FAILURE: '✗ ',
    Message.CRITICAL: '✗✗✗ ',
}


def format_summary(item):
    lines = _encode_text(item).splitlines()

    if len(lines) == 0:
        return '(empty)'
    elif len(lines) == 1:
        return lines[0]
    else:
        return '%s [...] %s' % (lines[0], lines[-1])


def _encode_text(item, indent=0):
    indent_str = '  ' * indent

    if isinstance(item, Message):
        return '%s%s %s' % (indent_str,
                            _DECORATION_MAP[item.severity],
                            item.message)
    elif isinstance(item, Sequence):
        sub = '\n'.join(map(lambda i: _encode_text(i, indent + 1),
                            item.items))

        return '%s%s%s\n%s' % (indent_str,
                               _DECORATION_MAP[item.resolution],
                               item.description,
                               sub)
    elif isinstance(item, Trace):
        sub = '\n'.join(map(lambda f: _encode_text(f, indent),
                            item.frames))

        return '%s\n%s' % (sub, _encode_text(item.summary, indent))
    elif isinstance(item, Trace.Summary):
        return '%s✗ %s: %s' % (indent_str,
                               item.description,
                               item.exception)
    elif isinstance(item, Trace.Frame):
        return '%s↪ %s, %d: %s' % (indent_str,
                                   item.filename,
                                   item.linenumber,
                                   item.line)
    else:
        raise NotImplementedError()
