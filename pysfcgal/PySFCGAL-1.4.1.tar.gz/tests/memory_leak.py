from pysfcgal.sfcgal import read_wkt


def wkt_leak():
    while True:
        p = read_wkt("POINT (1 2)")
        p.wkt


if __name__ == "__main__":
    wkt_leak()
