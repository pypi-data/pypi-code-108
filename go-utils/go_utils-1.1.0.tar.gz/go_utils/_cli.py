import argparse

import matplotlib.pyplot as plt
import pandas as pd

from go_utils import lc, mhm
from go_utils.download import convert_dates_to_datetime, get_api_data
from go_utils.geoenrich import get_country_api_data
from go_utils.photo_download import download_lc_photos, download_mhm_photos

protocol_map = {"mosquito": "mosquito_habitat_mapper", "landcover": "land_covers"}


def add_download_args(parser):
    parser.add_argument("--out", "-o", help="Output Directory of the command")
    parser.add_argument(
        "--start",
        "-s",
        help="Start date (if you want data from the api, so don't specify -i)",
    )
    parser.add_argument(
        "--end",
        "-e",
        help="End date (if you want data from the api, so don't specify -i)",
    )
    parser.add_argument(
        "--countries",
        "-co",
        help="Desired Countries separated by commas (if you want data from the api, so don't specify -i)",
    )
    parser.add_argument(
        "--regions",
        "-r",
        help="Desired Regions separated by commas (if you want data from the api, so don't specify -i)",
    )
    parser.add_argument(
        "--box",
        "-b",
        help="Bounding Box (if you want data from the api, so don't specify -i). Put coordinates in order of 'min lat, min lon, max lat, max lon'",
        type=list,
    )


def download_data(protocol, args):
    func_args = {"protocol": protocol}
    if args.start:
        func_args["start_date"] = args.start
    if args.end:
        func_args["end_date"] = args.end
    if args.box:
        coords = [float(coord.strip()) for coord in args.box.split(",")]
        box = {
            "min_lat": coords[0],
            "min_lon": coords[1],
            "max_lat": coords[1],
            "max_lon": coords[3],
        }
        func_args["latlon_box"] = box
    if args.countries:
        func_args["countries"] = [
            country.strip() for country in args.countries.split(",")
        ]
    if args.regions:
        func_args["regions"] = [region.strip() for region in args.regions.split(",")]

    if "countries" in func_args or "regions" in func_args:
        df = get_country_api_data(**func_args)
    else:
        df = get_api_data(**func_args)

    return df


def mhm_data_download():
    parser = argparse.ArgumentParser(
        description="GLOBE Observer Mosquito Habitat Mapper API Download CLI"
    )
    add_download_args(parser)
    parser.add_argument(
        "--hasgenus",
        "-hg",
        help="Filter data if it has a genus as a record",
        action="store_true",
    )
    parser.add_argument(
        "--iscontainer",
        "-ic",
        help="Filter data if the record's watersource is a container",
        action="store_true",
    )
    parser.add_argument(
        "--hasphotos",
        "-hp",
        help="Filter data if it has photo records",
        action="store_true",
    )
    parser.add_argument(
        "--minlarvae", "-ml", help="Filter data by minimum larvae count", type=int
    )
    args = parser.parse_args()
    df = download_data("mosquito_habitat_mapper", args)

    filter_args = {}
    filter_args["has_genus"] = args.hasgenus
    filter_args["is_container"] = args.iscontainer
    filter_args["has_photos"] = args.hasphotos

    if args.minlarvae:
        filter_args["min_larvae_count"] = args.minlarvae

    df = mhm.qa_filter(df, **filter_args)

    if args.out:
        df.to_csv(args.out)
    else:
        mhm.diagnostic_plots(df)
        plt.show()


def lc_data_download():
    parser = argparse.ArgumentParser(
        description="GLOBE Observer Land Cover API Download CLI"
    )
    add_download_args(parser)

    # TODO: Group args to reduce user confusion
    parser.add_argument(
        "--hasclassification",
        "-hc",
        help="Filter data if it has atleast one classification as a record",
        action="store_true",
    )
    parser.add_argument(
        "--hasphoto",
        "-hp",
        help="Filter data if it has atleast one photo as a record",
        action="store_true",
    )
    parser.add_argument(
        "--hasallclassifications",
        "-hac",
        help="Filter data if it has all classifications for each record",
        action="store_true",
    )
    parser.add_argument(
        "--hasallphotos",
        "-hap",
        help="Filter data if it has all photos for each record",
        action="store_true",
    )
    args = parser.parse_args()
    df = download_data("land_covers", args)

    filter_args = {}
    filter_args["has_classification"] = args.hasclassification
    filter_args["has_photo"] = args.hasphoto
    filter_args["has_all_classifications"] = args.hasallclassifications
    filter_args["has_all_photos"] = args.hasallphotos
    df = lc.qa_filter(df, **filter_args)

    if args.out:
        df.to_csv(args.out)
    else:
        lc.diagnostic_plots(df)
        plt.show()


