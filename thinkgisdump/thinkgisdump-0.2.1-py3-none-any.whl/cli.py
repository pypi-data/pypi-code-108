import argparse
import json
import re
import sys
from urllib.parse import parse_qs, urlparse

import lxml.etree
import lxml.html
import requests

from .geom import parse_geometry


def parse_feature(content, feat_id):
    # Need to manually remove CData here because it contains HTML which lxml reads as
    # an invalid end to the CData section
    cdata_section = re.search(r"\<!\[CDATA.*\]\]\>", content).group()
    html_str = re.search(r"(?<=A\[).*(?=\]\])", cdata_section).group()
    html_tree = lxml.html.fromstring(html_str)
    feature_props = {"id": feat_id}
    for row in html_tree.xpath("//tr"):
        field = row.xpath("//td[@class='ftrfld']/text()")[0].strip()
        value = row.xpath("//td[@class='ftrval']/text()")[0].strip()
        feature_props[field] = value

    xml_str = content.replace(cdata_section, "")
    tree = lxml.etree.fromstring(xml_str)
    geometry = parse_geometry(tree.xpath("//poly/text()"))

    return {"type": "Feature", "properties": feature_props, "geometry": geometry}


def get_feature(baseurl, layer_id, feat_id):
    content = requests.get(
        f"{baseurl}/tgis/getftr.aspx", params={"D": layer_id, "F": feat_id, "Z": "1"}
    ).text

    return parse_feature(content, feat_id)


def get_feature_ids(baseurl, layer_id, count):
    content = requests.get(
        f"{baseurl}/tgis/Index.ashx",
        params={"action": "getFtrs", "dsid": layer_id, "cnt": count},
    ).content

    # The text is returned invalid because it's using \x1e and \x1f as separators, but
    # immediately next to numbers which is causing Python to try and interpret the whole
    # sequence as a unicode character. \x1e separates groupings of (index, id, name) and
    # \x1f separates items within that, so we can use that to parse out items
    escaped_text = content.decode().encode("unicode-escape").decode()
    return [
        feature_group.split("\\x1f")[1] for feature_group in escaped_text.split("\\x1e")
    ]


def get_feature_count(baseurl, layer_id):
    content = requests.get(
        f"{baseurl}/tgis/Index.ashx", params={"action": "layerIndex", "dsid": layer_id}
    ).text
    tree = lxml.etree.fromstring(content)
    data = tree.xpath("//bigTable/text()")[0]
    return data.split("|")[2]


def parse_args(args):
    parser = argparse.ArgumentParser(description="Scrape GeoJSON from ThinkGIS sites")
    parser.add_argument(
        "url",
        help=(
            "ThinkGIS server URL, layer ID will be parsed from the dsid query param "
            "if present"
        ),
    )
    parser.add_argument(
        "-l", "--layer-id", help="Layer ID (in the dsid query param) to be scraped"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Output file name, defaults to stdout",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        default=False,
        action="store_true",
        help="Suppress logging of feature requests",
    )
    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])
    parsed_url = urlparse(args.url)

    baseurl = f"{parsed_url.scheme}://{parsed_url.netloc}"
    url_params = parse_qs(parsed_url.query)
    layer_id = args.layer_id or url_params.get("dsid")
    if not layer_id:
        raise ValueError(
            "Layer ID is required in either the URL or the --layer-id flag"
        )

    feature_count = get_feature_count(baseurl, layer_id)
    feature_ids = get_feature_ids(baseurl, layer_id, feature_count)

    args.output.write('{"type": "FeatureCollection", "features": [\n')
    # Use the parsed feature IDs to request XML data for each feature
    for idx, feat_id in enumerate(feature_ids):
        feature = get_feature(baseurl, layer_id, feat_id)
        sep = ",\n"
        if idx == len(feature_ids) - 1:
            sep = "\n"
        args.output.write(f"{json.dumps(feature)}{sep}")
        if not args.quiet:
            print(f"Parsed feature {feat_id}", file=sys.stderr)

    args.output.write("]}")


if __name__ == "__main__":
    main()
