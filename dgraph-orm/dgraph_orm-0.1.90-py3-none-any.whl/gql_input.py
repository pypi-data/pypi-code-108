import typing as T
from enum import Enum
from datetime import datetime
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from dgraph_orm import GQLException

_NULL = "null-12345**792387fsijfoijf"


class GQLInput(BaseModel):
    def to_gql_str(self) -> str:
        str_lst: T.List[str] = []
        for field_name in self.dict(exclude_none=True, by_alias=True):
            val = getattr(self, field_name, None)
            if val is None:
                val = getattr(self, f"{field_name}_")
            if type(val) is set:
                val = list(val)
            if type(val) is list:
                if len(val) == 0:
                    raise GQLException(f"List in filter cannot be empty, {self=}")
                if isinstance(val[0], Enum):
                    v_str = ",".join(f"{v.value}" for v in val)
                    s = f"{field_name}: [{v_str}]"
                    str_lst.append(s)
                elif isinstance(val[0], GQLInput):
                    s = f'{field_name}: {{ {",".join([v.to_gql_str() for v in val])} }}'
                    str_lst.append(s)
                else:
                    s = f"{field_name}: {jsonable_encoder(val)}"
                    str_lst.append(s)
            else:
                if val == _NULL:
                    s = f"{field_name}: null"
                    str_lst.append(s)
                elif isinstance(val, GQLInput):
                    val = val.to_gql_str()
                    s = f"{field_name}: {{ {val} }}"
                    str_lst.append(s)
                elif isinstance(val, Enum):
                    s = f"{field_name}: {val.value}"
                    str_lst.append(s)
                elif type(val) is str:
                    s = f'{field_name}: "{val}"'
                    str_lst.append(s)
                elif type(val) is bool:
                    s = f'{field_name}: {"false" if val is False else "true"}'
                    str_lst.append(s)
                elif type(val) is datetime:
                    s = f'{field_name}: "{val.isoformat()}"'
                    str_lst.append(s)
                else:
                    s = f"{field_name}: {val}"
                    str_lst.append(s)
        final_s = ",".join(str_lst)
        final_s = final_s.replace("'", '"')
        return final_s

    class Config:
        #     use_enum_values = True
        allow_population_by_field_name = True
