from typing import Set
from itertools import product


BLOCK_DEF_CODE = '00'  # '00 used at start of block def

digits = [str(i) for i in range(10)]

valid_block_codes: Set[str] = set([''.join(combs) for combs in product(digits, repeat=2)])
header_body_codes: Set[str] = set(['L' + n for n in digits])
valid_header_codes: Set[str] = header_body_codes.union({BLOCK_DEF_CODE})
all_valid_codes = valid_block_codes.union(valid_header_codes)


def validate_header_code(code: str):
    if code not in valid_header_codes:
        raise ValueError(f"Error validating header code, got '{code}', "
                         f"expected one of: {sorted(valid_header_codes)}")


def validate_block_code(code: str):
    if code not in all_valid_codes:
        raise ValueError(f"Error validating header code, got '{code}', expected either a two digit "
                         f"numerical code or a header code from: {sorted(valid_header_codes)}")


def validate_header_block_def_code(code: str):
    if code != BLOCK_DEF_CODE:
        raise ValueError(f"Expected to be at the start of a block definition, this should start "
                         f"with code '{BLOCK_DEF_CODE}', but got code '{code}'.")


def validate_header_body_code(code: str):
    if code not in header_body_codes:
        raise ValueError(f"Error validating header body code, got '{code}', "
                         f"expected one of: {sorted(header_body_codes)}")


def validate_code(code: str, for_header: bool):
    if for_header:
        validate_header_code(code)
    else:
        validate_block_code(code)
