from typing import List
import re

from pydantic import BaseModel, StrictBool, StrictStr, validator


class CountryData(BaseModel):
    direct: StrictBool = False
    region: StrictStr
    id: StrictStr

    @validator("region", "id")
    def lower_str_values(cls, value):
        return value.lower()

    @validator("id")
    def regex_check_country_id(cls, v):
        if re.search("^[a-zA-Z]{2}$", v) is None:
            raise ValueError("must be a two-letter code")
        return v


class CountriesData(BaseModel):
    countries: List[CountryData]


class HttpCountriesData(BaseModel):
    body: CountriesData
