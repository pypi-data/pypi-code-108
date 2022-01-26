from typing import Any
from typing import Dict
from typing import List


def parse_timeseries(
    timeseries_str, time_input_unit="minute", time_output_unit="second"
) -> List[List[float]]:
    """Create a list of 2-list [timestep (seconds), value (mm/hour)]."""
    if not timeseries_str:
        return [[]]
    output = []
    for line in timeseries_str.split():
        timestep, value = line.split(",")
        if time_input_unit == "second":
            timestep = int(timestep.strip())
        else:
            timestep = int(timestep.strip())
            if time_output_unit == "second":
                timestep *= 60
        output.append([timestep, float(value.strip())])
    return output


def strip_dict_none_values(value: Any):
    if isinstance(value, List):
        for x in value:
            strip_dict_none_values(x)
    if isinstance(value, Dict):
        to_delete = []
        for k, v in value.items():
            if v == None:
                to_delete.append(k)
            else:
                strip_dict_none_values(v)

        for x in to_delete:
            del value[x]
