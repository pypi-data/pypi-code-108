import os
import logging
import googlemaps
import pandas as pd


def get_coord(*args):

    gmaps_args = ", ".join(tuple(map(str, filter(lambda x: x is not None, args))))

    gmaps_key = os.getenv("GOOGLE_MAPS_KEY")

    assert gmaps_key is not None, "GOOGLE_MAPS_KEY not found in environment variables."

    gmaps = googlemaps.Client(key=gmaps_key)

    try:
        location = gmaps.geocode(gmaps_args)
        lat = location[0]["geometry"]["location"]["lat"]
        long = location[0]["geometry"]["location"]["lng"]

        if pd.isna(lat):
            location = gmaps.geocode(gmaps_args)
            lat = location[0]["geometry"]["location"]["lat"]
            long = location[0]["geometry"]["location"]["lng"]
    except Exception as err:
        logging.error(err)
        lat = np.nan
        long = np.nan

    return lat, long

    print(", ".join(not_null_args))
