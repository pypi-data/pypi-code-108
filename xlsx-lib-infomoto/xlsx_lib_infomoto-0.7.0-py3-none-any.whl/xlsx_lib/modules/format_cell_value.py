from typing import Optional


def format_cell_value(cell_value: Optional[str]) -> Optional[str]:
    if cell_value is None:
        return None

    cell_value = str(cell_value) \
        .lstrip() \
        .rstrip() \
        .replace("b'", "") \
        .replace("'", "")

    if cell_value in ["-"]:
        return None

    for spaces in ["   ", "  "]:
        cell_value = cell_value.replace(spaces, " - ")

    # TODO: To dict replace
    if "OHMIOS" in cell_value:
        cell_value = cell_value.replace("OHMIOS", "Ω")

    return cell_value
