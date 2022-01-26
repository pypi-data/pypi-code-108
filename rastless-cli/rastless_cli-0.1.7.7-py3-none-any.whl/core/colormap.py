import xmltodict

from rastless.db.models import ColorMap


def hex_to_rgba_interval(hex_color, opacity):
    """
    Hex to RGBA for matplotlib colormap generation
    :param hex_color: e.g. "#4287f5"
    :param opacity: Float / Str value in a closed interval [0, 1]
    :return: RGBA (red, green, blue, alpha) tuple of float values in a closed interval [0, 1]
    """
    hex_value = hex_color.lstrip('#')
    rgb = tuple(int(hex_value[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return rgb + (float(opacity),)


def create_colormap(name: str, sld_filepath: str, description: str) -> ColorMap:
    with open(sld_filepath, "rb") as fobj:
        xml = xmltodict.parse(fobj)

    entries = xml['sld:StyledLayerDescriptor']["sld:NamedLayer"]["sld:UserStyle"]["sld:FeatureTypeStyle"]["sld:Rule"][
        "sld:RasterSymbolizer"]["sld:ColorMap"]["sld:ColorMapEntry"]

    levels = [float(entry['@quantity']) for entry in entries]
    colors = [hex_to_rgba_interval(entry["@color"], entry.get("@opacity", 1)) for entry in entries]
    return ColorMap(name=name, levels=levels, colors=colors, description=description)
