import os
from hestia_earth.utils.lookup import column_name, get_table_value, load_lookup
from hestia_earth.utils.tools import non_empty_list

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def ecoinventV3_impacts(ecoinventName: str):
    lookup = load_lookup(filepath=f"{os.path.join(CURRENT_DIR, 'ecoinventV3')}.csv", keep_in_memory=True)

    def emission(index: int):
        id = get_table_value(
            lookup, column_name('ecoinventName'), ecoinventName, column_name(f"emissionsResourceUse.{index}.term.id")
        )
        value = get_table_value(
            lookup, column_name('ecoinventName'), ecoinventName, column_name(f"emissionsResourceUse.{index}.value")
        )
        return (id, value) if id else None

    return non_empty_list(map(emission, range(0, 12)))
