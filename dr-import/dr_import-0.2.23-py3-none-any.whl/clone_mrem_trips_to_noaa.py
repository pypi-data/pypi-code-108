import argparse

from dr_import import clone_mrem_section

def main(
        host: str,
        token: str,
        section_name: str,
        year: int) -> None:
    """ Clones the given NEMM MREM section to NOAA's review project the without copying annotations

    :param host: Tator URL
    :param token: Tator API token
    :param section_name: Section to clone

    """

    print("\n")
    print("----------------------------------------------------------------")
    print("Clone MREM NEMM Tator Trip to NOAA's Tator Project: STARTED")
    print("----------------------------------------------------------------")
    print("\n")

    if year == 2020:
        clone_mrem_section.main(
            in_host=host,
            in_token=token,
            in_src_project=30,
            in_dest_project=32,
            in_src_section_name=section_name,
            in_dest_section_name=section_name,
            in_copy_annotations=False)

    elif year == 2021:
        clone_mrem_section.main(
            in_host=host,
            in_token=token,
            in_src_project=57,
            in_dest_project=60,
            in_src_section_name=section_name,
            in_dest_section_name=section_name,
            in_copy_annotations=False)

    else:
        print("\n")
        print("ERROR: Valid fishing year values are 2020, 2021")
        return

    print("\n")
    print("----------------------------------------------------------------")
    print("Clone MREM NEMM Tator Trip to NOAA's Tator Project: FINISHED")
    print("----------------------------------------------------------------")
    print("\n")

def parse_args() -> None:
    """ Process script's arguments
    """

    parser=argparse.ArgumentParser()
    parser.add_argument('--host', type=str,default='https://www.tatorapp.com')
    parser.add_argument("--token", type=str, required=True, help="Tator API user token")
    parser.add_argument("--trip-name", type=str, required=True, help="Name of section/trip in NEMM MREM Tator Project to clone")
    parser.add_argument("--year", type=int, required=True, help="Fishing Year")
    args = parser.parse_args()
    return args

def script_main() -> None:
    """ Script's entry point
    """

    args = parse_args()
    main(host=args.host, token=args.token, section_name=args.trip_name, year=args.year)

if __name__ == "__main__":
    script_main()