from enum import Enum
from typing import Union, List

from pydantic import BaseModel, Extra, validator


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


SortOrderOption = Union[SortOrder, None]


class SortOption(BaseModel):
    key1: SortOrderOption
    key2: SortOrderOption
    key3: SortOrderOption
    key4: SortOrderOption
    key5: SortOrderOption
    key6: SortOrderOption
    key7: SortOrderOption
    key8: SortOrderOption
    key9: SortOrderOption
    key10: SortOrderOption
    key11: SortOrderOption
    key12: SortOrderOption
    key13: SortOrderOption
    key14: SortOrderOption
    key15: SortOrderOption
    key16: SortOrderOption
    key17: SortOrderOption
    key18: SortOrderOption
    key19: SortOrderOption
    key20: SortOrderOption
    range_key1: SortOrderOption
    range_key2: SortOrderOption
    range_key3: SortOrderOption
    range_key4: SortOrderOption
    range_key5: SortOrderOption
    range_key6: SortOrderOption
    range_key7: SortOrderOption
    range_key8: SortOrderOption
    range_key9: SortOrderOption
    range_key10: SortOrderOption
    created_at: SortOrderOption
    updated_at: SortOrderOption
    expires_at: SortOrderOption

    class Config:
        extra = Extra.forbid
        use_enum_values = True

    @validator("*", pre=True)
    def forbid_multiple_options(cls, value, values, config, field):
        if value is None:
            raise ValueError("value cannot be None")

        used_key = next(filter(lambda k: values.get(k, None), values.keys()), None)
        if used_key:
            raise ValueError(f"sort option may have only one field selected, already got '{used_key}'")
        return value


class SortFilter(BaseModel):
    sort: Union[List[SortOption], None] = []

    @validator("sort", each_item=True)
    def sort_options_to_dict(cls, value, values, config, field):
        dict_value = value.dict(exclude_unset=True)
        if len(dict_value) == 0:
            raise ValueError("cannot be empty dict")
        return dict_value

    @validator("sort")
    def sort_check_duplicate_keys(cls, value, values, config, field):
        if value is None:
            return value
        duplicate_keys = []
        sort_keys = set()
        for sort_option in value:
            sort_key = next(iter(sort_option.keys()), None)
            if sort_key in sort_keys and sort_key not in duplicate_keys:
                duplicate_keys.append(sort_key)
            sort_keys.add(sort_key)
        if len(duplicate_keys) > 0:
            raise ValueError(f"got duplicate sort options for keys: {duplicate_keys}")

        return value
