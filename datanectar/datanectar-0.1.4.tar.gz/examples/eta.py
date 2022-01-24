import os
import argparse
import pandas as pd

ROLLUPS_DIR = 'rollups'

def get_eta(origin, dest):
    # NOTE: This only works for nodes which are adjacent; in order for full route eta, we
    # would need to either (1) pass in route plan or (2) do to-ultimate-destination calculations
    latest_rollup = sorted(os.listdir(ROLLUPS_DIR))[-1]
    rollup = pd.read_parquet(f'{ROLLUPS_DIR}/{latest_rollup}')['travel_time']
    eta = rollup[(int(origin), int(dest))]
    return eta
    

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-o', '--origin', required=True)
    ap.add_argument('-d', '--dest', required=True)

    args = ap.parse_args()
    origin = args.origin
    dest = args.dest
    print(f'ETA from {origin} to {dest}...')
    eta = get_eta(origin, dest)
    print(f'ETA: {eta}')