def mhm_photo_download():
    parser = argparse.ArgumentParser(
        description="GLOBE Observer Mosquito Habitat Mapper Photo Downloader CLI"
    )
    parser.add_argument("input", help="Input Directory of the command")
    parser.add_argument("out", help="Output Directory of the command")

    photo_group = parser.add_argument_group(
        "Photo Types", "Includes: larvae, watersource, abdomen, all"
    )
    photo_group.add_argument(
        "--larvae", "-l", help="Include Larvae Photos", action="store_true"
    )
    photo_group.add_argument(
        "--watersource", "-w", help="Include Watersource Photos", action="store_true"
    )
    photo_group.add_argument(
        "--abdomen", "-ab", help="Include Abdomen Photos", action="store_true"
    )

    photo_group.add_argument(
        "--all",
        "-a",
        help="Include all of the flags",
        action="store_true",
    )

    name_group = parser.add_argument_group(
        "Photo Naming", "Allows naming customization"
    )
    name_group.add_argument(
        "--name_additional",
        "-add",
        help="Include additonal info in photo names.",
        type=str,
        action="store",
    )

    mhm_name_fields = [
        "url_type",
        "watersource",
        "latitude",
        "longitude",
        "date_str",
        "mhm_id",
        "classification",
    ]
    name_group.add_argument(
        "--nargs_include",
        "-in",
        nargs="+",
        help="Include these fields from photo names.",
        choices=mhm_name_fields,
        type=str,
        action="store",
    )

    args = parser.parse_args()

    download_args = {}
    if not args.larvae:
        download_args["larvae_photo"] = ""
    if not args.watersource:
        download_args["watersource_photo"] = ""
    if not args.abdomen:
        download_args["abdomen_photo"] = ""

    df = pd.read_csv(args.input)
    convert_dates_to_datetime(df)

    if args.all:
        download_mhm_photos(
            df,
            args.out,
            include_in_name=args.nargs_include,
            additional_name_stem=args.name_additional,
        )
    else:
        download_mhm_photos(
            df,
            args.out,
            **download_args,
            include_in_name=args.nargs_include,
            additional_name_stem=args.name_additional
        )


def lc_photo_download():
    parser = argparse.ArgumentParser(
        description="GLOBE Observer Land Cover Photo Downloader CLI"
    )
    parser.add_argument("input", help="Input Directory of the command")
    parser.add_argument("out", help="Output Directory of the command")

    photo_group = parser.add_argument_group(
        "Photo Types", "Includes: up, down, north, south, east, west"
    )
    photo_group.add_argument(
        "--up", "-u", help="Include Upward Photos", action="store_true"
    )
    photo_group.add_argument(
        "--down", "-d", help="Include Downward Photos", action="store_true"
    )
    photo_group.add_argument(
        "--north", "-n", help="Include Northern Photos", action="store_true"
    )
    photo_group.add_argument(
        "--south", "-s", help="Include Southern Photos", action="store_true"
    )
    photo_group.add_argument(
        "--east", "-e", help="Include Eastern Photos", action="store_true"
    )
    photo_group.add_argument(
        "--west", "-w", help="Include Western Photos", action="store_true"
    )
    photo_group.add_argument(
        "--all", "-a", help="Include All Photos", action="store_true"
    )

    name_group = parser.add_argument_group(
        "Photo Naming", "Allows naming customization"
    )
    name_group.add_argument(
        "--name_additional",
        "-add",
        help="Include additonal info in photo names.",
        type=str,
        action="store",
    )

    lc_name_fields = ["direction", "latitude", "longitude", "date_str", "lc_id"]
    name_group.add_argument(
        "--nargs_include",
        "-in",
        nargs="+",
        help="Exclude these fields from photo names.",
        choices=lc_name_fields,
        type=str,
        action="store",
    )

    args = parser.parse_args()

    download_args = {}
    if not args.up:
        download_args["up_photo"] = ""
    if not args.down:
        download_args["down_photo"] = ""
    if not args.north:
        download_args["north_photo"] = ""
    if not args.south:
        download_args["south_photo"] = ""
    if not args.east:
        download_args["east_photo"] = ""
    if not args.west:
        download_args["west_photo"] = ""

    df = pd.read_csv(args.input)
    convert_dates_to_datetime(df)

    if args.all:
        download_lc_photos(
            df,
            args.out,
            include_in_name=args.nargs_include,
            additional_name_stem=args.name_additional,
        )
    else:
        download_lc_photos(
            df,
            args.out,
            **download_args,
            include_in_name=args.nargs_include,
            additional_name_stem=args.name_additional
        )
