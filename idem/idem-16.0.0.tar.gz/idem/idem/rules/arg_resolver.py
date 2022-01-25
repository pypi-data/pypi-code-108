import re


def check(hub, name, ctx, condition, reqret, chunk):
    """
    Parse argument binding reference and update the chunk argument with the requisite value.
    For example:
    - arg_bind:
        - cloud.referenced_resource_def:
            referenced_resource:
                referenced_resource_property: this_resource_property
    """
    if condition != "arg_bind":
        return {"errors": [f'"{condition}" is not a supported arg resolver.']}

    if not isinstance(reqret.get("args", {}), dict):
        return {"errors": [f'"{condition}" is not in a supported format.']}

    for req_key_chain, chunk_key_chain in reqret.get("args", {}).items():
        # TODO: Should we use "changes" to look-up args or just "new_state"?
        if "new_state" not in reqret["ret"]:
            return {
                "errors": [
                    f'"{name}" state does not have "new_state" in the state returns.'
                ]
            }
        req_value = reqret["ret"]["new_state"]
        for req_key in req_key_chain.split("."):
            req_key, indexes = parse_index(req_key)

            if req_key not in req_value:
                return {
                    "errors": [
                        f'"{req_key_chain}" is not found as part of "{name}" state "new_state".'
                    ]
                }

            req_value = req_value[req_key]
            if indexes is not None:
                for index in indexes:
                    if not isinstance(req_value, list) or len(req_value) < index + 1:
                        return {
                            "errors": [
                                f'"{req_key_chain}" cannot be parsed for "{name}" state, because "{req_key}" '
                                f'is not a list or it does not include element with index "{index}".'
                            ]
                        }
                    req_value = req_value[index]

        try:
            chunk = set_chunk_arg_value(
                chunk, chunk_key_chain.split("."), req_value, None
            )
        except AttributeError as ex:
            return {"errors": [f"{ex}"]}

    return {}


def parse_index(key_to_parse):
    """
    Parse indexes of key. For example, test[0][1] will return "test" as parsed key and [0,1] as parsed indexes.
    """
    indexes = re.findall(r"\[\d+\]", key_to_parse)
    if indexes:
        index_digits = []
        for index in indexes:
            index_digit = re.search(r"\d+", index).group(0)
            index_digits.append(int(index_digit))

        return key_to_parse[0 : key_to_parse.index("[")], index_digits

    return key_to_parse, None


def set_chunk_arg_value(chunk, arg_keys, arg_value, chunk_indexes):
    """
    Recursively iterate over arg_keys and update the chunk desired key with the referenced value
    """
    arg_key = arg_keys.pop(0)
    arg_key, next_chunk_indexes = parse_index(arg_key)
    if len(arg_keys) == 0:
        indexed_chunk = chunk
        if chunk_indexes:
            for index in chunk_indexes:
                if (
                    not isinstance(indexed_chunk, list)
                    or len(indexed_chunk) < index + 1
                ):
                    raise AttributeError(
                        f'Cannot set argument value for index "{index}", because "{arg_key}" '
                        f'is not a list or it does not include element with index "{index}".'
                    )
                indexed_chunk = chunk[index]
        indexed_chunk[arg_key] = arg_value
        return chunk
    if arg_key not in chunk:
        chunk[arg_key] = {}

    chunk[arg_key] = set_chunk_arg_value(
        chunk[arg_key], arg_keys, arg_value, next_chunk_indexes
    )
    return chunk
