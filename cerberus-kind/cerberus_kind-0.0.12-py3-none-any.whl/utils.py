import re

def parse_error(errors, with_path=False):
    ignore_path_pattern=[
        re.compile('.*oneof.*')
    ]

    def get_message(errors, stack=[]):
        message = []
        path = '.'.join(filter(None, stack))
        if not [True for _ in ignore_path_pattern if _.match(path)]:
            if isinstance(errors, str):
                if with_path:
                    if path:
                        message.append(f"{path}: {errors}")
                    else:
                        message.append(f"{errors}")
                else:
                    message.append(f"{errors}")
            elif isinstance(errors, dict):
                for k, v in errors.items():
                    stack.append(str(k))
                    message += get_message(v, stack)
                    stack.pop(-1)
            elif isinstance(errors, list):
                for item in errors:
                    message += get_message(item, stack)
        return message

    if '__root__' in errors:
        return ', '.join(get_message(errors['__root__']))
    else:
        return ', '.join(get_message(errors))

def kind_schema(kind, allowed=None):
    return {
        'type': 'string',
        'allowed': allowed if allowed else [kind.title()],
        'default': kind.title(),
        'order': -1
    }
    