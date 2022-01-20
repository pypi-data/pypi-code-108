from pydantic import BaseModel, constr, StrictInt, StrictStr

from .common.custom_types import DateISO8601Field

MAX_LEN_NON_HASHED = 256


BODY_KEYS = [
    "body",
    "precommit_body",
]

SERVICE_KEYS = [
    "record_key",
    "profile_key",
    "service_key1",
    "service_key2",
    "service_key3",
    "service_key4",
    "service_key5",
    "parent_key",
]

SEARCH_KEYS = [
    "key1",
    "key2",
    "key3",
    "key4",
    "key5",
    "key6",
    "key7",
    "key8",
    "key9",
    "key10",
    "key11",
    "key12",
    "key13",
    "key14",
    "key15",
    "key16",
    "key17",
    "key18",
    "key19",
    "key20",
]

RANGE_KEYS = [
    "range_key1",
    "range_key2",
    "range_key3",
    "range_key4",
    "range_key5",
    "range_key6",
    "range_key7",
    "range_key8",
    "range_key9",
    "range_key10",
]

INT_KEYS = RANGE_KEYS + ["version"]

STRING_KEYS = SEARCH_KEYS + SERVICE_KEYS + BODY_KEYS

SERVER_DATE_KEYS = [
    "created_at",
    "updated_at",
]

USER_DATE_KEYS = ["expires_at"]

USER_KEYS = BODY_KEYS + SERVICE_KEYS + SEARCH_KEYS + RANGE_KEYS + USER_DATE_KEYS

DATE_KEYS = SERVER_DATE_KEYS + USER_DATE_KEYS


SORT_KEYS = SEARCH_KEYS + RANGE_KEYS + DATE_KEYS


class Record(BaseModel):
    record_key: constr(strict=True, min_length=1)
    body: StrictStr = None
    precommit_body: StrictStr = None
    profile_key: StrictStr = None
    service_key1: StrictStr = None
    service_key2: StrictStr = None
    service_key3: StrictStr = None
    service_key4: StrictStr = None
    service_key5: StrictStr = None
    parent_key: StrictStr = None
    key1: StrictStr = None
    key2: StrictStr = None
    key3: StrictStr = None
    key4: StrictStr = None
    key5: StrictStr = None
    key6: StrictStr = None
    key7: StrictStr = None
    key8: StrictStr = None
    key9: StrictStr = None
    key10: StrictStr = None
    key11: StrictStr = None
    key12: StrictStr = None
    key13: StrictStr = None
    key14: StrictStr = None
    key15: StrictStr = None
    key16: StrictStr = None
    key17: StrictStr = None
    key18: StrictStr = None
    key19: StrictStr = None
    key20: StrictStr = None
    range_key1: StrictInt = None
    range_key2: StrictInt = None
    range_key3: StrictInt = None
    range_key4: StrictInt = None
    range_key5: StrictInt = None
    range_key6: StrictInt = None
    range_key7: StrictInt = None
    range_key8: StrictInt = None
    range_key9: StrictInt = None
    range_key10: StrictInt = None
    expires_at: DateISO8601Field = None


class RecordNonHashed(Record):
    key1: constr(strict=True, min_length=0, max_length=MAX_LEN_NON_HASHED) = None
    key2: constr(strict=True, min_length=0, max_length=MAX_LEN_NON_HASHED) = None
    key3: constr(strict=True, min_length=0, max_length=MAX_LEN_NON_HASHED) = None
    key4: constr(strict=True, min_length=0, max_length=MAX_LEN_NON_HASHED) = None
    key5: constr(strict=True, min_length=0, max_length=MAX_LEN_NON_HASHED) = None
    key6: constr(strict=True, min_length=0, max_length=MAX_LEN_NON_HASHED) = None
    key7: constr(strict=True, min_length=0, max_length=MAX_LEN_NON_HASHED) = None
    key8: constr(strict=True, min_length=0, max_length=MAX_LEN_NON_HASHED) = None
    key9: constr(strict=True, min_length=0, max_length=MAX_LEN_NON_HASHED) = None
    key10: constr(strict=True, min_length=0, max_length=MAX_LEN_NON_HASHED) = None
    key11: constr(strict=True, min_length=0, max_length=MAX_LEN_NON_HASHED) = None
    key12: constr(strict=True, min_length=0, max_length=MAX_LEN_NON_HASHED) = None
    key13: constr(strict=True, min_length=0, max_length=MAX_LEN_NON_HASHED) = None
    key14: constr(strict=True, min_length=0, max_length=MAX_LEN_NON_HASHED) = None
    key15: constr(strict=True, min_length=0, max_length=MAX_LEN_NON_HASHED) = None
    key16: constr(strict=True, min_length=0, max_length=MAX_LEN_NON_HASHED) = None
    key17: constr(strict=True, min_length=0, max_length=MAX_LEN_NON_HASHED) = None
    key18: constr(strict=True, min_length=0, max_length=MAX_LEN_NON_HASHED) = None
    key19: constr(strict=True, min_length=0, max_length=MAX_LEN_NON_HASHED) = None
    key20: constr(strict=True, min_length=0, max_length=MAX_LEN_NON_HASHED) = None
