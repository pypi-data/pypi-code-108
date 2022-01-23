from hestia_earth.utils.lookup import download_lookup, _get_single_table_value, column_name, extract_grouped_data
from hestia_earth.utils.tools import safe_parse_float


def get_ecoClimateZone_lookup_value(eco_climate_zone: str, col_name: str, group_name: str = None) -> float:
    """
    Get a value from the `ecoClimateZone` lookup table.

    Parameters
    ----------
    eco_climate_zone : str
        The `ecoClimateZone` as a string.
    col_name : str
        The name of the column in the lookup table.
    group_name : str
        Optional - the name of the group if the data is in the format `group1:value1;group2:value2`.

    Returns
    -------
    float
        The value associated with the `ecoClimateZone`.
    """
    try:
        lookup = download_lookup('ecoClimateZone.csv', True)
        code = int(str(eco_climate_zone))
        data = _get_single_table_value(lookup, column_name('ecoClimateZone'), code, column_name(col_name))
        return safe_parse_float(
            data if group_name is None else extract_grouped_data(data, group_name)
        )
    except Exception:
        return 0
